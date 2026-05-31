/**
 * Drivewayz USA — DEBUG VERSION of Pages Middleware
 *
 * Same logic as production, but on requests with `?_dbg=1` query param,
 * it returns a JSON payload with diagnostic info INSTEAD of the page.
 * This lets us see exactly what's failing in the BigQuery write path
 * without needing log access.
 *
 * Once we confirm the pipeline works, REPLACE THIS with _middleware.ts (no debug).
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
  function detectAiBot(ua: string): string | null { for (const {name,match} of AI_BOTS) if (match.test(ua)) return name; return null; }
  function detectSearchBot(ua: string): string | null { for (const {name,match} of SEARCH_BOTS) if (match.test(ua)) return name; return null; }
  function detectDeviceType(ua: string): string {
    if (/Mobile|iPhone|Android.*Mobile|Windows Phone|iPod/i.test(ua)) return "mobile";
    if (/iPad|Tablet|Android(?!.*Mobile)/i.test(ua)) return "tablet";
    if (/Mozilla|Chrome|Safari|Firefox|Edge|MSIE|Trident|bot|spider|crawler/i.test(ua)) return "desktop";
    return "unknown";
  }
  
  interface SAKey { client_email: string; private_key: string; token_uri: string; project_id: string; }
  
  async function getAccessToken(env: Env): Promise<{ token: string|null; error: string|null }> {
    try {
      if (!env.GCP_SA_KEY) return { token: null, error: "GCP_SA_KEY env var is empty or undefined" };
      let sa: SAKey;
      try { sa = JSON.parse(env.GCP_SA_KEY); }
      catch (e: any) { return { token: null, error: `JSON.parse failed: ${e.message}. First 100 chars: ${env.GCP_SA_KEY.slice(0,100)}` }; }
  
      const now = Math.floor(Date.now() / 1000);
      const header = { alg: "RS256", typ: "JWT" };
      const claim = { iss: sa.client_email, scope: "https://www.googleapis.com/auth/bigquery.insertdata", aud: sa.token_uri, exp: now + 3600, iat: now };
      const enc = (o: object) => btoa(JSON.stringify(o)).replace(/=+$/,"").replace(/\+/g,"-").replace(/\//g,"_");
      const toSign = `${enc(header)}.${enc(claim)}`;
  
      let cryptoKey;
      try {
        const pem = sa.private_key.replace(/-----[^-]+-----/g, "").replace(/\s+/g, "");
        const keyBytes = Uint8Array.from(atob(pem), c => c.charCodeAt(0));
        cryptoKey = await crypto.subtle.importKey("pkcs8", keyBytes, { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, false, ["sign"]);
      } catch (e: any) {
        return { token: null, error: `crypto.subtle.importKey failed: ${e.message}` };
      }
  
      let sig;
      try {
        sig = new Uint8Array(await crypto.subtle.sign("RSASSA-PKCS1-v1_5", cryptoKey, new TextEncoder().encode(toSign)));
      } catch (e: any) {
        return { token: null, error: `crypto.subtle.sign failed: ${e.message}` };
      }
  
      const sigB64 = btoa(String.fromCharCode(...sig)).replace(/=+$/,"").replace(/\+/g,"-").replace(/\//g,"_");
      const jwt = `${toSign}.${sigB64}`;
  
      const tokenRes = await fetch(sa.token_uri, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: `grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion=${jwt}`,
      });
      if (!tokenRes.ok) return { token: null, error: `OAuth POST returned ${tokenRes.status}: ${await tokenRes.text()}` };
      const data = await tokenRes.json() as { access_token?: string };
      if (!data.access_token) return { token: null, error: `OAuth response had no access_token: ${JSON.stringify(data)}` };
      return { token: data.access_token, error: null };
    } catch (e: any) {
      return { token: null, error: `Outer catch: ${e.message}` };
    }
  }
  
  async function streamToBigQuery(env: Env, row: Record<string, any>): Promise<{ ok: boolean; error: string|null }> {
    const { token, error } = await getAccessToken(env);
    if (!token) return { ok: false, error };
    const url = "https://bigquery.googleapis.com/bigquery/v2/projects/drivewayz-logs/datasets/drivewayz/tables/raw_logs/insertAll";
    const res = await fetch(url, {
      method: "POST",
      headers: { "Authorization": `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify({ skipInvalidRows: true, ignoreUnknownValues: true, rows: [{ json: row }] }),
    });
    if (!res.ok) return { ok: false, error: `BQ insert ${res.status}: ${await res.text()}` };
    const body = await res.json() as any;
    if (body.insertErrors) return { ok: false, error: `BQ insertErrors: ${JSON.stringify(body.insertErrors)}` };
    return { ok: true, error: null };
  }
  
  export const onRequest: PagesFunction<Env> = async (context) => {
    const { request, env, next } = context;
    const url = new URL(request.url);
    const isDebug = url.searchParams.has("_dbg");
  
    // ────────── DEBUG MODE ──────────
    // Run the BigQuery insert synchronously and return the result as JSON.
    if (isDebug) {
      const ua = request.headers.get("user-agent") || "";
      const aiBot = detectAiBot(ua), searchBot = detectSearchBot(ua);
      const row = {
        timestamp: new Date().toISOString(),
        url: url.pathname + (url.search || ""),
        method: request.method, status: 200,
        user_agent: ua.slice(0, 500),
        ai_bot: aiBot, search_bot: searchBot, is_bot: !!(aiBot || searchBot),
        device_type: detectDeviceType(ua),
        client_ip: request.headers.get("CF-Connecting-IP") || "",
        country: (request.cf as any)?.country || "",
        referer: (request.headers.get("referer") || "").slice(0, 500),
        bytes_sent: 0,
      };
      const result = await streamToBigQuery(env, row);
      return new Response(JSON.stringify({
        debug: true,
        env_key_present: !!env.GCP_SA_KEY,
        env_key_length: env.GCP_SA_KEY ? env.GCP_SA_KEY.length : 0,
        row_attempted: row,
        bq_insert_ok: result.ok,
        bq_insert_error: result.error,
      }, null, 2), {
        headers: { "content-type": "application/json", "cache-control": "no-store" },
        status: 200,
      });
    }
  
    // ────────── NORMAL MODE ──────────
    const response = await next();
    const ASSET_RE = /\.(css|js|woff2?|ttf|otf|png|jpe?g|gif|svg|webp|ico|map|txt|xml|json)$/i;
    if (ASSET_RE.test(url.pathname) || url.pathname === "/favicon.ico") return response;
  
    const ua = request.headers.get("user-agent") || "";
    const aiBot = detectAiBot(ua), searchBot = detectSearchBot(ua);
    const row = {
      timestamp: new Date().toISOString(),
      url: url.pathname + (url.search || ""),
      method: request.method, status: response.status,
      user_agent: ua.slice(0, 500),
      ai_bot: aiBot, search_bot: searchBot, is_bot: !!(aiBot || searchBot),
      device_type: detectDeviceType(ua),
      client_ip: request.headers.get("CF-Connecting-IP") || "",
      country: (request.cf as any)?.country || "",
      referer: (request.headers.get("referer") || "").slice(0, 500),
      bytes_sent: parseInt(response.headers.get("content-length") || "0", 10) || 0,
    };
    context.waitUntil(streamToBigQuery(env, row));
    return response;
  };