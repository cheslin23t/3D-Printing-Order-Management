def makeResponseJSON(success, message="Request processed successfully.", code=200, data={}):
    response = {
    "success": success,  # Indicates whether the operation was successful
    "message": message,  # A human-readable message
    "data": data
    }
    return (response, code)