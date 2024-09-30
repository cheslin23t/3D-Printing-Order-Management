from functools import wraps
from flask import Flask, render_template, session, request, redirect
authorizedUsers = {
    "Colin": 1,
    "Kavi": 2,
    "Keane": 3,
    "Matthew": 4
}
# 1 Admin
# 2 Printer
# 3 Addon
# 4 Referrer

def logged_in(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if "admin_logged_in" not in session:
            return redirect("/admin/verify")
        if authorizedUsers.get(session.get('user')) is not None:
            return f(*args, **kwargs)
        return "Bro don't change the shortcut code, you're not allowed to do that"
    return decorated_func
def admin(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if authorizedUsers.get(session.get('user')) <= 1:
            return f(*args, **kwargs)
        return "Admin Only...."
    return decorated_func

def printer(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if authorizedUsers.get(session.get('user')) <= 2:
            return f(*args, **kwargs)
        return "Printer+ Only...."
    return decorated_func

def addon(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if authorizedUsers.get(session.get('user')) <= 3:
            return f(*args, **kwargs)
        return "Addon+ Only...."
    return decorated_func

def referrer(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if authorizedUsers.get(session.get('user')) <= 4:
            return f(*args, **kwargs)
        return "Referrer+ Only...."
    return decorated_func