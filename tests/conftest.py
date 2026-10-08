import os
import sys
import gc
import tempfile
import pytest

# Add parent directory to path so imports work seamlessly
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import create_app
from seed import seed_database
from database.db import get_db_connection

class TestConfig:
    TESTING = True
    SECRET_KEY = "test-secret-key"
    MAX_ACTIVE_REQUESTS = 5
    CHARGE_THRESHOLD = 1000.0
    BELOW_THRESHOLD_CHARGE = 50.0
    ABOVE_THRESHOLD_CHARGE = 0.0

@pytest.fixture
def test_db():
    """
    Creates an isolated temporary SQLite database for each test with clean initial demo baseline.
    """
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)
    seed_database(db_path, include_sample_requests=False)
    yield db_path
    gc.collect()
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
    except OSError:
        pass

@pytest.fixture
def app(test_db):
    """
    Creates a Flask test application instance configured with the temporary database.
    """
    class AppTestConfig(TestConfig):
        DATABASE_PATH = test_db

    app = create_app(AppTestConfig)
    return app

@pytest.fixture
def client(app):
    """
    Flask test client fixture.
    """
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()
