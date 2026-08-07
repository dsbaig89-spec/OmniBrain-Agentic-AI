import { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  // Upload PDF / Image / CSV
  const uploadFile = async () => {
    if (!file) {
      alert("Select a file first");
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
      alert("Only PDF, Image or CSV files are supported.");
      return;
    }

    setLoading(true);

    try {
      const res = await axios.post(endpoint, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      console.log(res.data);
      alert("File uploaded successfully.");
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
      const res = await axios.post(
        "http://127.0.0.1:8000/search",
        {
          query: query,
        }
      );

      setAnswer(res.data.answer);
    } catch (err) {
      console.error(err);
      alert("Search failed.");
    }

    setLoading(false);
  };

  return (
    <div className="container">
      <h1>🧠 OmniBrain Agentic AI</h1>
       <p className="subtitle">
        Enterprise Multimodal AI Assistant
       </p>
      <input
        type="file"
        accept=".pdf,.csv,.png,.jpg,.jpeg,image/*"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <button onClick={uploadFile}>
        Upload File
      </button>

      <br /><br />

      <textarea
        rows="3"
        placeholder="Ask a question..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />

      <br />

      <button onClick={askQuestion}>
        Ask AI
      </button>

      {loading && <h3>Processing...</h3>}

      <div className="answer">
        {answer}
      </div>
    </div>
  );
}

export default App;