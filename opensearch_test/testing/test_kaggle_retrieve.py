import os

from ..src.opensearch_client import OpenSearchManager

from dotenv import load_dotenv

load_dotenv()

# Steps to testing with personal Kaggle username and key:
# Log in to or create an account with Kaggle.
# Click on the profile icon in top-right corner of the window
# click settings (gear icon).
# Under API, click "Create New Token". Kaggle will automatically 
# create a file with the appropriate information.
# Copy the username, key to personal .env file like:
# KAGGLE_USERNAME="xxx"
# KAGGLE_KEY="yyy"
KAGGLE_USERNAME = os.environ.get('KAGGLE_USERNAME')
KAGGLE_KEY = os.environ.get('KAGGLE_KEY')
INDEX_NAME = os.environ.get('INDEX_NAME')
METADATA_FOLDER = os.environ.get('METADATA_FOLDER')

m = OpenSearchManager()

from kaggle.api.kaggle_api_extended import KaggleApi # type: ignore

# Get owner slug and dataset slug name from URL. For example:
# https://www.kaggle.com/datasets/uciml/iris would have 
# owner: uciml and datasetName: iris
api = KaggleApi()
api.authenticate()

# def test_data_uploaded():

def test_everything_indexed():
    index = m.populate_index(INDEX_NAME, METADATA_FOLDER)
    dataset_count = 0
    for file in os.listdir(METADATA_FOLDER):
        if file.endswith('.json'):
            dataset_count += 1
    print(dataset_count)
    print(str(index))
    assert dataset_count == str(index).count("_id")

    assert index["items"][0]["index"]["_index"] == INDEX_NAME
    s = m.search("sports", INDEX_NAME)
    num_hits = s["hits"]["total"]["value"]
    assert num_hits > 0
    
def test_search_data():
    m.populate_index(INDEX_NAME, METADATA_FOLDER)
    s = m.search("sports", INDEX_NAME)
    num_hits = s["hits"]["total"]["value"]
    assert num_hits > 0

    test_owner = "rkiattisak"
    test_datasetName = "sports-car-prices-dataset"
    metadata = api.metadata_get(test_owner, test_datasetName)
    test_metadata = str(metadata)
    assert test_metadata.__contains__("'datasetSlugNullable': 'sports-car-prices-dataset', 'ownerUserNullable': 'rkiattisak'")
    test_metadata = "'datasetSlugNullable': 'sports-car-prices-dataset', 'ownerUserNullable': 'rkiattisak'"
