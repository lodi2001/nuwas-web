import { VideoBanner as VideoBannerType } from "@/lib/types";

export default function VideoBanner({ data }: { data: VideoBannerType }) {
  if (!data || !data.is_active) return null;

  const videoSrc = data.video || "/hero-video.mp4";

  return (
    <section className="video-banner">
      <video
        autoPlay
        muted
        loop
        playsInline
        preload="auto"
        key={videoSrc}
      >
        <source src={videoSrc} type="video/mp4" />
      </video>
      <div className="video-overlay" />
      <div className="video-phrase" data-aos="fade-up">
        <h2>{data.phrase_ar}</h2>
      </div>
    </section>
  );
}
