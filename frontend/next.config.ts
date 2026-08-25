import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  experimental: {
    // Explicitly scope turbopack root to frontend folder
  },
};

export default nextConfig;

