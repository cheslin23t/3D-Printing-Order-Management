# admin.py (Flask Blueprint)
from flask import render_template, Blueprint, session, request, jsonify, abort
from webauthn import generate_registration_options, generate_authentication_options, verify_registration_response, verify_authentication_response
import os
import base64
import binascii
import uuid
from ..utils.database import mydb

app = Blueprint('admin', __name__, template_folder='../../templates')
mycursor = mydb.cursor(dictionary=True)

# Helper function to decode base64url
def base64url_decode(base64url_str):
    base64_str = base64url_str.replace('-', '+').replace('_', '/')
    padding = len(base64_str) % 4
    if padding:
        base64_str += '=' * (4 - padding)
    return base64.b64decode(base64_str)
def base64url_encode(data):
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')
# Generate Registration Options
@app.route('/get-registration-options', methods=['GET'])
def get_registration_options_route():
    user_id = str(uuid.uuid4()).encode('utf-8')  # User ID must be in bytes

    # Generate registration options with rp_id matching your domain
    options = generate_registration_options(
        rp_name="Printed",  # Relying Party (RP) Name
        rp_id="chesdev.me",  # RP ID (use localhost during local dev)
        user_id=user_id,
        user_name=f'{uuid.uuid4()}',  # Replace with actual user data in production
    )

    session['registration_options'] = options  # Store registration options in session

    # Helper function to encode data in base64url format
    def encode_base64url(data):
        return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

    # Properly encode challenge and user ID in base64url format
    serialized_options = {
        'challenge': encode_base64url(options.challenge),  # Encode challenge
        'rp': options.rp,  # RP details
        'user': {
            'id': encode_base64url(user_id),  # Encode user ID
            'name': options.user.name,  # Username
            'displayName': options.user.display_name  # User display name
        },
        'pubKeyCredParams': options.pub_key_cred_params,  # Public key credential parameters
        'timeout': options.timeout,  # Timeout
        'attestation': options.attestation,  # Attestation type
        'authenticatorSelection': options.authenticator_selection  # Authenticator selection criteria
    }

    # Optional: Add excludeCredentials if you want to avoid registering the same device again
    serialized_options['excludeCredentials'] = []  # Add any existing credentials to avoid re-registration

    # Optional: Add extensions if necessary
    #serialized_options['extensions'] = options.extensions if options.extensions else {}

    return jsonify(serialized_options), 200

# Verify the Registration Response
@app.route('/verify-registration', methods=['POST'])
def verify_registration():
    data = request.get_json()
    options = session.get('registration_options')  # Fetch the saved options from session

    if not options:
        return jsonify({"status": "error", "message": "No registration options found."}), 400

    try:
        verification = verify_registration_response(
            credential=data,
            expected_challenge=options.challenge,
            expected_origin=["https://chesdev.me"],
            expected_rp_id="chesdev.me",  # Replace with your domain
            require_user_verification=True
        )

        credential_id = verification.credential_id
        public_key = verification.credential_public_key
        sign_count = verification.sign_count

        # Convert binary data to hexadecimal
        credential_id_hex = binascii.hexlify(credential_id).decode('utf-8')
        public_key_hex = binascii.hexlify(public_key).decode('utf-8')

        # Print the SQL statement
        print("Registration successful!")
        print(f"Credential ID: {credential_id}")
        print(f"Public Key: {public_key}")
        print(f"Sign Count: {sign_count}")

        print(f"INSERT INTO Admins (username, admin_type, credential_id, public_key, sign_count) VALUES "
              f"('admin_user', 'type_value', "
              f"HEX(BINARY '{credential_id_hex}'), "
              f"HEX(BINARY '{public_key_hex}'), "
              f"{sign_count});")

        return jsonify({"status": "success", "message": "Registration verified successfully."})

    except Exception as e:
        print(f"Verification failed: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400

# Generate Login Options (Authentication)
@app.route('/get-login-options', methods=['GET'])
def get_login_options_route():
    #user_id = str(uuid.uuid4())  # Fetch the user ID from your database in a real scenario

    # Fetch stored credentials for the user from the database
    mycursor.execute("SELECT credential_id FROM Admins")
    credentials = mycursor.fetchall()
    credential_ids = [c['credential_id'] for c in credentials]
    if not credential_ids:
        return jsonify({'status': 'error', 'message': 'No credentials found.'}), 403

    # Generate authentication options
    options = generate_authentication_options(
        rp_id="chesdev.me",
        # allow_credentials=[{
        #     'id': cid,
        #     'type': 'public-key',
        # } for cid in credential_ids],
        user_verification='required'
    )

    session['auth_challenge'] = options.challenge  # Save challenge for later verification

    response = {
        'challenge': base64url_encode(options.challenge),
        'rp_id': options.rp_id,
        # 'allow_credentials': [
        #     {
        #         'id': base64.urlsafe_b64encode(cred['id']).decode('utf-8'),
        #         'type': cred['type']
        #     } for cred in options.allow_credentials
        # ],
        'user_verification': options.user_verification,
        'timeout': options.timeout
    }

    return jsonify(response)

# Verify the Authentication Response
@app.route('/verify-authentication', methods=['POST'])
def verify_authentication():
    data = request.get_json()
    challenge = session.get('auth_challenge')

    try:
        verification = verify_authentication_response(
            credential=data,
            expected_challenge=challenge,
            expected_origin=["https://chesdev.me"],
            expected_rp_id="chesdev.me",
            require_user_verification=True
        )

         # Convert credential_id to hexadecimal
        credential_id_hex = binascii.hexlify(verification.credential_id).decode('utf-8')

        # Check if credential exists in your database
        mycursor.execute("SELECT * FROM Admins WHERE HEX(credential_id) = %s", (credential_id_hex,))
        admin = mycursor.fetchone()


        if not admin:
            return jsonify({"status": "error", "message": "Credential not recognized."}), 403

        session['admin_logged_in'] = True  # Mark the admin as logged in
        return jsonify({"status": "success", "message": "Authentication successful."})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
