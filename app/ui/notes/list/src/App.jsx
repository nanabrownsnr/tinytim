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

export default function ListNotesApp() {
  const [notes, setNotes] = useState([]);
  const [selectedNote, setSelectedNote] = useState(null);
  const [isFetching, setIsFetching] = useState(false);
  const [status, setStatus] = useState("loading");
  const [actionError, setActionError] = useState(null);

  const onAppCreated = useCallback(function (createdApp) {
    createdApp.ontoolresult = function (result) {
      var sc = result.structuredContent;
      if (sc) {
        if (sc.notes !== undefined) {
          setNotes(sc.notes || []);
          setStatus(sc.count > 0 ? "ok" : "empty");
        } else if (sc.note) {
          setSelectedNote(sc.note);
        }
      }
    };
  }, []);

  var appInfo = {
    name: "tinytim-notes-list-ui",
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
      fetchNotes();
    }
  }, [app, isConnected]);

  function fetchNotes() {
    if (!app) return;
    setIsFetching(true);
    setActionError(null);
    setStatus("loading");

    app
      .callServerTool({ name: "list_notes" })
      .then(function (result) {
        var sc = result.structuredContent;
        if (sc && Array.isArray(sc.notes)) {
          setNotes(sc.notes);
          setStatus(sc.count > 0 ? "ok" : "empty");
        } else {
          setStatus("error");
          setActionError("Failed to load notes.");
        }
      })
      .catch(function (err) {
        setStatus("error");
        setActionError(
          err instanceof Error ? err.message : "Failed to load notes."
        );
      })
      .finally(function () {
        setIsFetching(false);
      });
  }

  function handleSelect(note) {
    setSelectedNote(note);
  }

  var connectionHint = "";
  if (error) {
    connectionHint = "Unable to connect to MCP client: " + error.message;
  } else if (!isConnected) {
    connectionHint = "Connecting to the MCP client...";
  }

  var renderedTags = [];
  if (selectedNote && Array.isArray(selectedNote.tags)) {
    renderedTags = escapeHtmlList(selectedNote.tags);
  }

  return React.createElement(
    "main",
    { className: "card", "aria-live": "polite", "data-host-theme": theme },
    React.createElement("p", { className: "eyebrow" }, "List Notes"),
    React.createElement(
      "div",
      { className: "list-container" },
      React.createElement(
        "div",
        { className: "list-header" },
        React.createElement("h2", null, "Notes"),
        React.createElement(
          "button",
          {
            className: "refresh-btn",
            onClick: fetchNotes,
            disabled: isFetching,
          },
          isFetching ? "Refreshing..." : "Refresh"
        )
      ),
      status === "loading" && !isFetching
        ? React.createElement("p", { className: "empty-hint" }, "Loading notes...")
        : isFetching
        ? React.createElement("p", { className: "loading" }, "Loading...")
        : null,
      status === "empty" && !isFetching
        ? React.createElement("p", { className: "empty-hint" }, "No notes found.")
        : null,
      status === "ok" || status === "empty"
        ? React.createElement(
            "ul",
            { className: "note-list" },
            notes.map(function (note) {
              var isActive = selectedNote && selectedNote.id === note.id;
              var preview = note.body ? note.body.slice(0, 60) : "";
              if (note.body && note.body.length > 60) {
                preview += "...";
              }
              return React.createElement(
                "li",
                {
                  key: note.id,
                  className: isActive ? "note-item active" : "note-item",
                  onClick: function () {
                    handleSelect(note);
                  },
                },
                React.createElement(
                  "div",
                  { className: "note-item-content" },
                  React.createElement(
                    "span",
                    { className: "note-title" },
                    escapeHtml(note.title)
                  ),
                  preview
                    ? React.createElement(
                        "span",
                        { className: "note-preview" },
                        escapeHtml(preview)
                      )
                    : null,
                  note.tags && note.tags.length > 0
                    ? React.createElement(
                        "div",
                        { className: "note-tags-inline" },
                        note.tags.map(function (tag, i) {
                          return React.createElement(
                            "span",
                            { key: i, className: "tag" },
                            escapeHtml(tag)
                          );
                        })
                      )
                    : null
                ),
                React.createElement(
                  "span",
                  { className: "note-meta" },
                  new Date(note.created_at).toLocaleDateString()
                )
              );
            })
          )
        : null,
      status === "error" && !isFetching
        ? React.createElement("p", { className: "error-hint" }, actionError || "An error occurred.")
        : null
    ),
    selectedNote
      ? React.createElement(
          "div",
          { className: "detail-preview" },
          React.createElement("h3", { className: "detail-title" }, escapeHtml(selectedNote.title)),
          React.createElement(
            "p",
            { className: "detail-body" },
            escapeHtml(selectedNote.body)
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
            : null,
          React.createElement(
            "p",
            { className: "detail-meta" },
            "ID: ",
            escapeHtml(selectedNote.id),
            "  |  Status: ",
            escapeHtml(selectedNote.status),
            "  |  Created: ",
            new Date(selectedNote.created_at).toLocaleString()
          )
        )
      : null,
    actionError
      ? React.createElement("p", { className: "error-hint" }, actionError)
      : null,
    connectionHint && !actionError
      ? React.createElement("p", { className: "hint" }, connectionHint)
      : null
  );
}
