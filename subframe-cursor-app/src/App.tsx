import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { Auth0Provider } from "@auth0/auth0-react";
import SourceTrace from "./pages/SourceTrace";

export default function App() {
  return (
    <Auth0Provider
      domain={import.meta.env.VITE_AUTH0_DOMAIN ?? ''}
      clientId={import.meta.env.VITE_AUTH0_CLIENT_ID ?? ''}
      authorizationParams={{
        redirect_uri: window.location.origin
      }}
    >
      <Router>
        <Routes>
          <Route path="/" element={<SourceTrace />} />
        </Routes>
      </Router>
    </Auth0Provider>
  );
}
