import { SectionHeader, LearnCard } from "@/lib/types";
import SectionTitle from "./SectionTitle";

export default function LearnSection({
  header,
  cards,
}: {
  header: SectionHeader;
  cards: LearnCard[];
}) {
  return (
    <section className="section-padding" id="learn">
      <div className="container">
        <SectionTitle header={header} />
        <div className="card-grid">
          {cards.map((card, i) => (
            <div
              className="card"
              data-aos="fade-up"
              data-aos-delay={i * 100}
              key={card.title_ar}
            >
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
