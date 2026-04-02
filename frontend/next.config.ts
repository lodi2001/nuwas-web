import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      { protocol: "http", hostname: "localhost", port: "8008" },
      { protocol: "http", hostname: "167.99.237.239", port: "8008" },
    ],
  },
  async rewrites() {
    return [
      {
        source: "/media/:path*",
        destination: `${process.env.API_URL || "http://localhost:8008"}/media/:path*`,
      },
      {
        source: "/submit-contact/",
        destination: `${process.env.API_URL || "http://localhost:8008"}/api/contact/`,
      },
    ];
  },
};

export default nextConfig;
