/**
 * exposure-scope API Proxy (Vercel Serverless Function)
 * Forwards scan requests to the VPS HUNTER engine.
 */

const VPS_BACKEND = process.env.VPS_BACKEND_URL || 'http://srv1102669.hstgr.cloud:8115';

export default async function handler(req, res) {
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { target, type } = req.body || {};

  if (!target) {
    return res.status(400).json({ error: 'Target is required' });
  }

  try {
    const backendRes = await fetch(`${VPS_BACKEND}/api/scan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target, type: type || 'auto' }),
      signal: AbortSignal.timeout(60000),
    });

    const data = await backendRes.json();
    res.status(backendRes.status).json(data);
  } catch (err) {
    console.error('Backend error:', err.message);
    res.status(502).json({
      error: 'Backend unavailable',
      message: err.message,
    });
  }
}
