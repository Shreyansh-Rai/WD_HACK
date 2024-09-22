from flask import Flask, request, jsonify
import requests
import json
import mysql.connector
from mysql.connector import MySQLConnection
from config import Config

app = Flask(__name__)

# Function to identify the type of resource described by the input text
def identify_resource_type(text: str) -> str:
    text_lower = text.lower()
    if any(word in text_lower for word in ["photo", "image", "picture", "pic"]):
        return "image"
    elif any(word in text_lower for word in ["document", "pdf", "file"]):
        return "document"
    else:
        return "unknown"

# Function to get the embedding for the input text
def get_text_embedding(text: str) -> list:
    api_url = "http://localhost:8000/embed/"  # Replace with the actual API endpoint
    headers = {"Content-Type": "application/json"}
    
    # Prepare the payload in the expected JSON format
    payload = {"text": [text]}

    # Make the API request
    response = requests.post(api_url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        data = response.json()
        embedding = data.get("embeddings", [])[0]
        
        # Identify the resource type (optional)
        resource_type = identify_resource_type(text)
        return embedding
    else:
        return []

# Database connection setup
def get_db_connection() -> MySQLConnection:
    config = Config()
    db_conf = {
        "host": config.tidb_host,
        "port": config.tidb_port,
        "user": config.tidb_user,
        "password": config.tidb_password,
        "database": config.tidb_db_name,
        "autocommit": True,  # Set autocommit as needed
        "use_pure": True
    }
    
    if config.ca_path:
        db_conf["ssl_verify_cert"] = True
        db_conf["ssl_verify_identity"] = True
        db_conf["ssl_ca"] = config.ca_path
    
    return mysql.connector.connect(**db_conf)

# Function to find top 3 closest embeddings and their file paths
def find_top_three_embeddings(input_embedding: list) -> list:
    if not input_embedding:
        return []

    conn = get_db_connection()
    cursor = conn.cursor()

    # Convert input_embedding to a string format compatible with the SQL query
    input_embedding_str = json.dumps(input_embedding)
    
    # Query to find the top 3 closest embeddings and their associated file paths
    query = f'''
    SELECT files.path 
    FROM embeddings
    JOIN files ON embeddings.file_id = files.id
    ORDER BY Vec_Cosine_Distance(embeddings.embedding_data, VEC_FROM_TEXT('{input_embedding_str}')) ASC
    LIMIT 5;
    '''

    try:
        cursor.execute(query)
        results = cursor.fetchall()
        return [result[0] for result in results]  # Return only the file paths

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []

    finally:
        conn.close()

@app.route('/respond', methods=['POST'])
def respond():
    data = request.json
    input_text = data.get('message', '')
    
    embedding = get_text_embedding(input_text)
    top_paths = find_top_three_embeddings(embedding)
    return jsonify({"file_paths": top_paths})

if __name__ == "__main__":
    app.run(port=4000, debug=True)  # Ensure this matches your frontend fetch URL
