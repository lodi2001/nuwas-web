"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import { NavLink, SiteSettings } from "@/lib/types";

export default function Navbar({
  navLinks,
  settings,
}: {
  navLinks: NavLink[];
  settings: SiteSettings;
}) {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 50);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <nav className={scrolled ? "scrolled" : ""}>
      <div className="container nav-container">
        <a href="#home" className="logo">
          <Image
            src="/logo.png"
            alt={settings.site_name_ar}
            width={160}
            height={60}
            style={{
              height: "45px",
              width: "auto",
              filter: scrolled ? "none" : "brightness(0) invert(1)",
              transition: "filter 0.4s",
            }}
            priority
          />
        </a>

        <ul className="nav-links">
          {navLinks.map((link) => (
            <li key={link.href}>
              <a href={link.href}>{link.label_ar}</a>
            </li>
          ))}
        </ul>

        <div className="nav-actions">
          <a
            href="#contact"
            className="btn btn-primary"
          >
            طلب عرض سعر
          </a>
        </div>
      </div>
    </nav>
  );
}
