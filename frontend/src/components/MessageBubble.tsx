import type { Finding } from '../types';
import { AGENTS } from '../types';

interface MessageBubbleProps {
  finding: Finding;
  index: number;
}

function getAgentInfo(agentId: string) {
  return AGENTS.find((a) => a.id === agentId) ?? {
    id: agentId,
    name: agentId,
    icon: '\u{1F916}',
    color: '#64748B',
    specialty: '',
  };
}

const impactColors: Record<string, string> = {
  Crítico: 'impact-critical',
  Alto: 'impact-high',
  Medio: 'impact-medium',
  Bajo: 'impact-low',
};

export default function MessageBubble({ finding, index }: MessageBubbleProps) {
  const agent = getAgentInfo(finding.agent);
  const impactClass = impactColors[finding.impacto] ?? 'impact-low';

  return (
    <article
      className="card p-4 animate-fade-in border-l-4 transition-all duration-300 hover:border-l-opacity-80"
      style={{
        borderLeftColor: agent.color,
        animationDelay: `${index * 100}ms`,
      }}
      aria-label={`Hallazgo de ${agent.name}, ronda ${finding.ronda}`}
    >
      {/* Header */}
      <div className="flex items-center gap-2 mb-3">
        <span className="text-lg" role="img" aria-hidden="true">
          {agent.icon}
        </span>
        <span className="font-semibold text-sm" style={{ color: agent.color }}>
          {agent.name}
        </span>
        <span className="text-xs text-slate-500 bg-slate-700/50 px-2 py-0.5 rounded-full">
          R{finding.ronda}
        </span>
      </div>

      {/* Pirámide Invertida: Hallazgo primero */}
      <p className="text-white font-medium text-sm leading-relaxed mb-2">
        <span className="text-slate-400 font-semibold">HALLAZGO: </span>
        {finding.hallazgo}
      </p>

      <div className="space-y-1.5 text-sm ml-2">
        <p className="text-slate-300 leading-relaxed">
          <span className="text-slate-500 font-medium">Detalle: </span>
          {finding.detalle}
        </p>

        <p className="flex items-center gap-2">
          <span
            className={`inline-block text-xs font-semibold px-2 py-0.5 rounded ${impactClass}`}
          >
            {finding.impacto}
          </span>
        </p>

        <p className="text-slate-300 leading-relaxed">
          <span className="text-slate-500 font-medium">Propuesta: </span>
          {finding.propuesta}
        </p>
      </div>
    </article>
  );
}
