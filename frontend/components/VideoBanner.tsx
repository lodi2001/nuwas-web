import { VideoBanner as VideoBannerType } from "@/lib/types";

export default function VideoBanner({ data }: { data: VideoBannerType }) {
  if (!data || !data.is_active) return null;

  // Rewrite localhost URLs to public API URL for client-side playback
  let videoSrc = data.video || "/hero-video.mp4";
  if (videoSrc && videoSrc.includes("localhost")) {
    const publicApi = process.env.NEXT_PUBLIC_API_URL || "";
    videoSrc = videoSrc.replace(/http:\/\/localhost:\d+/, publicApi);
  }

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
