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

    // 3. Redirect trailing-slash URLs to non-trailing (canonical)
    // Matches any path that ends with / except the root "/"
    redirectsList.push({
      source: '/:path+/',
      destination: '/:path+',
      permanent: true,
    });

    return redirectsList;
  },
};

module.exports = nextConfig;
