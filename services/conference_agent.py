from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import requests

def get_text_from_url(url):
    response = requests.request("GET", url)
    return BeautifulSoup(response.text).get_text()

class ConferenceAgent:
    def __init__(self, llm):
        self.llm           = llm
        self.guap_data     = None
        self.informer_data = None
        self.guap_text     = ''
        self.informer_text = ''
        self.cat_text      = ''
        if self.guap_data     is None:
            self.get_conferences_from_guap()
        if self.informer_data is None:
            self.get_conferences_from_informer()
        if self.cat_text == '':
            self.get_titles_texts()

    def get_conferences_from_guap(self, date_check = datetime(2024, 1, 24, 21, 23, 44, 356951)):
        url_conference = "https://api.guap.ru/data/get-nidannoconfs"
        response_conference = requests.request("GET", url_conference) #, headers=headers, data=payload, verify=False)
        jrc = response_conference.json()
        df_jrc = pd.DataFrame(jrc)
        df_jrc['bdf'] = df_jrc['DateBegin'].apply(datetime.fromisoformat) #[0]
        self.guap_data = df_jrc[df_jrc['bdf'] > date_check] 
        return self.guap_data

    def get_conferences_from_informer(self):
        def get_datakonferencii(_args):
            str_data = "ci=1"
            str_data += '&category='        + _args[0];
            str_data += '&count='           + _args[1];
            str_data += '&color='           + _args[2];
            str_data += '&title_color='     + _args[3];
            str_data += '&text_color='      + _args[4];
            str_data += '&title_font_size=' + _args[5];
            str_data += '&text_font_size='  + _args[6];
            str_data += '&field_sorting='   + _args[7];
            str_data += '&sorting='         + _args[8];
            return str_data
        data =get_datakonferencii( ["106,127,128,131,132,134,137,139,142,143", "15", "#ffffff", "#008efa", "#000000", "16", "14", "date_creation", "desc"])
        headers = {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
        my_url = 'https://na-konferencii.ru/wp-content/themes/conference/informer.php'
        response = requests.request("POST", my_url, headers=headers, data=data) #,  data=payload, verify=False)
        parsed_html = BeautifulSoup(response.text)
        moid = {mo[1]:str(mo[0]+1) for mo in enumerate(['января','февраля','марта','апреля','мая','июня','июля','августа', 'сентября','октября','ноября','декабря'] )}
        confs = parsed_html.find_all("div", { "class" : "conference-slider-slide-item" })
        self.informer_data = []
        for conf in confs:
            title = conf.find("a").getText() 
            href = conf.find("a", href=True)['href'] 
            interval = conf.find("p", { "class" : "conference-list-date" }).getText() 
            splited = interval.split()
            place = conf.find_all("p")[-1].getText() 
            begin = splited[:1] + [moid[splited[1].lower()]] +splited[-2:-1]
            end   = [splited[3]] + [moid[splited[4].lower()]] + [splited[5]]
            begin.reverse()
            end.reverse() 
            date_begin = datetime(*map(int, begin))
            date_end = datetime(*map(int, begin))
            self.informer_data.append(  { 'Title' : title,
                             'SiteLink'  : href,
                             'DateBegin' : date_begin,
                             'DateEnd'   : date_end,
                             'Place' : place
                           }  )
        return self.informer_data

    def get_titles_texts(self):
        self.guap_texts = [ "id:"+str(titlesid) +", " + titletext  for titlesid, titletext in enumerate(list(self.guap_data['Title']))]
        self.informer_texts = [ "id:"+str(titlesid+len(self.guap_texts)) +",  " + titletext['Title']  for titlesid, titletext in enumerate(list(self.informer_data))]
        self.cat_text = "\n".join(self.guap_texts+self.informer_texts)
        return self.cat_text
    
    def check_idx(self, idx, source1, source2):
        if idx < len(source1):
            return list(source1['Info'])[idx]
        elif idx< len(source1)+ len(source2):
            return get_text_from_url(  source2[idx-len(source1)]['SiteLink'] )
        else:
            assert False, "Указанный идентификатор выходит за границы массива"
            
    def get_info_by_id(self, idx, source1, source2):
        if idx < len(source1):
            info = { tag:list(source1[tag])[idx] for tag in ['DateBegin', 'DateEnd', 'Title', 'Place', 'SiteLink']}
        elif idx< len(source1)+ len(source2):
            info = { tag:source2[idx - len(source1) ][tag] for tag in ['DateBegin', 'DateEnd', 'Title', 'Place', 'SiteLink']}
        else:
            assert False, "Указанный идентификатор выходит за границы массива"
        return info

    def process_query (self, user_query):

        conf_idx = []
        counter = 0
        while (len(conf_idx) == 0) and (counter < 3) :
            counter += 1
            answer = self.llm.invoke('По запросу пользователя: ['+user_query+'] выведи чисела id наиболее подходящих конференций : ' + self.cat_text ).content
            conf_idx = [int(one_char.strip()) for one_char in answer.split(',') if (one_char.strip().isdigit()) and ( int(one_char.strip()) < (len( self.guap_data )+len( self.informer_data )) )]
        if (len(conf_idx) == 0):
            return '', None 
        descr =[ (self.check_idx(oneidx, self.guap_data ,  self.informer_data), oneidx)  for oneidx in conf_idx]    
        # display('answer',   answer)
        # display('conf_idx', conf_idx)
        # display('descr',    descr)
        resp = []
        for conf_info, oneidx in descr:
            q = 'Напиши ответ да или нет. Соответствует ли запрос ['+user_query+'] одному из научных направлений данной конференции : [' + conf_info + ']'
            r1 = self.llm.invoke(q).content
            if r1.lower()[:2] == 'да':
                resp.append(oneidx)
        if len(resp) != 0:
            
            row = self.get_info_by_id(resp[0], self.guap_data, self.informer_data)
            textrows = row['DateBegin'] + ' ' + row['Title'] + ' ' + row['Place']
            text_request =  self.llm.invoke("Напиши очень краткий анонс конференции, на которой не точно, но скорее всего будет информация по "+user_query+" : ["+textrows+"]").content
            #text_request =  self.llm.invoke("Очень кратко сообщи что будет конференция, на которой не точно, но скорее всего будет информация по "+user_query+" : ["+textrows+"]").content
            #text_request =  self.llm.invoke("По запросу ["+user_query+"] очень кратко сообщи когда и где будет конференция, на которой  : ["+textrows+"]").content
            return text_request, row
        else:
            return '', None

def test_ConferenceAgent(llm):
        user_query = 'Что нового в лечении рака груди?'
        ca = ConferenceAgent(llm)
        op = ca.process_query(user_query)
        print(op)
        
