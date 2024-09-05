from flask import render_template, Blueprint, session, request, abort, redirect, url_for, session, jsonify
from webauthn import generate_registration_options, verify_registration_response, generate_authentication_options, verify_authentication_response
#INSERT INTO Admin (username, admin_type, credential_id, public_key, sign_count) VALUES ('username', 'admin_type', 'credential_id_here', 'public_key_here', sign_count_here);
import os
import uuid
from ..utils.database import mydb
mycursor = mydb.cursor(dictionary=True)
app = Blueprint('admin', __name__, template_folder='../../templates')
import base64
def get_registration_options(user_id, user_name, user_display_name):
    options = generate_registration_options(
        rp_name="Printed",
        rp_id="chesdev.me",  # Set the RP ID to your main domain
        user_id=user_id,  # Replace with your user identifier
        user_name=user_name,  # Replace with your username
        user_display_name=user_display_name  # Replace with your user's display name
    )
    return options
def special_get_registration_options(user_id):
    options = generate_registration_options(
        rp_name="Printed",
        rp_id="chesdev.me",  # Set the RP ID to your main domain
        user_id=user_id,  # Replace with your user identifier
        user_name=str(uuid.uuid4()),  # Replace with your username
    )
    return options
def base64url_decode(base64url_str):
    # Replace '-' with '+' and '_' with '/'
    base64_str = base64url_str.replace('-', '+').replace('_', '/')
    # Pad the base64 string with '=' if necessary
    padding = len(base64_str) % 4
    if padding:
        base64_str += '=' * (4 - padding)
    return base64.b64decode(base64_str)

@app.route('/get-registration-options', methods=['GET'])
def get_registration_options_route():
    user_id = str(uuid.uuid4()).encode('utf-8')  # Generate a unique ID for the user

    # Generate registration options
    options = special_get_registration_options(user_id)

    # Convert bytes to base64url encoding for JSON serialization
    def encode_base64url(data):
        return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

    serialized_options = {
        'challenge': encode_base64url(options.challenge),  # Convert bytes to base64url
        'rp': options.rp,
        'user': {
            'id': user_id.decode('utf-8'),  # Convert bytes to string for JSON
            'name': options.user.name,
            'displayName': options.user.display_name
        },
        'pubKeyCredParams': options.pub_key_cred_params,
        'timeout': options.timeout,
        'attestation': options.attestation,
        'authenticatorSelection': options.authenticator_selection
    }

    # Store the raw options in session for later verification
    session['registration_options'] = options
    return jsonify(serialized_options), 200


@app.route('/get-login-options', methods=['GET'])
def get_login_options_route():
    # Replace with actual user details as needed
    user_id = str(uuid.uuid4())

    # Fetch stored credentials for the user from the database
    mycursor.execute("SELECT credential_id FROM Admins WHERE user_id = %s", (user_id,))
    credentials = mycursor.fetchall()
    credential_ids = [c['credential_id'] for c in credentials]

    if not credential_ids:
        return jsonify({'status': 'Forbidden'}), 403

    # Generate authentication options
    options = generate_authentication_options(
        rp_id="chesdev.me",  # Set your RP ID here
        allow_credentials=[{
            'id': base64url_decode(cid),
            'type': 'public-key',
        } for cid in credential_ids],
        user_verification='required'
    )
    session['auth_challenge'] = options.challenge

    # Construct the response dictionary
    response = {
        'challenge': base64.urlsafe_b64encode(options.challenge).decode('utf-8'),
        'rp_id': options.rp_id,
        'allow_credentials': [
            {
                'id': base64.urlsafe_b64encode(cred['id']).decode('utf-8'),
                'type': cred['type']
            } for cred in options.allow_credentials
        ],
        'user_verification': options.user_verification,
        'timeout': options.timeout
    }

    return jsonify(response)


def verify_registration_response(response, expected_challenge, user):
    verification = verify_registration_response(
        credential=response,
        expected_challenge=expected_challenge,
        expected_origin=["http://localhost", "https://chesdev.me"],
        expected_rp_id="chesdev.me",  # Set your main RP ID here
        require_user_verification=True
    )
    return verification
@app.route('/admin/register_credential', methods=['POST'])
def register_credential():
    user_id = request.json.get('user_id')
    user_name = request.json.get('username')
    user_display_name = request.json.get('display_name')

    options = get_registration_options(user_id.encode(), user_name, user_display_name)

    session['registration_options'] = options
    return jsonify(options)
@app.route('/admin/verify_registration', methods=['POST'])
def verify_registration():
    data = request.get_json()
    options = session.get('registration_options')

    try:
        verification = verify_registration_response(
            response=data,
            expected_challenge=options.challenge,
            user={'id': data['id']}
        )

        credential_id = verification['credential_id']
        public_key = verification['credential_public_key']
        sign_count = verification['sign_count']

        # Check if the credential already exists in the Admin table
        mycursor.execute("SELECT * FROM Admin WHERE credential_id = %s", (credential_id,))
        admin = mycursor.fetchone()

        if admin:
            return jsonify({"status": "error", "message": "Credential already registered."})

        # If the credential isn't in the database, print info for manual addition
        print("New credential detected!")
        print(f"User ID: {data['id']}")
        print(f"Username: {data['username']}")
        print(f"Admin Type: 'Specify the admin type'")
        print(f"Credential ID: {credential_id}")
        print(f"Public Key: {public_key}")
        print(f"Sign Count: {sign_count}")

        return jsonify({"status": "Forbidden", "message": "Credentials do not match any existing admin records."})

    except Exception as e:
        print(f"Verification failed: {str(e)}")
        abort(400)

@app.route('/admin/send', methods=['POST'])
def sendRoute():
    print(request.get_json())
    data = request.get_json()
    def has_expected_format(d):
        expected_format = {
            'seller': str,
            'data': {
                'printName': str,
                'customer': str,
                'printCost': int,
                'payment': str,
                'image': str
            },
            'auth': str
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
    if data['auth'] != os.getenv('admin_auth'):
        abort(404)
    seller = data['seller']
    print_name = data['data']['printName']
    customer = data['data']['customer']
    print_cost = data['data']['printCost']
    payment = data['data']['payment']
    image = data['data']['image']
    printed = data['data']['printed']
    accepted = data['data']['accepted']
    if accepted == 'no':
        accepted = 0
    elif accepted == 'colin':
        accepted = 1
    elif accepted == 'kavi':
        accepted = 2
    paid = data['data']['paid']
    delivered = data['data']['delivered']
    # Execute the query
    mycursor.execute(
        """
        INSERT INTO Prints (Seller, PrintName, Customer, PrintCost, Payment, Image, Printed, Accepted, Paid, Delivered)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, 
        (seller, print_name, customer, print_cost, payment, image, printed, accepted, paid, delivered)
    )
    mydb.commit()  
    return "<body style='background-color: lime;'><center><h1>Success</h1></center></body>"
@app.route('/verify-registration', methods=['POST'])
def verify_registration_route():
    data = request.get_json()
    options = session.get('registration_options')

    if not options:
        return jsonify({"status": "error", "message": "No registration options found."}), 400

    try:
        # Extract challenge and rp_id from the options
        challenge = options.challenge
        rp_id = options.rp_id

        # Verify the registration response
        verification = verify_registration_response(
            credential=data,
            expected_challenge=challenge,
            expected_origin=["http://localhost", "https://chesdev.me"],
            expected_rp_id=rp_id,
            require_user_verification=True
        )

        credential_id = verification['credential_id']
        public_key = base64.urlsafe_b64encode(verification['credential_public_key']).decode('utf-8')
        sign_count = verification['sign_count']

        # Generate MySQL shell command
        mysql_command = f"""
        INSERT INTO Admin (username, admin_type, credential_id, public_key, sign_count)
        VALUES (
            'new_user',  -- Replace with actual username
            'admin',  -- Replace with actual admin type
            '{credential_id}', 
            '{public_key}', 
            {sign_count}
        );
        """

        # Print the command to console
        print("MySQL command to add new user:")
        print(mysql_command)

        # Return success response
        return jsonify({"status": "success", "message": "Verification successful, MySQL command generated.", "mysql_command": mysql_command})

    except Exception as e:
        print(f"Verification failed: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400
@app.route('/admin/authenticate', methods=['POST'])
def authenticate():
    data = request.get_json()

    try:
        options = generate_authentication_options(
            rp_id="chesdev.me",
            user_verification="required"
        )

        session['auth_options'] = options
        return jsonify(options)

    except Exception as e:
        print(f"Authentication failed: {str(e)}")
        abort(400)
@app.route('/admin/verify-authentication', methods=['POST'])
def verify_authentication():
    data = request.get_json()
    auth_options = session.get('auth_challenge')

    try:
        # Verify the authentication response
        verification = verify_authentication_response(
            credential=data,
            expected_challenge=base64url_decode(auth_options),
            expected_origin=["http://localhost", "https://chesdev.me"],
            expected_rp_id="chesdev.me",
            require_user_verification=True
        )

        credential_id = verification['credential_id']

        # Check if the credential exists in the Admin table
        mycursor.execute("SELECT * FROM Admin WHERE credential_id = %s", (credential_id,))
        admin = mycursor.fetchone()

        if not admin:
            # If the credential isn't found, print the necessary information
            print("Unrecognized credential attempted login!")
            print(f"Credential ID: {credential_id}")
            print(f"Public Key: {verification['credential_public_key']}")
            print(f"Sign Count: {verification['sign_count']}")
            return jsonify({"status": "error", "message": "Unrecognized credential."}), 403

        # Mark the admin as logged in
        session['admin_logged_in'] = True
        return jsonify({"status": "success", "message": "Authenticated successfully."})

    except Exception as e:
        print(f"Verification failed: {str(e)}")
        return jsonify({"status": "error", "message": "Verification failed."}), 400


@app.route('/admin')
def adminRoute():
    if not session.get('admin_logged_in'):
        return redirect(url_for('index.index'))

    # Fetch data from the database
    mycursor.execute("SELECT * FROM Prints")
    prints_data = mycursor.fetchall()

    # Pass the fetched data to the template
    return render_template('prints.html', prints=prints_data)
