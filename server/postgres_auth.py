import os
import sys
from dotenv import load_dotenv

load_dotenv()


required_vars = ["PG_HOST", "PG_PORT", "PG_DB", "PG_USER", "PG_PASSWORD"]

missing = [var for var in required_vars if var not in os.environ]
if missing:

    print(f"Missing environment variables: {', '.join(missing)}")
    sys.exit(1)

PG_HOST = os.getenv("PG_HOST")
PG_PORT = os.getenv("PG_PORT")
PG_DB = os.getenv("PG_DB")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")

db_url = f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"