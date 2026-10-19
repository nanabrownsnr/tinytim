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

export default function NotesApp() {
  const [notes, setNotes] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [tags, setTags] = useState("");
  const [message, setMessage] = useState("");
  const [status, setStatus] = useState("loading");
  const [isCreating, setIsCreating] = useState(false);
  const [isFetching, setIsFetching] = useState(false);
  const [actionError, setActionError] = useState(null);

  const onAppCreated = useCallback(function (createdApp) {
    createdApp.ontoolresult = function (result) {
      var sc = result.structuredContent;
      if (sc) {
        if (sc.note) {
          setMessage("Note created successfully.");
          setStatus("success");
          setNotes(function (prev) {
            var copy = prev.slice();
            var exists = copy.some(function (n) {
              return n.id === sc.note.id;
            });
            if (!exists) {
              copy.push(sc.note);
            }
            return copy;
          });
        } else if (sc.notes !== undefined) {
          setNotes(sc.notes || []);
          setStatus("ok");
        }
      }
    };
  }, []);

  var appInfo = {
    name: "tinytim-notes-ui",
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

  function handleCreate(e) {
    e.preventDefault();
    if (!app || isCreating) return;

    var trimmedTitle = title.trim();
    var trimmedBody = body.trim();

    if (!trimmedTitle || !trimmedBody) return;

    setIsCreating(true);
    setActionError(null);
    setStatus("loading");

    var tagList = tags.trim()
      ? tags
          .split(",")
          .map(function (t) {
            return t.trim();
          })
          .filter(function (t) {
            return t.length > 0;
          })
      : undefined;

    app
      .callServerTool({
        name: "create_note",
        arguments: { title: trimmedTitle, body: trimmedBody, tags: tagList },
      })
      .then(function () {
        setTitle("");
        setBody("");
        setTags("");
      })
      .catch(function (err) {
        setStatus("error");
        setActionError(
          err instanceof Error ? err.message : "Failed to create note."
        );
      })
      .finally(function () {
        setIsCreating(false);
      });
  }

  function handleSelect(note) {
    setSelectedId(note.id);
    setStatus("ok");
  }

  var selectedNote = notes.find(function (n) {
    return n.id === selectedId;
  });

  var renderedTags = [];
  if (selectedNote && Array.isArray(selectedNote.tags)) {
    var _escaped = escapeHtmlList(selectedNote.tags);
    renderedTags = _escaped;
  }

  var connectionHint = "";
  if (error) {
    connectionHint = "Unable to connect to MCP client: " + error.message;
  } else if (!isConnected) {
    connectionHint = "Connecting to the MCP client...";
  }

  return React.createElement(
    "main",
    { className: "card", "aria-live": "polite", "data-host-theme": theme },
    React.createElement("p", { className: "eyebrow" }, "MCP Notes App"),
    React.createElement(
      "div",
      { className: "layout" },
      React.createElement(
        "section",
        { className: "sidebar" },
        React.createElement(
          "div",
          { className: "sidebar-header" },
          React.createElement("h2", null, "Notes"),
          isFetching
            ? React.createElement("span", { className: "loading" }, "Loading...")
            : null
        ),
        status === "empty" && !isFetching
          ? React.createElement("p", { className: "empty-hint" }, "No notes yet. Create one below.")
          : null,
        React.createElement(
          "ul",
          { className: "note-list" },
          notes.map(function (note) {
            var isActive = note.id === selectedId;
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
                "span",
                { className: "note-title" },
                escapeHtml(note.title)
              ),
              React.createElement(
                "span",
                { className: "note-meta" },
                new Date(note.created_at).toLocaleDateString()
              )
            );
          })
        ),
        React.createElement(
          "button",
          { className: "refresh-btn", onClick: fetchNotes, disabled: isFetching },
          isFetching ? "Refreshing..." : "Refresh"
        )
      ),
      React.createElement(
        "section",
        { className: "detail" },
        selectedNote
          ? React.createElement(
              "div",
              null,
              React.createElement(
                "h3",
                { className: "detail-title" },
                escapeHtml(selectedNote.title)
              ),
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
                { className: "detail-date" },
                "Created: " +
                  new Date(selectedNote.created_at).toLocaleString()
              )
            )
          : React.createElement(
              "p",
              { className: "placeholder" },
              "Select a note or create a new one."
            )
      )
    ),
    React.createElement(
      "form",
      { className: "create-form", onSubmit: handleCreate },
      React.createElement("h3", null, "Create Note"),
      React.createElement("label", { htmlFor: "note-title" }, "Title"),
      React.createElement("input", {
        id: "note-title",
        name: "note-title",
        type: "text",
        value: title,
        placeholder: "Note title",
        autoComplete: "off",
        onChange: function (e) {
          return setTitle(e.target.value);
        },
        required: true,
        disabled: !isConnected || isCreating,
      }),
      React.createElement("label", { htmlFor: "note-body" }, "Body"),
      React.createElement("textarea", {
        id: "note-body",
        name: "note-body",
        value: body,
        placeholder: "Write your note...",
        onChange: function (e) {
          return setBody(e.target.value);
        },
        required: true,
        disabled: !isConnected || isCreating,
      }),
      React.createElement("label", { htmlFor: "note-tags" }, "Tags (comma separated)"),
      React.createElement("input", {
        id: "note-tags",
        name: "note-tags",
        type: "text",
        value: tags,
        placeholder: "work, idea, personal",
        onChange: function (e) {
          return setTags(e.target.value);
        },
        disabled: !isConnected || isCreating,
      }),
      React.createElement(
        "button",
        {
          type: "submit",
          disabled: !isConnected || isCreating || !title.trim() || !body.trim(),
        },
        isCreating ? "Creating..." : "Create Note"
      )
    ),
    message
      ? React.createElement("p", { className: "success-hint" }, message)
      : null,
    actionError
      ? React.createElement("p", { className: "error-hint" }, actionError)
      : null,
    connectionHint && !message && !actionError
      ? React.createElement("p", { className: "hint" }, connectionHint)
      : null
  );
}
