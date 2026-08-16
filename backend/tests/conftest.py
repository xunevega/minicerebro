from os import environ
from tempfile import NamedTemporaryFile

test_db = NamedTemporaryFile(prefix="minicerebro-tests-", suffix=".sqlite3", delete=False)  # noqa: SIM115
test_db.close()
environ["DATABASE_URL"] = f"sqlite:///{test_db.name}"
environ["APP_ENV"] = "local"
environ["AUTH_REQUIRED"] = "false"
environ["ENABLE_DOCS"] = "true"

from app.db.bootstrap import upgrade_database

upgrade_database()
