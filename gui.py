import os
import json
from cli import CLI

from flask import Flask, send_file, render_template


app = Flask(__name__, template_folder=os.path.join('web', 'templates'))

state = {
    "entities": [
        {"col":3,"row":3,"size":1,"fill":"#444444"},
        {"col":5,"row":3,"size":1,"fill":"#ff550d"},
        {"col":3,"row":5,"size":1,"fill":"#800080"},
        {"col":5,"row":5,"size":2,"fill":"#0c64e8"}
    ]
}


@app.route('/')
def main():
    return render_template('index.html')

@app.route('/grid')
def grid():
    return json.dumps(state)

@app.route('/create')
def create():
    pass

@app.route('/remove')
def remove():
    pass

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
    pass

app.run()