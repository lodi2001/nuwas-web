"use client";

import { useState, FormEvent } from "react";
import { SectionHeader } from "@/lib/types";

export default function ContactForm({ header }: { header: SectionHeader }) {
  const [status, setStatus] = useState<
    "idle" | "submitting" | "success" | "error"
  >("idle");

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setStatus("submitting");

    const formData = new FormData(e.currentTarget);
    const body = Object.fromEntries(formData);

    try {
      const res = await fetch(
        `/submit-contact/`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        }
      );
      setStatus(res.ok ? "success" : "error");
    } catch {
      setStatus("error");
    }
  }

  return (
    <section className="section-padding" id="contact">
      <div className="container">
        <div className="contact-section" data-aos="fade-up">
          <div className="pattern-decoration contact-pattern" />
          <div className="section-title">
            <h2>{header.title_ar}</h2>
            <p>{header.subtitle_ar}</p>
          </div>

          {status === "success" ? (
            <div className="form-success">
              <i
                className="fas fa-check-circle"
                style={{ fontSize: "3rem", marginBottom: "15px", display: "block" }}
              />
              تم إرسال طلبك بنجاح! سنتواصل معك قريباً.
            </div>
          ) : (
            <form onSubmit={handleSubmit}>
              <div className="form-grid">
                <input
                  type="text"
                  name="full_name"
                  placeholder="الاسم الكامل"
                  required
                />
                <input
                  type="email"
                  name="email"
                  placeholder="البريد الإلكتروني"
                  required
                />
                <input
                  type="tel"
                  name="phone"
                  placeholder="رقم الجوال (966+)"
                  required
                />
                <input
                  type="text"
                  name="company_name"
                  placeholder="اسم الشركة / المؤسسة"
                />
                <select name="project_type" required>
                  <option value="">نوع المشروع</option>
                  <option value="mobile_app">تطبيق جوال</option>
                  <option value="web_platform">منصة ويب</option>
                  <option value="ai_system">نظام ذكاء اصطناعي</option>
                  <option value="digital_transformation">تحول رقمي</option>
                  <option value="other">أخرى</option>
                </select>
                <select name="budget_range">
                  <option value="undecided">نطاق الميزانية</option>
                  <option value="under_50k">أقل من 50,000 ريال</option>
                  <option value="50k_150k">50,000 - 150,000 ريال</option>
                  <option value="150k_500k">150,000 - 500,000 ريال</option>
                  <option value="over_500k">أكثر من 500,000 ريال</option>
                </select>
                <select name="timeline" className="full-width">
                  <option value="flexible">الجدول الزمني</option>
                  <option value="1_3_months">1-3 أشهر</option>
                  <option value="3_6_months">3-6 أشهر</option>
                  <option value="6_12_months">6-12 شهر</option>
                </select>
                <textarea
                  name="project_description"
                  className="full-width"
                  rows={4}
                  placeholder="وصف فكرة المشروع (50 حرف على الأقل)"
                  minLength={50}
                  required
                />
                <button
                  type="submit"
                  className="btn btn-primary full-width"
                  style={{ fontSize: "1.1rem" }}
                  disabled={status === "submitting"}
                >
                  {status === "submitting" ? "جاري الإرسال..." : "إرسال الطلب"}
                </button>
              </div>
              {status === "error" && (
                <div className="form-error">
                  حدث خطأ أثناء الإرسال. يرجى المحاولة مرة أخرى.
                </div>
              )}
            </form>
          )}
        </div>
      </div>
    </section>
  );
}
