import Image from "next/image";
import { HeroSection } from "@/lib/types";

export default function Hero({ hero }: { hero: HeroSection }) {
  return (
    <section className="hero" id="home">
      <div className="pattern-decoration pattern-top" />
      <div className="pattern-decoration pattern-bottom" />
      <div className="container" style={{ display: "flex", alignItems: "center" }}>
        <div className="hero-content" data-aos="fade-left">
          <h1>{hero.heading_ar}</h1>
          <p>{hero.subheading_ar}</p>
          <div style={{ display: "flex", gap: "15px" }}>
            <a href={hero.cta_primary_link} className="btn btn-primary">
              {hero.cta_primary_text_ar}
            </a>
            <a href={hero.cta_secondary_link} className="btn btn-outline">
              {hero.cta_secondary_text_ar}
            </a>
          </div>
        </div>
        <div className="hero-visual" data-aos="zoom-in">
          <Image
            src="/nuwas-ai.svg"
            alt="Nuwas AI"
            width={500}
            height={200}
            style={{ width: "100%", height: "auto", maxWidth: "500px" }}
            priority
            unoptimized
          />
        </div>
      </div>
    </section>
  );
}
