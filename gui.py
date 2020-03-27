import os
import json
import uuid

from cli import CLI

from flask import Flask, send_file, render_template


app = Flask(__name__, template_folder=os.path.join('web', 'templates'))

dnd_backend = CLI()

with open('map1.json') as f:
    state = json.load(f)

entities = {}
for entity in state['entities']:
    eid = uuid.uuid1().hex
    entity['eid'] = eid
    entities[eid] = entity
    dnd_backend.query('new monster --name {name}'.format(name=eid))


@app.route('/')
def main():
    return render_template('index.html')

@app.route('/grid')
def grid():
    return json.dumps(list(entities.values()))

@app.route('/create/<etype>/<col>/<row>')
def create(etype, col, row):
    eid = uuid.uuid1().hex
    entity = {"col":col,"row":row,"size":1,"fill":"#444444", "type": etype, "eid": eid}
    entities[eid] = entity
    rc = dnd_backend.query('new monster --name ' + eid)
    if rc == -1:
        return 'Something went wrong', 500
    else:
        return eid

@app.route('/remove/<eid>')
def remove(eid):
    if eid not in entities:
        return "That entity id doesn't exist", 404
    del entities[eid]
    rc = dnd_backend.query('remove ' + eid)
    if rc == -1:
        return "Something went wrong", 500
    else:
        return "Success"

@app.route('/damage/<sourceid>/<destid>/<amt>')
def damage(srcid, destid, amt):
    rc = dnd_backend.query('damage {destid} {amt}'.format(destid=destid, amt=amt))
    if 'threat' not in entities[destid]:
        entities[destid]['threat'] = {}
    if srcid not in entities[destid]['threat']:
        entities[destid]['threat'][srcid] = 0
    entities[destid]['threat'][srcid] += amt
    if rc == -1:
        return 'Something went wrong', 500
    else:
        return "Success"

@app.route('/heal/<eid>/<amt>')
def heal(eid, amt):
    return dnd_backend.query('heal {eid} {amt}'.format(eid=eid, amt=amt))

@app.route('/check/<eid>/<stat>')
def check(eid, stat):
    return dnd_backend.query('check {eid} {stat}'.format(eid=eid, stat=stat))


@app.route('/update/pos/<eid>/<col>/<row>')
def updatePos(eid, col, row):
    if eid not in entities:
        return ':('
    entity = entities[eid]
    entity['col'] = int(col)
    entity['row'] = int(row)
    return ':)'

app.run()