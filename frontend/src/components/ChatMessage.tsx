import { useState } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import type {
  ChatMessageData,
  UserMessage,
  AgentProgressMessage,
  FindingMessage,
  ReportMessage,
  ErrorMessage,
} from '../types';
import { AGENTS } from '../types';

/* ─── Severity badge ─────────────────────────────────────────────────── */

function SeverityBadge({ severity }: { severity: string }) {
  const classMap: Record<string, string> = {
    Crítico: 'sev-critico',
    Alto: 'sev-alto',
    Medio: 'sev-medio',
    Bajo: 'sev-bajo',
  };
  const cls = classMap[severity] ?? 'sev-bajo';
  return <span className={cls}>{severity.toUpperCase()}</span>;
}

/* ─── Collapsible section ───────────────────────────────────────────── */

function CollapsibleSection({
  title,
  children,
  defaultOpen = false,
}: {
  title: string;
  children: React.ReactNode;
  defaultOpen?: boolean;
}) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="border border-retro-border">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between gap-2 px-3 py-2 text-xs font-bold text-gray-500 hover:text-retro-cyan hover:bg-retro-bg transition-colors uppercase tracking-wider"
        aria-expanded={open}
        aria-label={title}
      >
        <span>&gt; {title}</span>
        <svg
          className={`w-3.5 h-3.5 transition-transform duration-200 ${open ? 'rotate-180' : ''}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      {open && <div className="px-3 pb-3 text-sm text-gray-300 leading-relaxed border-t border-retro-border pt-2">{children}</div>}
    </div>
  );
}

/* ─── Sub-views ─────────────────────────────────────────────────────── */

function UserMessageView({ message }: { message: UserMessage }) {
  return (
    <div className="chat-message chat-message-user message-enter">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-xs font-bold text-retro-cyan">&gt; USER</span>
        <span className="text-[10px] text-gray-600">
          {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>
      <div className="border border-retro-border overflow-hidden">
        <SyntaxHighlighter
          language="typescript"
          style={oneDark}
          showLineNumbers
          customStyle={{
            margin: 0,
            borderRadius: 0,
            fontSize: '0.75rem',
            lineHeight: '1.5',
            maxHeight: '400px',
            fontFamily: "'Courier New', Courier, monospace",
          }}
          wrapLongLines
        >
          {message.code}
        </SyntaxHighlighter>
      </div>
    </div>
  );
}

function AgentProgressView({ message }: { message: AgentProgressMessage }) {
  const allDone = message.agents.every((a) => a.status === 'complete' || a.status === 'error');
  return (
    <div className="message-enter">
      <div className="flex items-center gap-2 mb-3">
        <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">&gt; {message.label}</span>
        {!allDone && (
          <span className="flex gap-0.5">
            <span className="w-1.5 h-1.5 bg-retro-cyan status-dot" />
            <span className="w-1.5 h-1.5 bg-retro-cyan status-dot" style={{ animationDelay: '0.3s' }} />
            <span className="w-1.5 h-1.5 bg-retro-cyan status-dot" style={{ animationDelay: '0.6s' }} />
          </span>
        )}
        {allDone && (
          <span className="text-[10px] text-retro-green font-bold uppercase">
            [OK]
          </span>
        )}
      </div>
      <div className="flex flex-wrap gap-2">
        {message.agents.map((agent) => (
          <div
            key={agent.id}
            className="agent-pill"
            style={{
              borderLeft: `3px solid ${agent.color}`,
              opacity: agent.status === 'waiting' ? 0.5 : 1,
            }}
            role="status"
            aria-label={`${agent.name}: ${agent.status}`}
          >
            <span className="text-xs font-bold" style={{ color: agent.color }} aria-hidden="true">
              [{agent.icon}]
            </span>
            <span className="text-gray-300">{agent.name}</span>
            {agent.status === 'analyzing' && (
              <span className="flex gap-0.5 ml-1">
                <span className="w-1 h-1 bg-current animate-pulse" style={{ color: agent.color }} />
                <span className="w-1 h-1 bg-current animate-pulse" style={{ color: agent.color, animationDelay: '200ms' }} />
                <span className="w-1 h-1 bg-current animate-pulse" style={{ color: agent.color, animationDelay: '400ms' }} />
              </span>
            )}
            {agent.status === 'complete' && (
              <span className="text-retro-green text-[10px] ml-1">[OK]</span>
            )}
            {agent.status === 'error' && (
              <span className="text-retro-red text-[10px] ml-1">[ERR]</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function FindingView({ message }: { message: FindingMessage }) {
  const { finding, agentName, agentIcon, agentColor, round } = message;

  return (
    <div
      className="chat-message chat-message-finding message-enter"
      style={{ borderLeftColor: agentColor }}
    >
      {/* Header */}
      <div className="flex items-center gap-2 mb-2 flex-wrap">
        <span className="text-xs font-bold" style={{ color: agentColor }}>
          [{agentIcon}] {agentName}
        </span>
        <SeverityBadge severity={finding.impacto} />
        <span className="text-[10px] text-gray-600 border border-retro-border px-1.5 py-0.5 font-mono">
          R{round}
        </span>
      </div>

      {/* Finding conclusion */}
      <div className="mb-2">
        <p className="text-sm font-bold text-gray-100 leading-relaxed">
          {finding.hallazgo}
        </p>
      </div>

      {/* Detail */}
      {finding.detalle && (
        <div className="mb-1.5">
          <CollapsibleSection title="DETALLE">
            <p>{finding.detalle}</p>
          </CollapsibleSection>
        </div>
      )}

      {/* Proposal */}
      {finding.propuesta && (
        <CollapsibleSection title="PROPUESTA">
          <p>{finding.propuesta}</p>
        </CollapsibleSection>
      )}
    </div>
  );
}

function ReportView({ message }: { message: ReportMessage }) {
  const { report, sessionId } = message;

  // Count by severity
  const counts: Record<string, number> = { Crítico: 0, Alto: 0, Medio: 0, Bajo: 0 };
  for (const f of report.findings) {
    if (counts[f.impacto] !== undefined) counts[f.impacto]++;
    else counts.Bajo++;
  }

  const [expandedIdx, setExpandedIdx] = useState<number | null>(null);

  return (
    <div className="message-enter">
      {/* Report header */}
      <div className="flex items-center gap-3 mb-3 px-1">
        <span className="text-sm font-bold text-retro-cyan uppercase tracking-wider">
          &gt; REPORTE CONSOLIDADO
        </span>
        <span className="text-[10px] text-gray-600 font-mono">
          {report.participants.length} agents &middot; {report.rounds} rounds &middot; {sessionId.slice(0, 8)}
        </span>
      </div>

      {/* Executive summary */}
      <div className="finding-item mb-3">
        <p className="text-[10px] text-retro-cyan font-bold uppercase tracking-wider mb-1">
          &gt; RESUMEN EJECUTIVO
        </p>
        <p className="text-sm text-gray-300 leading-relaxed whitespace-pre-wrap">
          {report.summary}
        </p>
      </div>

      {/* Severity distribution */}
      <div className="flex flex-wrap gap-2 mb-3">
        {Object.entries(counts).map(([sev, count]) => {
          if (count === 0) return null;
          return <SeverityBadge key={sev} severity={sev} />;
        })}
        <span className="text-[10px] text-gray-600 self-center">
          {report.findings.length} finding{report.findings.length !== 1 ? 's' : ''}
        </span>
      </div>

      {/* Consolidated findings */}
      <div className="space-y-2">
        {report.findings.map((finding, idx) => {
          // Find which agent voted what for display
          const voteEntries = Object.entries(finding.votes);
          return (
            <div key={idx} className="finding-item">
              <button
                onClick={() => setExpandedIdx(expandedIdx === idx ? null : idx)}
                className="w-full flex items-center justify-between gap-3 text-left"
                aria-expanded={expandedIdx === idx}
                aria-label={`Finding ${idx + 1}`}
              >
                <div className="flex items-center gap-2 min-w-0">
                  <span className="text-xs text-gray-600 font-mono flex-shrink-0">
                    [{idx + 1}]
                  </span>
                  <SeverityBadge severity={finding.impacto} />
                  <span className="text-sm font-bold text-gray-200 truncate">
                    {finding.hallazgo}
                  </span>
                </div>
                <svg
                  className={`w-3.5 h-3.5 text-gray-600 flex-shrink-0 transition-transform duration-200 ${
                    expandedIdx === idx ? 'rotate-180' : ''
                  }`}
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                >
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {expandedIdx === idx && (
                <div className="mt-2 pt-2 space-y-2 border-t border-retro-border">
                  <p className="text-sm text-gray-400">
                    <span className="text-retro-cyan font-bold text-[10px] uppercase tracking-wider">Detalle: </span>
                    {finding.detalle}
                  </p>
                  <p className="text-sm text-gray-400">
                    <span className="text-retro-cyan font-bold text-[10px] uppercase tracking-wider">Propuesta: </span>
                    {finding.propuesta}
                  </p>
                  {voteEntries.length > 0 && (
                    <div>
                      <span className="text-[10px] text-gray-600 font-bold uppercase tracking-wider">Votos: </span>
                      <div className="flex flex-wrap gap-1.5 mt-1">
                        {voteEntries.map(([agentId, vote]) => {
                          const agent = AGENTS.find((a) => a.id === agentId);
                          const sevClass = (sev: string) => {
                            if (sev.toLowerCase().includes('crit') || sev.toLowerCase().includes('alto')) return 'text-retro-red';
                            if (sev.toLowerCase().includes('med')) return 'text-retro-yellow';
                            return 'text-retro-green';
                          };
                          return (
                            <span
                              key={agentId}
                              className="inline-flex items-center gap-1 text-[10px] px-1.5 py-0.5 border border-retro-border bg-retro-bg text-gray-400 font-mono"
                            >
                              <span style={{ color: agent?.color ?? '#666' }}>{agentId}</span>
                              : <span className={sevClass(vote)}>{vote}</span>
                            </span>
                          );
                        })}
                      </div>
                    </div>
                  )}
                  <div className="flex items-center gap-2 text-[10px] text-gray-600 font-mono">
                    <span>Consensus: {Math.round(finding.consensus_score * 100)}%</span>
                    <span className="text-retro-border">|</span>
                    <span>{finding.consensus_level}</span>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Session ID footer */}
      <p className="text-[10px] text-gray-700 font-mono text-center mt-3">
        SESSION: {sessionId}
      </p>
    </div>
  );
}

function ErrorView({ message }: { message: ErrorMessage }) {
  return (
    <div className="chat-message message-enter border-retro-red" role="alert">
      <div className="flex items-center gap-2 mb-1">
        <span className="text-xs font-bold text-retro-red">[ERROR]</span>
      </div>
      <p className="text-sm text-gray-300">{message.text}</p>
    </div>
  );
}

/* ─── Main component ────────────────────────────────────────────────── */

interface ChatMessageProps {
  message: ChatMessageData;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  switch (message.role) {
    case 'user':
      return <UserMessageView message={message} />;
    case 'agent-progress':
      return <AgentProgressView message={message} />;
    case 'finding':
      return <FindingView message={message} />;
    case 'report':
      return <ReportView message={message} />;
    case 'error':
      return <ErrorView message={message} />;
    default:
      return null;
  }
}
