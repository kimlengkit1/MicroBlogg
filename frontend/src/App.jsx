import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./pages/LoginPage";

function HomePage() {
  return <h1>Welcome to MicroBlogg</h1>
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/home" element={<HomePage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;