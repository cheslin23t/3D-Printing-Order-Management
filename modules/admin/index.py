from flask import render_template, Blueprint, session, request, abort
import pprint
import os
from ..utils.database import mydb
mycursor = mydb.cursor(dictionary=True)
app = Blueprint('admin', __name__, template_folder='../../templates')

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
    
    # Execute the query
    mycursor.execute(
        """
        INSERT INTO Prints (Seller, PrintName, Customer, PrintCost, Payment, Image, Printed, Accepted, Paid, Delivered)
        VALUES (%s, %s, %s, %s, %s, %s, TRUE, TRUE, TRUE)
        """, 
        (seller, print_name, customer, print_cost, payment, image)
    )
    mydb.commit()  
    return "<body style='background-color: lime;'><center><h1>Success</h1></center></body>"
        
    
@app.route('/test')
def test():
    testin = [{"name": "Benchy", "price": 1, "Customer": "Joe", }]
    return render_template('prints.html')