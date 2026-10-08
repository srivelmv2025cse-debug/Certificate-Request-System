import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "se-project-sat2-secret-key-2026")
    DATABASE_PATH = os.environ.get(
        "DATABASE_PATH",
        os.path.join(BASE_DIR, "database.db")
    )
    MAX_ACTIVE_REQUESTS = 5
    CHARGE_THRESHOLD = 1000.0
    BELOW_THRESHOLD_CHARGE = 50.0
    ABOVE_THRESHOLD_CHARGE = 0.0
