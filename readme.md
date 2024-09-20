# Smart Seek - Revolutionizing File Search with Vector Databases

## Overview

Smart Seek leverages advanced AI models and TiDB’s vector database to enable accurate file retrieval through descriptive queries. By simply providing the path to the folders you want to be searchable, Smart Seek indexes them in the background, allowing you to search via natural language descriptions.

## Features

- **File Indexing:** Select folders to index, and Smart Seek processes the files using captioning, embedding, and OCR models.
- **Vector Database:** Uses TiDB’s vector database to store embeddings and perform fast, scalable searches.
- **Search Capability:** Retrieve files using natural language queries, with results ranked by semantic similarity.
- **Future Scope:** Integration with cloud storage providers, and an extension for enhanced search capabilities using an LLM interface.

## Prerequisites

- Python 3.10+
- Node.js and npm
- Ensure you have TiDB and any required credentials set up.

## Setup Instructions

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/yourusername/smart-seek.git
    cd smart-seek
    ```

2. **Install Dependencies:**
    ```bash
    cd Backend && pip install -r requirements.txt
    ```

3. **Environment Variables:**
   Set up any required environment variables for TiDB, file paths, etc.

4. **Running the Backend:**
   Navigate to the `Backend` folder and run the following commands:
    ```bash
    cd Backend
    uvicorn Backend:app --reload --host 0.0.0.0 --port 8001
    uvicorn TiDb_Hack_Backend:app --reload --host 0.0.0.0 --port 8000
    python3 processFolder.py
    python3 searchSimilar.py
    ```

5. **Running the Frontend:**
   Navigate to the `frontend` folder and start the frontend server:
    ```bash
    cd ../frontend
    npm start
    ```

6. **Handling CORS Issues:**
   If you encounter CORS issues, you can bypass them by launching your browser with web security disabled:
   - **Windows:**
     ```bash
     chrome.exe --user-data-dir="C://Chrome dev session" --disable-web-security
     ```
   - **OSX:**
     ```bash
     open -n -a /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --args --user-data-dir="/tmp/chrome_dev_test" --disable-web-security
     ```
   - **Linux:**
     ```bash
     google-chrome --disable-web-security
     ```

7. **Firebase Integration:**

   To enable Google Sign-In, you need to set up Firebase:

   **a. Create a Firebase Project:**
   - Go to [Firebase Console](https://console.firebase.google.com/).
   - Click "Add project" and follow the steps to create a new project.

   **b. Register Your App:**
   - Click on the Web icon `</>` to add a web app.
   - Register your app and copy the Firebase configuration snippet provided.

   **c. Enable Google Authentication:**
   - In the Firebase console, go to the "Authentication" section.
   - Click "Sign-in method" and enable "Google."
   - Click "Save" to apply changes.

   **d. Create and Configure `.env` File:**
   - In the root directory of your frontend project, create a `.env` file.
   - Add the following Firebase configuration:
     ```plaintext
     REACT_APP_FIREBASE_KEY=your_api_key
     REACT_APP_FIREBASE_AUTH_DOMAIN=your_project_id.firebaseapp.com
     REACT_APP_FIREBASE_PROJECT_ID=your_project_id
     REACT_APP_FIREBASE_STORAGE_BUCKET=your_project_id.appspot.com
     REACT_APP_FIREBASE_MESSAGING_SENDER_ID=your_messaging_sender_id
     REACT_APP_FIREBASE_APP_ID=your_app_id
     REACT_APP_FIREBASE_MEASUREMENT_ID=your_measurement_id
     ```
   - Replace placeholders with actual values from your Firebase configuration.

8. **Restart Your Frontend Server:**
   - Restart the frontend server to apply the new environment variables.

chrome.exe --user-data-dir="C:/Chrome dev session" --disable-web-security