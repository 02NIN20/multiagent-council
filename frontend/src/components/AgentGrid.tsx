import { AGENTS, type AgentStatus } from '../types';
import AgentCard from './AgentCard';

interface AgentGridProps {
  statuses: Record<string, AgentStatus>;
}

export default function AgentGrid({ statuses }: AgentGridProps) {
  return (
    <section className="card p-4 mb-6" aria-label="Agent council grid">
      <h2 className="card-header mb-4">Consejo de Agentes</h2>

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
        {AGENTS.map((agent) => (
          <AgentCard
            key={agent.id}
            agent={agent}
            status={statuses[agent.id] ?? 'waiting'}
          />
        ))}
      </div>
    </section>
  );
}
