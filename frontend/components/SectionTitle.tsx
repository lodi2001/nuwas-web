import { SectionHeader } from "@/lib/types";

export default function SectionTitle({ header }: { header: SectionHeader }) {
  return (
    <div className="section-title">
      <h2>{header.title_ar}</h2>
      <p>{header.subtitle_ar}</p>
    </div>
  );
}
