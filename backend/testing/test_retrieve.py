import pytest
import os
from typing import Any

from opensearchpy import Date, Document, Index, Text, OpenSearch
from opensearchpy.helpers import analysis

from ..src.opensearch_client import OpenSearchManager

METADATA_FOLDER = os.environ.get('METADATA_FOLDER')

m = OpenSearchManager()

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


def test_index_can_be_saved_even_with_settings(write_client: Any) -> None:
    i = Index("test-blog", using=write_client)
    i.settings(number_of_replicas=0)
    i.save()
    i.settings(number_of_replicas=1)
    i.save()

    assert (
        "1" == i.get_settings()["test-blog"]["settings"]["index"]["number_of_replicas"]
    )

def test_index_can_be_created_with_settings_and_mappings(write_client: Any) -> None:
    i = Index("test-blog", using=write_client)
    if i.exists():
        i.delete()
    # i = Index("test-blog", using=write_client)
    i.document(Post)
    i.settings(number_of_replicas=1, number_of_shards=3)
    i.create()

    assert {
        "test-blog": {
            "mappings": {
                "properties": {
                    "title": {"type": "text", "analyzer": "my_analyzer"},
                    "published_from": {"type": "date"},
                }
            }
        }
    } == write_client.indices.get_mapping(index="test-blog")

    settings = write_client.indices.get_settings(index="test-blog")
    assert settings["test-blog"]["settings"]["index"]["number_of_replicas"] == "1"
    assert settings["test-blog"]["settings"]["index"]["number_of_shards"] == "3"
    assert settings["test-blog"]["settings"]["index"]["analysis"] == {
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
    i = m.create_index("test-blog")
    try:
        i = m.delete_index("test-blog")
        assert i == None
        i = m.delete_index("test-blog")
    except Exception as e:
        print("Error:", e)
        assert isinstance(e, NameError)
    assert i == None


def test_get_index_by_name():
    i = None
    i = m.create_index("test-blog")
    assert i != None
    assert m.get_index_by_name("test-blog") == True
    m.delete_index("test-blog")
    assert m.get_index_by_name("test-blog") == False

# Must have at least one dataset in METADATA FOLDER to pass
def test_populate_index():
    i = None
    i = m.populate_index("test-blog", METADATA_FOLDER)
    assert i != None
    assert m.get_index_by_name("test-blog") == True
    m.delete_index("test-blog")
    assert m.get_index_by_name("test-blog") == False

# test_query: Specify fields and document you want to get.
# Or keep it simple and match against topic.
def test_search():
    m.populate_index("test-blog", METADATA_FOLDER)
    s = None
    s = m.search("sports", "test-blog")
    s = str(s)
    assert s != None
    assert s.__contains__("'hits': {'total': {'value': 0")
    m.delete_index("test-blog")

    try:
        m.search("sports", "test-blog")
    except Exception as e:
        assert m.get_index_by_name("test-blog") == False

