from flask import render_template, Blueprint, session, redirect, request
from ..utils.database import mydb
from ..utils.error import makeResponseJSON
import hashlib
import json
from datetime import datetime as Datetime
mycursor = mydb.cursor(dictionary=True)
app = Blueprint('orders', __name__, template_folder='../../templates')
from decimal import Decimal

@app.route('/order/submit', methods=['POST'])
def submitOrder():
    data = request.form
    def has_expected_format(d):
        expected_format = {
            "Referrer": str,
            "additionalNotes": str,
            "budget": str,
            "email": str,
            "fullName": str,
            "modelDetails": str,
            "modelImage": str,
            "modelSize": str,
            "phoneNumber": str,
            "printStuff": str,
            "thingiverseUrl": str,
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
    if not has_expected_format(data):
        return makeResponseJSON(400, "Invalid data format")
    referrer = data['Referrer']
    additionalNotes = data['additionalNotes']
    budget = data['budget']
    email = data['email']
    fullName = data['fullName']
    modelDetails = data['modelDetails']
    modelImage = data['modelImage']
    modelSize = data['modelSize']
    phoneNumber = data['phoneNumber']
    printStuff = data['printStuff']
    thingiverseUrl = data['thingiverseUrl']
    if budget.isdigit() == False:
        return makeResponseJSON(400, "Invalid budget format")
    saveOrder = {"date": Datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                 "client": fullName,
                 "email": email,
                 "phone": phoneNumber,
                 "budget": int(budget),
                 "referrer": referrer}
    
    if phoneNumber != '':
        saveOrder['phone'] = phoneNumber
    else:
        saveOrder['phone'] = "No phone number provided."
    if printStuff == 'yes':
        saveOrder['thingiverseUrl'] = "No URL Provided"
        saveOrder['customModel'] = True
        if additionalNotes != '':
            saveOrder['additionalNotes'] = additionalNotes
        else:
            saveOrder['additionalNotes'] = "No additional notes provided."
        if modelImage != '':
            saveOrder['modelImage'] = modelImage
        else:
            saveOrder['modelImage'] = "No image provided."
        saveOrder['modelSize'] = modelSize
        saveOrder['modelDetails'] = modelDetails
    elif printStuff == 'no':
        saveOrder['customModel'] = False
        saveOrder['thingiverseUrl'] = thingiverseUrl
        saveOrder['additionalNotes'] = "No additional notes provided."
        saveOrder['modelImage'] = "No image provided."
        saveOrder['modelSize'] = "No size provided."
        saveOrder['modelDetails'] = "No details provided."
    else:
        return makeResponseJSON(400, "Invalid values")
    
    
    """
    TABLE Submissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATETIME DEFAULT CURRENT_TIMESTAMP,
    client VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    budget DECIMAL(10, 2),
    referrer VARCHAR(255),
    customModel BOOLEAN,
    additionalNotes TEXT,
    modelImage TEXT,
    modelSize VARCHAR(100),
    modelDetails TEXT,
    thingiverseUrl TEXT
);
    """
    # Grab data from saveOrder dict
    mycursor.execute("INSERT INTO Submissions (client, email, phone, budget, referrer, customModel, additionalNotes, modelImage, modelSize, modelDetails, thingiverseUrl) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (saveOrder['client'], saveOrder['email'], saveOrder['phone'], saveOrder['budget'], saveOrder['referrer'], saveOrder['customModel'], saveOrder['additionalNotes'], saveOrder['modelImage'], saveOrder['modelSize'], saveOrder['modelDetails'], saveOrder['thingiverseUrl']))
    mydb.commit()
    return saveOrder