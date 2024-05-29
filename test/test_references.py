from conftest import References


def test_should_use_prefix():
    references = References(prefix="prefix-")
    assert next(references) == "prefix-0001"


def test_should_increment():
    references = References(prefix="prefix-")
    assert [next(references), next(references)] == ["prefix-0001", "prefix-0002"]
