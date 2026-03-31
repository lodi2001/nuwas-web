export interface SiteSettings {
  site_name_ar: string;
  site_name_en: string;
  logo: string | null;
  email: string;
  phone: string;
  address_ar: string;
  address_en: string;
  linkedin_url: string;
  twitter_url: string;
  instagram_url: string;
  copyright_text_ar: string;
  copyright_text_en: string;
  footer_description_ar: string;
  footer_description_en: string;
}

export interface HeroSection {
  heading_ar: string;
  heading_en: string;
  subheading_ar: string;
  subheading_en: string;
  cta_primary_text_ar: string;
  cta_primary_text_en: string;
  cta_primary_link: string;
  cta_secondary_text_ar: string;
  cta_secondary_text_en: string;
  cta_secondary_link: string;
  background_image: string | null;
}

export interface StatItem {
  number: string;
  label_ar: string;
  label_en: string;
  order: number;
}

export interface SectionHeader {
  section: string;
  title_ar: string;
  title_en: string;
  subtitle_ar: string;
  subtitle_en: string;
}

export interface LearnCard {
  icon_class: string;
  title_ar: string;
  title_en: string;
  description_ar: string;
  description_en: string;
  order: number;
}

export interface ServiceCard {
  icon_class: string;
  title_ar: string;
  title_en: string;
  description_ar: string;
  description_en: string;
  order: number;
}

export interface Product {
  name: string;
  logo: string | null;
  description_ar: string;
  description_en: string;
  features_ar: string;
  features_en: string;
  features_list_ar: string[];
  features_list_en: string[];
  link: string;
  order: number;
}

export interface NavLink {
  label_ar: string;
  label_en: string;
  href: string;
  order: number;
}

export interface FooterLink {
  label_ar: string;
  label_en: string;
  href: string;
  order: number;
}

export interface VideoBanner {
  video: string | null;
  phrase_ar: string;
  phrase_en: string;
  is_active: boolean;
}

export interface LandingPageData {
  site_settings: SiteSettings;
  hero: HeroSection;
  stats: StatItem[];
  section_headers: SectionHeader[];
  learn_cards: LearnCard[];
  service_cards: ServiceCard[];
  products: Product[];
  nav_links: NavLink[];
  footer_links: FooterLink[];
  video_banner: VideoBanner;
}
