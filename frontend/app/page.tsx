import { getLandingData } from "@/lib/api";
import { SectionHeader } from "@/lib/types";
import AOSInit from "@/components/AOSInit";
import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import StatsStrip from "@/components/StatsStrip";
import LearnSection from "@/components/LearnSection";
import ServicesSection from "@/components/ServicesSection";
import NeuralProductsSection from "@/components/NeuralProductsSection";
import VideoBanner from "@/components/VideoBanner";
import ContactForm from "@/components/ContactForm";
import Footer from "@/components/Footer";

function findHeader(
  headers: SectionHeader[],
  section: string
): SectionHeader {
  return (
    headers.find((h) => h.section === section) ?? {
      section,
      title_ar: "",
      title_en: "",
      subtitle_ar: "",
      subtitle_en: "",
    }
  );
}

export default async function Home() {
  const data = await getLandingData();

  return (
    <>
      <AOSInit />
      <Navbar navLinks={data.nav_links} settings={data.site_settings} />
      <VideoBanner data={data.video_banner} />
      <Hero hero={data.hero} />
      <StatsStrip stats={data.stats} />
      <LearnSection
        header={findHeader(data.section_headers, "learn")}
        cards={data.learn_cards}
      />
      <ServicesSection
        header={findHeader(data.section_headers, "services")}
        cards={data.service_cards}
      />
      <NeuralProductsSection
        header={findHeader(data.section_headers, "products")}
        products={data.products}
      />
      <ContactForm
        header={findHeader(data.section_headers, "contact")}
      />
      <Footer settings={data.site_settings} links={data.footer_links} />
    </>
  );
}
