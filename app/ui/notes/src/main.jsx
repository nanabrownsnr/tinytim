import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import NotesApp from "./App.jsx";
import "./style.css";

createRoot(document.querySelector("#root")).render(
  <StrictMode>
    <NotesApp />
  </StrictMode>
);
