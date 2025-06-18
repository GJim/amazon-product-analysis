import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  output: 'export',
  async rewrites() {
    return [
      {
        source: '/api/:path*', // Match any request starting with /api/
        destination: 'http://localhost:8000/api/:path*', // Proxy it to your FastAPI backend
      },
    ];
  },
};

export default nextConfig;
