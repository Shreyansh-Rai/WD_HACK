import React, { useState } from "react";
import axios from "axios"; // Import axios for making HTTP requests
import { ReactComponent as FolderIcon } from '../folder.svg'; // Import your SVG icon
import "../App.css"; // Ensure your CSS file includes the necessary styles

const NewChat = ({ setChatLog, setShowMenu }) => {
  const [showDialog, setShowDialog] = useState(false);
  const [showLoader, setShowLoader] = useState(false);

  const handleFolderSelect = async (event) => {
    const files = event.target.files;

    if (files.length > 0) {
      // Extract the folder path from the first file's webkitRelativePath
      console.log(files[0]);
      let folderPath = files[0].webkitRelativePath.split("/").slice(0, -1).join("/");
      folderPath = "/Users/shreyanshrai/Desktop/" + folderPath;
      console.log(`Selected folder path: ${folderPath}`);

      // Close the dialog before showing the loader
      setShowDialog(false);

      // Show the loader backdrop
      setShowLoader(true);

      // Simulate a delay of 3 seconds for loader
      setTimeout(async () => {
        // Prepare the payload for the Flask server
        const payload = {
          path: folderPath,
        };
        try {
          // Make the API request to the Flask server
          const response = await axios.post(
            "http://127.0.0.1:5000/process-folder", // Update to your Flask server endpoint
            payload
          );

          // Log the response data
          console.log("Server Response:", response.data);

          // Optionally, handle the response data (e.g., update the chat log)
          setChatLog(response.data.results);
        } catch (error) {
          console.error("Error fetching data:", error);
        } finally {
          // Hide the loader after 3 seconds
          setShowLoader(false);
        }
      }, 3000); // 3-second loader delay
    } else {
      setShowDialog(false); // Close the dialog if no files are selected
    }
  };

  return (
    <div>
      <div
        className="sideMenuButton"
        onClick={() => {
          setChatLog([]);
          setShowMenu(false);
          setShowDialog(true);
        }}
      >
        <span>+</span>
        Add Folder
      </div>

      {showDialog && (
        <div className="overlay">
          <div className="modal">
            <div className="modalContent">
              <div className="modalHeader">
                <FolderIcon width={50} height={50} /> {/* SVG icon on the left */}
                <h3>Folder Manager</h3> {/* Modal heading */}
              </div>
              <div className="uploadOptions">
                <label className="uploadButton">
                  Add
                  <input
                    type="file"
                    webkitdirectory=""
                    directory=""
                    onChange={handleFolderSelect}
                    style={{ display: "none" }} // Hide the file input
                  />
                </label>

                <button
                  className="uploadButton cancelButton"
                  onClick={() => setShowDialog(false)}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {showLoader && (
        <div className="loaderBackdrop">
          <div className="spinner"></div> {/* Spinner element */}
          <span style={{ marginLeft: '10px', color: 'white' }}>Processing...</span>
        </div>
      )}
    </div>
  );
};

export default NewChat;
