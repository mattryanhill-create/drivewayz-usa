/** @type {import('next').NextConfig} */
const nextConfig = {
  trailingSlash: false,

  async redirects() {
    const host = 'https://drivewayzusa.co';
    const redirectsList = [];

    // 1. Force HTTPS: only if request came over HTTP (Next.js receives it as such)
    redirectsList.push({
      source: '/:path*',
      has: [{ type: 'header', key: 'x-forwarded-proto', value: 'http' }],
      destination: `${host}/:path*`,
      permanent: true,
    });

    // 2. Force non‑www: redirect www.drivewayzusa.co to drivewayzusa.co
    redirectsList.push({
      source: '/:path*',
      has: [{ type: 'host', value: 'www.drivewayzusa.co' }],
      destination: `${host}/:path*`,
      permanent: true,
    });

    // 3. REMOVED: trailing-slash→non-trailing caused redirect loop with /cost-calculator.
    // Canonical URLs use trailing slash (sitemap, _redirects). Do NOT redirect /path/ to /path.

    return redirectsList;
  },
};

module.exports = nextConfig;
