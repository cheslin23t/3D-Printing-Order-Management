from flask import render_template, Blueprint, session

app = Blueprint('index', __name__, template_folder='../../templates')

@app.route('/')
def index():
    #print(session.get('user'))
    return render_template('index.html', user=session.get('user'))

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')