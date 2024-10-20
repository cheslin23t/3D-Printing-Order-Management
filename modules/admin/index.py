# admin.py (Flask Blueprint)
from flask import render_template, Blueprint, session, request, jsonify, abort, redirect
from webauthn import (
    generate_registration_options,
    generate_authentication_options,
    verify_registration_response,
    verify_authentication_response,
)
import os
import base64
import binascii
import uuid
from ..utils.database import mydb
from ..utils.decorators import logged_in, admin, printer, addon, referrer, authorizedUsers
login_keys = []
app = Blueprint("admin", __name__, template_folder="../../templates")
mycursor = mydb.cursor(dictionary=True)
import secrets


def generate_secure_code():
    # Generate a random 12-digit number
    return "".join([str(secrets.randbelow(10)) for _ in range(12)])


@app.route("/admin/verify", methods=["GET", "POST"])
def verify_registration():
    if request.method == "POST":
        success = False
        print("Verifying registration: %s" % request.form)
        for key in login_keys:
            if key["code"] == request.form.get("accessCode"):
                list.remove(login_keys, key)
                session["admin_logged_in"] = True
                print('e')
                session["user"] = key["user"]
                print('User logged in as ' + session.get('user'))
                return redirect("/admin")
        print('User login rejected: Invalid Code.')
        return render_template("forbidden.html")
    print('User login rejected: Not POST Route.')
    return render_template("forbidden.html")

@app.route("/admin/logout")
@logged_in
def logout():
    session.pop("admin_logged_in", None)
    session.pop("user", None)
    return redirect("/")


@app.route("/admin/generate_code", methods=["POST"])
def gen_code():
    data = request.get_json()

    def has_expected_format(d):
        expected_format = {"auth": str, "user": str}

        def check_format(d, format_spec):
            if isinstance(format_spec, dict):
                if not isinstance(d, dict):
                    return False
                for key, value_type in format_spec.items():
                    if key not in d:
                        return False
                    if not check_format(d[key], value_type):
                        return False
                return True
            else:
                return isinstance(d, format_spec)

        return check_format(d, expected_format)

    if has_expected_format(data) is False:
        abort(404)
        print('Rejected generate_code due to invalid format.')
    if data["auth"] != os.getenv("admin_auth"):
        abort(404)
        print('Rejected generate_code due to incorrect authentication.')
    v_code = generate_secure_code()
    newEntry = {"user": data["user"], "code": v_code}
    login_keys.append(newEntry)
    print('Generated new code for user: ' + data["user"])
    return v_code


@app.route("/admin")
@logged_in
def admin():
    rank = authorizedUsers.get(session.get("user"))
    if rank is not None:
        if rank <= 2:
            return redirect("/admin/prints")
        elif rank == 3:
            return redirect("/admin/addons")
        elif rank == 4:
            return redirect("/admin/referrers")
        else:
            return "tell me to add a page for you"

@app.route("/admin/prints")
@logged_in
@printer
def getPrints():
    # Fetch data from the database
    mycursor.execute("SELECT * FROM Prints")
    prints_data = mycursor.fetchall()
    # Pass the fetched data to the template
    return render_template("prints.html", prints=prints_data)

@app.route("/admin/submissions")
@logged_in
@printer
def getSubmissions():
    # Fetch data from the database
    mycursor.execute("SELECT * FROM Submissions")
    prints_data = mycursor.fetchall()
    # Pass the fetched data to the template
    return render_template("submissions.html", prints=prints_data)
@app.route("/admin/addons")
@logged_in
@printer
def getAddons():
    # Fetch data from the database
    #mycursor.execute("SELECT * FROM Prints")
    #prints_data = mycursor.fetchall()
    prints_data = []
    # Pass the fetched data to the template
    return render_template("extensions.html", prints=prints_data)
@app.route("/admin/referrers")
@logged_in
@printer
def getReferrers():
    # Fetch data from the database
    #mycursor.execute("SELECT * FROM Prints")
    #prints_data = mycursor.fetchall()
    prints_data = []
    # Pass the fetched data to the template
    return render_template("sales.html", prints=prints_data)
@app.route("/admin/send", methods=["POST"])
def sendRoute():
    #print(request.get_json())
    data = request.get_json()

    def has_expected_format(d):
        expected_format = {
            "seller": str,
            "data": {
                "printName": str,
                "customer": str,
                "printCost": int,
                "payment": str,
                "image": str,
            },
            "auth": str,
        }

        def check_format(d, format_spec):
            if isinstance(format_spec, dict):
                if not isinstance(d, dict):
                    return False
                for key, value_type in format_spec.items():
                    if key not in d:
                        return False
                    if not check_format(d[key], value_type):
                        return False
                return True
            else:
                return isinstance(d, format_spec)

        return check_format(d, expected_format)

    if has_expected_format(data) is False:
        abort(404)
    if data["auth"] != os.getenv("admin_auth"):
        abort(404)
    seller = data["seller"]
    print_name = data["data"]["printName"]
    customer = data["data"]["customer"]
    print_cost = data["data"]["printCost"]
    payment = data["data"]["payment"]
    image = data["data"]["image"]
    printed = data["data"]["printed"]
    accepted = data["data"]["accepted"]
    if accepted == "no":
        accepted = 0
    elif accepted == "colin":
        accepted = 1
    elif accepted == "kavi":
        accepted = 2
    paid = data["data"]["paid"]
    delivered = data["data"]["delivered"]
    # Execute the query
    mycursor.execute(
        """
        INSERT INTO Prints (Seller, PrintName, Customer, PrintCost, Payment, Image, Printed, Accepted, Paid, Delivered)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            seller,
            print_name,
            customer,
            print_cost,
            payment,
            image,
            printed,
            accepted,
            paid,
            delivered,
        ),
    )
    mydb.commit()
    return (
        "<body style='background-color: lime;'><center><h1>Success</h1></center></body>"
    )


# Helper function to decode base64url
# def base64url_decode(base64url_str):
#     base64_str = base64url_str.replace('-', '+').replace('_', '/')
#     padding = len(base64_str) % 4
#     if padding:
#         base64_str += '=' * (4 - padding)
#     return base64.b64decode(base64_str)
# def base64url_encode(data):
#     return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')
# # Generate Registration Options
# @app.route('/get-registration-options', methods=['GET'])
# def get_registration_options_route():
#     user_id = str(uuid.uuid4()).encode('utf-8')  # User ID must be in bytes

#     # Generate registration options with rp_id matching your domain
#     options = generate_registration_options(
#         rp_name="Printed",  # Relying Party (RP) Name
#         rp_id="chesdev.me",  # RP ID (use localhost during local dev)
#         user_id=user_id,
#         user_name=f'{uuid.uuid4()}',  # Replace with actual user data in production
#     )

#     session['registration_options'] = options  # Store registration options in session

#     # Helper function to encode data in base64url format
#     def encode_base64url(data):
#         return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

#     # Properly encode challenge and user ID in base64url format
#     serialized_options = {
#         'challenge': encode_base64url(options.challenge),  # Encode challenge
#         'rp': options.rp,  # RP details
#         'user': {
#             'id': encode_base64url(user_id),  # Encode user ID
#             'name': options.user.name,  # Username
#             'displayName': options.user.display_name  # User display name
#         },
#         'pubKeyCredParams': options.pub_key_cred_params,  # Public key credential parameters
#         'timeout': options.timeout,  # Timeout
#         'attestation': options.attestation,  # Attestation type
#         'authenticatorSelection': options.authenticator_selection  # Authenticator selection criteria
#     }

#     # Optional: Add excludeCredentials if you want to avoid registering the same device again
#     serialized_options['excludeCredentials'] = []  # Add any existing credentials to avoid re-registration

#     # Optional: Add extensions if necessary
#     #serialized_options['extensions'] = options.extensions if options.extensions else {}

#     return jsonify(serialized_options), 200

# # Verify the Registration Response
# @app.route('/verify-registration', methods=['POST'])
# def verify_registration():
#     data = request.get_json()
#     options = session.get('registration_options')  # Fetch the saved options from session

#     if not options:
#         return jsonify({"status": "error", "message": "No registration options found."}), 400

#     try:
#         verification = verify_registration_response(
#             credential=data,
#             expected_challenge=options.challenge,
#             expected_origin=["https://chesdev.me"],
#             expected_rp_id="chesdev.me",  # Replace with your domain
#             require_user_verification=True
#         )

#         credential_id = verification.credential_id
#         public_key = verification.credential_public_key
#         sign_count = verification.sign_count

#         # Convert binary data to hexadecimal
#         credential_id_hex = binascii.hexlify(credential_id).decode('utf-8')
#         public_key_hex = binascii.hexlify(public_key).decode('utf-8')

#         # Print the SQL statement
#         print("Registration successful!")
#         print(f"Credential ID: {credential_id}")
#         print(f"Public Key: {public_key}")
#         print(f"Sign Count: {sign_count}")

#         print(f"INSERT INTO Admins (username, admin_type, credential_id, public_key, sign_count) VALUES "
#               f"('admin_user', 'type_value', "
#               f"HEX(BINARY '{credential_id_hex}'), "
#               f"HEX(BINARY '{public_key_hex}'), "
#               f"{sign_count});")

#         return jsonify({"status": "success", "message": "Registration verified successfully."})

#     except Exception as e:
#         print(f"Verification failed: {str(e)}")
#         return jsonify({"status": "error", "message": str(e)}), 400

# # Generate Login Options (Authentication)
# @app.route('/get-login-options', methods=['GET'])
# def get_login_options_route():
#     #user_id = str(uuid.uuid4())  # Fetch the user ID from your database in a real scenario

#     # Fetch stored credentials for the user from the database
#     mycursor.execute("SELECT credential_id FROM Admins")
#     credentials = mycursor.fetchall()
#     credential_ids = [c['credential_id'] for c in credentials]
#     if not credential_ids:
#         return jsonify({'status': 'error', 'message': 'No credentials found.'}), 403

#     # Generate authentication options
#     options = generate_authentication_options(
#         rp_id="chesdev.me",
#         # allow_credentials=[{
#         #     'id': cid,
#         #     'type': 'public-key',
#         # } for cid in credential_ids],
#         user_verification='required'
#     )

#     session['auth_challenge'] = options.challenge  # Save challenge for later verification

#     response = {
#         'challenge': base64url_encode(options.challenge),
#         'rp_id': options.rp_id,
#         # 'allow_credentials': [
#         #     {
#         #         'id': base64.urlsafe_b64encode(cred['id']).decode('utf-8'),
#         #         'type': cred['type']
#         #     } for cred in options.allow_credentials
#         # ],
#         'user_verification': options.user_verification,
#         'timeout': options.timeout
#     }

#     return jsonify(response)

# # Verify the Authentication Response
# @app.route('/verify-authentication', methods=['POST'])
# def verify_authentication():
#     data = request.get_json()
#     challenge = session.get('auth_challenge')

#     try:
#         verification = verify_authentication_response(
#             credential=data,
#             expected_challenge=challenge,
#             expected_origin=["https://chesdev.me"],
#             expected_rp_id="chesdev.me",
#             require_user_verification=True
#         )

#          # Convert credential_id to hexadecimal
#         credential_id_hex = binascii.hexlify(verification.credential_id).decode('utf-8')

#         # Check if credential exists in your database
#         mycursor.execute("SELECT * FROM Admins WHERE HEX(credential_id) = %s", (credential_id_hex,))
#         admin = mycursor.fetchone()


#         if not admin:
#             return jsonify({"status": "error", "message": "Credential not recognized."}), 403

#         session['admin_logged_in'] = True  # Mark the admin as logged in
#         return jsonify({"status": "success", "message": "Authentication successful."})

#     except Exception as e:
#         return jsonify({"status": "error", "message": str(e)}), 400
