## WIP

# from contextlib import asynccontextmanager
import os
import json

from fastapi import FastAPI, Depends, Response
from typing import Annotated, Any, Optional, List, Dict
from src.opensearch import OpenSearchManager
from src.relevance import compute_relevance

INDEX_NAME = os.environ.get('INDEX_NAME')
METADATA_FOLDER = os.environ.get('METADATA_FOLDER')

app = FastAPI()
manager = OpenSearchManager()

@app.get("/query")
def query_opensearch(response: Response, query: str, offset: Optional[int] = 0):
    data = manager.search(query, INDEX_NAME)
    raw_data = data['hits']['hits']
    datasets = list_conversion_helper(query, raw_data)

    print(datasets)

    response.headers["X-Offset-Count"] = str(offset)
    response.headers["X-Total-Count"] = str(10)

    return datasets

@app.get("/query/single")
def query_opensearch():
    data = manager.single_search('entertainment', INDEX_NAME)
    raw_data = data['hits']['hits']
    datasets = list_conversion_helper(raw_data)

    score = [compute_relevance('entertainment',  raw_data[0]["title"], raw_data[0]["tags"], raw_data[0]["topic"])]
    datasets[0]['score'] = score

    return datasets

# @app.post("/index")
# def index_to_opensearch(folder: UploadFile = File(...)):
#     if folder.filename.endswith('.zip'):
#         with ZipFile(folder.file, 'r') as zip_ref:
#             zip_ref.extractall(METADATA_FOLDER)

    
#     manager.populate_index(INDEX_NAME, METADATA_FOLDER)


def list_conversion_helper(query: str, datasets: List[Dict[str, any]]) -> List[Dict[str, any]]:
    """Helper function to convert the JSON fields to proper form.
    
    Parameters:
        datasets (list[Dict[str, any]]): The input list of JSON objects to format.

    Returns:
        list[Dict[str, any]]: The formatted list of JSON objects.
    """

    ret = []

    for data in datasets:
        # Clean up tags field, parse hits string
        dataset = data['_source']

        dataset['score'] = compute_relevance(query, dataset["title"], dataset["tags"], dataset["topic"])
        
        # print(dataset)
        if 'tags' in dataset and isinstance(dataset['tags'], list):
            dataset['tags'] = [tag.replace("\"", "").replace("{", "").replace("}", "") for tag in dataset['tags']]
            dataset['tags'] = ', '.join([tag.capitalize() for tag in dataset['tags']])
        # Clean up licenses field
        if 'licenses' in dataset and isinstance(dataset['licenses'], list):
            dataset['licenses'] = [license_item['name'].replace("\"", "").replace("{", "").replace("}", "") for license_item in dataset['licenses']]
            dataset['licenses'] = ', '.join(license for license in dataset['licenses'])
        
        # Clean up col_names field
        if 'col_names' in dataset and isinstance(dataset['col_names'], list):
            dataset['col_names'] = [col_name.replace("\"", "").replace("{", "").replace("}", "") for col_name in dataset['col_names']]
        
        ret.append(dataset)
    return ret
