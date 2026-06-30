import type { AgentInfo, AgentStatus } from '../types';

interface AgentCardProps {
  agent: AgentInfo;
  status: AgentStatus;
}

const statusConfig: Record<AgentStatus, { label: string; icon: string; className: string }> = {
  waiting: {
    label: 'Esperando...',
    icon: '⏳',
    className: 'border-slate-700 text-slate-500',
  },
  analyzing: {
    label: 'Analizando',
    icon: '⏳',
    className: 'border-blue-500/50 text-blue-400 animate-pulse',
  },
  complete: {
    label: 'Completado',
    icon: '✅',
    className: 'border-green-500/50 text-green-400',
  },
  error: {
    label: 'Error',
    icon: '❌',
    className: 'border-red-500/50 text-red-400',
  },
};

export default function AgentCard({ agent, status }: AgentCardProps) {
  const config = statusConfig[status];

  return (
    <div
      className={`card p-4 flex flex-col items-center gap-2 transition-all duration-300
        ${status === 'analyzing' ? 'ring-2 ring-offset-2 ring-offset-slate-900 shadow-lg' : ''}
        ${status === 'complete' ? 'opacity-100' : 'opacity-80 hover:opacity-100'}`}
      style={{
        borderColor: status === 'analyzing' ? agent.color : undefined,
        '--tw-ring-color': status === 'analyzing' ? agent.color : undefined,
      } as React.CSSProperties}
      role="article"
      aria-label={`Agente ${agent.name}: ${config.label}`}
    >
      <span
        className="text-2xl transition-transform duration-300"
        style={{ transform: status === 'analyzing' ? 'scale(1.15)' : 'scale(1)' }}
        role="img"
        aria-hidden="true"
      >
        {agent.icon}
      </span>

      <div className="text-center">
        <p
          className="text-sm font-semibold text-white truncate max-w-[100px]"
          style={status === 'complete' ? { color: agent.color } : undefined}
        >
          {agent.name}
        </p>
        <p className="text-[10px] text-slate-500 leading-tight mt-0.5">
          {agent.specialty}
        </p>
      </div>

      <div className={`flex items-center gap-1.5 text-xs mt-1 ${config.className}`}>
        <span className="text-sm">{config.icon}</span>
        <span className="font-medium">{config.label}</span>
      </div>

      {status === 'analyzing' && (
        <div className="flex gap-1 mt-1">
          <span
            className="w-1.5 h-1.5 rounded-full animate-bounce"
            style={{ backgroundColor: agent.color, animationDelay: '0ms' }}
          />
          <span
            className="w-1.5 h-1.5 rounded-full animate-bounce"
            style={{ backgroundColor: agent.color, animationDelay: '150ms' }}
          />
          <span
            className="w-1.5 h-1.5 rounded-full animate-bounce"
            style={{ backgroundColor: agent.color, animationDelay: '300ms' }}
          />
        </div>
      )}
    </div>
  );
}
