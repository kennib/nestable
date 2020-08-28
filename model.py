import sqlite3
import json
import uuid
from pypika import Query, Table, Columns

from collections import defaultdict

def create_model_table():
  model_table = Table('model')
  model_columns = Columns(('nestable', 'VARCHAR(120)'), ('column', 'VARCHAR(120)'), ('datatype', 'VARCHAR(120)'))
  q = Query.create_table(model_table).columns(*model_columns)
  return str(q)

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
    c.execute(create_model_table())
    c.execute(create_data_table())
  except sqlite3.OperationalError:
    pass

  # Save
  conn.commit()


TYPES_QUERY = '''
WITH RECURSIVE
  subvalues(type, id, value) AS (
    SELECT data.nestable, data.row, json_group_object(data.column, data.data)
    FROM data
    GROUP BY data.row
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
SELECT nestable AS 'table'
FROM model
GROUP BY nestable
'''

COLUMN_QUERY = '''
SELECT nestable AS 'table', column, datatype AS type
FROM model
WHERE nestable = ?
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

def query_data(table=None):
  data = Table('data')
  q = Query.from_(data).select(data.nestable, data.column, data.row, data.data)
  q = q.where(data.nestable == table) if table else q
  return str(q)

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
    types[row['type']] = row
  
  # The type table contains types
  types.update({t['type']: t for t in types['type']['subvalues']})

  return types


def get_table(conn, table=None):
  c = conn.cursor()
  columns = c.execute(COLUMN_QUERY, (table,)).fetchall()
  cell_data = c.execute(query_data(table)).fetchall()

  # Store in dict[row][column] format
  row_data = defaultdict(dict)
  for id, cell in enumerate(cell_data):
    row_data[cell['row']][cell['column']] = json.loads(cell['data'])
  
  # Add the id to each row
  for id, row in enumerate(row_data):
    row_data[row]['id'] = row

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