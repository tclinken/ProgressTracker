import duckdb
import pandas as pd
from typing import Optional

class Database:
    def __init__(self, db_file: str):
        self.conn = duckdb.connect(db_file)

    def sql(self, query: str) -> Optional[pd.DataFrame]:
        db_result = self.conn.sql(query)
        return db_result.df() if db_result else None
