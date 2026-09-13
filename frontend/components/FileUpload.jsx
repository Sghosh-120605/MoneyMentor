"use client";
import { useState, useRef } from "react";

export default function FileUpload({ onFileSelect, isLoading }) {
  const [dragOver, setDragOver] = useState(false);
  const [fileName, setFileName] = useState(null);
  const inputRef = useRef(null);

  const handleFile = (file) => {
    if (!file) return;
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      alert("Please upload a PDF file.");
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      alert("File too large. Max 10MB.");
      return;
    }
    setFileName(file.name);
    onFileSelect(file);
  };

  return (
    <div
      className={`upload-zone p-10 text-center ${dragOver ? "drag-over" : ""}`}
      onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
      onDragLeave={() => setDragOver(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragOver(false);
        handleFile(e.dataTransfer.files[0]);
      }}
      onClick={() => !isLoading && inputRef.current?.click()}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf"
        className="hidden"
        onChange={(e) => handleFile(e.target.files[0])}
        disabled={isLoading}
      />

      {isLoading ? (
        <div className="space-y-4">
          <div className="w-16 h-16 mx-auto rounded-full border-4 border-indigo-500/30 border-t-indigo-500 animate-spin" />
          <p className="text-indigo-300 font-medium">Analyzing your Form 16…</p>
          <p className="text-sm text-gray-500">Extracting salary, deductions & computing tax</p>
        </div>
      ) : fileName ? (
        <div className="space-y-3">
          <div className="w-16 h-16 mx-auto rounded-2xl bg-green-500/10 flex items-center justify-center text-3xl">
            ✅
          </div>
          <p className="text-green-400 font-semibold">{fileName}</p>
          <p className="text-sm text-gray-500">Click or drop to replace</p>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="w-20 h-20 mx-auto rounded-2xl bg-indigo-500/10 flex items-center justify-center text-4xl">
            📄
          </div>
          <div>
            <p className="text-white font-semibold text-lg">
              Drop your Form 16 here
            </p>
            <p className="text-gray-500 text-sm mt-1">
              or click to browse • PDF up to 10MB
            </p>
          </div>
          <div className="flex items-center justify-center gap-2 text-xs text-gray-600">
            <span className="flex items-center gap-1">🔒 Secure</span>
            <span>•</span>
            <span>Files are not stored</span>
          </div>
        </div>
      )}
    </div>
  );
}
