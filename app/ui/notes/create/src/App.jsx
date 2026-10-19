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

export default function CreateNoteApp() {
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [tags, setTags] = useState("");
  const [createdNote, setCreatedNote] = useState(null);
  const [isCreating, setIsCreating] = useState(false);
  const [status, setStatus] = useState("idle");
  const [actionError, setActionError] = useState(null);
  const [validationError, setValidationError] = useState("");

  const onAppCreated = useCallback(function (createdApp) {
    createdApp.ontoolresult = function (result) {
      var sc = result.structuredContent;
      if (sc && sc.note) {
        setCreatedNote(sc.note);
        setStatus("success");
      }
    };
  }, []);

  var appInfo = {
    name: "tinytim-notes-create-ui",
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
      setStatus("idle");
    }
  }, [app, isConnected]);

  function validateForm() {
    var trimmedTitle = title.trim();
    var trimmedBody = body.trim();
    if (!trimmedTitle) {
      setValidationError("Title is required.");
      return false;
    }
    if (!trimmedBody) {
      setValidationError("Body is required.");
      return false;
    }
    setValidationError("");
    return true;
  }

  function handleCreate(e) {
    e.preventDefault();
    if (!app || isCreating) return;

    if (!validateForm()) return;

    setIsCreating(true);
    setActionError(null);
    setCreatedNote(null);
    setStatus("submitting");

    var trimmedTitle = title.trim();
    var trimmedBody = body.trim();
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

  function handleReset() {
    setCreatedNote(null);
    setTitle("");
    setBody("");
    setTags("");
    setStatus("idle");
    setActionError(null);
  }

  var connectionHint = "";
  if (error) {
    connectionHint = "Unable to connect to MCP client: " + error.message;
  } else if (!isConnected) {
    connectionHint = "Connecting to the MCP client...";
  }

  var renderedTags = [];
  if (createdNote && Array.isArray(createdNote.tags)) {
    renderedTags = escapeHtmlList(createdNote.tags);
  }

  return React.createElement(
    "main",
    { className: "card", "aria-live": "polite", "data-host-theme": theme },
    React.createElement("p", { className: "eyebrow" }, "Create Note"),
    createdNote
      ? React.createElement(
          "div",
          { className: "created-note" },
          React.createElement("h3", { className: "detail-title" }, escapeHtml(createdNote.title)),
          React.createElement(
            "p",
            { className: "detail-body" },
            escapeHtml(createdNote.body)
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
            escapeHtml(createdNote.id),
            "  |  Status: ",
            escapeHtml(createdNote.status),
            "  |  Created: ",
            new Date(createdNote.created_at).toLocaleString()
          ),
          React.createElement(
            "p",
            { className: "success-hint" },
            "Note created successfully."
          ),
          React.createElement(
            "button",
            { className: "create-btn", onClick: handleReset },
            "Create Another"
          )
        )
      : React.createElement(
          "form",
          { className: "create-form", onSubmit: handleCreate },
          React.createElement("h3", null, "New Note"),
          React.createElement("label", { htmlFor: "note-title" }, "Title *"),
          React.createElement("input", {
            id: "note-title",
            name: "note-title",
            type: "text",
            value: title,
            placeholder: "Note title",
            autoComplete: "off",
            onChange: function (e) {
              setTitle(e.target.value);
              if (validationError) setValidationError("");
            },
            required: true,
            disabled: !isConnected || isCreating,
          }),
          validationError && !createdNote
            ? React.createElement("p", { className: "error-hint" }, validationError)
            : null,
          React.createElement("label", { htmlFor: "note-body" }, "Body *"),
          React.createElement("textarea", {
            id: "note-body",
            name: "note-body",
            value: body,
            placeholder: "Write your note...",
            onChange: function (e) {
              setBody(e.target.value);
              if (validationError) setValidationError("");
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
              setTags(e.target.value);
            },
            disabled: !isConnected || isCreating,
          }),
          React.createElement(
            "button",
            {
              type: "submit",
              className: "create-btn",
              disabled: !isConnected || isCreating || !title.trim() || !body.trim(),
            },
            isCreating
              ? "Creating..."
              : status === "submitting"
              ? "Submitting..."
              : "Create Note"
          ),
          actionError
            ? React.createElement("p", { className: "error-hint" }, actionError)
            : null,
          status === "submitting" && !actionError
            ? React.createElement("p", { className: "hint" }, "Submitting your note...")
            : null,
          connectionHint && !actionError
            ? React.createElement("p", { className: "hint" }, connectionHint)
            : null
        )
  );
}
