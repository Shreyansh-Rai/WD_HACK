import React, { useEffect, useState } from "react";
import "../App.css"; // CSS file for styling

const FileCard = ({ path }) => {
  const [shineEffect, setShineEffect] = useState(false);

  useEffect(() => {
    // Set shineEffect to true on component mount
    setShineEffect(true);

    // Clean up function to reset the effect after the first animation
    return () => {
      setShineEffect(false);
    };
  }, []);

  const handleCardClick = () => {
    const filePath = `file:///${path.replace(/\\/g, '/')}`; // Assuming `path` contains the file path
    navigator.clipboard.writeText(filePath)
      .then(() => {
        console.log("File path copied to clipboard:", filePath);
        alert("File path copied to clipboard!");
      })
      .catch((err) => {
        console.error("Failed to copy file path to clipboard:", err);
        alert("Failed to copy the file path.");
      });
    // const fileURL = `file:///${path.replace(/\\/g, '/')}`; // Convert Windows path to URL format
    // console.log(fileURL)
    // window.open(fileURL);
  };
  return (
    <div
      className={`fileCard ${shineEffect ? "shine" : ""}`}
      onClick={handleCardClick}
    >
      {path}
    </div>
  );
};

export default FileCard;
