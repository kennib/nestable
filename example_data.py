import json
from pypika import Table, Query

def create(conn):
  c = conn.cursor()

  model = Table('model')
  data = Table('data')

  # Example of a codenames nestable
  qs = [
    Query.into(data).insert('table', 'name', 'table', 'table'),
    Query.into(data).insert('column', 'table', 'table-name', 'table'),
    Query.into(data).insert('column', 'name', 'table-name', 'name'),
    Query.into(data).insert('column', 'type', 'table-name', 'text'),

    Query.into(data).insert('table', 'name', 'column', 'column'),
    Query.into(data).insert('column', 'table', 'column-table', 'column'),
    Query.into(data).insert('column', 'name', 'column-table', 'table'),
    Query.into(data).insert('column', 'type', 'column-table', 'table'),
    Query.into(data).insert('column', 'table', 'column-name', 'column'),
    Query.into(data).insert('column', 'name', 'column-name', 'name'),
    Query.into(data).insert('column', 'type', 'column-name', 'text'),
    Query.into(data).insert('column', 'table', 'column-type', 'column'),
    Query.into(data).insert('column', 'name', 'column-type', 'type'),
    Query.into(data).insert('column', 'type', 'column-type', 'datatype'),

    Query.into(data).insert('table', 'name', 'type', 'type'),
    Query.into(data).insert('column', 'table', 'type-name', 'type'),
    Query.into(data).insert('column', 'name', 'type-name', 'name'),
    Query.into(data).insert('column', 'type', 'type-name', 'text'),
    Query.into(data).insert('column', 'table', 'type-value', 'type'),
    Query.into(data).insert('column', 'name', 'type-value', 'value'),
    Query.into(data).insert('column', 'type', 'type-value', 'datatype'),
    Query.into(data).insert('type', 'type', 'type1', 'ID'),
    Query.into(data).insert('type', 'value', 'type1', '{hole: text}'),
    Query.into(data).insert('type', 'type', 'type2', 'text'),
    Query.into(data).insert('type', 'value', 'type2', '{hole: text}'),
    Query.into(data).insert('type', 'type', 'type3', 'boolean'),
    Query.into(data).insert('type', 'value', 'type3', '{hole: boolean}'),
    Query.into(data).insert('type', 'type', 'type4', 'image'),
    Query.into(data).insert('type', 'value', 'type4', '{hole: image}'),

    Query.into(data).insert('table', 'name', 'grid', 'grid'),
    Query.into(data).insert('column', 'table', 'grid-id', 'grid'),
    Query.into(data).insert('column', 'name', 'grid-id', 'id'),
    Query.into(data).insert('column', 'type', 'grid-id', 'ID'),
    Query.into(data).insert('column', 'table', 'grid-card', 'grid'),
    Query.into(data).insert('column', 'name', 'grid-card', 'card'),
    Query.into(data).insert('column', 'type', 'grid-card', 'card'),
    Query.into(data).insert('column', 'table', 'grid-team', 'grid'),
    Query.into(data).insert('column', 'name', 'grid-team', 'team'),
    Query.into(data).insert('column', 'type', 'grid-team', 'team'),
    Query.into(data).insert('column', 'table', 'grid-revealed', 'grid'),
    Query.into(data).insert('column', 'name', 'grid-revealed', 'revealed'),
    Query.into(data).insert('column', 'type', 'grid-revealed', 'boolean'),

    Query.into(data).insert('table', 'name', 'team', 'team'),
    Query.into(data).insert('column', 'table', 'team-name', 'team'),
    Query.into(data).insert('column', 'name', 'team-name', 'name'),
    Query.into(data).insert('column', 'type', 'team-name', 'text'),
    Query.into(data).insert('team', 'name', 'team1', 'blue'),
    Query.into(data).insert('team', 'name', 'team2', 'red'),
    Query.into(data).insert('team', 'name', 'team3', 'grey'),
    Query.into(data).insert('team', 'name', 'team4', 'black'),

    Query.into(data).insert('table', 'name', 'card', 'card'),
    Query.into(data).insert('column', 'table', 'card-content', 'card'),
    Query.into(data).insert('column', 'name', 'card-content', 'content'),
    Query.into(data).insert('column', 'type', 'card-content', 'content'),

    Query.into(data).insert('table', 'name', 'content', 'content'),
    Query.into(data).insert('column', 'table', 'content-name', 'content'),
    Query.into(data).insert('column', 'name', 'content-name', 'name'),
    Query.into(data).insert('column', 'type', 'content-name', 'text'),
    Query.into(data).insert('column', 'table', 'content-value', 'content'),
    Query.into(data).insert('column', 'name', 'content-value', 'value'),
    Query.into(data).insert('column', 'type', 'content-value', 'datatype'),
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