# import os
# import json
# import numpy as np
# import mysql.connector
# from mysql.connector import MySQLConnection
# from mysql.connector.cursor import MySQLCursor
# from config import Config

# # Database connection setup
# def get_db_connection() -> MySQLConnection:
#     config = Config()
#     db_conf = {
#         "host": config.tidb_host,
#         "port": config.tidb_port,
#         "user": config.tidb_user,
#         "password": config.tidb_password,
#         "database": config.tidb_db_name,
#         "autocommit": True,  # Set autocommit as needed
#         "use_pure": True
#     }
    
#     if config.ca_path:
#         db_conf["ssl_verify_cert"] = True
#         db_conf["ssl_verify_identity"] = True
#         db_conf["ssl_ca"] = config.ca_path
    
#     return mysql.connector.connect(**db_conf)

# # Drop existing tables and create new ones
# def recreate_tables() -> None:
#     conn = get_db_connection()
#     cursor = conn.cursor()
    
#     # Drop tables if they exist
#     cursor.execute('DROP TABLE IF EXISTS embeddings')
#     cursor.execute('DROP TABLE IF EXISTS files')
#     cursor.execute('DROP TABLE IF EXISTS file_types')
#     cursor.execute('DROP TABLE IF EXISTS directories')

#     # Create directories table
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS directories (
#             id INT AUTO_INCREMENT PRIMARY KEY,
#             path VARCHAR(1024) NOT NULL
#         )
#     ''')
    
#     # Create file_types table
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS file_types (
#             id INT AUTO_INCREMENT PRIMARY KEY,
#             type VARCHAR(255) NOT NULL
#         )
#     ''')
    
#     # Create files table
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS files (
#             id INT AUTO_INCREMENT PRIMARY KEY,
#             name VARCHAR(255) NOT NULL,
#             path VARCHAR(1024) NOT NULL,
#             type_id INT,
#             caption TEXT,
#             ocr_text TEXT,
#             directory_id INT,
#             FOREIGN KEY (type_id) REFERENCES file_types(id),
#             FOREIGN KEY (directory_id) REFERENCES directories(id)
#         )
#     ''')
    
#     # Create embeddings table
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS embeddings (
#             id INT AUTO_INCREMENT PRIMARY KEY,
#             file_id INT,
#             embedding_type VARCHAR(255),
#             embedding_data VECTOR(128),
#             FOREIGN KEY (file_id) REFERENCES files(id)
#         )
#     ''')
    
#     conn.commit()
#     conn.close()

# # Store embeddings into the database
# def store_embeddings(file_id: int, embedding_type: str, embeddings: np.ndarray) -> None:
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     query = f'''
#     INSERT INTO embeddings (file_id, embedding_type, embedding_data) 
#     VALUES ({file_id}, '{embedding_type}', VEC_FROM_TEXT('{embeddings.tolist()[0]}'));
#     '''
#     print("Executing ", query)
#     cursor.execute(query)
#     conn.commit()
#     conn.close()

# # Store file types into the database
# def store_file_type(file_type: str) -> int:
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute('''
#         INSERT IGNORE INTO file_types (type)
#         VALUES (%s)
#     ''', (file_type,))
#     conn.commit()
#     cursor.execute('''
#         SELECT id FROM file_types WHERE type = %s
#     ''', (file_type,))
#     file_type_id = cursor.fetchone()[0]
#     conn.close()
#     return file_type_id

# # Store file data into the database
# def store_file(file_data: dict, directory_id: int) -> None:
#     file_type_id = store_file_type(file_data['type'])
    
#     # Extract the file name from the path
#     file_name = os.path.basename(file_data['path'])
    
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute('''
#         INSERT INTO files (name, path, type_id, caption, ocr_text, directory_id)
#         VALUES (%s, %s, %s, %s, %s, %s)
#     ''', (file_name, file_data['path'], file_type_id, file_data['caption'], file_data['ocr_text'], directory_id))
#     file_id = cursor.lastrowid
#     conn.commit()
#     conn.close()

#     # Store embeddings for the file
#     for embed_type, embed_data in file_data['embeddings'].items():
#         store_embeddings(file_id, embed_type, np.array(embed_data['embeddings']))

# # Process JSON file and store data into the database
# def process_json_file(file_path: str) -> None:
#     with open(file_path, 'r') as f:
#         data = json.load(f)

#     conn = get_db_connection()
#     cursor = conn.cursor()

#     # Store directory data
#     for result in data['results']:
#         directory_path = result['directory']
#         cursor.execute('''
#             INSERT IGNORE INTO directories (path) VALUES (%s)
#         ''', (directory_path,))
#         directory_id = cursor.lastrowid

#         # Store file data
#         for file_data in result['files']:
#             store_file(file_data, directory_id)

#     conn.commit()
#     conn.close()

# if __name__ == "__main__":
#     # Recreate tables
#     recreate_tables()

#     # Process the JSON file and store data into the database
#     process_json_file('response.json')  # Replace 'response.json' with your actual JSON file path
