import sqlite3
import json
import uuid
from pypika import Query, Table, Columns

from collections import defaultdict

def init(conn):
  # Create a cursor for the results
  c = conn.cursor()
  
  # Create default tables
  import os
  cmd = 'sqlite3 nestable.db < "schema.sql"'
  os.system(cmd)
  #cmd = 'sqlite3 nestable.db <<< ".separator \",\"\n.import data.csv data"'
  #os.system(cmd)

  # Save
  conn.commit()

DATA_QUERY = '''
SELECT json_insert(json_insert(json_group_object(column, data), '$.id',id), '$.nestable', nestable) AS 'row'
FROM data
GROUP BY id
ORDER BY ROWID
'''

NESTABLE_QUERY = '''
SELECT json_insert(json_group_object(column, data), '$.id',id) AS 'row'
FROM data
WHERE nestable = ?
GROUP BY id
ORDER BY ROWID
'''

ROW_DELETE = '''
DELETE FROM data
WHERE id = ?
AND nestable = ?
'''

CELL_ADD = '''
INSERT INTO data
VALUES(?, ?, ?, ?)
'''

CELL_UPDATE = '''
INSERT OR REPLACE INTO data
VALUES(?, ?, ?, ?)
'''

def get_nestables(conn, builtins=False):
  c = conn.cursor()
  nestable_rows = c.execute(NESTABLE_QUERY, ('nestable',)).fetchall()
  nestables_list = [json.loads(row['row']) for row in nestable_rows]
  nestables_dict = {nestable['id']: nestable for nestable in nestables_list}

  if builtins:
    builtin_rows = get_nestable_data(conn, 'builtin-nestable')
    builtins = {row['builtin-nestable-name']: json.loads(row['builtin-nestable-value']) for row in builtin_rows}
    nestables_dict.update(builtins)

  return nestables_dict

def get_data(conn):
  c = conn.cursor()
  rows = c.execute(DATA_QUERY).fetchall()
  data = [json.loads(row['row']) for row in rows]
  return data 

def get_nestable_data(conn, nestable):
  c = conn.cursor()
  nestable_rows = c.execute(NESTABLE_QUERY, (nestable,)).fetchall()
  nestables_list = [json.loads(row['row']) for row in nestable_rows]
  return nestables_list

def get_columns(conn):
  c = conn.cursor()
  column_rows = c.execute(NESTABLE_QUERY, ('column',)).fetchall()
  columns_list = [json.loads(row['row']) for row in column_rows]
  columns_dict = {column['id']: column for column in columns_list}
  return columns_dict 

def add_row(conn, nestable, row):
  c = conn.cursor()

  # Generate an ID for the row if it doesn't have one
  if 'id' not in row:
    row['id'] = str(uuid.uuid4())

  # Add the data for each column
  for column, datum in row.items():
    if column != 'id':
      c.execute(CELL_ADD, (row['id'], nestable, column, datum))
  
  conn.commit()

  return row

def delete_row(conn, nestable, row):
  c = conn.cursor()

  # Delete the row
  c.execute(ROW_DELETE, (row['id'], nestable))
  
  conn.commit()

def update_cell(conn, id, nestable, column, datum):
  c = conn.cursor()

  # Update the data for the cell
  c.execute(CELL_UPDATE, (id, nestable, column, datum))
  
  conn.commit()

if __name__ == '___main__':
  # Connect to DB
  conn = sqlite3.connect('nestable.db')

  # Initialise the model
  init()
