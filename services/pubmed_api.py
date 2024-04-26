from Bio import Entrez


class PubmedAPI:
    def __init__(self):
        pass

    def get_articles(self, query: str):
        # Set search parameters
        search_params = {
            'retmax': 10,  # Number of results to retrieve (max 10,000)
            'usehistory': 'y',  # Use history (allows for retrieval of previous search results)
            'sort': 'relevance',  # Sort results by relevance (default: publication date)
        }

        # Send search request to PubMed
        search_handle = Entrez.esearch(db='pubmed', term=query, **search_params)

        # Parse search results
        search_results = Entrez.read(search_handle)

        # Retrieve details for each search result
        records = []
        for id_ in search_results['IdList']:
            fetch_handle = Entrez.efetch(db='pubmed', id=id_, retmode='xml')
            record = Entrez.read(fetch_handle)
            records.append({'id': id_, 'data': record})

        return records

    def parse_record(self, rec_id, record):
        if len(record.get('PubmedArticle', None)) == 0:
            return {'id': '', 'title': '', 'journal': '', 'abstract': ''}    
        title = record.get('PubmedArticle', None)[0].get('MedlineCitation', None).get('Article', None).get(
            'ArticleTitle', None)
        journal = record.get('PubmedArticle', None)[0].get('MedlineCitation', None).get('Article', None).get('Journal',
                                                                                                             None).get(
            'Title')
        abstract = \
        record.get('PubmedArticle')[0].get('MedlineCitation').get('Article').get('Abstract').get('AbstractText')[0]
        # ids = record.get('PubmedArticle')[0].get('MedlineCitation').get('Article').get('ELocationID')
        # article_date = record['PubmedArticle'][0]['MedlineCitation']['Article']['ArticleDate']

        parsed_dict = {'id': rec_id, 'title': title, 'journal': journal, 'abstract': abstract}
        return parsed_dict
