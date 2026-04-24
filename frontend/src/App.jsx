import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./pages/LoginPage";
import SignUp from "./pages/SignUpPage";
import HomePage from "./pages/Homepage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="/home" element={<HomePage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;