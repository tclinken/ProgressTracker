from .database import Database
import pandas as pd


def query_data(db_file: str) -> pd.DataFrame:
    db = Database(db_file)
    result = db.sql(
       """
       select
         date_trunc('week', completed_at) as time_week,
         projects.name as project_name,
         count(*) as num_items
       from items join projects on 1=1
         and items.project_id = projects.id
       group by time_week, project_name
       order by time_week
       """
    )
    assert result is not None
    return result
