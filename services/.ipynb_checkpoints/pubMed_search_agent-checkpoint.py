import services.pubmed_api as pubmed_api
from langchain.schema import HumanMessage
from langchain_community.embeddings.gigachat import GigaChatEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_transformers import (
    LongContextReorder,
)
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain, StuffDocumentsChain



class PubMedSearchAgent:
    def __init__(self, llm):
        self.llm           = llm
        self.pubmedAPI     = pubmed_api.PubmedAPI()
        
    def translate_text(self, text, target_lang):
        # Assuming we have a method in OpenAI to perform translation
        prompt = f"Translate the following text to {target_lang}: {text}"
        response = self.llm.invoke(prompt)
        return response.content.strip()
    
    def process_user_input(self, user_input):
        # Создание промпта для LLM, который преобразует вопрос пользователя в поисковые запросы для PubMed
        prompt = (
            "I am an AI designed to assist with scientific research. I need to convert a user's question "
            "from Russian into five distinct sets of key English terms for a PubMed search query. "
            "These terms will be used to retrieve relevant scientific articles. "
            "Please provide five separate sets of search terms, formatted as lists in Python:\n\n"
            f"User's question in Russian: '{user_input}'\n\n"
            "Translated and formatted search terms for PubMed in English:"
        )
        original_lang = "Russian" if self.is_russian(user_input) else "English"
        response = self.llm.invoke(prompt)  # Предполагается метод invoke для обращения к LLM
        return self.parse_model_output(response.content), original_lang

    def del_spec_chars(self, text):
        for char in list("!@#$%^&*()_+.,[]{}\\|/\"'~`"):
            text = text.replace(char, '')
        return text


    def parse_model_output(self, output):
        # Парсинг выходных данных LLM для извлечения ключевых слов
        lines = output.split('\n')
        keyword_lists = []
        for line in lines:
            clean_line = line.strip().split('. ')[-1]
            #keywords = [format_fields(self.del_spec_chars(keyword).strip(), search_fields)  for keyword in clean_line.split(',')]
            keywords = [self.del_spec_chars(keyword).strip()  for keyword in clean_line.split(',')]
            keyword_lists.extend(keywords)
        return list(set(keyword_lists))

    def get_query_by_keywords(self, user_query, keyword_lists):
        prompt = f'''Given the user query and the list of key terms, generate a precise and effective search query using logical operators for a medical document search system
        User's question: '{user_query}'
        List of key terms: {keyword_lists}
        Generated search query:
        '''
        return self.llm.invoke([HumanMessage(content=prompt)]).content
    
    def execute_queries(self, api_query):
        results = self.pubmedAPI.get_articles(api_query)
        return [ self.pubmedAPI.parse_record(one_pub['id'], one_pub['data'])['abstract'] for one_pub in results]

    def is_russian(self, text):
        return any(char in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя' for char in text.lower())

    def process_query (self, user_query):
        keyword_lists, lang = self.process_user_input(user_query)
        api_query = self.get_query_by_keywords(user_query, keyword_lists)
        search_results = self.execute_queries(api_query)

        texts = []
        for result in search_results: #.items(): #query_num
            texts.append(result)

        embeddings = GigaChatEmbeddings(credentials=self.llm.credentials, scope='GIGACHAT_API_CORP', verify_ssl_certs=False)
        retriever = FAISS.from_texts(texts, embedding=embeddings).as_retriever(
            search_kwargs={"k": 10}
        )
        if self.is_russian(user_query):
            eng_user_query = self.translate_text(user_query, "Russian")
        else:
            eng_user_query = user_query
        docs = retriever.invoke(eng_user_query)
        reordering = LongContextReorder()
        reordered_docs = reordering.transform_documents(docs)

        document_prompt = PromptTemplate(
            input_variables=["page_content"], template="{page_content}"
        )
        document_variable_name = "context"
        stuff_prompt_override = """Given this text extracts:
        -----
        {context}
        -----
        Please answer the following question:
        {query}"""
        prompt = PromptTemplate(
            template=stuff_prompt_override, input_variables=["context", "query"]
        )

        llm_chain = LLMChain(llm=self.llm, prompt=prompt)
        chain = StuffDocumentsChain(
            llm_chain=llm_chain,
            document_prompt=document_prompt,
            document_variable_name=document_variable_name,
        )
        answer = chain.run(input_documents=reordered_docs, query=user_query)

        if lang == "Russian":
            return self.translate_text(answer, "Russian")
        else:
            return answer

def test_PubMedSearchAgent(llm):
        user_query = 'Что нового в лечении рака груди?'
        pma = PubMedSearchAgent(llm)
        op = pma.process_query(user_query)
        print(op)
        
