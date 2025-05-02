import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import SourceTrace from "./pages/SourceTrace";

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<SourceTrace />} />
      </Routes>
    </Router>
  );
}
