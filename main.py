import sqlite3
from flask import Flask, g, render_template, request

import model
import example_data

DATABASE = 'nestable.db'

app = Flask('app')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = lambda c, r: dict([(col[0], r[idx]) for idx, col in enumerate(c.description)])
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def initialise():
  with app.app_context():
    db = get_db()
    model.init(db)
    #example_data.create(db)
    db.commit()

@app.route('/api/table/row', methods=['POST'])
def add_row():
  data = request.json
  row = model.add_row(get_db(), data['table'], data['row'])
  return {'success': True, 'row': row}

@app.route('/api/table/row', methods=['DELETE'])
def delete_row():
  data = request.json
  model.delete_row(get_db(), data['table'], data['row'])
  return {'success': True}

@app.route('/api/table/cell', methods=['PATCH'])
def update_row():
  data = request.json
  model.update_cell(get_db(), data['table'], data['row'], data['column'], data['datum'])
  return {'success': True}

@app.route('/')
def tables():
  types = model.get_types(get_db())
  tables = model.get_tables(get_db())
  return render_template('tables.html', types=types, tables=tables)

@app.route('/table/<table>')
def table(table=None):
  types = model.get_types(get_db())
  table_data = model.get_table(get_db(), table)
  return render_template('table.html', types=types, table=table_data)

initialise()
app.run(host='0.0.0.0', port=8080, debug=True)