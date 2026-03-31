# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Corporate website for **Nuwas Innovative IT** (نواس الابتكارية لتقنية المعلومات), a Saudi Arabia-based IT company. The site is bilingual Arabic/English with Arabic (RTL) as the primary language.

## Architecture

Django backend (CMS via admin) + Next.js frontend (App Router, TypeScript).

- `backend/` — Django project (`nuwas/` settings, `landing/` app with models, admin, DRF API)
- `frontend/` — Next.js project (App Router, server components, ISR with 60s revalidation)
- `documentation/` — original static HTML prototype (reference only)

### Backend (Django)

- **Models**: Singleton pattern for `SiteSettings` and `HeroSection`; ordered list models for `StatItem`, `SectionHeader`, `LearnCard`, `ServiceCard`, `Product`, `NavLink`, `FooterLink`; `ContactSubmission` for form entries
- **API**: Two endpoints — `GET /api/landing/` (all page content) and `POST /api/contact/` (form submissions)
- **Admin**: Singleton guards (no add/delete), `list_editable` ordering, read-only contact submissions with mark-as-read actions
- **DB**: SQLite (v1)
- **Venv**: `backend/venv/`

### Frontend (Next.js)

- `app/layout.tsx` — RTL html, IBM Plex fonts via `next/font/google`, Font Awesome + AOS via CDN
- `app/page.tsx` — Server component, fetches all data from `/api/landing/`
- `components/` — Navbar (client), Hero, StatsStrip, LearnSection, ServicesSection, ProductsSection, ContactForm (client), Footer, SectionTitle, AOSInit (client)
- `lib/api.ts` — fetch helper; `lib/types.ts` — TypeScript interfaces matching API response

## Development

```bash
# Backend
cd backend && source venv/bin/activate
python manage.py runserver 8008

# Frontend (separate terminal)
cd frontend
npm run dev   # runs on port 3008
```

**Ports**: Django **8008**, Next.js **3008** (not defaults — other apps use 8000/3000).

**Admin**: http://localhost:8008/admin/ (credentials: admin / admin)

**Seed data**: `python manage.py seed_content` — populates all models from the prototype content

## Key Conventions

- **RTL layout**: `<html lang="ar" dir="rtl">`
- **Fonts**: IBM Plex Sans Arabic + IBM Plex Sans
- **CSS custom properties** in `globals.css`: `--primary-blue`, `--accent-cyan`, `--light-bg`, etc.
- **Bilingual fields**: all content models have `_ar` and `_en` variants; English is `blank=True` for v1
- Sections: `#home`, `#learn`, `#services`, `#products`, `#contact`
- Responsive breakpoints at 992px and 600px
