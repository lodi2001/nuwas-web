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
        `${process.env.NEXT_PUBLIC_API_URL}/api/contact/`,
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
                  name="organization"
                  placeholder="اسم الجهة / الشركة"
                />
                <select name="service_type" className="full-width" required>
                  <option value="">نوع الخدمة المطلوبة</option>
                  <option value="تطوير برمجيات">تطوير برمجيات</option>
                  <option value="ذكاء اصطناعي">ذكاء اصطناعي</option>
                  <option value="تحول رقمي">تحول رقمي</option>
                </select>
                <textarea
                  name="project_description"
                  className="full-width"
                  rows={4}
                  placeholder="وصف المشروع"
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
