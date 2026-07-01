import { useState, useRef, useEffect, useCallback, type DragEvent, type ChangeEvent } from 'react';

interface ChatInputProps {
  onSubmit: (code: string, files: { filename: string; content: string }[], imageUrl?: string, instruction?: string) => void;
  onChatSubmit: (message: string) => void;
  disabled: boolean;
}

const ACCEPTED_EXTENSIONS = [
  '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.json',
  '.md', '.txt', '.sql', '.java', '.cpp', '.c', '.go', '.rs',
  '.rb', '.php', '.swift', '.kt', '.yaml', '.yml', '.toml',
  '.sh', '.bash', '.zsh', '.dockerfile', '.graphql', '.proto',
];

const ACCEPT_STRING = ACCEPTED_EXTENSIONS.join(',');
const MAX_FILE_SIZE = 50 * 1024; // 50 KB

interface SelectedFile {
  name: string;
  size: number;
  content: string;
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

const FILE_ICONS: Record<string, string> = {
  py: '🐍', js: '🟨', ts: '🔵', jsx: '⚛️', tsx: '⚛️',
  html: '🌐', css: '🎨', json: '📋', md: '📝', sql: '🗄️',
  java: '☕', cpp: '⚙️', c: '⚙️', go: '🔷', rs: '🦀',
  rb: '💎', php: '🐘', swift: '🐦', kt: '📱', yaml: '📄',
  yml: '📄', toml: '📄', sh: '💻', dockerfile: '🐳',
};

function fileIcon(filename: string): string {
  const ext = filename.split('.').pop()?.toLowerCase() || '';
  return FILE_ICONS[ext] || '📄';
}

export default function ChatInput({ onSubmit, onChatSubmit, disabled }: ChatInputProps) {
  const [files, setFiles] = useState<SelectedFile[]>([]);
  const [chatText, setChatText] = useState('');
  const [isDragOver, setIsDragOver] = useState(false);
  const [showImageInput, setShowImageInput] = useState(false);
  const [imageUrl, setImageUrl] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const imageInputRef = useRef<HTMLInputElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    const ta = textareaRef.current;
    if (ta) {
      ta.style.height = 'auto';
      ta.style.height = Math.min(ta.scrollHeight, 200) + 'px';
    }
  }, [chatText]);

  // Reset file input value after selection
  useEffect(() => {
    if (fileInputRef.current) fileInputRef.current.value = '';
  }, [files]);

  // ── File handling ─────────────────────────────────────────────

  const readFiles = useCallback((fileList: FileList) => {
    const pending: SelectedFile[] = [];
    let hasOversized = false;
    for (const f of Array.from(fileList)) {
      if (f.size > MAX_FILE_SIZE) { hasOversized = true; continue; }
      pending.push({ name: f.name, size: f.size, content: '' });
    }
    if (hasOversized) {
      alert(`Some files were skipped (max ${formatFileSize(MAX_FILE_SIZE)} each).`);
    }
    if (pending.length === 0) return;

    let loaded = 0;
    const results: SelectedFile[] = [];
    for (const pf of pending) {
      const found = Array.from(fileList).find((f) => f.name === pf.name);
      if (!found) continue;
      const reader = new FileReader();
      reader.onload = () => {
        results.push({ name: pf.name, size: pf.size, content: reader.result as string });
        loaded++;
        if (loaded === pending.length) setFiles((prev) => [...prev, ...results]);
      };
      reader.onerror = () => { loaded++; };
      reader.readAsText(found);
    }
  }, []);

  const handleFileSelect = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    const fl = e.target.files;
    if (!fl || fl.length === 0) return;
    readFiles(fl);
  }, [readFiles]);

  const handleRemoveFile = useCallback((idx: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== idx));
  }, []);

  // ── Drag & drop ──────────────────────────────────────────────

  const handleDragOver = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
    const fl = e.dataTransfer.files;
    if (!fl || fl.length === 0) return;
    readFiles(fl);
  }, [readFiles]);

  // ── Submit logic ──────────────────────────────────────────────

  const handleSend = useCallback(() => {
    if (disabled) return;

    // If files are attached → code review mode
    if (files.length > 0) {
      const payload = files.map((f) => ({
        filename: f.name,
        content: f.content,
      }));
      const instruction = chatText.trim() || undefined;
      onSubmit('', payload, imageUrl.trim() || undefined, instruction);
      setFiles([]);
      setChatText('');
      setImageUrl('');
      setShowImageInput(false);
      return;
    }

    // If text only → general chat mode
    if (chatText.trim()) {
      onChatSubmit(chatText.trim());
      setChatText('');
    }
  }, [files, chatText, imageUrl, disabled, onSubmit, onChatSubmit]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      handleSend();
    }
    // Shift+Enter for newline (default behavior), Enter alone sends
    if (e.key === 'Enter' && !e.shiftKey && !e.ctrlKey && !e.metaKey) {
      e.preventDefault();
      handleSend();
    }
  }, [handleSend]);

  const canSend = (files.length > 0 || chatText.trim().length > 0) && !disabled;

  // ── Render ──────────────────────────────────────────────────

  return (
    <div
      className="relative border-t-2 border-retro-border bg-retro-surface"
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {/* ── Drag overlay ── */}
      {isDragOver && (
        <div className="absolute inset-0 z-20 flex items-center justify-center bg-[#0d1117]/90 border-2 border-dashed border-retro-cyan">
          <div className="text-center">
            <svg className="w-10 h-10 mx-auto text-retro-cyan mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
            </svg>
            <p className="text-retro-cyan font-bold text-sm tracking-wider uppercase">Drop files here</p>
            <p className="text-gray-500 text-xs mt-1">.py .js .ts .html .css .json ...</p>
          </div>
        </div>
      )}

      {/* ── Hidden file input ── */}
      <input
        ref={fileInputRef}
        type="file"
        accept={ACCEPT_STRING}
        multiple
        className="hidden"
        onChange={handleFileSelect}
        aria-hidden="true"
      />

      {/* ── Image URL input (expandable) ── */}
      {showImageInput && (
        <div className="px-4 pt-3 pb-1 animate-fade-in">
          <div className="flex items-center gap-2">
            <span className="text-xs text-retro-cyan font-mono">🖼️</span>
            <input
              type="url"
              value={imageUrl}
              onChange={(e) => setImageUrl(e.target.value)}
              placeholder="Paste image URL for additional context..."
              className="flex-1 bg-[#0d1117] border border-retro-border px-3 py-1.5 text-xs text-gray-300 placeholder:text-gray-600 outline-none focus:border-retro-cyan transition-colors font-mono"
              disabled={disabled}
            />
            {imageUrl && (
              <button onClick={() => setImageUrl('')} className="text-gray-500 hover:text-retro-cyan text-xs" aria-label="Clear image">✕</button>
            )}
          </div>
          {imageUrl && (
            <div className="mt-1 max-h-20 overflow-hidden border border-retro-border">
              <img src={imageUrl} alt="Preview" className="w-full h-auto object-contain max-h-20" onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }} />
            </div>
          )}
        </div>
      )}

      {/* ── Main input bar ── */}
      <div className="flex items-end gap-1.5 px-3 py-2.5">
        {/* Attach files button */}
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={disabled}
          className="p-2 text-gray-500 hover:text-retro-cyan transition-colors disabled:opacity-30 flex-shrink-0"
          aria-label="Attach files"
          title="Attach files"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M18.375 12.739l-7.693 7.693a4.5 4.5 0 01-6.364-6.364l10.94-10.94A3 3 0 1119.5 7.372L8.552 18.32m.009-.01l-.01.01m5.699-9.941l-7.81 7.81a1.5 1.5 0 002.112 2.13" />
          </svg>
        </button>

        {/* Attach image button */}
        <button
          onClick={() => setShowImageInput(!showImageInput)}
          disabled={disabled}
          className={`p-2 transition-colors flex-shrink-0 ${showImageInput ? 'text-retro-cyan' : 'text-gray-500 hover:text-retro-cyan'} disabled:opacity-30`}
          aria-label="Attach image URL"
          title="Attach image URL"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909M3.75 21h16.5A2.25 2.25 0 0022.5 18.75V5.25A2.25 2.25 0 0020.25 3H3.75A2.25 2.25 0 001.5 5.25v13.5A2.25 2.25 0 003.75 21z" />
          </svg>
        </button>

        {/* ── File chips + textarea ── */}
        <div className="flex-1 min-w-0">
          {/* File chips (only when files attached) */}
          {files.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mb-1.5">
              {files.map((f, idx) => (
                <span
                  key={`${f.name}-${idx}`}
                  className="inline-flex items-center gap-1 px-2 py-0.5 bg-[#161b22] border border-retro-border rounded text-xs text-gray-300 font-mono"
                >
                  <span className="text-[11px]">{fileIcon(f.name)}</span>
                  <span className="max-w-[120px] truncate">{f.name}</span>
                  <span className="text-[10px] text-gray-500">({formatFileSize(f.size)})</span>
                  <button
                    onClick={() => handleRemoveFile(idx)}
                    className="ml-0.5 text-gray-500 hover:text-retro-red transition-colors"
                    aria-label={`Remove ${f.name}`}
                  >✕</button>
                </span>
              ))}
            </div>
          )}

          {/* Textarea */}
          <textarea
            ref={textareaRef}
            value={chatText}
            onChange={(e) => setChatText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              files.length > 0
                ? "Add instructions for the review... (or press Enter to send)"
                : "Ask the expert panel a question, paste code, or attach files..."
            }
            className="w-full bg-transparent text-sm text-gray-200 placeholder:text-gray-600 outline-none resize-none font-mono leading-relaxed"
            rows={1}
            disabled={disabled}
            aria-label="Message input"
          />
        </div>

        {/* Send button */}
        <button
          onClick={handleSend}
          disabled={!canSend}
          className={`p-2 rounded-lg transition-all duration-150 flex-shrink-0 ${
            canSend
              ? 'bg-retro-cyan text-black hover:bg-retro-cyan/90'
              : 'bg-gray-800 text-gray-600'
          } disabled:opacity-40 disabled:cursor-not-allowed`}
          aria-label="Send"
        >
          {disabled ? (
            <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
          ) : (
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
            </svg>
          )}
        </button>
      </div>

      {/* ── Footer hint ── */}
      {!disabled && files.length === 0 && !chatText.trim() && (
        <div className="pb-2 px-4">
          <p className="text-[10px] text-gray-700 text-center flex items-center justify-center gap-3">
            <span>Enter to send · Shift+Enter for new line</span>
            <span className="text-gray-800">·</span>
            <span>Drag & drop files to attach</span>
          </p>
        </div>
      )}
      {!disabled && files.length > 0 && (
        <div className="pb-2 px-4">
          <p className="text-[10px] text-gray-700 text-center">
            Files attached · Press Enter to start code review
          </p>
        </div>
      )}
    </div>
  );
}
