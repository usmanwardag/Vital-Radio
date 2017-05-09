from flask import Flask, render_template
from radiotest import Radio

app = Flask(__name__)
app.debug = True

@app.route('/')
def index():
    return render_template('index.html', data = ['17.5', 'Breathing', 'Medium',
    						'Hang tight, your breathing is being monitored!'])

@app.route('/faq')
def guess():
    return render_template('faq.html')

@app.route('/usrp_calculate')
def usrp():
	def generate():
		radio = Radio()
		data = radio.track()
		print(data)
		return [str(data)]

	return app.response_class(generate(), mimetype='text/xml')

if __name__ == '__main__':
    app.run()