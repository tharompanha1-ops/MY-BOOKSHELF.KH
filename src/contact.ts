/**
 * MY BOOKSHELF — Contact form endpoint (TypeScript, serverless).
 *
 * Receives the contact-form payload and forwards it to Telegram.
 *
 * SECURITY: The Telegram bot token and chat id are read from
 * environment variables and NEVER appear in client-side code.
 *
 * Required environment variables (set in your deployment platform):
 *   TELEGRAM_BOT_TOKEN  — bot token from @BotFather
 *   TELEGRAM_CHAT_ID    — target chat/channel id
 *
 * Deploy as a serverless function (e.g. Vercel, Netlify, Cloudflare)
 * at the /api/contact route. Expects POST with JSON:
 *   { name, email, subject, message }
 */

interface ContactPayload {
  name?: string;
  email?: string;
  subject?: string;
  message?: string;
}

interface ApiResponse {
  ok: boolean;
  error?: string;
}

const TELEGRAM_API = "https://api.telegram.org";

function json(status: number, body: ApiResponse): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8" },
  });
}

export default async function handler(req: Request): Promise<Response> {
  // Only accept POST with JSON
  if (req.method !== "POST") {
    return json(405, { ok: false, error: "Method not allowed" });
  }

  let payload: ContactPayload;
  try {
    const raw = await req.text();
    payload = JSON.parse(raw || "{}") as ContactPayload;
  } catch {
    return json(400, { ok: false, error: "Invalid JSON" });
  }

  const name = String(payload.name ?? "").slice(0, 120);
  const email = String(payload.email ?? "").slice(0, 160);
  const subject = String(payload.subject ?? "").slice(0, 200);
  const message = String(payload.message ?? "").slice(0, 4000);

  if (!name || !email || !message) {
    return json(400, { ok: false, error: "Missing required fields" });
  }

  const token = process.env.TELEGRAM_BOT_TOKEN;
  const chatId = process.env.TELEGRAM_CHAT_ID;

  if (!token || !chatId) {
    // Misconfiguration must never leak details to the client.
    console.error(
      "Contact endpoint: TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID not set",
    );
    return json(500, { ok: false, error: "Server is not configured" });
  }

  const text =
    "📩 **សារថ្មីពីវេបសាយ MY BOOKSHELF**\n\n" +
    `👤 **ឈ្មោះ:** ${name}\n` +
    `📞 **ទំនាក់ទំនង:** ${email}\n` +
    `📌 **ប្រធានបទ:** ${subject}\n` +
    `💬 **សារ:** ${message}`;

  try {
    const res = await fetch(`${TELEGRAM_API}/bot${token}/sendMessage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        chat_id: chatId,
        text,
        parse_mode: "Markdown",
      }),
    });

    if (!res.ok) {
      const detail = await res.text().catch(() => "");
      console.error("Telegram send failed:", res.status, detail);
      return json(502, { ok: false, error: "Failed to deliver message" });
    }

    return json(200, { ok: true });
  } catch (err) {
    console.error("Telegram request error:", err);
    return json(500, { ok: false, error: "Failed to deliver message" });
  }
}
