import os
import json
from typing import Any
from opensearch import OpenSearchManager

from dotenv import load_dotenv

load_dotenv()

manager = OpenSearchManager()

METADATA_FOLDER = os.environ.get('METADATA_FOLDER')
INDEX_NAME = os.environ.get('INDEX_NAME')

if __name__ == '__main__':
    #create index
    manager.populate_index(INDEX_NAME, METADATA_FOLDER)