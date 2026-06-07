import { Routes, Route, useSearchParams } from "react-router-dom";
import HomePage from "./pages/HomePage";
import WorkspacePage from "./pages/WorkspacePage";
import HistoryPage from "./pages/HistoryPage";
import HistoryDetailPage from "./pages/HistoryDetailPage";

function WorkspaceRoute() {
  const [params] = useSearchParams();
  return <WorkspacePage key={params.get("id") || "default"} />;
}

export default function App() {
  return (
    <div className="app">
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/workspace" element={<WorkspaceRoute />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/history/:id" element={<HistoryDetailPage />} />
      </Routes>
    </div>
  );
}
