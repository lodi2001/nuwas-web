import { StatItem } from "@/lib/types";

export default function StatsStrip({ stats }: { stats: StatItem[] }) {
  return (
    <section className="stats-strip">
      <div className="pattern-decoration stats-pattern" />
      <div className="container">
        <div className="stats-grid">
          {stats.map((stat) => (
            <div className="stat-item" key={stat.number}>
              <h3>{stat.number}</h3>
              <p>{stat.label_ar}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
