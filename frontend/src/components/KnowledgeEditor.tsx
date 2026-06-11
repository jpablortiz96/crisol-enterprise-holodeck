"use client";

import { useState } from "react";
import { FileText, Save } from "lucide-react";
import { useWarRoomStore } from "@/store/warRoomStore";

export function KnowledgeEditor() {
  const {
    workspaceKnowledge,
    isWorkspaceSaving,
    saveKnowledge,
  } = useWarRoomStore();
  const [fileName, setFileName] = useState("operations-guide.md");
  const [content, setContent] = useState("# Operations Guide\n\nAdd sanitized training guidance here.");
  const [message, setMessage] = useState<string | null>(null);

  async function submit() {
    setMessage(null);
    try {
      await saveKnowledge(fileName, content);
      setMessage("Knowledge document saved.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Knowledge document could not be saved.");
    }
  }

  return (
    <section className="war-panel workspace-editor-panel">
      <div className="panel-header">
        <div>
          <p className="panel-kicker">Knowledge Studio</p>
          <h2 className="panel-title">Knowledge Editor</h2>
        </div>
        <FileText className="h-5 w-5 text-cyan-300" />
      </div>
      <div className="workspace-editor-body">
        <label className="technical-field">
          File name
          <input value={fileName} onChange={(event) => setFileName(event.target.value)} />
        </label>
        <label className="technical-field">
          Markdown
          <textarea
            className="workspace-textarea workspace-textarea-medium"
            value={content}
            onChange={(event) => setContent(event.target.value)}
          />
        </label>
        <button
          type="button"
          className="control-button control-primary workspace-save"
          disabled={isWorkspaceSaving}
          onClick={() => void submit()}
        >
          <Save className="h-4 w-4" />
          Save Knowledge
        </button>
        {message && <p className="workspace-form-message">{message}</p>}
        <div className="workspace-record-list">
          {workspaceKnowledge.map((document) => (
            <button
              type="button"
              key={document.file_name}
              onClick={() => {
                setFileName(document.file_name);
                setContent(document.content ?? "");
              }}
            >
              <strong>{document.title}</strong>
              <span>{document.file_name}</span>
            </button>
          ))}
          {!workspaceKnowledge.length && <p>No workspace knowledge documents yet.</p>}
        </div>
      </div>
    </section>
  );
}
