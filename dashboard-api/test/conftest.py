import pytest
from dotenv import find_dotenv, load_dotenv
from src.db import engine, dm

@pytest.fixture(scope="session", autouse=True)
def load_env():
    load_dotenv(find_dotenv(".env.tests"))

@pytest.fixture(autouse=True)
def reset_local_db():
    # Util to clear out db schema between tests
    # make sure you're not pointed at a production db ;)
    dm.Base.metadata.drop_all(bind=engine)
    dm.Base.metadata.create_all(bind=engine)
    yield
    dm.Base.metadata.drop_all(bind=engine)
    dm.Base.metadata.create_all(bind=engine)
