import os
import json
import uuid

from cli import CLI
from pathfinding import PathFinder

from flask import Flask, send_file, render_template



app = Flask(__name__, template_folder=os.path.join('web', 'templates'))

dnd_backend = CLI()
pathFinder = PathFinder()

with open('map1.json') as f:
    state = json.load(f)

entities = {}
for entity in state['entities']:
    eid = uuid.uuid1().hex
    entity['eid'] = eid
    entities[eid] = entity
    # Deal with entities with different sizes
    pathFinder.addEntityToG(entity)

    dnd_backend.query('new monster --name {name}'.format(name=eid))

# path = pathFinder.navigate(state['entities'][0], state['entities'][2])

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/grid')
def grid():
    return json.dumps(list(entities.values()))

@app.route('/pathfind/<eid>')
def pathFind(eid):
    # Perform logic to path to all players
    # I'll need to sort a list of players by everything except for distance
    # Well, assuming best case scenario distance

    # players = []
    # averageHealth = 0
    # for entity in entities:
        # if entity['type'] == "player":
            # players.append([entity])
            # averageHealth += val

    # for player in players:
    #     score = 0

        # For all of this, I need to be able to tap into the stats of these entities
        # Might want to consider keeping track of a list of players and monsters as well.

        # Monster health

        # Pathing difficulty

        # Threat level

        # Player health


        # player[1] = score

    print(entities[eid])
    path = pathFinder.navigate(state['entities'][0], entities[eid])
    if not path:
        path = [] # Really, this should do something smart
    else:
        updatePos(eid, path[0][0], path[0][1])
    return json.dumps(path)

@app.route('/create/<etype>/<col>/<row>')
def create(etype, col, row):
    eid = uuid.uuid1().hex
    entity = {"col":int(col),"row":int(row),"size":1,"fill":"#444444", "type": etype, "eid": eid}
    entities[eid] = entity
    pathFinder.addEntityToG(entity)
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
    pathFinder.removeEntityFromG(entity)
    entity['col'] = int(col)
    entity['row'] = int(row)
    pathFinder.addEntityToG(entity)
    return ':)'

app.run()