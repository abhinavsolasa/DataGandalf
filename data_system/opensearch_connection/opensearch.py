import os
import json
from typing import Any

from opensearchpy import OpenSearch

from dotenv import load_dotenv

load_dotenv()

class OpenSearchManager:
    def __init__(self):
        port = os.environ.get('OS_PORT')
        host = 'localhost'
        auth = (os.environ.get('OPENSEARCH_USER'), os.environ.get('OPENSEARCH_PW'))
        print(auth)
        self.client = OpenSearch(
            hosts = [{'host': host, 'port': port}],
            http_compress = True, # enables gzip compression for request bodies
            http_auth = auth
        )

    ## to be redefined later in compliance with RAG techinque
    def search(self, q, index_name):
        #Validate query using self.client.indices.validate_query first?

        query = {
        'size': 10,
        'query': {
                'multi_match': {
                'query': q,
                'fields': ['topic', 'tag']
                }
            }
        }

        response = self.client.search(
            body = query,
            index = index_name
        )

        return response

        
    def create_index(self, name):
        if self.get_index_by_name("test-blog") == True:
            self.delete_index("test-blog")
        if name == None: 
            raise NameError(f"No index could be found with name {name}")
        try:
            self.get_index_by_name(name)
        except:
            raise NameError(f"Index {name} already exists.")
        
        index_body = {
            'settings': {
                'index': {
                    'number_of_shards': 4
                }
            }
        }

        response = self.client.indices.create(name, index_body)

        return response
    
    def delete_index(self, alias):
        if self.get_index_by_name(alias):
            self.client.indices.delete(alias)
        else:
            raise NameError(f"No index could be found with name {alias}")
        
    def get_index_by_name(self, alias):
        assert alias != None
        if alias == None:
            raise NameError(f"No index could be found with name {alias}")
        try:
            return self.client.indices.get(alias).__contains__(alias)
        except:
            return False
        
    def populate_index(self, name, folder_path):
        # index data
        data_list: Any = []
        for filename in os.listdir(folder_path):
            if filename.endswith('.json'):
                file_path = os.path.join(folder_path, filename)
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    data_list.append({"create": {"_index": name}})
                    data_list.append(data)
        
        response = self.client.bulk(data_list)
        if response["errors"]:
            print(file_path)
            print(f"There were errors!")
            for item in response["items"]:
                print(f"{item['index']['status']}: {item['index']['error']['type']}")
        else:
            print(f"Bulk-inserted {len(response['items'])} items.")

    def clear_index(self, name, body):
        self.client.delete_by_query(name, body)
