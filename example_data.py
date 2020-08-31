import os

def create(conn):
  cmd = 'sqlite3 nestable.db < "schema.sql"'
  os.system(cmd)
  cmd = 'sqlite3 nestable.db <<< ".separator \",\"\n.import example.csv data"'
  os.system(cmd)
