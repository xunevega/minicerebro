from tempfile import NamedTemporaryFile
from os import environ


test_db = NamedTemporaryFile(prefix="minicerebro-tests-", suffix=".sqlite3", delete=False)
test_db.close()
environ["DATABASE_URL"] = f"sqlite:///{test_db.name}"

