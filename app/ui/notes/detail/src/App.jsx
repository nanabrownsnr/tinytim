import React, { useCallback, useEffect, useState } from "react";
import {
  useApp,
  useDocumentTheme,
  useHostFonts,
  useHostStyleVariables,
} from "@modelcontextprotocol/ext-apps/react";

function escapeHtml(value) {
  const div = document.createElement("div");
  div.appendChild(document.createTextNode(String(value)));
  return div.innerHTML;
}

function escapeHtmlList(items) {
  return items.map(function (t) {
    return escapeHtml(t);
  });
}

export default function NoteDetailApp() {
  const [note, setNote] = useState(null);
  const [noteId, setNoteId] = useState(null);
  const [isFetching, setIsFetching] = useState(false);
  const [status, setStatus] = useState("loading");
  const [actionError, setActionError] = useState(null);

  const onAppCreated = useCallback(function (createdApp) {
    createdApp.ontoolresult = function (result) {
      var sc = result.structuredContent;
      if (sc && sc.note) {
        setNote(sc.note);
        setStatus("ok");
      }
    };
  }, []);

  var appInfo = {
    name: "tinytim-notes-detail-ui",
    version: "1.0.0",
  };

  var _a = useApp({
    appInfo: appInfo,
    capabilities: {},
    onAppCreated: onAppCreated,
    autoResize: true,
  });
  var app = _a.app;
  var isConnected = _a.isConnected;
  var error = _a.error;

  useHostStyleVariables(app, app ? app.getHostContext() : undefined);
  useHostFonts(app, app ? app.getHostContext() : undefined);
  var theme = useDocumentTheme();

  useEffect(function () {
    if (app && isConnected) {
      var params = app.getHostContext ? app.getHostContext() : {};
      var id = params.noteId || params.id || null;
      if (id) {
        setNoteId(id);
        fetchNote(id);
      } else {
        setStatus("idle");
      }
    }
  }, [app, isConnected]);

  function fetchNote(id) {
    if (!app || !id) return;
    setIsFetching(true);
    setNote(null);
    setActionError(null);
    setStatus("loading");

    app
      .callServerTool({ name: "get_note", arguments: { note_id: id } })
      .then(function (result) {
        var sc = result && result.structuredContent;
        if (sc && sc.note) {
          setNote(sc.note);
          setStatus("ok");
        } else {
          setStatus("not-found");
          setActionError("Note not found.");
        }
      })
      .catch(function (err) {
        setStatus("not-found");
        setActionError(
          err instanceof Error ? err.message : "Note not found."
        );
      })
      .finally(function () {
        setIsFetching(false);
      });
  }

  var connectionHint = "";
  if (error) {
    connectionHint = "Unable to connect to MCP client: " + error.message;
  } else if (!isConnected) {
    connectionHint = "Connecting to the MCP client...";
  }

  var renderedTags = [];
  if (note && Array.isArray(note.tags)) {
    renderedTags = escapeHtmlList(note.tags);
  }

  return React.createElement(
    "main",
    { className: "card", "aria-live": "polite", "data-host-theme": theme },
    React.createElement("p", { className: "eyebrow" }, "Note Detail"),
    status === "idle"
      ? React.createElement(
          "p",
          { className: "empty-hint" },
          "No note ID provided. Pass a noteId parameter to view a note."
        )
      : null,
    status === "loading" && !isFetching
      ? React.createElement("p", { className: "empty-hint" }, "Loading note...")
      : isFetching
      ? React.createElement("p", { className: "loading" }, "Loading...")
      : null,
    status === "not-found" && !isFetching
      ? React.createElement("p", { className: "error-hint" }, actionError || "Note not found.")
      : null,
    note
      ? React.createElement(
          "div",
          { className: "detail-view" },
          React.createElement("h3", { className: "detail-title" }, escapeHtml(note.title)),
          React.createElement(
            "p",
            { className: "detail-body" },
            escapeHtml(note.body)
          ),
          renderedTags.length > 0
            ? React.createElement(
                "div",
                { className: "tags" },
                renderedTags.map(function (tag, i) {
                  return React.createElement(
                    "span",
                    { key: i, className: "tag" },
                    tag
                  );
                })
              )
            : React.createElement(
                "p",
                { className: "no-tags" },
                "No tags"
              ),
          React.createElement(
            "dl",
            { className: "detail-meta" },
            React.createElement("dt", null, "ID"),
            React.createElement("dd", null, escapeHtml(note.id)),
            React.createElement("dt", null, "Status"),
            React.createElement("dd", null, escapeHtml(note.status)),
            React.createElement("dt", null, "Created"),
            React.createElement("dd", null, new Date(note.created_at).toLocaleString())
          )
        )
      : null,
    actionError && status !== "not-found"
      ? React.createElement("p", { className: "error-hint" }, actionError)
      : null,
    connectionHint && !actionError && status !== "idle"
      ? React.createElement("p", { className: "hint" }, connectionHint)
      : null
  );
}
