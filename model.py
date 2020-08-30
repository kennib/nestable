import sqlite3
import json
import uuid
from pypika import Query, Table, Columns

from collections import defaultdict

def create_data_table():
  data_table = Table('data')
  data_columns = Columns(('nestable', 'VARCHAR(120)'), ('column', 'VARCHAR(120)'), ('row', 'VARCHAR(120)'), ('data', 'JSON'))
  q = Query.create_table(data_table).columns(*data_columns)
  return str(q)

def init(conn):
  # Create a cursor for the results
  c = conn.cursor()
  
  # Create tables
  try:
    c.execute(create_data_table())
  except sqlite3.OperationalError:
    pass

  # Save
  conn.commit()


TYPES_QUERY = '''
WITH RECURSIVE
  subvalues(type, id, value) AS (
    SELECT nestable, row, json_group_object(json_extract(column, '$.id'), data)
    FROM data
    GROUP BY row
  ),
  all_subvalues(type) AS (
    SELECT type
    FROM subvalues
      UNION ALL
    SELECT type
    FROM subvalues
    JOIN all_subvalues USING(type)
  )
SELECT type, json_group_array(json_insert(value, '$.id', id)) AS subvalues
FROM subvalues
GROUP BY type
'''

TABLES_QUERY = '''
SELECT data AS 'table'
FROM data
WHERE json_extract(nestable, '$.id') = 'table'
AND json_extract(column, '$.id') = 'name'
'''

COLUMN_QUERY = '''
SELECT json_group_object(json_extract(column, '$.id'), data) AS column
FROM data
WHERE json_extract(nestable, '$.id') = 'column'
GROUP BY row
ORDER BY ROWID
'''

DATA_QUERY = '''
SELECT row AS id, json_group_object(json_extract(column, '$.id'), data) AS data
FROM data
WHERE json_extract(nestable, '$.id') = ?
GROUP BY row
ORDER BY ROWID
'''

ROW_DELETE = '''
DELETE FROM data
WHERE nestable = ?
AND row = ?
'''

CELL_ADD = '''
INSERT INTO data
VALUES(?, ?, ?, ?)
'''

CELL_UPDATE = '''
INSERT OR REPLACE INTO data
VALUES(?, ?, ?, ?)
'''

def get_types(conn):
  c = conn.cursor()
  type_rows = c.execute(TYPES_QUERY).fetchall()
  
  # Load JSON in types
  def load_json(value):
    for key in value:
      try:
        value[key] = json.loads(value[key])
      except:
        pass
    
    if 'subvalues' in value:
      for subvalue in value['subvalues']:
        load_json(subvalue)
  
  for row in type_rows:
    load_json(row)

  # Format as a dictionary of {types: type dictionaries}
  types = {}
  for row in type_rows:
    type = row['type']['id']
    types[type] = row

  # Add the types subtable as individual types
  for type in types['type']['subvalues']:
    types[type['id']] = type
  
  return types


def get_table(conn, table=None):
  c = conn.cursor()
  columns = c.execute(COLUMN_QUERY).fetchall()
  columns = [json.loads(column['column']) for column in columns]
  columns = [column for column in columns if column['table'] == table]
  data = c.execute(DATA_QUERY, (table,)).fetchall()

  # Store in dict[row][column] format
  row_data = defaultdict(dict)
  for row in data:
    try:
      data = json.loads(row['data'])
    except:
      data = row['data']

    row_data[row['id']] = data
  
  return {'name': table, 'data': row_data, 'columns': columns}

def get_tables(conn):
  c = conn.cursor()
  tables = c.execute(TABLES_QUERY).fetchall()

  return tables


def add_row(conn, table, row):
  c = conn.cursor()

  # Generate an ID for the row if it doesn't have one
  if 'id' not in row:
    row['id'] = str(uuid.uuid4())

  # Add the data for each column
  for column, datum in row.items():
    c.execute(CELL_ADD, (table, column, row['id'], json.dumps(datum)))
  
  conn.commit()

  return row

def delete_row(conn, table, row):
  c = conn.cursor()

  # Delete the row
  c.execute(ROW_DELETE, (table, row['id']))
  
  conn.commit()

def update_cell(conn, table, row, column, datum):
  c = conn.cursor()

  # Update the data for the cell
  c.execute(CELL_UPDATE, (table, column, row, json.dumps(datum)))
  
  conn.commit()

if __name__ == '___main__':
  # Connect to DB
  conn = sqlite3.connect('nestable.db')

  # Initialise the model
  init()