import { VideoBanner as VideoBannerType } from "@/lib/types";

export default function VideoBanner({ data }: { data: VideoBannerType }) {
  if (!data || !data.is_active) return null;

  // Rewrite video URL to go through Next.js proxy (avoids cross-origin blocking)
  let videoSrc = data.video || "/hero-video.mp4";
  if (videoSrc && videoSrc.includes("/media/")) {
    // Extract the /media/... path and serve through Next.js rewrite proxy
    const mediaPath = videoSrc.match(/\/media\/.+/)?.[0];
    if (mediaPath) videoSrc = mediaPath;
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
