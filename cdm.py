from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from urllib.parse import quote_plus
import os

app = Flask(__name__)
CORS(app)

# MongoDB connection settings
username = "pratham3229"
password = "pspd@123"  # Replace this with your actual password
encoded_username = quote_plus(username)
encoded_password = quote_plus(password)

# Create the connection string
MONGO_URI = f'mongodb+srv://{encoded_username}:{encoded_password}@cluster0.rc2vy.mongodb.net/downtime_data?retryWrites=true&w=majority'
DATABASE_NAME = 'downtime_data'  # Name of the database
COLLECTION_NAME = 'downtime'  # Name of the collection

# Initialize the MongoDB client
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# Save downtime data to the MongoDB database
@app.route('/save_downtime', methods=['POST'])
def save_downtime():
    data = request.json
    entry_id = data.get('entry_id')
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    category = data.get('category')
    reason = data.get('reason')
    chipper = data.get('chipper', 'Unknown Chipper')  # Default to 'Unknown Chipper' if not provided

    # Check if any required fields are missing
    if not start_time or not end_time or not reason or not category:
        return jsonify({'error': 'start_time, end_time,category and reason are required fields.'}), 400

    # Insert the data into the MongoDB collection
    downtime_record = {
        'entry_id': entry_id,
        'start_time': start_time,
        'end_time': end_time,
        'category' : category,
        'reason': reason,
        'chipper': chipper
    }
    collection.insert_one(downtime_record)

    return jsonify({'message': 'Downtime saved successfully!'})

# Fetch all downtime records
@app.route('/get_downtime', methods=['GET'])
def get_downtime():
    data = collection.find()
    
    # Convert the data to a JSON-friendly format
    downtime_list = []
    for record in data:
        downtime_list.append({
            'entry_id': record['entry_id'],  # Convert ObjectId to string
            'start_time': record['start_time'],
            'end_time': record['end_time'],
            'category':record['category'],
            'reason': record['reason'],
            'chipper': record.get('chipper', 'Unknown Chipper')
        })

    return jsonify(downtime_list)
    
@app.route('/update_entry/<string:custom_id>', methods=['PUT'])
def update_entry(custom_id):
    data = request.json  # Get data from the request body
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Update the entry based on the custom_id
    result = collection.update_one({"entry_id": custom_id}, {"$set": data})
    
    if result.matched_count > 0:
        return jsonify({"message": "Entry updated successfully"}), 200
    else:
        return jsonify({"error": "Entry not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
