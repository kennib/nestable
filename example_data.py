import json
from pypika import Table, Query

def create(conn):
  c = conn.cursor()

  model = Table('model')
  data = Table('data')

  # Example of a codenames nestable
  qs = [
    Query.into(model).insert('type', 'type', 'text'),
    Query.into(model).insert('type', 'value', 'datatype'),
    Query.into(data).insert('type', 'type', 'type1', 'ID'),
    Query.into(data).insert('type', 'value', 'type1', '{hole: text}'),
    Query.into(data).insert('type', 'type', 'type2', 'text'),
    Query.into(data).insert('type', 'value', 'type2', '{hole: text}'),
    Query.into(data).insert('type', 'type', 'type3', 'boolean'),
    Query.into(data).insert('type', 'value', 'type3', '{hole: boolean}'),
    Query.into(data).insert('type', 'type', 'type4', 'image'),
    Query.into(data).insert('type', 'value', 'type4', '{hole: image}'),

    Query.into(model).insert('grid', 'ID', 'ID'),
    Query.into(model).insert('grid', 'card', 'card'),
    Query.into(model).insert('grid', 'team', 'team'),
    Query.into(model).insert('grid', 'revealed', 'boolean'),

    Query.into(model).insert('team', 'name', 'text'),
    Query.into(data).insert('team', 'name', 'team1', 'blue'),
    Query.into(data).insert('team', 'name', 'team2', 'red'),
    Query.into(data).insert('team', 'name', 'team3', 'grey'),
    Query.into(data).insert('team', 'name', 'team4', 'black'),

    Query.into(model).insert('card', 'content', 'content'),

    Query.into(model).insert('content', 'name', 'text'),
    Query.into(model).insert('content', 'content', 'datatype'),
    Query.into(data).insert('content', 'name', 'content1', 'word'),
    Query.into(data).insert('content', 'content', 'content1', '{hole: text}'),
    Query.into(data).insert('content', 'name', 'content2', 'picture'),
    Query.into(data).insert('content', 'content', 'content2', '{hole: image}'),
  ]

  # Add some example words to the nestable
  words = open('words.txt').readlines()
  for id, word in enumerate(words):
    q = Query.into(data).insert('card', 'content', 'word'+str(id), json.dumps({'content': word.strip()}))
    qs.append(q)

  # Insert into DB
  for q in qs:
    c.execute(str(q))