import { useState } from "react";

function App() {
  const [prompt, setPrompt] = useState("");
  const [youtubeUrl, setYoutubeUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [gifs, setGifs] = useState([]);
  const [contentAnalysis, setContentAnalysis] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Prepare a FormData object to send with the POST request.
      const formData = new FormData();
      formData.append("prompt", prompt);
      formData.append("youtube_url", youtubeUrl);

      // Adjust the URL below to point to your backend API.
      const response = await fetch("http://localhost:5001/api/gif/generate", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      setGifs(data.gifs || []);
      setContentAnalysis(data.content_analysis || "");
    } catch (error) {
      console.error("Error generating GIFs!", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-3xl mx-auto bg-white rounded-lg shadow p-6">
        <h1 className="text-3xl font-bold mb-4 text-center">
          AI GIF Generator
        </h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-gray-700">Prompt:</label>
            <input
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              className="w-full border border-gray-300 rounded-md p-2 text-gray-900 placeholder-gray-500 focus:outline-none focus:ring focus:ring-blue-200"
              placeholder="Enter your prompt (e.g. funny moments)"
            />
          </div>
          <div>
            <label className="block text-gray-700">YouTube URL:</label>
            <input
              type="text"
              value={youtubeUrl}
              onChange={(e) => setYoutubeUrl(e.target.value)}
              className="w-full border border-gray-300 rounded-md p-2 text-gray-900 placeholder-gray-500 focus:outline-none focus:ring focus:ring-blue-200"
              placeholder="Enter YouTube URL"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-500 text-white p-2 rounded-md hover:bg-blue-600 transition"
          >
            {loading ? "Generating..." : "Generate GIFs"}
          </button>
        </form>

        {contentAnalysis && (
          <div className="mt-6">
            <h2 className="text-2xl font-semibold mb-2">Content Analysis</h2>
            <p className="text-gray-800">{contentAnalysis}</p>
          </div>
        )}

        {gifs.length > 0 && (
          <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 gap-4">
            {gifs.map((gif, idx) => (
              <div
                key={idx}
                className="border rounded-lg overflow-hidden shadow"
              >
                <img src={gif.url} alt={gif.caption} className="w-full" />
                <div className="p-2">
                  <p className="text-gray-700 font-medium">{gif.caption}</p>
                  <p className="text-xs text-gray-500">
                    Time: {gif.start} - {gif.end}s
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
