/**
 * Drivewayz USA — Cloudflare Pages Middleware
 *
 * Captures every request to the site and asynchronously streams it to
 * BigQuery (drivewayz-logs.drivewayz.raw_logs) for SEO/AI-bot analytics.
 *
 * Zero-latency design:
 *   - Logging runs in event.waitUntil() — the response is returned to the
 *     user BEFORE the log write completes.
 *   - JWT signing + BigQuery POST happen in the background.
 *
 * Auth: A GCP service account JSON key is stored as an encrypted env var
 *       (GCP_SA_KEY) in Cloudflare Pages. The middleware signs a JWT,
 *       exchanges it for a 1-hour OAuth token, and caches the token in
 *       Cloudflare's edge cache for reuse.
 */

interface Env {
  GCP_SA_KEY: string;
}

/* ──────────────────────────────────────────────────────────────────────
 * Bot Detection — order matters (most specific patterns first)
 * Add new bots by appending to the relevant array.
 * ────────────────────────────────────────────────────────────────────── */

const AI_BOTS: Array<{ name: string; match: RegExp }> = [
  { name: "OAI-SearchBot",         match: /OAI-SearchBot/i },
  { name: "ChatGPT-User",          match: /ChatGPT-User/i },
  { name: "GPTBot",                match: /GPTBot/i },
  { name: "Claude-User",           match: /Claude-User/i },
  { name: "Claude-Web",            match: /Claude-Web/i },
  { name: "ClaudeBot",             match: /ClaudeBot/i },
  { name: "Google-CloudVertexBot", match: /Google-CloudVertexBot/i },
  { name: "Google-Extended",       match: /Google-Extended/i },
  { name: "PerplexityUser",        match: /Perplexity-?User/i },
  { name: "PerplexityBot",         match: /PerplexityBot/i },
  { name: "Grok-DeepSearch",       match: /Grok-DeepSearch/i },
  { name: "GrokBot",               match: /GrokBot/i },
  { name: "DeepSeekBot",           match: /DeepSeekBot/i },
  { name: "Meta-ExternalAgent",    match: /Meta-ExternalAgent/i },
  { name: "Applebot-Extended",     match: /Applebot-Extended/i },
];

const SEARCH_BOTS: Array<{ name: string; match: RegExp }> = [
  { name: "Googlebot-Image",       match: /Googlebot-Image/i },
  { name: "Googlebot-Smartphone",  match: /Googlebot.*Mobile/i },
  { name: "Googlebot",             match: /Googlebot/i },
  { name: "Bingbot",               match: /bingbot/i },
  { name: "Applebot",              match: /Applebot/i },
  { name: "DuckDuckBot",           match: /DuckDuckBot/i },
  { name: "YandexBot",             match: /YandexBot/i },
  { name: "Baiduspider",           match: /Baiduspider/i },
  { name: "Bytespider",            match: /Bytespider/i },
  { name: "Amazonbot",             match: /Amazonbot/i },
  { name: "FacebookBot",           match: /FacebookBot|facebookexternalhit/i },
  { name: "Twitterbot",            match: /Twitterbot/i },
  { name: "LinkedInBot",           match: /LinkedInBot/i },
  { name: "Slackbot",              match: /Slackbot/i },
  { name: "Discordbot",            match: /Discordbot/i },
  { name: "PinterestBot",          match: /Pinterestbot/i },
  { name: "Pingdom",               match: /pingdom/i },
  { name: "UptimeRobot",           match: /UptimeRobot/i },
];

// Third-party SEO / analytics crawlers (Lumar-relevant but not search-engine bots).
const SEO_BOTS: Array<{ name: string; match: RegExp }> = [
  { name: "SemrushBot",            match: /SemrushBot/i },
  { name: "AhrefsBot",             match: /AhrefsBot/i },
  { name: "AhrefsSiteAudit",       match: /AhrefsSiteAudit/i },
  { name: "MJ12bot",               match: /MJ12bot/i },
  { name: "DotBot",                match: /DotBot/i },
  { name: "BLEXBot",               match: /BLEXBot/i },
  { name: "DataForSeoBot",         match: /DataForSeoBot/i },
  { name: "MozBot",                match: /rogerbot|dotbot/i },
  { name: "LumarBot",              match: /Lumar|DeepCrawl/i },
  { name: "ScreamingFrog",         match: /Screaming Frog/i },
  { name: "PetalBot",              match: /PetalBot/i },
];

// Generic catch-all for anything else that smells like a bot. Used only to set
// the is_bot boolean; name is logged in user_agent for later analysis.
const GENERIC_BOT_RX = /bot|crawl|spider|scraper|fetch|monitor|preview|http-?client|libwww|wget|curl|python|node-fetch|axios|java\/|go-http/i;

function detectAiBot(ua: string): string | null {
  for (const { name, match } of AI_BOTS) if (match.test(ua)) return name;
  return null;
}

function detectSearchBot(ua: string): string | null {
  for (const { name, match } of SEARCH_BOTS) if (match.test(ua)) return name;
  return null;
}

function detectSeoBot(ua: string): string | null {
  for (const { name, match } of SEO_BOTS) if (match.test(ua)) return name;
  return null;
}

function isGenericBot(ua: string): boolean {
  return !!ua && GENERIC_BOT_RX.test(ua);
}

function detectDeviceType(ua: string): string {
  if (/Mobile|iPhone|Android.*Mobile|Windows Phone|iPod/i.test(ua)) return "mobile";
  if (/iPad|Tablet|Android(?!.*Mobile)/i.test(ua)) return "tablet";
  if (/Mozilla|Chrome|Safari|Firefox|Edge|MSIE|Trident|bot|spider|crawler/i.test(ua)) return "desktop";
  return "unknown";
}

/* ──────────────────────────────────────────────────────────────────────
 * GCP OAuth: sign a JWT and exchange for a 1-hour access token.
 * Token is cached in Cloudflare's edge cache for 50 minutes.
 * ────────────────────────────────────────────────────────────────────── */

interface ServiceAccountKey {
  client_email: string;
  private_key: string;
  token_uri: string;
  project_id: string;
}

async function getAccessToken(env: Env): Promise<string | null> {
  try {
    if (!env.GCP_SA_KEY) return null;

    // Cloudflare's env var UI sometimes converts literal \n into real newlines
    // inside JSON string values, which breaks JSON.parse. Re-escape them inside
    // the private_key field before parsing.
    const repaired = env.GCP_SA_KEY.replace(
      /("private_key"\s*:\s*")([^"]*?)(")/,
      (_m, p1, body, p3) => p1 + body.replace(/\r?\n/g, "\\n") + p3
    );
    const sa: ServiceAccountKey = JSON.parse(repaired);

    // Token cache (50 min — tokens last 60 min)
    const cacheKey = new Request(`https://gcp-token-cache.drivewayzusa.co/${sa.client_email}`);
    const cache = caches.default;
    const cached = await cache.match(cacheKey);
    if (cached) return await cached.text();

    // Build JWT
    const now = Math.floor(Date.now() / 1000);
    const header = { alg: "RS256", typ: "JWT" };
    const claim = {
      iss: sa.client_email,
      scope: "https://www.googleapis.com/auth/bigquery.insertdata",
      aud: sa.token_uri,
      exp: now + 3600,
      iat: now,
    };
    const enc = (o: object) =>
      btoa(JSON.stringify(o)).replace(/=+$/, "").replace(/\+/g, "-").replace(/\//g, "_");
    const toSign = `${enc(header)}.${enc(claim)}`;

    // Sign the JWT with the RSA private key
    const pem = sa.private_key.replace(/-----[^-]+-----/g, "").replace(/\s+/g, "");
    const keyBytes = Uint8Array.from(atob(pem), c => c.charCodeAt(0));
    const cryptoKey = await crypto.subtle.importKey(
      "pkcs8", keyBytes,
      { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" },
      false, ["sign"]
    );
    const sig = new Uint8Array(
      await crypto.subtle.sign("RSASSA-PKCS1-v1_5", cryptoKey, new TextEncoder().encode(toSign))
    );
    const sigB64 = btoa(String.fromCharCode(...sig))
      .replace(/=+$/, "").replace(/\+/g, "-").replace(/\//g, "_");
    const jwt = `${toSign}.${sigB64}`;

    // Exchange JWT for access token
    const tokenRes = await fetch(sa.token_uri, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: `grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion=${jwt}`,
    });
    if (!tokenRes.ok) {
      console.error("OAuth failed:", await tokenRes.text());
      return null;
    }
    const { access_token } = await tokenRes.json() as { access_token: string };

    await cache.put(cacheKey, new Response(access_token, {
      headers: { "Cache-Control": "max-age=3000" }
    }));
    return access_token;
  } catch (e) {
    console.error("getAccessToken error:", e);
    return null;
  }
}

/* ──────────────────────────────────────────────────────────────────────
 * Streaming insert to BigQuery raw_logs table
 * ────────────────────────────────────────────────────────────────────── */

async function streamToBigQuery(env: Env, row: Record<string, any>) {
  const token = await getAccessToken(env);
  if (!token) return;

  const url =
    "https://bigquery.googleapis.com/bigquery/v2/projects/drivewayz-logs/" +
    "datasets/drivewayz/tables/raw_logs/insertAll";

  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      skipInvalidRows: true,
      ignoreUnknownValues: true,
      rows: [{ json: row }],
    }),
  });

  if (!res.ok) {
    console.error("BQ insert failed:", res.status, await res.text());
  }
}

/* ──────────────────────────────────────────────────────────────────────
 * Middleware — runs on every request to drivewayzusa.co
 * ────────────────────────────────────────────────────────────────────── */


// ─────────────────────────────────────────────────────────────────────────
// Social meta injection (Phase 1: Open Graph + Twitter Cards)
// ─────────────────────────────────────────────────────────────────────────

const BRAND_OG_IMAGE = "https://drivewayzusa.co/images/logov3.png";
const BRAND_SITE_NAME = "Drivewayz USA";
const BRAND_TWITTER = "@drivewayzusa";

function htmlEscape(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/"/g, "&quot;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

/**
 * HTMLRewriter-based injector. Streams the response, captures <title> and
 * <meta name="description">, and appends og + twitter tags before </head>.
 * Skips injection if og:title already present (homepage etc.).
 */
// ─────────────────────────────────────────────────────────────────────────
// Cache-Control by path type (Phase 1: enable edge caching, max 5min stale)
// ─────────────────────────────────────────────────────────────────────────
//
// Origin currently sets `Cache-Control: public, max-age=0, must-revalidate`,
// which forces every request to the origin (cf-cache-status: DYNAMIC) and
// produces 180-220ms TTFB on every page. This kills crawl efficiency for
// Googlebot/ClaudeBot and risks 499s under load.
//
// Strategy: rewrite Cache-Control to enable edge caching with a fresh window
// short enough that content updates land within 5 minutes WITHOUT a manual
// purge, AND long enough (24h at the edge) to maximize cache hit rate.
//
// When the Cloudflare purge token is wired up via the deploy workflow,
// updates will land instantly; until then, 5min browser cache is the worst-
// case staleness window for HTML pages.

function setCacheControl(response: Response, pathname: string): Response {
  // Don't touch responses that already have a long-cache directive, or that
  // are non-2xx (errors should not be cached aggressively).
  if (response.status < 200 || response.status >= 400) return response;

  // Sitemap + robots → short cache (search engines need fresh signals)
  if (pathname === "/sitemap.xml"
      || pathname === "/guides-sitemap.xml"
      || pathname === "/robots.txt") {
    response.headers.set("Cache-Control",
      "public, max-age=300, s-maxage=300");
    return response;
  }

  // Static assets → 1 year edge + browser cache, immutable
  if (/\.(css|js|woff2?|ttf|otf|png|jpe?g|gif|svg|webp|ico)$/i.test(pathname)) {
    response.headers.set("Cache-Control",
      "public, max-age=31536000, immutable");
    return response;
  }

  // HTML pages (everything else) → 5min browser cache, 24h edge cache.
  // Edge cache will be invalidated on deploy once Cloudflare purge token wired.
  response.headers.set("Cache-Control",
    "public, max-age=300, s-maxage=86400");
  return response;
}

function injectSocialMeta(response: Response, pageUrl: string): Response {
  // Only operate on HTML responses
  const ct = response.headers.get("content-type") || "";
  if (!ct.includes("text/html")) return response;

  let pageTitle = "";
  let pageDescription = "";
  let alreadyHasOg = false;

  const rewriter = new HTMLRewriter()
    .on("title", {
      text(text) {
        pageTitle += text.text;
      },
    })
    .on('meta[name="description"]', {
      element(el) {
        const content = el.getAttribute("content");
        if (content) pageDescription = content;
      },
    })
    .on('meta[property="og:title"]', {
      element() {
        alreadyHasOg = true;
      },
    })
    .on("head", {
      element(el) {
        // Defer to end-tag handler — at that point title/description/og-detection
        // have all run because head is parsed top-to-bottom.
        el.onEndTag((endTag) => {
          if (alreadyHasOg) return;
          if (!pageTitle) return;

          const t = htmlEscape(pageTitle.trim());
          const d = htmlEscape((pageDescription || pageTitle).trim());
          const u = htmlEscape(pageUrl);
          const img = htmlEscape(BRAND_OG_IMAGE);
          const site = htmlEscape(BRAND_SITE_NAME);
          const twitter = htmlEscape(BRAND_TWITTER);

          const tags = [
            `<meta property="og:type" content="article">`,
            `<meta property="og:site_name" content="${site}">`,
            `<meta property="og:title" content="${t}">`,
            `<meta property="og:description" content="${d}">`,
            `<meta property="og:url" content="${u}">`,
            `<meta property="og:image" content="${img}">`,
            `<meta property="og:image:width" content="1200">`,
            `<meta property="og:image:height" content="630">`,
            `<meta name="twitter:card" content="summary_large_image">`,
            `<meta name="twitter:site" content="${twitter}">`,
            `<meta name="twitter:title" content="${t}">`,
            `<meta name="twitter:description" content="${d}">`,
            `<meta name="twitter:image" content="${img}">`,
          ].join("\n  ");

          endTag.before("\n  " + tags + "\n", { html: true });
        });
      },
    });

  return rewriter.transform(response);
}

export const onRequest: PagesFunction<Env> = async (context) => {
  const { request, env, next } = context;

  // Serve the page first — logging never blocks.
  const rawResponse = await next();

  // Skip logging for static asset paths (CSS, JS, images, etc.) to keep
  // signal high and volume low.
  const url = new URL(request.url);
  const ASSET_RE = /\.(css|js|woff2?|ttf|otf|png|jpe?g|gif|svg|webp|ico|map|txt|xml|json)$/i;
  if (ASSET_RE.test(url.pathname) || url.pathname === "/favicon.ico") {
    // Apply long edge cache to static assets even on the early-return path.
    return setCacheControl(rawResponse, url.pathname);
  }

  // Inject Open Graph + Twitter Card meta tags into HTML responses.
  // Skips if og:title already present (e.g. homepage). Static assets already
  // returned above so this only touches actual page renders.
  let response = injectSocialMeta(rawResponse, request.url);

  // Rewrite Cache-Control to enable edge caching. Origin currently sends
  // max-age=0 which forces a full origin round-trip on every request.
  response = setCacheControl(response, url.pathname);

  const ua = request.headers.get("user-agent") || "";
  const aiBot     = detectAiBot(ua);
  const searchBot = detectSearchBot(ua);
  const seoBot    = detectSeoBot(ua);
  // Roll SEO crawlers up into the search_bot column so they reach Lumar; keep
  // ai_bot reserved strictly for AI assistants (ChatGPT, Claude, Perplexity, etc.).
  const searchBotEffective = searchBot || seoBot;

  const row = {
    timestamp:   new Date().toISOString(),
    url:         url.pathname + (url.search || ""),
    method:      request.method,
    status:      response.status,
    user_agent:  ua.slice(0, 500),
    ai_bot:      aiBot,
    search_bot:  searchBotEffective,
    is_bot:      !!(aiBot || searchBotEffective) || isGenericBot(ua),
    device_type: detectDeviceType(ua),
    client_ip:   request.headers.get("CF-Connecting-IP") || "",
    country:     (request.cf as any)?.country || "",
    referer:     (request.headers.get("referer") || "").slice(0, 500),
    bytes_sent:  parseInt(response.headers.get("content-length") || "0", 10) || 0,
  };

  // Fire-and-forget — response already on its way to the user.
  context.waitUntil(streamToBigQuery(env, row));

  return response;
};
