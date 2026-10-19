import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import NoteDetailApp from "./App.jsx";
import "./style.css";

createRoot(document.querySelector("#root")).render(
  <StrictMode>
    <NoteDetailApp />
  </StrictMode>
);
