from leaftracker.adapters.elastic_index import Index
from tools import delete_test_indexes


def test_delete_test_indexes():
    mappings = {
        "properties": {
            "content": {"type": "text"}
        }
    }

    index_names = ["test_index_a", "test_index_b", "test_index_c"]

    for name in index_names:
        Index(name, mappings).lifecycle.create()

    delete_test_indexes()
    for name in index_names:
        assert not Index(name, mappings).lifecycle.exists()
