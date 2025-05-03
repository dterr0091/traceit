import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import SourceTrace from "./pages/SourceTrace";

const PERPLEXITY_API_KEY = import.meta.env.VITE_PERPLEXITY_API_KEY;

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<SourceTrace />} />
      </Routes>
    </Router>
  );
}
