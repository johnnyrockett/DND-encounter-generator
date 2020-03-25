import os
from cli import CLI

from flask import Flask, send_file, render_template


app = Flask(__name__, template_folder=os.path.join('web', 'templates'))


@app.route('/')
def main():
    return render_template('index.html')




app.run()