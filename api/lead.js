// Lead capture for fands.io. Receives the walk-through form, validates it, and forwards it by email.
// Transport: Web3Forms (WEB3FORMS_KEY env var). Without a key the function answers 503 and the page
// falls back to a prefilled email to hello@fands.io, so nothing is lost either way.
const MAX = { name: 120, business: 200, email: 200, phone: 40, pain: 2000 };

function clean(v, max) { return String(v || '').replace(/[\u0000-\u001f]+/g, ' ').trim().slice(0, max); }

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method !== 'POST') { res.statusCode = 405; return res.end(JSON.stringify({ ok: false, error: 'method' })); }
  let body = req.body;
  if (typeof body === 'string') { try { body = JSON.parse(body); } catch (e) { body = {}; } }
  body = body || {};
  if (body.company) { res.statusCode = 200; return res.end(JSON.stringify({ ok: true })); } // honeypot: pretend success
  const lead = {
    name: clean(body.name, MAX.name), business: clean(body.business, MAX.business),
    email: clean(body.email, MAX.email), phone: clean(body.phone, MAX.phone), pain: clean(body.pain, MAX.pain),
  };
  if (!lead.name || !lead.business || !(lead.email || lead.phone)) { res.statusCode = 400; return res.end(JSON.stringify({ ok: false, error: 'fields' })); }
  if (lead.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(lead.email)) { res.statusCode = 400; return res.end(JSON.stringify({ ok: false, error: 'email' })); }
  const key = process.env.WEB3FORMS_KEY;
  if (!key) { res.statusCode = 503; return res.end(JSON.stringify({ ok: false, error: 'transport' })); }
  const ua = req.headers['user-agent'] || '';
  const payload = {
    access_key: key,
    subject: 'Walk-through request: ' + lead.business,
    from_name: 'fands.io',
    replyto: lead.email || undefined,
    name: lead.name, business: lead.business, email: lead.email, phone: lead.phone,
    message: lead.pain || '(no details given)',
    page: 'https://fands.io', user_agent: ua.slice(0, 200),
  };
  try {
    const r = await fetch('https://api.web3forms.com/submit', { method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify(payload) });
    const j = await r.json().catch(() => ({}));
    if (!r.ok || !j.success) { res.statusCode = 502; return res.end(JSON.stringify({ ok: false, error: 'upstream' })); }
    res.statusCode = 200; return res.end(JSON.stringify({ ok: true }));
  } catch (e) { res.statusCode = 502; return res.end(JSON.stringify({ ok: false, error: 'upstream' })); }
};
