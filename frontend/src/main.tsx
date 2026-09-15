import React from "react";
import { HelmetProvider } from "react-helmet-async";
import { Toaster } from "react-hot-toast";
import ReactDOM from "react-dom/client";
import App from "./App";

// Root for App, Helmet wraps App and provides Page Titles
ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <HelmetProvider>
      <App />
      <Toaster />
    </HelmetProvider>
  </React.StrictMode>
);
