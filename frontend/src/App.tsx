import { useState, useCallback, useRef, useEffect } from 'react';
import type {
  AppPhase,
  AgentStatus,
  ReviewResponse,
  Report,
  Finding,
  SessionSummary,
} from './types';
import { AGENTS } from './types';
import { submitReview, getSessions } from './api/council';
import CouncilHeader from './components/CouncilHeader';
import CodeInput from './components/CodeInput';
import AgentGrid from './components/AgentGrid';
import DebateTimeline from './components/DebateTimeline';
import FinalReport from './components/FinalReport';

const INITIAL_STATUSES: Record<string, AgentStatus> = Object.fromEntries(
  AGENTS.map((a) => [a.id, 'waiting'])
);

/**
 * Simula la llegada progresiva de hallazgos agente por agente.
 * Como el backend real podría devolver todo junto, esta función
 * emula el streaming para dar la sensación de debate en vivo.
 */
function buildProgressiveRounds(
  response: ReviewResponse,
  onRoundUpdate: (round: number, findings: Finding[], allStatuses: Record<string, AgentStatus>) => void,
  onComplete: (response: ReviewResponse) => void
): () => void {
  const statuses: Record<string, AgentStatus> = { ...INITIAL_STATUSES };
  let cancelled = false;

  const roundKeys: (keyof typeof response.rounds)[] = ['round_1', 'round_2', 'round_3'];

  function releaseRound(roundIndex: number) {
    if (cancelled) return;

    const roundKey = roundKeys[roundIndex];
    const findings = response.rounds[roundKey];

    if (!findings || findings.length === 0) {
      // Skip empty rounds
      if (roundIndex < 2) {
        setTimeout(() => releaseRound(roundIndex + 1), 300);
      } else {
        onComplete(response);
      }
      return;
    }

    // Mark all agents as analyzing
    for (const id of Object.keys(statuses)) {
      statuses[id] = 'analyzing';
    }
    onRoundUpdate(roundIndex + 1, [], { ...statuses });

    // Release findings one by one with delays
    const delays = findings.map((_, idx) => (idx + 1) * 600);

    findings.forEach((finding, idx) => {
      setTimeout(() => {
        if (cancelled) return;
        statuses[finding.agent] = 'complete';
        onRoundUpdate(roundIndex + 1, findings.slice(0, idx + 1), { ...statuses });
      }, delays[idx]);
    });

    // After all agents complete, move to next round
    const totalDelay = Math.max(...delays, findings.length * 600) + 400;
    setTimeout(() => {
      if (cancelled) return;
      if (roundIndex < 2) {
        releaseRound(roundIndex + 1);
      } else {
        onComplete(response);
      }
    }, totalDelay);
  }

  // Start round 1 after a brief pause
  setTimeout(() => releaseRound(0), 800);

  return () => {
    cancelled = true;
  };
}

export default function App() {
  const [phase, setPhase] = useState<AppPhase>('idle');
  const [currentRound, setCurrentRound] = useState(0);
  const [agentStatuses, setAgentStatuses] = useState<Record<string, AgentStatus>>(INITIAL_STATUSES);
  const [rounds, setRounds] = useState<ReviewResponse['rounds']>({
    round_1: [],
    round_2: [],
    round_3: [],
  });
  const [report, setReport] = useState<Report | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [history, setHistory] = useState<SessionSummary[]>([]);

  const cancelRef = useRef<(() => void) | null>(null);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      cancelRef.current?.();
    };
  }, []);

  const handleSubmit = useCallback(
    async (code: string) => {
      // Reset state
      setError(null);
      setReport(null);
      setSessionId(null);
      setRounds({ round_1: [], round_2: [], round_3: [] });
      setCurrentRound(0);
      setPhase('analyzing');

      // Cancel any previous animation
      cancelRef.current?.();

      // Set all agents to analyzing
      const analyzingStatuses: Record<string, AgentStatus> = Object.fromEntries(
        AGENTS.map((a) => [a.id, 'analyzing'])
      );
      setAgentStatuses(analyzingStatuses);

      try {
        const response = await submitReview(code);

        setSessionId(response.session_id);

        // Start progressive animation of findings
        cancelRef.current = buildProgressiveRounds(
          response,
          (round, findings, statuses) => {
            setCurrentRound(round);
            setAgentStatuses(statuses);

            setRounds((prev) => {
              const key = `round_${round}` as keyof typeof prev;
              return { ...prev, [key]: findings };
            });

            // Update phase based on round
            if (round === 1) setPhase('round1');
            else if (round === 2) setPhase('round2');
            else if (round === 3) setPhase('round3');
          },
          (finalResponse) => {
            setReport(finalResponse.report);
            setPhase('complete');
            setAgentStatuses(
              Object.fromEntries(AGENTS.map((a) => [a.id, 'complete']))
            );
            cancelRef.current = null;
          }
        );
      } catch (err) {
        setPhase('error');
        setError(
          err instanceof Error ? err.message : 'Error desconocido al conectar con el backend'
        );
        setAgentStatuses(
          Object.fromEntries(AGENTS.map((a) => [a.id, 'error']))
        );
      }
    },
    []
  );

  const handleNewReview = useCallback(() => {
    cancelRef.current?.();
    cancelRef.current = null;
    setPhase('idle');
    setCurrentRound(0);
    setAgentStatuses(INITIAL_STATUSES);
    setRounds({ round_1: [], round_2: [], round_3: [] });
    setReport(null);
    setError(null);
    setSessionId(null);
  }, []);

  const handleHistory = useCallback(async () => {
    try {
      const sessions = await getSessions();
      setHistory(sessions);
    } catch {
      // Silently fail for optional feature
    }
  }, []);

  const hasActiveReview = phase !== 'idle';

  return (
    <div className="min-h-screen bg-slate-900">
      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Header */}
        <CouncilHeader
          phase={phase}
          currentRound={currentRound}
          totalRounds={3}
        />

        {/* Error banner */}
        {phase === 'error' && error && (
          <div
            className="card p-4 mb-6 border-red-500/40 bg-red-500/5 animate-fade-in"
            role="alert"
          >
            <div className="flex items-start gap-3">
              <span className="text-xl flex-shrink-0" role="img" aria-label="error">
                ❌
              </span>
              <div>
                <p className="text-red-400 font-semibold text-sm mb-1">
                  Error de conexión
                </p>
                <p className="text-slate-300 text-sm">{error}</p>
                <button
                  onClick={handleNewReview}
                  className="mt-3 text-sm text-blue-400 hover:text-blue-300 underline underline-offset-2"
                >
                  Intentar de nuevo
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Code Input — visible always, but disabled during review */}
        <CodeInput onSubmit={handleSubmit} disabled={hasActiveReview} />

        {/* Agent Grid — shows status of all agents */}
        {hasActiveReview && <AgentGrid statuses={agentStatuses} />}

        {/* Debate Timeline — shows as rounds complete */}
        {(phase === 'round1' ||
          phase === 'round2' ||
          phase === 'round3' ||
          phase === 'complete') && (
          <DebateTimeline rounds={rounds} currentRound={currentRound} />
        )}

        {/* Loading indicator when analyzing and no rounds yet */}
        {phase === 'analyzing' &&
          rounds.round_1.length === 0 &&
          rounds.round_2.length === 0 &&
          rounds.round_3.length === 0 && (
            <div className="card p-12 mb-6 flex flex-col items-center justify-center animate-fade-in">
              <div className="flex gap-2 mb-4">
                {AGENTS.map((agent) => (
                  <span
                    key={agent.id}
                    className="text-2xl animate-bounce"
                    style={{
                      animationDelay: `${AGENTS.indexOf(agent) * 150}ms`,
                      color: agent.color,
                    }}
                    role="img"
                    aria-label={agent.name}
                  >
                    {agent.icon}
                  </span>
                ))}
              </div>
              <p className="text-slate-400 text-sm">
                Los agentes están revisando el código...
              </p>
              <p className="text-slate-600 text-xs mt-1">
                Cada especialista analiza desde su perspectiva
              </p>
            </div>
          )}

        {/* Final Report */}
        {phase === 'complete' && report && (
          <FinalReport
            report={report}
            onNewReview={handleNewReview}
            onHistory={handleHistory}
          />
        )}

        {/* Session ID footer */}
        {sessionId && (
          <div className="text-center mt-8 mb-4">
            <p className="text-xs text-slate-600 font-mono">
              Sesión: {sessionId}
            </p>
          </div>
        )}

        {/* History modal (simple) */}
        {history.length > 0 && phase === 'idle' && (
          <div className="card p-4 mt-4 animate-fade-in">
            <h3 className="card-header mb-3">Historial de Revisiones</h3>
            <div className="space-y-2">
              {history.map((s) => (
                <div
                  key={s.id}
                  className="flex items-center justify-between text-sm py-2 px-3 bg-slate-700/30 rounded-lg"
                >
                  <span className="text-slate-400 font-mono text-xs">
                    {s.id.slice(0, 8)}...
                  </span>
                  <span className="text-slate-500 text-xs">
                    {new Date(s.created_at).toLocaleDateString()}
                  </span>
                  <span className="text-slate-400 text-xs">
                    Score: {s.score}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
