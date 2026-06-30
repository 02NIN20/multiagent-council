import { useState, useRef, useEffect } from 'react';

interface CodeInputProps {
  onSubmit: (code: string) => void;
  disabled: boolean;
}

export default function CodeInput({ onSubmit, disabled }: CodeInputProps) {
  const [code, setCode] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = () => {
    const trimmed = code.trim();
    if (trimmed.length === 0) return;
    onSubmit(trimmed);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
      e.preventDefault();
      handleSubmit();
    }
  };

  useEffect(() => {
    if (!disabled && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [disabled]);

  const lineCount = code.split('\n').length;

  return (
    <section className="card p-4 mb-6" aria-label="Code input section">
      <h2 className="card-header mb-3 flex items-center justify-between">
        <span>Código a Revisar</span>
        {code.length > 0 && (
          <span className="text-xs text-slate-500 font-mono">
            {lineCount} líneas · {code.length} caracteres
          </span>
        )}
      </h2>

      <div className="relative">
        <div className="flex rounded-lg overflow-hidden border border-slate-700 focus-within:border-blue-500 transition-colors">
          {code.length > 0 && (
            <div className="hidden sm:flex flex-col py-3 px-2 bg-slate-850 text-slate-600 text-xs leading-6 font-mono text-right select-none border-r border-slate-700">
              {Array.from({ length: lineCount }, (_, i) => (
                <span key={i}>{i + 1}</span>
              ))}
            </div>
          )}
          <textarea
            ref={textareaRef}
            value={code}
            onChange={(e) => setCode(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Pega tu código aquí para que el consejo de agentes lo revise..."
            className="flex-1 bg-slate-850 text-slate-100 p-4 font-mono text-sm leading-6
                       placeholder:text-slate-600 resize-none outline-none min-h-[200px]"
            disabled={disabled}
            rows={8}
            spellCheck={false}
            aria-label="Código fuente a revisar"
          />
        </div>
      </div>

      <div className="flex items-center justify-between mt-4">
        <p className="text-xs text-slate-500">
          <kbd className="px-1.5 py-0.5 bg-slate-700 rounded text-xs font-mono">Ctrl+Enter</kbd>{' '}
          para enviar
        </p>

        <button
          onClick={handleSubmit}
          disabled={disabled || code.trim().length === 0}
          className="btn-primary flex items-center gap-2"
          aria-label="Iniciar revisión de código"
        >
          {disabled ? (
            <>
              <span className="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Analizando...
            </>
          ) : (
            <>
              <span className="text-lg" role="img" aria-hidden="true">
                🚀
              </span>
              Iniciar Review
            </>
          )}
        </button>
      </div>
    </section>
  );
}
