import type { AppPhase } from '../types';

interface CouncilHeaderProps {
  phase: AppPhase;
  currentRound: number;
  totalRounds: number;
}

export default function CouncilHeader({ phase, currentRound, totalRounds }: CouncilHeaderProps) {
  const progress =
    phase === 'idle'
      ? 0
      : phase === 'analyzing'
        ? 10
        : phase === 'round1'
          ? 33
          : phase === 'round2'
            ? 66
            : phase === 'round3'
              ? 90
              : phase === 'complete'
                ? 100
                : 0;

  const isActive = phase !== 'idle' && phase !== 'error';

  return (
    <header className="card p-4 mb-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-2xl" role="img" aria-label="search">
            🔍
          </span>
          <div>
            <h1 className="text-xl font-bold text-white tracking-tight">
              QWEN COUNCIL
            </h1>
            <p className="text-xs text-slate-500 -mt-0.5">Multi-Agent Code Review</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {isActive && (
            <div className="flex items-center gap-2 text-sm">
              <span className="text-slate-400">
                Ronda{' '}
                <span className="text-white font-semibold">
                  {Math.min(currentRound, totalRounds)}
                </span>
                <span className="text-slate-500">/{totalRounds}</span>
              </span>
            </div>
          )}

          <div className="flex items-center gap-2">
            <div className="w-28 h-2 bg-slate-700 rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-700 ease-out"
                style={{
                  width: `${progress}%`,
                  background:
                    progress === 100
                      ? 'linear-gradient(90deg, #22C55E, #16A34A)'
                      : 'linear-gradient(90deg, #3B82F6, #2563EB)',
                }}
              />
            </div>
            <span className="text-xs text-slate-500 w-8 text-right">
              {progress}%
            </span>
          </div>
        </div>
      </div>

      {phase === 'analyzing' && (
        <p className="text-sm text-slate-400 mt-3 flex items-center gap-2">
          <span className="inline-block w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
          Los agentes están analizando el código...
        </p>
      )}

      {phase === 'complete' && (
        <p className="text-sm text-green-400 mt-3 flex items-center gap-2">
          <span className="inline-block w-2 h-2 bg-green-500 rounded-full" />
          Revisión completada — Reporte listo
        </p>
      )}
    </header>
  );
}
