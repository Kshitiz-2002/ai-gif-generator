import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { Label } from "@/components/ui/Label";
import { Loader2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function App() {
  const [prompt, setPrompt] = useState("");
  const [youtubeUrl, setYoutubeUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [gifs, setGifs] = useState([]);
  const [contentAnalysis, setContentAnalysis] = useState("");
  const [requestId, setRequestId] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("prompt", prompt);
      formData.append("youtube_url", youtubeUrl);

      const response = await fetch("/api/gif/generate", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      setGifs(data.gifs || []);
      setContentAnalysis(data.content_analysis || "");
      setRequestId(data.request_id || "");
    } catch (error) {
      console.error("Error generating GIFs!", error);
    }

    setLoading(false);
  };

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-gradient-to-br from-gray-100 to-gray-50">
      <Card className="flex flex-col flex-1 w-full h-full bg-white p-8 shadow-none rounded-none">
        {/* Header */}
        <CardHeader className="text-center mb-6">
          <CardTitle className="text-3xl font-bold text-black">
            AI GIF Generator
          </CardTitle>
        </CardHeader>

        {/* Form */}
        <form onSubmit={handleSubmit} className="flex flex-col space-y-5 mb-8">
          <div className="flex flex-col md:flex-row md:space-x-4 space-y-4 md:space-y-0">
            <div className="flex-1">
              <Label htmlFor="prompt" className="text-black">
                Prompt
              </Label>
              <Input
                id="prompt"
                placeholder="e.g. funny moments"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                className="text-black"
              />
            </div>
            <div className="flex-1">
              <Label htmlFor="youtubeUrl" className="text-black">
                YouTube URL
              </Label>
              <Input
                id="youtubeUrl"
                placeholder="https://www.youtube.com/..."
                value={youtubeUrl}
                onChange={(e) => setYoutubeUrl(e.target.value)}
                className="text-black"
              />
            </div>
          </div>

          <Button
            type="submit"
            className="w-full py-3 bg-gray-900 hover:bg-black"
            disabled={loading}
          >
            {loading && (
              <Loader2 className="animate-spin h-5 w-5 mr-2 text-white" />
            )}
            <span className="text-white">
              {loading ? "Generating..." : "Generate GIFs"}
            </span>
          </Button>
        </form>

        {/* Content Analysis */}
        {contentAnalysis && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="mb-8"
          >
            <h2 className="text-2xl font-semibold text-black mb-2">
              Content Analysis
            </h2>
            <p className="text-black leading-relaxed">{contentAnalysis}</p>
          </motion.div>
        )}

        {/* GIF Grid */}
        <AnimatePresence>
          {gifs.length > 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.5 }}
              className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6"
            >
              {requestId && (
                <div className="col-span-full">
                  <p className="text-sm text-gray-600">
                    Request ID:{" "}
                    <span className="font-mono text-black">{requestId}</span>
                  </p>
                </div>
              )}

              {gifs.map((gif) => (
                <motion.div
                  key={gif.id}
                  whileHover={{ scale: 1.02 }}
                  className="bg-white rounded-xl shadow-md overflow-hidden"
                >
                  <img
                    src={gif.url}
                    alt={gif.caption}
                    className="w-full object-cover h-56"
                  />
                  <CardContent className="p-4">
                    <p className="font-medium text-black mb-1">
                      {gif.caption}
                    </p>
                    <p className="text-xs text-gray-600">
                      Time: {gif.start}s – {gif.end}s
                      <br />
                      Duration: {gif.duration.toFixed(2)}s
                    </p>
                  </CardContent>
                </motion.div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </Card>
    </div>
  );
}
