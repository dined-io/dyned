import pytest

@pytest.fixture
def id_regexp() -> str:
    return r'id[0-9]+_[a-z/0-9/^\S/]*.csv'

@pytest.fixture
def studies_metadata() -> str:
    return './dined/metadata/studies.json'

@pytest.fixture
def measures_metadata() -> str:
    return './dined/metadata/measures.json'

@pytest.fixture
def target_dir():
    return './dined/tests/fixtures/data'