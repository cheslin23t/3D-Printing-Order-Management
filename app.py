from __future__ import print_function
from flask import Flask, render_template, send_from_directory, session, current_app, request
from dotenv import load_dotenv
import traceback
import os
from flask_compress import Compress
import waitress
#import ngrok
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('flask_session')
activeRoutes=['index', 'admin', 'orders']
from flask_session import Session
app.config['SECRET_KEY'] = os.getenv('flask_session')
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
Compress(app)
from importlib import import_module
from datetime import timedelta
#listener = ngrok.forward(addr="localhost:443", authtoken_from_env=True, domain="repeatedly-organic-ghost.ngrok-free.app")
#print(f"Ingress established at {listener.url()}")
class PrintColored:
    DEFAULT = '\033[0m'
    # Styles
    BOLD = '\033[1m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    UNDERLINE_THICK = '\033[21m'
    HIGHLIGHTED = '\033[7m'
    HIGHLIGHTED_BLACK = '\033[40m'
    HIGHLIGHTED_RED = '\033[41m'
    HIGHLIGHTED_GREEN = '\033[42m'
    HIGHLIGHTED_YELLOW = '\033[43m'
    HIGHLIGHTED_BLUE = '\033[44m'
    HIGHLIGHTED_PURPLE = '\033[45m'
    HIGHLIGHTED_CYAN = '\033[46m'
    HIGHLIGHTED_GREY = '\033[47m'

    HIGHLIGHTED_GREY_LIGHT = '\033[100m'
    HIGHLIGHTED_RED_LIGHT = '\033[101m'
    HIGHLIGHTED_GREEN_LIGHT = '\033[102m'
    HIGHLIGHTED_YELLOW_LIGHT = '\033[103m'
    HIGHLIGHTED_BLUE_LIGHT = '\033[104m'
    HIGHLIGHTED_PURPLE_LIGHT = '\033[105m'
    HIGHLIGHTED_CYAN_LIGHT = '\033[106m'
    HIGHLIGHTED_WHITE_LIGHT = '\033[107m'

    STRIKE_THROUGH = '\033[9m'
    MARGIN_1 = '\033[51m'
    MARGIN_2 = '\033[52m' # seems equal to MARGIN_1
    # colors
    BLACK = '\033[30m'
    RED_DARK = '\033[31m'
    GREEN_DARK = '\033[32m'
    YELLOW_DARK = '\033[33m'
    BLUE_DARK = '\033[34m'
    PURPLE_DARK = '\033[35m'
    CYAN_DARK = '\033[36m'
    GREY_DARK = '\033[37m'

    BLACK_LIGHT = '\033[90m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'

    def __init__(self):
        self.print_original = print # old value to the original print function
        self.current_color = self.DEFAULT

    def __call__(self,
                 *values: object, sep: str | None = None,
                 end: str | None = None,
                 file: str | None = None,
                 flush: bool = False,
                 color: str|None = None,
                 default_color: str|None = None,
    ):
        if default_color:
            self.current_color = default_color

        default = self.current_color
        if color:
            values = (color, *values, default)  # wrap the content within a selected color an a default
        else:
            values = (*values, default)  # wrap the content within a selected color an a default
        self.print_original(*values, end=end, file=file, flush=flush)

print = PrintColored()
for route in activeRoutes:
    print("Loading module {module}".format(module=route), end='\r', color=print.YELLOW)
    m = import_module(f'modules.{route}.index')
    app.register_blueprint(m.app)
    print("Module {module} loaded successfully.".format(module=route), color=print.GREEN)

@app.route('/static/<path:path>')
def send_report(path):
    return send_from_directory('static', path)
app.config['TRAP_HTTP_EXCEPTIONS']=True

@app.errorhandler(Exception)
def handle_error(e):
    try:
        print(f"Error on {request.path}", color=print.YELLOW)
        print(e, color=print.RED)
        
        # Get the stack trace if it's a 500 error
        if e == 500:
            stack_trace = traceback.format_exc()
        else:
            stack_trace = None
        # Flask has built-in descriptions for HTTP status codes
        error_description = f"{e} - {request.url_rule}" if e == 404 else "Internal Server Error"

        # What happened? Provide more info on the request and the error
        error_msg = f"Error occurred on: {request.path}"
        
        # If it's 500, include the stack trace in the message
        if stack_trace:
            error_msg += f"\n\nStack Trace:\n{stack_trace}"

        return render_template('error.html', error=e, error_description=error_description, error_msg=error_msg)
    except Exception as ex:
        # Fallback if something in the error handler breaks
        return f"Error code: 500. Additional issue: {str(ex)}"

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
print("All routes loaded successfully.")
print('Server Started.')
waitress.serve(app, listen='localhost:443')