import { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activePage, setActivePage] = useState("upload");

  // Upload File
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
      await axios.post(endpoint, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      alert("✅ File uploaded successfully.");
    } catch (err) {
      console.error(err);
      alert("Upload failed.");
    }

    setLoading(false);
  };

  // Ask AI
  const askQuestion = async () => {
    if (!query.trim()) {
      alert("Enter a question.");
      return;
    }

    setLoading(true);

    try {
      const res = await axios.post("http://127.0.0.1:8000/search", {
        query,
      });

      setMessages((prev) => [
  ...prev,
  {
    question: query,
    answer: res.data.answer,
    sources: res.data.sources || [],
  },
]);

      setQuery("");
    } catch (err) {
      console.error(err);
      alert("Search failed.");
    }

    setLoading(false);
  };

  return (
    <div className="app-layout">
      {/* Sidebar */}
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

      {/* Main Content */}
      <div className="container">
        <h1>🧠 OmniBrain Agentic AI</h1>

        <p className="subtitle">
          Enterprise Multimodal AI Assistant
        </p>

        {/* Features */}
        <div className="features">
          <div className="feature-card">📄 PDF</div>
          <div className="feature-card">🖼 Image</div>
          <div className="feature-card">📊 CSV</div>
          <div className="feature-card">🤖 AI Search</div>
        </div>

        {/* Upload Card */}
        <div className="card">
          <h2>📤 Upload Document</h2>

          <input
            type="file"
            accept=".pdf,.csv,.png,.jpg,.jpeg,image/*"
            onChange={(e) => setFile(e.target.files[0])}
          />

          <br />
          <br />

          <button onClick={uploadFile}>
            Upload File
          </button>
        </div>

        {/* Ask AI */}
        <div className="card">
          <h2>💬 Ask OmniBrain</h2>

          <textarea
            rows="4"
            placeholder="Ask a question about the uploaded document..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />

          <br />

          <button onClick={askQuestion}>
            Ask AI
          </button>

          {loading && (
            <div className="loading">
              🤖 OmniBrain is thinking...
            </div>
          )}
        </div>

        {/* Conversation */}
        <div className="card">
          <h2>🤖 Conversation</h2>

          <div className="chat-window">
            {messages.length === 0 ? (
              <div className="welcome">
                <h3>Welcome to OmniBrain 🚀</h3>

                <p>
                  Upload a PDF, Image or CSV and start chatting.
                </p>

                <br />

                <strong>Try asking:</strong>

                <ul>
                  <li>Summarize the uploaded file.</li>
                  <li>What are the key points?</li>
                  <li>Explain this image.</li>
                  <li>Analyze the CSV.</li>
                </ul>
              </div>
            ) : (
              messages.map((msg, index) => (
                <div key={index}>
                  <div className="user-message">
                    <strong>👤 You</strong>
                    <p>{msg.question}</p>
                  </div>

                  <div className="bot-message">
                    <strong>🤖 OmniBrain</strong>
                    <p>{msg.answer}</p>
                    {msg.sources && msg.sources.length > 0 && (
  <div className="sources">
    <h4>📚 Sources</h4>

    {msg.sources.map((source, index) => (
      <div className="source-item" key={index}>
        <strong>Source {index + 1}</strong>
        <p>{source.text}</p>
      </div>
    ))}
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