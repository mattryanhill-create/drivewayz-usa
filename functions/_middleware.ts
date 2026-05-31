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
  
  const AI_BOTS: Array<{ name: string; match: RegExp }> = [
    { name: "OAI-SearchBot",      match: /OAI-SearchBot/i },
    { name: "ChatGPT-User",       match: /ChatGPT-User/i },
    { name: "GPTBot",             match: /GPTBot/i },
    { name: "Claude-User",        match: /Claude-User/i },
    { name: "Claude-Web",         match: /Claude-Web/i },
    { name: "ClaudeBot",          match: /ClaudeBot/i },
    { name: "Google-CloudVertexBot", match: /Google-CloudVertexBot/i },
    { name: "Google-Extended",    match: /Google-Extended/i },
    { name: "PerplexityUser",     match: /Perplexity-?User/i },
    { name: "PerplexityBot",      match: /PerplexityBot/i },
    { name: "Grok-DeepSearch",    match: /Grok-DeepSearch/i },
    { name: "GrokBot",            match: /GrokBot/i },
    { name: "DeepSeekBot",        match: /DeepSeekBot/i },
    { name: "Meta-ExternalAgent", match: /Meta-ExternalAgent/i },
    { name: "Applebot-Extended",  match: /Applebot-Extended/i },
  ];
  
  const SEARCH_BOTS: Array<{ name: string; match: RegExp }> = [
    { name: "Googlebot-Image",      match: /Googlebot-Image/i },
    { name: "Googlebot-Smartphone", match: /Googlebot.*Mobile/i },
    { name: "Googlebot",            match: /Googlebot/i },
    { name: "Bingbot",              match: /bingbot/i },
    { name: "Applebot",             match: /Applebot/i },
    { name: "DuckDuckBot",          match: /DuckDuckBot/i },
    { name: "YandexBot",            match: /YandexBot/i },
    { name: "Baiduspider",          match: /Baiduspider/i },
  ];
  
  function detectAiBot(ua: string): string | null {
    for (const { name, match } of AI_BOTS) if (match.test(ua)) return name;
    return null;
  }
  
  function detectSearchBot(ua: string): string | null {
    for (const { name, match } of SEARCH_BOTS) if (match.test(ua)) return name;
    return null;
  }
  
  function detectDeviceType(ua: string): string {
    if (/Mobile|iPhone|Android.*Mobile|Windows Phone|iPod/i.test(ua)) return "mobile";
    if (/iPad|Tablet|Android(?!.*Mobile)/i.test(ua)) return "tablet";
    if (/Mozilla|Chrome|Safari|Firefox|Edge|MSIE|Trident|bot|spider|crawler/i.test(ua)) return "desktop";
    return "unknown";
  }
  
  interface ServiceAccountKey {
    client_email: string;
    private_key: string;
    token_uri: string;
    project_id: string;
  }
  
  async function getAccessToken(env: Env): Promise<string | null> {
    try {
      const sa: ServiceAccountKey = JSON.parse(env.GCP_SA_KEY);
      const cacheKey = new Request(`https://gcp-token-cache.drivewayzusa.co/${sa.client_email}`);
      const cache = caches.default;
      const cached = await cache.match(cacheKey);
      if (cached) return await cached.text();
  
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
  
  export const onRequest: PagesFunction<Env> = async (context) => {
    const { request, env, next } = context;
    const response = await next();
  
    const url = new URL(request.url);
    const ASSET_RE = /\.(css|js|woff2?|ttf|otf|png|jpe?g|gif|svg|webp|ico|map|txt|xml|json)$/i;
    if (ASSET_RE.test(url.pathname) || url.pathname === "/favicon.ico") {
      return response;
    }
  
    const ua = request.headers.get("user-agent") || "";
    const aiBot     = detectAiBot(ua);
    const searchBot = detectSearchBot(ua);
  
    const row = {
      timestamp:   new Date().toISOString(),
      url:         url.pathname + (url.search || ""),
      method:      request.method,
      status:      response.status,
      user_agent:  ua.slice(0, 500),
      ai_bot:      aiBot,
      search_bot:  searchBot,
      is_bot:      !!(aiBot || searchBot),
      device_type: detectDeviceType(ua),
      client_ip:   request.headers.get("CF-Connecting-IP") || "",
      country:     (request.cf as any)?.country || "",
      referer:     (request.headers.get("referer") || "").slice(0, 500),
      bytes_sent:  parseInt(response.headers.get("content-length") || "0", 10) || 0,
    };
  
    context.waitUntil(streamToBigQuery(env, row));
  
    return response;
  };