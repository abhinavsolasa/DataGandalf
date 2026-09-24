import os
import json
from time import sleep
from typing import Any
from opensearchpy import OpenSearch
from dotenv import load_dotenv
import requests

load_dotenv()

# Opensearch API call timeout
WAIT = 0.25

class OpenSearchManager:
    def __init__(self):
        port = os.environ.get('OS_PORT')
        host = 'localhost'
        auth = (os.environ.get('OPENSEARCH_USER'), os.environ.get('OPENSEARCH_PW'))
        self.client = OpenSearch(
            hosts = [{'host': host, 'port': port}],
            http_compress = True, # enables gzip compression for request bodies
            http_auth = auth
        )

        # RAG STUFF
        self.cluster_set = False
        self.connector_id = None
        self.llm_model = "huggingface/sentence-transformers/all-MiniLM-L6-v2"
        self.model_id = None
        self.model_group = None
        self.rag = False


    ## to be redefined later in compliance with RAG techinque
    def search(self, q, index_name):
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
        
    def create_index(self, name, rag_true=False):
        if self.get_index_by_name(name) == True:
            self.delete_index(name)
        if name == None: 
            raise NameError(f"No index could be found with name {name}")
        try:
            self.get_index_by_name(name)
        except:
            raise NameError(f"Index {name} already exists.")
        
        index_body = {
            "settings": {
                "index.number_of_shards" : 4        # Only required argument for regular search 
            },
            "mappings": {
                "properties": {
                "text": {
                    "type": "text"
                }
                }
            }
        }
        if rag_true:
            index_body["settings"]["index.search.default_pipeline"] = "rag_pipeline"

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
        if not self.client.indices.exists(name):
            response = self.create_index(name)

            print(response)

        # index data
        data_list: Any = []
        i = 0
        for filename in os.listdir(folder_path):
            i += 1
            if filename.endswith('.json'):
                file_path = os.path.join(folder_path, filename)  # Full path to JSON file
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    data_list.append({"index": {"_index": name, "_id": i}})
                    data_list.append(data)
        
        response = self.client.bulk(data_list)
        if response["errors"]:
            print(file_path)
            print(f"There were errors!")
            for item in response["items"]:
                print(f"{item['index']['status']}: {item['index']['error']['type']}")
        else:
            print(f"Bulk-inserted {len(response['items'])} items.")
        
        return response


    ################## RAG/GPT PIPELINE ####################

    def set_cluster_settings(self):
        if not self.cluster_set:
            cluster_settings = {
                "persistent": {
                    "plugins": {
                        "ml_commons": {
                            "memory_feature_enabled": True,
                            "allow_registering_model_via_url": True,
                            "only_run_on_ml_node": False,
                            "model_access_control_enabled": True,
                            "native_memory_threshold": "99",
                            "rag_pipeline_feature_enabled": True,
                            "trusted_connector_endpoints_regex": [
                                "^https://api-inference\\.huggingface\\.co/.*$"
                            ]
                        }
                    }
                }
            }
            response = self.client.http.put("/_cluster/settings", body=cluster_settings)
            # print(response)
            self.cluster_set = response["acknowledged"] == True
        
        return self.cluster_set            
    

    def set_connector(self):
        if self.connector_id is None:    
            # Connector bluprint for model registration
            connector = {
                "name": self.llm_model,
                "description": "The connector to Hugging Face GPT Language Model",
                "version": "1.0.1",
                "protocol": "http",
                "parameters": {
                    "endpoint": "api-inference.huggingface.co",
                    "model": "gpt2",
                    "temperature": 1.0
                },
                "credential": {
                    "HF_key": "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"
                },
                "actions": [
                    {
                        "action_type": "predict",
                        "method": "POST",
                        "url": "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2",
                        "headers": {
                            "Authorization": "Bearer ${credential.HF_key}"
                        },
                        "request_body": """{ 
                            "model": "${parameters.model}", 
                            "messages": ${parameters.messages},
                            "temperature": ${parameters.temperature},
                            "inputs" : {"source_sentence": "meep", "sentences": ["moop"]}
                        }""",
                        "pre_process_function": "\n    StringBuilder builder = new StringBuilder();\n    builder.append(\"\\\"\");\n    String first = params.text_docs[0];\n    builder.append(first);\n    builder.append(\"\\\"\");\n    def parameters = \"{\" +\"\\\"inputText\\\":\" + builder + \"}\";\n    return  \"{\" +\"\\\"parameters\\\":\" + parameters + \"}\";",
                        "post_process_function": "\n      def name = \"sentence_embedding\";\n      def dataType = \"FLOAT32\";\n      if (params.embedding == null || params.embedding.length == 0) {\n        return params.message;\n      }\n      def shape = [params.embedding.length];\n      def json = \"{\" +\n                 \"\\\"name\\\":\\\"\" + name + \"\\\",\" +\n                 \"\\\"data_type\\\":\\\"\" + dataType + \"\\\",\" +\n                 \"\\\"shape\\\":\" + shape + \",\" +\n                 \"\\\"data\\\":\" + params.embedding +\n                 \"}\";\n      return json;\n    "
                    }
                ]
            }
            self.connector_id = self.client.http.post("/_plugins/_ml/connectors/_create", body=connector)['connector_id']
        
        return self.connector_id
    

    def set_model(self):
        # REGISTRATION
        # https://artifacts.opensearch.org/models/ml-models/huggingface/sentence-transformers/all-MiniLM-L6-v2/1.0.1/torch_script/config.json
        register_model = {
            "name": self.llm_model,
            "function_name": "remote",
            "description": "test model",
            "connector_id": f"{self.connector_id}"
        }

        task_id = self.client.http.post("/_plugins/_ml/models/_register", body=register_model)["task_id"]
        print(f"model registration task_id: {task_id}\n")

        # Now, retrieve the model status using the task ID returned from registration. 
        # Make sure status is COMPLETED.
        model_status = self.client.http.get(f"/_plugins/_ml/tasks/{task_id}")
        print(f"model_status: {model_status}\n")

        failed_time = 5.
        while model_status["state"] != 'COMPLETED' and failed_time != 0:
            sleep(WAIT)
            failed_time -= WAIT
            model_status = self.client.http.get(f"/_plugins/_ml/tasks/{task_id}")
            print(f"model_status: {model_status}\n")

        if model_status["state"] != 'COMPLETED':
            raise Exception("Model failed to register")

        self.model_id = model_status["model_id"]
        self.deploy_model()
        
        return self.model_id
    
    
    def deploy_model(self):
        # DEPLOYMENT
        deploy_model = self.client.http.post(f"/_plugins/_ml/models/{self.model_id}/_deploy")
        print(f"deploying model: {deploy_model}\n")

        failed_time = 5.
        while deploy_model['status'] != 'COMPLETED' and failed_time != 0:
            sleep(WAIT)
            failed_time -= WAIT
            deploy_model = self.client.http.post(f"/_plugins/_ml/models/{self.model_id}/_deploy")
            print(f"deploying model: {deploy_model}\n")

        if deploy_model["status"] != 'COMPLETED':
            raise Exception("Model failed to deploy")
        
    
    def set_rag(self):
        # SETUP RAG
        headers = {'Content-Type': 'application/json'}
        data = {
            "response_processors": [
                {
                    "retrieval_augmented_generation": {
                        "tag": "rag_pipeline",
                        "description": "HuggingFace Connector pipeline",
                        "model_id": f"{self.model_id}",
                        "context_field_list": ["text"],
                        "system_prompt": "You are a dataset search tool",
                        "user_instructions": "For a given search query, list the top 10 most relevant datasets as answers."
                    }
                }
            ]
        }

        url = "http://localhost:9200/_search/pipeline/rag_pipeline"
        response = requests.put(url, headers=headers, json=data)
        print(f"{response.status_code}: {response.text}")
        self.rag = response.status_code == 200

        return self.rag
    
    # def train(self):
    #     task = {
    #         "parameters": {
    #             "centroids": 3,
    #             "iterations": 10,
    #             "distance_type": "COSINE"
    #         },
    #         "input_query": {
    #             "_source": ["Car Make", "Car Model"],
    #             "size": 1000
    #         },
    #         "input_index": [
    #             "test-blog"
    #         ]
    #     }
    #     self.client.http.post(f"/_plugins/_ml/_train/kmeans", body=task)

    #     return True


    def conversational_search(self):

        # Set up the cluster settings to enable rag and ml nodes
        if not self.cluster_set:
            assert( self.set_cluster_settings() is True )

        # Make the connector for the model using its blueprint
        if not self.connector_id:
            assert( self.set_connector() is not None )

        # Registering the model with the connector
        if not self.model_id:
            assert( self.set_model() is not None )

        # SETUP RAG
        if not self.rag:
            assert( self.set_rag() is True )

        # Task: enable auto redeploy. For more details, see 
        # https://opensearch.org/docs/latest/ml-commons-plugin/cluster-settings/#enable-auto-redeploy

        return True
    
    
    def add_to_conversation(self, question, search_title):
        # If there is no name provided for the conversation, name it by first 10 words in search.
        if search_title is None:
            search_title = question.split()[:10]
        memory_id = self.client.http.post("/_plugins/_ml/memory/", question)
        print(f"Convo name: {search_title}")
        return memory_id
    

    def rag_search(self, q, index_name, memory_id=None):
        # url = f"http://localhost:9200/{index_name}/_search"
        # headers = {"Content-Type": "application/json"}
        assert( self.conversational_search() is True )

        query = {
            "query": {
                "match": {
                "text": q
                }
            },
            "ext": {
                "generative_qa_parameters": {
                "llm_question": q,
                "llm_model": self.llm_model,
                "context_size": 5,
                "timeout": 15
                }
            }
        }
        if memory_id:
            query["ext"]["generative_qa_parameters"]["memory_id"] = memory_id

        response = self.client.search(
            body = query,
            index = index_name
        )
        # print(response)
        return response

        # search_results = self.client.http.get(f"/{index_name}/_search", query)
        # print(search_results)
        # search_results = search_results["ext"]["retrieval_augmented_generation"]
        # print(search_results)
        # return (search_results["answer"], search_results["message_id"])