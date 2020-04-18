import os
import json
import uuid

from cli import CLI
from pathfinding import PathFinder

from flask import Flask, send_file, render_template



app = Flask(__name__, template_folder=os.path.join('web', 'templates'))

dnd_backend = CLI()
pathFinder = PathFinder()

entities = None
types = None
expected = None

def resetDataStructures():
    global entities
    entities = {}
    global types
    types = {
        "player": [],
        "monster": [],
        "obstacle": []
    }


def init(mapJSON):

    with open('maps/' + mapJSON) as f:
        state = json.load(f)

    global expected
    expected = state['expected'] if 'expected' in state else None


    resetDataStructures()
    for entity in state['entities']:
        eid = uuid.uuid1().hex
        entity['eid'] = eid
        entities[eid] = entity
        types[entity['type']].append(entity)
        # Deal with entities with different sizes
        pathFinder.addEntityToG(entity)

        creationCMD = 'new monster --name {name}'.format(name=eid)

        if 'health' in entity:
            creationCMD += ' --health ' + str(entity['health'])

        if 'speed' in entity:
            creationCMD += ' --speed ' + str(entity['speed'])

        dnd_backend.query(creationCMD)

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/grid')
def grid():
    return json.dumps(list(entities.values()))

@app.route('/pathfind/<eid>')
def pathFind(eid):

        # Monster health
    averageHealth = 0
    thisHealth = 0
    for monster in types['monster']:
        health = int(dnd_backend.query('check ' + eid + ' _current_health'))
        if monster['eid'] == eid:
            thisHealth += health

        averageHealth += health
    averageHealth /= len(types['monster'])

    healthVal = thisHealth / averageHealth

        # Pathing difficulty

    speed = int(dnd_backend.query('check ' + eid + ' _speed'))
    relativeSpeed = speed / 30

        # Threat level

    if 'threat' in entities[eid]:
        threat = entities[eid]['threat']
    else:
        threat = {}

        # Player health

    averageHealth = 0
    for player in types['player']:
        health = int(dnd_backend.query('check ' + player['eid'] + ' _current_health'))

        averageHealth += health

    avgPlayerHealth = thisHealth / len(types['player'])

    candidates = [{'col': p['col'], 'row': p['row'], 'eid': p['eid']} for p in types['player']]

    # Compute static & dynamic debates
    for candidate in candidates:
        static = healthVal
        candidate['static'] = static + (threat[candidate['eid']] if candidate['eid'] in threat else 0) + int(dnd_backend.query('check ' + candidate['eid'] + ' _current_health')) / avgPlayerHealth
        dynamic = relativeSpeed
        candidate['dynamic'] = dynamic

    path = pathFinder.navigateToOne(entities[eid], candidates)
    if not path:
        path = [] # Really, this should do something smart
    else:
        steps = speed/5
        if steps < len(path):
            path = path[int(-1*steps):]
        updatePos(eid, path[0][0], path[0][1])
    print(path[0])
    return json.dumps(path)

@app.route('/create/<etype>/<col>/<row>')
def create(etype, col, row):
    eid = uuid.uuid1().hex
    entity = {"col":int(col),"row":int(row),"size":1,"fill":"#444444", "type": etype, "eid": eid}
    entities[eid] = entity
    types[entity['type']].append(entity)
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

    for entity in types[entities[eid]['type']]:
        if entity['eid'] == eid:
            del entity

    del entities[eid]

    rc = dnd_backend.query('remove ' + eid)
    if rc == -1:
        return "Something went wrong", 500
    else:
        return "Success"

@app.route('/damage/<srcid>/<destid>/<amt>')
def damage(srcid, destid, amt):
    amt = int(amt)
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
    return str(dnd_backend.query('heal {eid} {amt}'.format(eid=eid, amt=amt)))

@app.route('/check/<eid>/<stat>')
def check(eid, stat):
    return str(dnd_backend.query('check {eid} {stat}'.format(eid=eid, stat=stat)))

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

if __name__ == "__main__":
    import sys
    args = sys.argv[1:]

    if args:
        if args[0] == 'test':
            for mapJSON in [f for f in os.listdir('maps') if os.path.isfile(os.path.join('maps', f)) and os.path.splitext(f)[1] == '.json']:
                init(mapJSON)
                if (not expected):
                    print(mapJSON + ': no expectations listed. Skipping')
                    continue
                locs = []
                for mon in types['monster']:
                    locs.append(json.loads(pathFind(mon['eid']))[0])
                if locs != expected:
                    print(mapJSON + ' FAILED: expecting: ' + str(expected) + ' but got ' + str(locs))
                else:
                    print(mapJSON + ' PASSED')
            exit(0)
        else:
            init(args[0])
    else:
        resetDataStructures()

    # if args[0] == '--headless':


app.run()
