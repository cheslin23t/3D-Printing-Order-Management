# Printed order management

This repository contains the software I built for a small 3D-printing business started with friends. It combines a customer order form with the internal workflow used to review submissions and turn accepted requests into print records.

The project is presented in my portfolio as **Printed**.

## What the application covers

### Customer intake

Customers can submit contact information, a budget, payment preference, and either an existing model link or details for a custom model. The order route validates the expected fields before saving a submission to MySQL.

### Administrative workflow

The admin area supports:

- Short-lived access-code login
- Role checks for different parts of the workflow
- A queue of pending submissions
- Approving a submission and creating its print record
- Denying a submission
- Viewing active print records
- Hiding a print from the active list

## Project structure

```text
app.py              Flask application setup and production server entry point
modules/index/      Public pages
modules/orders/     Customer order intake
modules/admin/      Review and print-management routes
modules/utils/      Database, access, and response helpers
templates/          Customer and admin views
static/             Styles, scripts, and images
```

## Configuration

The application expects these environment variables:

```text
flask_session
database_host
database_user
database_password
database_name
database_port
admin_auth
```

It also expects the MySQL tables used by the `Submissions` and `Prints` queries in the route modules. The repository does not currently include a migration or one-command local setup, so running it requires preparing that schema and installing the Python packages imported by the application.

The server entry point is:

```bash
python app.py
```

`app.py` starts Waitress on `localhost:443`; change that binding for ordinary local development if needed.

## Project status

Printed grew around a real small-business workflow, but this public repository is not offered as a production-ready commerce package. It is most useful as a look at the order intake and administrative system itself.
