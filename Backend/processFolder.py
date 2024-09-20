from flask import Flask, request, jsonify
import requests
import json
import os
import numpy as np
import mysql.connector
from mysql.connector import MySQLConnection
from config import Config
from flask_cors import CORS, cross_origin
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app, resources={r"/*": {
    "origins": "*",
    "methods": ["*"],
    "allow_headers": ["*"],
}}, supports_credentials=True)

# Database connection setup
def get_db_connection() -> MySQLConnection:
    load_dotenv()
    config = Config()
    db_conf = {
        "host": config.tidb_host,
        "port": config.tidb_port,
        "user": config.tidb_user,
        "password": config.tidb_password,
        "database": config.tidb_db_name,
        "autocommit": True,
        "use_pure": True
    }
    

    if config.ca_path:
        db_conf["ssl_verify_cert"] = True
        db_conf["ssl_verify_identity"] = True
        db_conf["ssl_ca"] = config.ca_path
    return mysql.connector.connect(**db_conf)

# Drop existing tables and create new ones
def recreate_tables() -> None:
    print("Starting")
    conn = get_db_connection()
    print("Conn est")
    cursor = conn.cursor()

    # Drop tables if they exist
    cursor.execute('DROP TABLE IF EXISTS embeddings')
    cursor.execute('DROP TABLE IF EXISTS files')
    cursor.execute('DROP TABLE IF EXISTS file_types')
    cursor.execute('DROP TABLE IF EXISTS directories')

    # Create directories table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS directories (
            id INT AUTO_INCREMENT PRIMARY KEY,
            path VARCHAR(1024) NOT NULL
        )
    ''')
    
    # Create file_types table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS file_types (
            id INT AUTO_INCREMENT PRIMARY KEY,
            type VARCHAR(255) NOT NULL
        )
    ''')
    
    # Create files table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            path VARCHAR(1024) NOT NULL,
            type_id INT,
            caption TEXT,
            ocr_text TEXT,
            directory_id INT,
            FOREIGN KEY (type_id) REFERENCES file_types(id),
            FOREIGN KEY (directory_id) REFERENCES directories(id)
        )
    ''')
    
    # Create embeddings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS embeddings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            file_id INT,
            embedding_type VARCHAR(255),
            embedding_data VECTOR(128),  # Change VECTOR to BLOB for compatibility
            FOREIGN KEY (file_id) REFERENCES files(id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Fetch API data and save to a file
def fetch_api_data(url, payload, output_file):
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("API RESPONSE, ",url," ", response)
        data = response.json()

        with open(output_file, 'w') as file:
            json.dump(data, file, indent=4)

        return data

    except requests.exceptions.HTTPError as http_err:
        return {"error": str(http_err)}
    except requests.exceptions.RequestException as req_err:
        return {"error": str(req_err)}
    except ValueError as json_err:
        return {"error": str(json_err)}

# Store embeddings into the database
def store_embeddings(file_id: int, embedding_type: str, embeddings: np.ndarray) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    query = f'''
    INSERT INTO embeddings (file_id, embedding_type, embedding_data) 
    VALUES ({file_id}, '{embedding_type}', VEC_FROM_TEXT('{embeddings.tolist()[0]}'));
    '''
    print("Executing Query To Store Embedding, \n", query)
    cursor.execute(query)
    conn.commit()
    conn.close()

# Store file types into the database
def store_file_type(file_type: str) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT IGNORE INTO file_types (type)
        VALUES (%s)
    ''', (file_type,))
    conn.commit()
    cursor.execute('''
        SELECT id FROM file_types WHERE type = %s
    ''', (file_type,))
    file_type_id = cursor.fetchone()[0]
    conn.close()
    return file_type_id

# Store file data into the database
def store_file(file_data: dict, directory_id: int) -> None:
    file_type_id = store_file_type(file_data['type'])

    # Extract the file name from the path
    file_name = os.path.basename(file_data['path'])

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO files (name, path, type_id, caption, ocr_text, directory_id)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (file_name, file_data['path'], file_type_id, file_data['caption'], file_data['ocr_text'], directory_id))
    file_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # Store embeddings for the file
    for embed_type, embed_data in file_data['embeddings'].items():
        store_embeddings(file_id, embed_type, np.array(embed_data['embeddings']))

# Process JSON file and store data into the database
def process_json_file(file_path: str) -> None:
    with open(file_path, 'r') as f:
        data = json.load(f)

    conn = get_db_connection()
    cursor = conn.cursor()

    # Store directory data
    for result in data['results']:
        directory_path = result['directory']
        cursor.execute('''
            INSERT IGNORE INTO directories (path) VALUES (%s)
        ''', (directory_path,))
        directory_id = cursor.lastrowid

        # Store file data
        for file_data in result['files']:
            store_file(file_data, directory_id)

    conn.commit()
    conn.close()

@app.route('/process-folder', methods=['POST', 'OPTIONS'])
def process_folder():
    if request.method == "OPTIONS":
        return '', 204  # Respond OK to preflight
    data = request.json
    folder_path = "C:\\Users\\Shreyansh\\Desktop\\TestWDFolder"
    print("Got request, ", request.json)
    if not folder_path:
        return jsonify({"error": "No folder path provided"}), 400

    api_url = "http://localhost:8001/permit-list/"
    output_file = "response.json"

    # Call the function to fetch data from the API and save it to a file
    response_data = fetch_api_data(api_url, {"paths": [folder_path]}, output_file)
    print("RESPONSE ", response_data)
    # Process the JSON file and store data into the database
    if 'error' not in response_data:
        process_json_file(output_file)  # Process the JSON file after successful fetch

    return jsonify(response_data)

if __name__ == "__main__":
    # Recreate tables when starting the server
    recreate_tables()
    app.run(debug=True,port=5000)
