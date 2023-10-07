import requests
import os
import sys
import json
from typing import Dict, List, Any, Optional
import pandas as pd
from io import StringIO
import json
from .database import Database
import datetime

def _get_df_from_list(l: List[Dict[str, Any]]) -> pd.DataFrame:
  return pd.read_json(StringIO(json.dumps(l)))

class Chunk:
  def __init__(self, items: pd.DataFrame, projects: pd.DataFrame):
    self.items = items
    self.projects = projects

  def num_items(self) -> int:
    return len(self.items.index)

def _download_chunk(offset) -> Chunk:
  URL="https://api.todoist.com/sync/v9/completed/get_all"
  LIMIT=200
  params={"offset":offset, "limit":LIMIT}
  headers={"Authorization": "Bearer {}".format(os.getenv("TODOIST_API_TOKEN"))}
  r = requests.get(URL, params=params, headers=headers)
  if r.status_code == 200:
    json_response = r.json()
    items_df = _get_df_from_list(json_response["items"])
    projects_df = _get_df_from_list(list(json_response["projects"].values()))
    return Chunk(items_df, projects_df)
  else:
    raise Exception("Error downloading ({})".format(r.status_code))

def _get_max_seen_timestamp(db: Database) -> Optional[datetime.datetime]:
  df = db.sql(
    """
    select
      max(completed_at) as max_completed_at
    from items where 1=1
    having max_completed_at is not null
    """
  )
  if df is None:
    return None
  else:
    return df["max_completed_at"].max()

def _get_chunk(offset) -> Chunk:
  URL="https://api.todoist.com/sync/v9/completed/get_all"
  LIMIT=200
  params={"offset":offset, "limit":LIMIT}
  headers={"Authorization": "Bearer {}".format(os.getenv("TODOIST_API_TOKEN"))}
  r = requests.get(URL, params=params, headers=headers)
  if r.status_code == 200:
    json_response = r.json()
    items_df = _get_df_from_list(json_response["items"])
    projects_df = _get_df_from_list(list(json_response["projects"].values()))
    return Chunk(items_df, projects_df)
  else:
    raise Exception("Error downloading ({})".format(r.status_code))


class DownloadIterator:
  def __init__(self, db: Database):
    self.db = db
    self.items_downloaded = 0
    self.done = False
    self.max_seen_timestamp = _get_max_seen_timestamp(db)

  def get_chunk(self) -> Chunk:
    assert not self.done
    result = _download_chunk(self.items_downloaded)
    self.items_downloaded += result.num_items()
    if result.num_items() == 0:
      self.done = True
    elif self.max_seen_timestamp and result.items["completed_at"].min() < self.max_seen_timestamp:
      self.done = True
    return result

  def is_done(self) -> bool:
    return self.done

  def get_items_downloaded(self) -> int:
    return self.items_downloaded

def _download(db: Database):
  it = DownloadIterator(db)
  while not it.is_done():
    chunk = it.get_chunk()
    if not chunk.items.empty:
      chunk_items = chunk.items
      db.sql(
        """
        insert into items
        select
          id,
          project_id,
          task_id,
          completed_at
        from chunk_items
        """
      )
    if not chunk.projects.empty:
      chunk_projects = chunk.projects
      db.sql(
        """
        insert into projects
        select
          id,
          name
        from chunk_projects
        """
      )
    print("Downloaded {} items...".format(it.get_items_downloaded()))

def _remove_duplicates(db: Database):
  db.sql(
    """
    create or replace table items as (
      select * from items
      union
      select * from items
    )
    """
  )
  db.sql(
    """
    create or replace table projects as (
      select * from projects
      union
      select * from projects
    )
    """
  )

def sync_data(db_file: str):
  db = Database(db_file)
  _download(db)
  _remove_duplicates(db)
