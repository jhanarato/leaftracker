from conftest import references


def test_should_use_prefix():
    refs = references(prefix="prefix-")
    assert next(refs) == "prefix-0001"


def test_should_increment():
    refs = references(prefix="prefix-")
    assert [next(refs), next(refs)] == ["prefix-0001", "prefix-0002"]
