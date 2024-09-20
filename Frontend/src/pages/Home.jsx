import React, { useEffect, useRef, useState } from "react";
import Avatar from "../components/Avatar";
import BotResponse from "../components/BotResponse";
import Error from "../components/Error";
import IntroSection from "../components/IntroSection";
import Loading from "../components/Loading";
import NavContent from "../components/NavContent";
import { ReactComponent as ArrowIcon } from '../arrow.svg'; // Adjust the path accordingly
import "./Home.css";

const Home = () => {
  const [showMenu, setShowMenu] = useState(false);
  const [inputPrompt, setInputPrompt] = useState("");
  const [chatLog, setChatLog] = useState([]);
  const [err, setErr] = useState(false);
  const [responseFromAPI, setResponseFromAPI] = useState(false);
  const [animatedText, setAnimatedText] = useState("Seek");
  const [fade, setFade] = useState(false); // State for fade effect

  const chatLogEndRef = useRef(null);
  const textOptions = ["Seek", "Find", "Search"];

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!responseFromAPI && inputPrompt.trim() !== "") {
      const newChatLogEntry = { id: Date.now(), chatPrompt: inputPrompt, botMessage: null }; // Ensure unique ID
      setChatLog((prevChatLog) => [...prevChatLog, newChatLogEntry]);
  
      // Hide the keyboard on mobile devices
      // e.target.querySelector("input").blur();
  
      setInputPrompt(""); // Clear input after submitting
      setResponseFromAPI(true); // Indicate that a response is being awaited
  
      // Simulate a delay to mimic API call
      setTimeout(async () => {
        try {
          // Simulated mock response (remove this when using actual API)
          const response = await fetch("http://localhost:4000/respond", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: inputPrompt }),
          });
  
          const resp = await response.json();
          console.log(resp.file_paths)
          const data = resp
  
          // Update chat log with the API response or mock response
          setChatLog((prevChatLog) => [
            ...prevChatLog.slice(0, prevChatLog.length - 1), // All entries except the last
            { 
              ...newChatLogEntry, 
              botMessage: "Top Matches are:\n" + 
                [...new Set(data.file_paths)] // Remove duplicates
                  .map((path, index) => `${index + 1}) ${path}`)
                  .join("\n")
            } // Update the last entry with the formatted and unique file paths
          ]);
  
          setErr(false); // No errors, set err to false
        } catch (error) {
          setErr(true); // Handle error case
          console.error("API call failed:", error);
        } finally {
          setResponseFromAPI(false); // Reset after receiving the response
        }
      }, 1000);
    }
  };
  

  // Change animated text at intervals
  useEffect(() => {
    const intervalId = setInterval(() => {
      setFade(true); // Trigger fade out

      setTimeout(() => {
        setAnimatedText((prev) => {
          const currentIndex = textOptions.indexOf(prev);
          return textOptions[(currentIndex + 1) % textOptions.length];
        });
        setFade(false); // Trigger fade in
      }, 500); // Wait for fade out before changing text

    }, 2000); // Change text every 2 seconds

    return () => clearInterval(intervalId); // Cleanup interval on unmount
  }, []);

  useEffect(() => {
    // Scroll to the bottom of the chat log to show the latest message
    if (chatLogEndRef.current) {
      chatLogEndRef.current.scrollIntoView({
        behavior: "smooth",
        block: "end",
      });
    }
  }, [chatLog]);

  return (
    <>
      <header>
        <div className="menu">
          <button onClick={() => setShowMenu(true)}>
            <svg
              width={24}
              height={24}
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              stroke="#d9d9e3"
              strokeLinecap="round"
            >
              <path d="M21 18H3M21 12H3M21 6H3" />
            </svg>
          </button>
        </div>
        <h1>Smart-Seek</h1>
      </header>

      {showMenu && (
        <nav>
          <div className="navItems">
            <NavContent
              chatLog={chatLog}
              setChatLog={setChatLog}
              setShowMenu={setShowMenu}
            />
          </div>
          <div className="navCloseIcon">
            <svg
              fill="#fff"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 100 100"
              xmlSpace="preserve"
              stroke="#fff"
              width={42}
              height={42}
              onClick={() => setShowMenu(false)}
            >
              <path d="m53.691 50.609 13.467-13.467a2 2 0 1 0-2.828-2.828L50.863 47.781 37.398 34.314a2 2 0 1 0-2.828 2.828l13.465 13.467-14.293 14.293a2 2 0 1 0 2.828 2.828l14.293-14.293L65.156 67.73c.391.391.902.586 1.414.586s1.023-.195 1.414-.586a2 2 0 0 0 0-2.828L53.691 50.609z" />
            </svg>
          </div>
        </nav>
      )}

      <aside className="sideMenu">
        <h2 className="appName">
          <span className="firstLetter">S</span>mart{" "}
          <span className={`animatedText ${fade ? 'fade-out' : 'fade-in'}`}>
            <span className="firstLetter">{animatedText.charAt(0)}</span>
            {animatedText.slice(1)}
          </span>
        </h2> {/* Display animated text */}
        <NavContent
          chatLog={chatLog}
          setChatLog={setChatLog}
          setShowMenu={setShowMenu}
        />
      </aside>

      <section className="chatBox">
        {chatLog.length > 0 ? (
          <div className="chatLogWrapper">
            {chatLog.map((chat, idx) => (
              <div className="chatLog" key={chat.id} id={`chat-${chat.id}`}>
                {/* User message */}
                <div className="chatPromptMainContainer">
                  <div className="chatPromptWrapper">
                    <Avatar bg="#5437DB" className="userSVG">
                      {/* User avatar */}
                    </Avatar>
                    <div id="chatPrompt">{chat.chatPrompt}</div>
                  </div>
                </div>
                {/* Bot response */}
                <div className="botMessageMainContainer">
                  <div className="botMessageWrapper">
                    <Avatar bg="#11a27f" className="openaiSVG">
                      {/* Bot avatar */}
                    </Avatar>
                    {chat.botMessage === "Loading..." ? (
                      <Loading />
                    ) : err ? (
                      <Error err={err} />
                    ) : (
                      <div id="botMessage">{chat.botMessage}</div>
                    )}
                  </div>
                </div>
              </div>
            ))}
            <div ref={chatLogEndRef} />{" "}
            {/* Invisible element to scroll into view */}
          </div>
        ) : (
          <IntroSection />
        )}
        <form onSubmit={handleSubmit}>
          <div className="inputPromptWrapper">
            <textarea
              name="inputPrompt"
              className="inputPrompttTextarea"
              rows="1"
              value={inputPrompt}
              onChange={(e) => {
                setInputPrompt(e.target.value);
              }} // Directly manage input changes here
              placeholder="Write the file description..." // Add placeholder here
            />
            <button aria-label="form submit" type="submit" className="submitButton">
              <ArrowIcon className="arrowIcon" width={36} height={36} />
            </button>
          </div>
        </form>
      </section>
    </>
  );
};

export default Home;
