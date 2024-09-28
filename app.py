from flask import Flask, render_template, send_from_directory, session, current_app, request
from dotenv import load_dotenv
import traceback
import os
#import ngrok
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('flask_session')
activeRoutes=['index', 'admin', 'orders']
from flask_session import Session
app.config['SECRET_KEY'] = os.getenv('flask_session')
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
from importlib import import_module
from datetime import timedelta
#listener = ngrok.forward(addr="localhost:443", authtoken_from_env=True, domain="repeatedly-organic-ghost.ngrok-free.app")
#print(f"Ingress established at {listener.url()}")
for route in activeRoutes:
    print(route)
    m = import_module(f'modules.{route}.index')
    app.register_blueprint(m.app)

@app.route('/static/<path:path>')
def send_report(path):
    return send_from_directory('static', path)
app.config['TRAP_HTTP_EXCEPTIONS']=True

# @app.errorhandler(Exception)
# def handle_error(e):
#     try:
#         # Get the stack trace if it's a 500 error
#         if e == 500:
#             stack_trace = traceback.format_exc()
#         else:
#             stack_trace = None
#         # Flask has built-in descriptions for HTTP status codes
#         error_description = f"{e} - {request.url_rule}" if e == 404 else "Internal Server Error"

#         # What happened? Provide more info on the request and the error
#         error_msg = f"Error occurred on: {request.path}"
        
#         # If it's 500, include the stack trace in the message
#         if stack_trace:
#             error_msg += f"\n\nStack Trace:\n{stack_trace}"

#         return render_template('error.html', error=e, error_description=error_description, error_msg=error_msg)
#     except Exception as ex:
#         # Fallback if something in the error handler breaks
#         return f"Error code: 500. Additional issue: {str(ex)}"
@app.route('/favicon.ico')
def flask_logo():
    return current_app.send_static_file('favicon.ico')
@app.route('/robots.txt')
def flask_robots():
    return current_app.send_static_file('robots.txt')
@app.template_filter('humanize')
def pretty_date(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    from datetime import datetime
    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time, datetime):
        diff = now - time
    elif not time:
        diff = 0
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return str(second_diff // 60) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str(second_diff // 3600) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(day_diff // 7) + " weeks ago"
    if day_diff < 365:
        return str(day_diff // 30) + " months ago"
    return str(day_diff // 365) + " years ago"

app.run(host='localhost', port=443)