import pytest
import os
from typing import Any

from opensearchpy import Date, Document, Index, Text, OpenSearch
from opensearchpy.helpers import analysis

from ..src.opensearch_client import OpenSearchManager

INDEX_NAME = os.environ.get('INDEX_NAME')
METADATA_FOLDER = os.environ.get('METADATA_FOLDER')

class Post(Document):
    title = Text(analyzer=analysis.analyzer("my_analyzer", tokenizer="keyword"))
    published_from = Date()

@pytest.fixture
def write_client():
    """ Basic opensearch client """
    client = OpenSearch([{'host': 'localhost', 'port': 9200}])
    return client

@pytest.fixture
def data_client():
    """ Basic opensearch client """
    client = OpenSearch([{'host': 'localhost', 'port': 9200}])
    return client

m = OpenSearchManager()

def test_index_can_be_saved_even_with_settings(write_client: Any) -> None:
    i = Index(INDEX_NAME, using=write_client)
    i.settings(number_of_replicas=0)
    i.save()
    i.settings(number_of_replicas=1)
    i.save()

    assert (
        "1" == i.get_settings()[INDEX_NAME]["settings"]["index"]["number_of_replicas"]
    )

def test_index_can_be_created_with_settings_and_mappings(write_client: Any) -> None:
    i = Index(INDEX_NAME, using=write_client)
    if i.exists():
        i.delete()
    # i = Index(INDEX_NAME, using=write_client)
    i.document(Post)
    i.settings(number_of_replicas=1, number_of_shards=3)
    i.create()

    assert {
        INDEX_NAME: {
            "mappings": {
                "properties": {
                    "title": {"type": "text", "analyzer": "my_analyzer"},
                    "published_from": {"type": "date"},
                }
            }
        }
    } == write_client.indices.get_mapping(index=INDEX_NAME)

    settings = write_client.indices.get_settings(index=INDEX_NAME)
    assert settings[INDEX_NAME]["settings"]["index"]["number_of_replicas"] == "1"
    assert settings[INDEX_NAME]["settings"]["index"]["number_of_shards"] == "3"
    assert settings[INDEX_NAME]["settings"]["index"]["analysis"] == {
        "analyzer": {"my_analyzer": {"type": "custom", "tokenizer": "keyword"}}
    }


def test_delete(write_client: Any) -> None:
    write_client.indices.create(
        index="test-delete-index",
        body={"settings": {"number_of_replicas": 0, "number_of_shards": 1}},
    )
    
    i = Index("test-delete-index", using=write_client)
    i.delete()
    assert not write_client.indices.exists(index="test-index-index")

def test_delete_index():
    i = None
    i = m.create_index(INDEX_NAME)
    try:
        i = m.delete_index(INDEX_NAME)
        assert i == None
        i = m.delete_index(INDEX_NAME)
    except Exception as e:
        print("Error:", e)
        assert isinstance(e, NameError)
    assert i == None


def test_get_index_by_name():
    i = None
    i = m.create_index(INDEX_NAME)
    assert i != None
    assert m.get_index_by_name(INDEX_NAME) == True
    m.delete_index(INDEX_NAME)
    assert m.get_index_by_name(INDEX_NAME) == False


# test_query: Specify fields and document you want to get.
# Or keep it simple and match against topic.
def test_search():
    m = OpenSearchManager()
    m.populate_index(INDEX_NAME, METADATA_FOLDER)
    s = None
    s = m.search("sports", INDEX_NAME)
    s = str(s)
    print(s)
    assert s != None
    # Assert that there are no hits for index with no files
    assert s.__contains__("'hits': {'total': {'value': 0")
    # Assert that there are hits for indexed data
    # assert not s.__contains__("'total': {'value': 0")
    m.delete_index(INDEX_NAME)

    # m.search("sports", INDEX_NAME)
    try:
        m.search("sports", INDEX_NAME)
    except Exception as e:
        assert m.get_index_by_name(INDEX_NAME) == False

############  RAG TESTING

def test_connector():
    m = OpenSearchManager()
    id = m.set_connector()
    connector = m.client.http.get(f"/_plugins/_ml/connectors/{id}")
    assert connector is not None
    assert connector["name"] == "huggingface/sentence-transformers/all-MiniLM-L6-v2"
    assert id == m.connector_id

def test_model_registration():
    m = OpenSearchManager()
    # m.set_connector()
    id = m.set_model()
    # registry = m.client.http.get(f"/_plugins/_ml/_register/{id}")
    # assert registry is not None
    # assert registry["name"] == "huggingface/sentence-transformers/all-MiniLM-L6-v2"
    # assert registry["description"] == "Sentence transformer model from Hugging Face"
    # assert registry["connector_id"] == m.connector_id
    assert id is not None
    assert id == m.model_id

# Works when the user's machine is located in the root directory, there is 
def test_conversational_search():
    m = OpenSearchManager()
    m.populate_index(INDEX_NAME, METADATA_FOLDER)
    rag_status = m.conversational_search()
    assert rag_status == True, rag_status

# Needs the dataset Sports Car Prices in the metadata folder to pass.
# Link to dataset: 
def test_rag():
    m = OpenSearchManager()
    m.create_index(INDEX_NAME, rag_true=True)
    query = "What was the price of a Bugatti Chiron car in 2021?"
    response = m.rag_search(query, INDEX_NAME)
    assert response.__contains__("Sports Car Prices"), response
    