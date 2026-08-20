import { ChangeEvent, DragEvent, useEffect, useMemo, useRef, useState } from "react";
import DiagramView from "./components/DiagramView";
import { Architecture, EditorCommand, ExplainResponse, NodeType } from "./types";
import SecurityPanel from "./components/SecurityPanel";
import ArchitectureDetails from "./components/ArchitectureDetails";

const API_URL = (import.meta.env.VITE_API_URL as string | undefined)?.replace(/\/$/, "") || "http://127.0.0.1:8000";
const EXPLAIN_URL = `${API_URL}/explain`;
const STORAGE_RESPONSE = "architectai-last-response";
const STORAGE_INPUT = "architectai-last-input";

const EXAMPLE_PROMPT =
  "A frontend web application served by a CDN that calls a REST API, which writes to a PostgreSQL database and publishes jobs to a Kafka queue.";

type AppStatus = "empty" | "generating" | "success" | "error";

type ThemeMode = "light" | "dark";

const EMPTY_ARCHITECTURE: Architecture = {
  nodes: [],
  edges: [],
};

function isExplainResponse(value: unknown): value is ExplainResponse {
  if (!value || typeof value !== "object") return false;
  const candidate = value as { architecture?: unknown };
  const arch = candidate.architecture as { nodes?: unknown; edges?: unknown } | undefined;
  return (
    !!arch &&
    Array.isArray(arch.nodes) &&
    Array.isArray(arch.edges) &&
    arch.nodes.length > 0 &&
    arch.edges.length > 0
  );
}

function App() {
  const [input, setInput] = useState(() => localStorage.getItem(STORAGE_INPUT) ?? "");
  const [response, setResponse] = useState<ExplainResponse | null>(() => {
    const raw = localStorage.getItem(STORAGE_RESPONSE);
    if (!raw) return null;
    try {
      const parsed = JSON.parse(raw) as unknown;
      return isExplainResponse(parsed) ? parsed : null;
    } catch {
      // Ignore malformed saved state.
      return null;
    }
  });
  const [status, setStatus] = useState<AppStatus>("empty");
  const [error, setError] = useState("");
  const [editorCommand, setEditorCommand] = useState<EditorCommand | null>(null);
  const [theme, setTheme] = useState<ThemeMode>(() => {
    const stored = localStorage.getItem("architectai-theme");
    return stored === "light" ? "light" : "dark";
  });
  const commandIdRef = useRef(0);
  const abortRef = useRef<AbortController | null>(null);
  const generatingRef = useRef(false);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    document.documentElement.classList.toggle("dark", theme === "dark");
    localStorage.setItem("architectai-theme", theme);
  }, [theme]);

  useEffect(() => {
    localStorage.setItem(STORAGE_INPUT, input);
  }, [input]);

  const architecture = useMemo(() => response?.architecture ?? null, [response]);

  const sendEditorCommand = (action: EditorCommand["action"]) => {
    commandIdRef.current += 1;
    setEditorCommand({ id: commandIdRef.current, action });
    if (action === "clear") {
      setResponse(null);
      localStorage.removeItem(STORAGE_RESPONSE);
    }
  };

  const onDragNodeTemplate = (event: DragEvent<HTMLButtonElement>, nodeType: NodeType) => {
    event.dataTransfer.setData("application/x-arch-node", nodeType);
    event.dataTransfer.effectAllowed = "move";
  };

  const stopGeneration = () => {
    abortRef.current?.abort();
    abortRef.current = null;
    generatingRef.current = false;
    setStatus("empty");
  };

  const onGenerate = async () => {
    if (generatingRef.current) return;

    setError("");
    const text = input.trim();
    if (!text) {
      setStatus("error");
      setError("Enter a description of the architecture you want generated.");
      return;
    }

    generatingRef.current = true;
    const controller = new AbortController();
    abortRef.current = controller;
    setStatus("generating");
    setResponse(null);
    sendEditorCommand("clear");

    try {
      let response: Response;
      try {
        response = await fetch(EXPLAIN_URL, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text }),
          signal: controller.signal,
        });
      } catch (err) {
        if ((err as Error).name === "AbortError") {
          return;
        }
        setStatus("error");
        setError("Backend unreachable. Start the backend (uvicorn backend.api.main:app) on 127.0.0.1:8000, then try again.");
        return;
      }

      if (!response.ok) {
        let backendMessage = `Request failed with status ${response.status}.`;
        try {
          const errorJson = (await response.json()) as { detail?: string };
          if (errorJson.detail) backendMessage = String(errorJson.detail);
        } catch {
          // Keep the status-based message when the body is not JSON.
        }
        if (response.status === 422) {
          backendMessage = `Generation failed: ${backendMessage}`;
        } else if (response.status === 400) {
          backendMessage = `Invalid request: ${backendMessage}`;
        } else if (response.status === 500) {
          backendMessage = `Inference failed: ${backendMessage}`;
        }
        setStatus("error");
        setError(backendMessage);
        return;
      }

      const data = (await response.json()) as unknown;
      if (!isExplainResponse(data)) {
        setStatus("error");
        setError("Backend returned an invalid response — expected an architecture with nodes and edges.");
        return;
      }

      setResponse(data);
      localStorage.setItem(STORAGE_RESPONSE, JSON.stringify(data));
      setStatus("success");
      sendEditorCommand("reset");
    } catch (err) {
      if ((err as Error).name === "AbortError") return;
      setStatus("error");
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      if (controller.signal.aborted === false) {
        abortRef.current = null;
      }
      generatingRef.current = false;
    }
  };

  const loadExample = () => {
    setInput(EXAMPLE_PROMPT);
  };

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand">
          <span className="brand-mark" aria-hidden="true" />
          <div className="brand-text">
            <h1>ArchitectAI</h1>
            <span className="brand-sub">CyberShield-Arch · Gemma 3 4B LoRA</span>
          </div>
        </div>
        <div className="header-meta">
          {response?.metadata?.provider ? <span className="provider-badge">{response.metadata.provider} / {response.metadata.source}</span> : null}
          <button
            type="button"
            className="theme-toggle"
            onClick={() => setTheme((current) => (current === "light" ? "dark" : "light"))}
            title="Toggle theme"
          >
            {theme === "dark" ? "Light" : "Dark"}
          </button>
        </div>
      </header>

      <div className="app-body">
        <aside className="control-panel">
          <section className="prompt-card">
            <label className="control-label" htmlFor="architecture-input">Architecture Request</label>
            <textarea
              id="architecture-input"
              value={input}
              onChange={(e: ChangeEvent<HTMLTextAreaElement>) => setInput(e.target.value)}
              rows={7}
              placeholder="Describe the system: components, data flow, and security requirements."
            />
            <div className="example-row">
              <span className="muted">No idea? </span>
              <button type="button" className="link-btn" onClick={loadExample}>Load an example prompt</button>
            </div>
            <div className="prompt-actions">
              {status === "generating" ? (
                <button type="button" className="btn stop" onClick={stopGeneration} disabled={!generatingRef.current}>
                  Stop
                </button>
              ) : (
                <button type="button" className="btn primary" onClick={onGenerate} disabled={generatingRef.current}>
                  Generate Architecture
                </button>
              )}
            </div>
          </section>

          <section className={`status-card status-${status}`} aria-live="polite">
            {status === "empty" && <p className="status-text">Ready. Describe a system and generate its architecture.</p>}
            {status === "generating" && (
              <div className="generating-state">
                <span className="spinner" aria-hidden="true" />
                <p className="status-text">Generating architecture with the local Gemma model…</p>
              </div>
            )}
            {status === "success" && (
              <p className="status-text success">
                Generated {architecture?.nodes.length ?? 0} components / {architecture?.edges.length ?? 0} connections.
              </p>
            )}
            {status === "error" && <p className="status-text error">{error}</p>}
          </section>

          {response ? (
            <>
              <SecurityPanel security={response.security} />
              <ArchitectureDetails
                architecture={response.architecture}
                validation={response.validation}
                metadata={response.metadata}
              />
            </>
          ) : null}

          {!response ? (
            <section className="tool-section">
              <h2>Node Tools</h2>
              <p className="muted">Drag an item onto the canvas to add a component.</p>
              <div className="tool-grid">
                <button type="button" draggable className="tool-btn draggable" onDragStart={(event) => onDragNodeTemplate(event, "ui")}>UI</button>
                <button type="button" draggable className="tool-btn draggable" onDragStart={(event) => onDragNodeTemplate(event, "service")}>Service</button>
                <button type="button" draggable className="tool-btn draggable" onDragStart={(event) => onDragNodeTemplate(event, "database")}>Database</button>
                <button type="button" draggable className="tool-btn draggable" onDragStart={(event) => onDragNodeTemplate(event, "cache")}>Cache</button>
                <button type="button" draggable className="tool-btn draggable" onDragStart={(event) => onDragNodeTemplate(event, "queue")}>Queue</button>
                <button type="button" draggable className="tool-btn draggable" onDragStart={(event) => onDragNodeTemplate(event, "container")}>Container</button>
              </div>
              <div className="tool-row">
                <button type="button" className="tool-btn" onClick={() => sendEditorCommand("reset")}>Reset Layout</button>
                <button type="button" className="tool-btn danger" onClick={() => sendEditorCommand("clear")}>Clear</button>
              </div>
            </section>
          ) : null}
        </aside>

        <section className="editor-canvas-panel">
          <DiagramView
            architecture={architecture ?? EMPTY_ARCHITECTURE}
            command={editorCommand}
            theme={theme}
            onToggleTheme={() => setTheme((current) => (current === "light" ? "dark" : "light"))}
            security={response?.security ?? null}
          />
        </section>
      </div>
    </div>
  );
}

export default App;