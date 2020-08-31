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

@app.route('/api/nestable/row', methods=['POST'])
def add_row():
  data = request.json
  row = model.add_row(get_db(), data['nestable'], data['row'])
  return {'success': True, 'row': row}

@app.route('/api/nestable/row', methods=['DELETE'])
def delete_row():
  data = request.json
  model.delete_row(get_db(), data['nestable'], data['row'])
  return {'success': True}

@app.route('/api/nestable/cell', methods=['PATCH'])
def update_cell():
  data = request.json
  model.update_cell(get_db(), data['id'], data['nestable'], data['column'], data['datum'])
  return {'success': True}


@app.route('/')
def tables():
  nestables = model.get_nestables(get_db())
  return render_template('nestables.html', nestables=nestables)

@app.route('/nestable/<nestable_id>')
def nestable(nestable_id=None):
  nestables = model.get_nestables(get_db(), builtins=True)
  nestable = nestables.get(nestable_id)
  columns = model.get_columns(get_db())
  data = model.get_data(get_db())
  return render_template('nestable.html', nestable=nestable, nestables=nestables, columns=columns, data=data)

initialise()
app.run(host='0.0.0.0', port=8080, debug=True)
