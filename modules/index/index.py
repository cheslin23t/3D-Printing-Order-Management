from flask import render_template, Blueprint, session

app = Blueprint('index', __name__, template_folder='../../templates')

@app.route('/')
def index():
    #print(session.get('user'))
    return render_template('index.html', user=session.get('user'))

