from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Path to SQLite database
DATABASE = 'downtime_data_mod.db'

# Initialize the SQLite database (create table if it doesn't exist)
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        # Create the downtime table with an additional 'chipper' column if not exists
        conn.execute('''CREATE TABLE IF NOT EXISTS downtime (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            start_time TEXT NOT NULL,
                            end_time TEXT NOT NULL,
                            reason TEXT NOT NULL,
                            chipper TEXT)''')

# Save downtime data to the SQLite database
@app.route('/save_downtime', methods=['POST'])
def save_downtime():
    data = request.json
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    reason = data.get('reason')
    chipper = data.get('chipper', 'Unknown Chipper')  # Get chipper from request or default to 'Unknown Chipper'

    # Check if any required fields are missing
    if not start_time or not end_time or not reason:
        return jsonify({'error': 'start_time, end_time, and reason are required fields.'}), 400

    # Insert the data into the SQLite database, including the chipper
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO downtime (start_time, end_time, reason, chipper) VALUES (?, ?, ?, ?)',
                       (start_time, end_time, reason, chipper))
        conn.commit()

    return jsonify({'message': 'Downtime saved successfully!'})

# Fetch all downtime records (optional, if you need to display data)
@app.route('/get_downtime', methods=['GET'])
def get_downtime():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM downtime')
        data = cursor.fetchall()

    # Convert the data to a JSON-friendly format
    downtime_list = []
    for row in data:
        # Ensure the row has the expected number of columns
        if len(row) == 5:  # id, start_time, end_time, reason, chipper
            downtime_list.append({
                'id': row[0],
                'start_time': row[1],
                'end_time': row[2],
                'reason': row[3],
                'chipper': row[4] or 'Unknown Chipper'
            })

    return jsonify(downtime_list)

if __name__ == '__main__':
    # Initialize the database before starting the app
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
