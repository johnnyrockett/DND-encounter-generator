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
    return state

app.run()