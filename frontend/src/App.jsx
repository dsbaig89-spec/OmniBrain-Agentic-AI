import { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  const uploadFile = async () => {
    if (!file) {
      alert("Select a file first");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    // Decide endpoint based on file type
    let endpoint = "";

    if (file.type === "application/pdf") {
      endpoint = "http://127.0.0.1:8000/upload";
    } else if (file.type.startsWith("image/")) {
      endpoint = "http://127.0.0.1:8000/upload-image";
    } else {
      alert("Only PDF or Image files are allowed.");
      return;
    }

    setLoading(true);

    try {
      await axios.post(endpoint, formData);

      alert("Uploaded Successfully");
    } catch (err) {
      console.error(err);
      alert("Upload Failed");
    }

    setLoading(false);
  };

  const askQuestion = async () => {
    if (!query) return;

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
      alert("Search Failed");
    }

    setLoading(false);
  };

  return (
    <div className="container">

      <h1>🧠 OmniBrain Agentic AI</h1>

      <input
        type="file"
        accept=".pdf,image/*"
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

      {loading && <h3>Thinking...</h3>}

      <div className="answer">
        {answer}
      </div>

    </div>
  );
}

export default App;