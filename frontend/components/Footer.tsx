import Image from "next/image";
import { SiteSettings, FooterLink } from "@/lib/types";

export default function Footer({
  settings,
  links,
}: {
  settings: SiteSettings;
  links: FooterLink[];
}) {
  return (
    <footer>
      <div className="pattern-decoration footer-pattern" style={{ filter: "brightness(0) invert(1)" }} />
      <div className="container">
        <div className="footer-grid">
          <div className="footer-col">
            <div style={{ marginBottom: "20px" }}>
              <Image
                src="/logo.png"
                alt={settings.site_name_ar}
                width={160}
                height={60}
                style={{ height: "45px", width: "auto", filter: "brightness(0) invert(1)" }}
              />
            </div>
            <p style={{ color: "#ccc", lineHeight: 1.6 }}>
              {settings.footer_description_ar}
            </p>
            <div className="social-links">
              {settings.linkedin_url && (
                <a href={settings.linkedin_url} target="_blank" rel="noopener noreferrer">
                  <i className="fab fa-linkedin" />
                </a>
              )}
              {settings.twitter_url && (
                <a href={settings.twitter_url} target="_blank" rel="noopener noreferrer">
                  <i className="fab fa-twitter" />
                </a>
              )}
              {settings.instagram_url && (
                <a href={settings.instagram_url} target="_blank" rel="noopener noreferrer">
                  <i className="fab fa-instagram" />
                </a>
              )}
            </div>
          </div>

          <div className="footer-col">
            <h4>روابط سريعة</h4>
            <ul>
              {links.map((link) => (
                <li key={link.href}>
                  <a href={link.href}>{link.label_ar}</a>
                </li>
              ))}
            </ul>
          </div>

          <div className="footer-col">
            <h4>تواصل معنا</h4>
            <ul>
              <li>
                <i className="fas fa-envelope" /> <span dir="ltr">{settings.email}</span>
              </li>
              <li>
                <i className="fas fa-phone" /> <span dir="ltr">{settings.phone}</span>
              </li>
              <li>
                <i className="fas fa-map-marker-alt" /> {settings.address_ar}
              </li>
            </ul>
          </div>

          <div className="footer-col">
            <h4>النشرة البريدية</h4>
            <input
              type="email"
              placeholder="بريدك الإلكتروني"
              style={{
                background: "#1a1f3d",
                border: "none",
                color: "white",
                marginBottom: "10px",
              }}
            />
            <button className="btn btn-primary" style={{ width: "100%" }}>
              اشتراك
            </button>
          </div>
        </div>

        <div className="footer-bottom">
          {settings.copyright_text_ar}
        </div>
      </div>
    </footer>
  );
}
