from flask import render_template, Blueprint, session, redirect, request
from ..utils.database import mydb
from ..utils.error import makeResponseJSON
import hashlib
import json
from datetime import datetime as Datetime
mycursor = mydb.cursor(dictionary=True)
app = Blueprint('account', __name__, template_folder='../../templates')


@app.route('/example', methods=['GET'])
def example():
    return "yep"