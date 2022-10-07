# import dependencies in order

import os 
from os import environ as env

from dotenv import load_dotenv
import pytest
from sqlalchemy import create_engine


from dined.export_sql_to_csv import *


if 'DB_PWD' in os.environ:
    del os.environ['DB_PWD']

load_dotenv()

DB_URI = f'mysql+mysqlconnector://{env["DB_USER"]}:{env["DB_PWD"]}@{env["DB_HOST"]}/{env["DB_NAME"]}'

# Create db fixture
@pytest.fixture
def db()-> sqlalchemy.engine.base.Engine:
    return create_engine(DB_URI)

@pytest.fixture
def test_db_connection(db: sqlalchemy.engine.base.Engine):
    assert db is not None


# Test that there is a valid database connection
def test_db_connection(db: sqlalchemy.engine.base.Engine):
    assert db is not None

# Test that written file matches the id regexp pattern
def test_file_name_matches_regexp(id_regexp: str, target_dir: str):
    files = os.listdir(target_dir)
    for file in files:
        assert re.match(id_regexp, file) is not None
    
# Test that the count of studies in database matches the list of data files


# Integration test