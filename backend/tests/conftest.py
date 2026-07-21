from tempfile import NamedTemporaryFile
from os import environ


test_db = NamedTemporaryFile(prefix="minicerebro-tests-", suffix=".sqlite3", delete=False)
test_db.close()
environ["DATABASE_URL"] = f"sqlite:///{test_db.name}"

from app.db.bootstrap import upgrade_database  # noqa: E402

upgrade_database()
