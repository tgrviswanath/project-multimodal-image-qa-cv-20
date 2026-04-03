import React, { useState, useRef } from "react";
import {
  Box, CircularProgress, Alert, Typography, Paper,
  TextField, Button, Chip, Divider, List, ListItem, ListItemText,
} from "@mui/material";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import SendIcon from "@mui/icons-material/Send";
import { askQuestion } from "../services/qaApi";

export default function QAPage() {
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [question, setQuestion] = useState("");
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const fileRef = useRef();

  const handleFile = (file) => {
    if (!file) return;
    setImageFile(file);
    setImagePreview(URL.createObjectURL(file));
    setHistory([]);
    setError("");
  };

  const handleAsk = async () => {
    if (!imageFile || !question.trim()) return;
    setLoading(true);
    setError("");
    try {
      const fd = new FormData();
      fd.append("file", imageFile);
      fd.append("question", question.trim());
      const r = await askQuestion(fd);
      setHistory((prev) => [r.data, ...prev]);
      setQuestion("");
    } catch (e) {
      setError(e.response?.data?.detail || "Request failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      {/* Image upload */}
      <Paper
        variant="outlined"
        onClick={() => fileRef.current.click()}
        onDrop={(e) => { e.preventDefault(); handleFile(e.dataTransfer.files[0]); }}
        onDragOver={(e) => e.preventDefault()}
        sx={{
          p: 2, mb: 2, textAlign: "center", cursor: "pointer", borderStyle: "dashed",
          "&:hover": { bgcolor: "action.hover" },
        }}
      >
        <input ref={fileRef} type="file" hidden accept=".jpg,.jpeg,.png,.bmp,.webp"
          onChange={(e) => handleFile(e.target.files[0])} />
        {imagePreview
          ? <img src={imagePreview} alt="uploaded" style={{ maxHeight: 280, maxWidth: "100%", borderRadius: 4 }} />
          : <Box sx={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 1 }}>
              <UploadFileIcon color="action" />
              <Typography color="text.secondary">Drag & drop or click to upload image</Typography>
            </Box>
        }
      </Paper>

      {/* Question input */}
      <Box sx={{ display: "flex", gap: 1, mb: 2 }}>
        <TextField
          fullWidth
          size="small"
          placeholder="Ask a question about the image…"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleAsk()}
          disabled={!imageFile || loading}
        />
        <Button
          variant="contained"
          endIcon={loading ? <CircularProgress size={16} color="inherit" /> : <SendIcon />}
          onClick={handleAsk}
          disabled={!imageFile || !question.trim() || loading}
        >
          Ask
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {/* Answer history */}
      {history.length > 0 && (
        <>
          <Divider sx={{ mb: 2 }} />
          <Typography variant="subtitle2" gutterBottom>Answers</Typography>
          <List disablePadding>
            {history.map((item, i) => (
              <Paper key={i} variant="outlined" sx={{ mb: 1, p: 1.5 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Q: {item.question}
                </Typography>
                <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                  <Typography variant="body1" fontWeight="bold">
                    A: {item.answer}
                  </Typography>
                  {item.confidence != null && (
                    <Chip label={`${item.confidence}%`} size="small" color="primary" variant="outlined" />
                  )}
                </Box>
              </Paper>
            ))}
          </List>
        </>
      )}
    </Box>
  );
}
