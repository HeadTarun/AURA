import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Proxy /api/v1/* → backend during local dev — eliminates CORS issues
  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        destination: "http://localhost:8001/api/v1/:path*",
      },
      {
        source: "/health",
        destination: "http://localhost:8001/health",
      },
    ];
  },
};

export default nextConfig;
