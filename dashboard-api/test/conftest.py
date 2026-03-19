import pytest
from dotenv import find_dotenv, load_dotenv

@pytest.fixture(scope="session", autouse=True)
def load_env():
    print("My code ran!")
    load_dotenv(find_dotenv(".env.tests"))
