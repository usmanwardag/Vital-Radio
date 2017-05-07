from flask import Flask, render_template
from flask.ext.socketio import SocketIO

app = Flask(__name__)
app.debug = True

@app.route('/')
def index():
    return render_template('index.html', data = ['17.5', 'Breathing', 'Medium',
    						'Hang tight, your breathing is being monitored!'])

@app.route('/faq')
def guess():
    return render_template('faq.html')

if __name__ == '__main__':
    app.run()