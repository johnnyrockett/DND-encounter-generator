import os
import json
import uuid

from cli import CLI

from flask import Flask, send_file, render_template


app = Flask(__name__, template_folder=os.path.join('web', 'templates'))

with open('map1.json') as f:
    state = json.load(f)

entities = {}
for entity in state['entities']:
    eid = uuid.uuid1().hex
    entity['eid'] = eid
    entities[eid] = entity


@app.route('/')
def main():
    return render_template('index.html')

@app.route('/grid')
def grid():
    return json.dumps(state)

@app.route('/create/<type>/<col>/<row>')
def create(etype, col, row):
    eid = uuid.uuid1().hex
    entity = {"col":col,"row":row,"size":1,"fill":"#444444", "type": etype}
    entities[eid] = entity
    stat['entities'].append(entity)
    return ':)'

@app.route('/remove/<eid>')
def remove(eid):
    if eid not in entities:
        return ':('
    entity = entities[eid]
    state['entities'].remove(entity)
    del entities[eid]
    return ':)'

@app.route('/damage/<sourceid>/<destid>/<amt>')
def damage(src, dest, amt):
    pass

@app.route('/heal/<eid>/<amt>')
def heal(eid, amt):
    pass

@app.route('/check/<eid>/<stat>')
def check(eid, stat):
    pass

@app.route('/update/pos/<eid>/<col>/<row>')
def updatePos(eid, col, row):
    if eid not in entities:
        return ':('
    entity = entities[eid]
    entity['col'] = int(col)
    entity['row'] = int(row)
    return ':)'

app.run()