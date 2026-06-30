import type { Finding } from '../types';
import MessageBubble from './MessageBubble';

interface DebateTimelineProps {
  rounds: {
    round_1: Finding[];
    round_2: Finding[];
    round_3: Finding[];
  };
  currentRound: number;
}

export default function DebateTimeline({ rounds, currentRound }: DebateTimelineProps) {
  const allRounds: { label: string; findings: Finding[]; round: number }[] = [
    { label: 'Ronda 1 — Análisis Individual', findings: rounds.round_1, round: 1 },
    { label: 'Ronda 2 — Debate Cruzado', findings: rounds.round_2, round: 2 },
    { label: 'Ronda 3 — Refinamiento', findings: rounds.round_3, round: 3 },
  ];

  const visibleRounds = allRounds.filter((r) => r.findings.length > 0);

  if (visibleRounds.length === 0) {
    return null;
  }

  const latestVisibleRound = Math.max(...visibleRounds.map((r) => r.round));

  return (
    <section className="card p-4 mb-6" aria-label="Debate timeline">
      <h2 className="card-header mb-4">Debate en Vivo</h2>

      <div className="relative">
        {/* Timeline vertical line */}
        <div className="absolute left-[18px] top-0 bottom-0 w-0.5 bg-slate-700" />

        <div className="space-y-6">
          {visibleRounds.map((round) => {
            const isLatest = round.round === latestVisibleRound;
            const isActive = round.round === currentRound;

            return (
              <div key={round.round} className="relative">
                {/* Round separator */}
                <div className="flex items-center gap-3 mb-3">
                  <div
                    className={`relative z-10 w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold
                      transition-all duration-300
                      ${isActive ? 'ring-2 ring-offset-2 ring-offset-slate-900 ring-blue-500' : ''}
                      ${isLatest ? 'bg-blue-600 text-white' : 'bg-slate-700 text-slate-400'}`}
                  >
                    {round.round}
                  </div>
                  <h3
                    className={`text-sm font-semibold ${
                      isLatest ? 'text-blue-400' : 'text-slate-500'
                    }`}
                  >
                    {round.label}
                  </h3>
                  <span className="text-xs text-slate-600">
                    ({round.findings.length} hallazgo{round.findings.length !== 1 ? 's' : ''})
                  </span>
                </div>

                {/* Messages */}
                <div className="ml-12 space-y-3">
                  {round.findings.map((finding, idx) => (
                    <MessageBubble key={`${finding.agent}-${finding.ronda}-${idx}`} finding={finding} index={idx} />
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
