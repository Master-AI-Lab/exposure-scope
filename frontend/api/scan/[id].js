/**
 * exposure-scope — Get scan results by ID
 */

const VPS_BACKEND = process.env.VPS_BACKEND_URL || 'http://31.97.71.196:8115';

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');

  const { id } = req.query;

  if (!id) {
    return res.status(400).json({ error: 'Scan ID is required' });
  }

  try {
    const backendRes = await fetch(`${VPS_BACKEND}/api/scan/${id}`, {
      signal: AbortSignal.timeout(30000),
    });

    const data = await backendRes.json();
    res.status(backendRes.status).json(data);
  } catch (err) {
    res.status(502).json({
      error: 'Backend unavailable',
      message: err.message,
    });
  }
}
