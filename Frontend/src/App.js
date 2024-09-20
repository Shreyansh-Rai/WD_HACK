import "./normal.css";
import "./App.css";
import Home from "./pages/Home";
import Login from "./pages/Login";
import LoginForm from "./components/login/LoginForm";
import { Route, Routes } from "react-router-dom";

function App() {
  return (
    <div className="App">
      <Routes>
        <Route index exact path="/" element={<Home />} />
        <Route exact path="auth/login" element={<Login />} />
        <Route exact path="login" element={<LoginForm />} />
      </Routes>
    </div>
  );
}

export default App;
