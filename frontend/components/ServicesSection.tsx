import { SectionHeader, ServiceCard } from "@/lib/types";
import SectionTitle from "./SectionTitle";

export default function ServicesSection({
  header,
  cards,
}: {
  header: SectionHeader;
  cards: ServiceCard[];
}) {
  return (
    <section
      className="section-padding"
      id="services"
      style={{ backgroundColor: "var(--light-bg)", position: "relative", overflow: "hidden" }}
    >
      <div className="pattern-decoration services-pattern" />
      <div className="container">
        <SectionTitle header={header} />
        <div className="card-grid">
          {cards.map((card) => (
            <div className="card" key={card.title_ar}>
              <i className={card.icon_class} />
              <h3>{card.title_ar}</h3>
              <p>{card.description_ar}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
