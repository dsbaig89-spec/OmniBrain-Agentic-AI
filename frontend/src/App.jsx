import { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activePage, setActivePage] = useState("upload");

  // ==========================================
  // Upload File
  // ==========================================

  const uploadFile = async () => {
    if (!file) {
      alert("Select a file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    let endpoint = "";

    if (file.type === "application/pdf") {
      endpoint = "http://127.0.0.1:8000/upload";
    } else if (file.type.startsWith("image/")) {
      endpoint = "http://127.0.0.1:8000/upload-image";
    } else if (file.name.toLowerCase().endsWith(".csv")) {
      endpoint = "http://127.0.0.1:8000/upload-csv";
    } else {
      alert("Only PDF, Image and CSV files are supported.");
      return;
    }

    setLoading(true);

    try {
      await axios.post(endpoint, formData);

      alert("✅ File uploaded successfully.");
    } catch (err) {
      console.error("Upload error:", err);

      const message =
        err.response?.data?.detail ||
        "Upload failed.";

      alert(message);
    } finally {
      setLoading(false);
    }
  };

  // ==========================================
  // Ask AI
  // ==========================================

  const askQuestion = async () => {
    const currentQuery = query.trim();

    if (!currentQuery) {
      alert("Enter a question.");
      return;
    }

    setLoading(true);

    try {
      const res = await axios.post(
        "http://127.0.0.1:8000/search",
        {
          query: currentQuery,
        }
      );

      console.log("Search response:", res.data);

      // Safely normalize sources
      const rawSources = Array.isArray(res.data?.sources)
        ? res.data.sources
        : [];

      const safeSources = rawSources.map((source) => {
        if (typeof source === "string") {
          return {
            text: source,
          };
        }

        return {
          text: source?.text || "",
          page: source?.page || null,
          filename: source?.filename || null,
        };
      });

      setMessages((prev) => [
        ...prev,
        {
          question: currentQuery,
          answer: res.data?.answer || "No answer received.",
          sources: safeSources,
        },
      ]);

      setQuery("");
    } catch (err) {
      console.error("Search error:", err);

      const errorMessage =
        err.response?.data?.detail ||
        "Search failed. Please make sure the backend is running.";

      alert(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // ==========================================
  // UI
  // ==========================================

  return (
    <div className="app-layout">

      {/* ======================================
          Sidebar
      ====================================== */}

      <div className="sidebar">

        <h2>🧠 OmniBrain</h2>

        <ul>
          <li
            className={activePage === "upload" ? "active" : ""}
            onClick={() => setActivePage("upload")}
          >
            📤 Upload
          </li>

          <li
            className={activePage === "chat" ? "active" : ""}
            onClick={() => setActivePage("chat")}
          >
            💬 AI Chat
          </li>
        </ul>

      </div>

      {/* ======================================
          Main Content
      ====================================== */}

      <div className="container">

        <h1>🧠 OmniBrain Agentic AI</h1>

        <p className="subtitle">
          Enterprise Multimodal AI Assistant
        </p>

        {/* ======================================
            Features
        ====================================== */}

        <div className="features">

          <div className="feature-card">
            📄 PDF
          </div>

          <div className="feature-card">
            🖼 Image
          </div>

          <div className="feature-card">
            📊 CSV
          </div>

          <div className="feature-card">
            🤖 AI Search
          </div>

        </div>

        {/* ======================================
            Upload Card
        ====================================== */}

        <div className="card">

          <h2>📤 Upload Document</h2>

          <input
            type="file"
            accept=".pdf,.csv,.png,.jpg,.jpeg,image/*"
            onChange={(e) => {
              const selectedFile = e.target.files?.[0] || null;
              setFile(selectedFile);
            }}
          />

          <br />
          <br />

          <button
            onClick={uploadFile}
            disabled={loading}
          >
            {loading ? "Uploading..." : "Upload File"}
          </button>

        </div>

        {/* ======================================
            Ask AI
        ====================================== */}

        <div className="card">

          <h2>💬 Ask OmniBrain</h2>

          <textarea
            rows="4"
            placeholder="Ask a question about the uploaded document..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />

          <br />

          <button
            onClick={askQuestion}
            disabled={loading}
          >
            {loading ? "Thinking..." : "Ask AI"}
          </button>

          {loading && (
            <div className="loading">
              🤖 OmniBrain is thinking...
            </div>
          )}

        </div>

        {/* ======================================
            Conversation
        ====================================== */}

        <div className="card">

          <h2>🤖 Conversation</h2>

          <div className="chat-window">

            {messages.length === 0 ? (

              <div className="welcome">

                <h3>
                  Welcome to OmniBrain 🚀
                </h3>

                <p>
                  Upload a PDF, Image or CSV and start chatting.
                </p>

                <br />

                <strong>
                  Try asking:
                </strong>

                <ul>
                  <li>
                    Summarize the uploaded file.
                  </li>

                  <li>
                    What are the key points?
                  </li>

                  <li>
                    Explain this image.
                  </li>

                  <li>
                    Analyze the CSV.
                  </li>
                </ul>

              </div>

            ) : (

              messages.map((msg, index) => (

                <div key={index}>

                  {/* User Message */}

                  <div className="user-message">

                    <strong>
                      👤 You
                    </strong>

                    <p>
                      {msg.question}
                    </p>

                  </div>

                  {/* AI Message */}

                  <div className="bot-message">

                    <strong>
                      🤖 OmniBrain
                    </strong>

                    <p>
                      {msg.answer}
                    </p>

                    {/* ==================================
                        Sources
                    ================================== */}

                    {Array.isArray(msg.sources) &&
                      msg.sources.length > 0 && (

                        <div className="sources">

                          <h4>
                            📚 Sources
                          </h4>

                          {msg.sources.map(
                            (source, sourceIndex) => (

                              <div
                                className="source-item"
                                key={sourceIndex}
                              >

                                <strong>
                                  Source {sourceIndex + 1}
                                </strong>

                                <p>
                                  {source?.text || ""}
                                </p>

                                {source?.page && (
                                  <small>
                                    📄 Page {source.page}
                                  </small>
                                )}

                                {source?.filename && (
                                  <small>
                                    <br />
                                    📁 {source.filename}
                                  </small>
                                )}

                              </div>

                            )
                          )}

                        </div>

                      )}

                  </div>

                </div>

              ))

            )}

          </div>

        </div>

      </div>

    </div>
  );
}

export default App;