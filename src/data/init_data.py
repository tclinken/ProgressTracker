from .database import Database

def init_data(db_file: str):
    db = Database(db_file)
    db.sql(
        f"""
        create or replace table items(
          id int64,
          project_id int64,
          task_id int64,
          completed_at timestamptz
        )
        """
    )
    db.sql(
        f"""
        create or replace table projects(
          id int64,
          name varchar
        )
        """
    )
