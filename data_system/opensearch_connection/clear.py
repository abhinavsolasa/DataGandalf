import os
import json
from typing import Any
from opensearch import OpenSearchManager

from dotenv import load_dotenv

load_dotenv()

manager = OpenSearchManager()

INDEX_NAME = os.environ.get('INDEX_NAME')

if __name__ == '__main__':
    #create index
    body = {
        "query": {
            "match_all": {}
        }
}
    manager.clear_index(INDEX_NAME, body)