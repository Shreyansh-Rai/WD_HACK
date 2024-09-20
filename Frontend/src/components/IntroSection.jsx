import React from "react";
import BotResponse from "./BotResponse";

const IntroSection = () => {
  return (
    <div id="introsection">
      <h1>
        Introducing Smart-Seek
        <BotResponse response=" - The Ultimate AI Assistant" />
      </h1>
      <h2>
        A cutting-edge AI-powered app that provides instant file search and discovery.
        With Smart-Seek, you'll never be left searching for
        files again. 
      </h2>
      Features:
      <ul>
        <li>Instant Searches</li>
        <li>Deep learning technology that improves with usage</li>
        <li>Continuously Learning</li>
        <li>User-friendly interface</li>
        <li>Available 24/7</li>
      </ul>
      <p>
        Say goodbye to endless searching Smart-Seek, with
        your personal AI assistant !
      </p>
    </div>
  );
};

export default IntroSection;
