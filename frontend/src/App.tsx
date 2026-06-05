import { Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import WorkspacePage from "./pages/WorkspacePage";

export default function App() {
  return (
    <div className="app">
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/workspace" element={<WorkspacePage />} />
      </Routes>
    </div>
  );
}
