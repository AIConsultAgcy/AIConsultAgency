// Lead capture for fands.io. Receives the workflow-review, Field Notes and privacy-request forms, validates them,
// filters obvious spam and forwards them to the configured Google Apps Script Web App.
const MAX = { name: 120, company: 200, email: 254, interest: 40, workflow: 2000, source: 120, request: 80, state: 40 };
const INTEREST = { diagnostic: 'Workflow diagnostic', pilot: 'Workflow pilot', care: 'Ongoing system care', unsure: 'Help me find the right starting point' };
const REQUESTS = ['Delete my personal information', 'Tell me what personal information you hold', 'Correct my personal information', 'Stop sale or sharing and all marketing'];
const MIN_FILL_MS = 2500; // humans take longer than this to fill a form; most bots do not

function clean(v, max) { return String(v || '').replace(/[\u0000-\u001f]+/g, ' ').trim().slice(0, max); }
function send(res, code, body) { res.statusCode = code; res.setHeader('Content-Type', 'application/json'); return res.end(JSON.stringify(body)); }
function looksLikeSpam(text) { return (text.match(/https?:\/\//gi) || []).length > 3 || /<a\s|\[url=/i.test(text); }

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method !== 'POST') return send(res, 405, { ok: false, error: 'method' });
  let body = req.body;
  if (typeof body === 'string') { try { body = JSON.parse(body); } catch (e) { body = {}; } }
  body = body || {};
  // honeypot filled, or the form was submitted faster than a person could: pretend success so bots learn nothing
  if (body.website || (Number(body.elapsed) > 0 && Number(body.elapsed) < MIN_FILL_MS)) return send(res, 200, { ok: true });
  const kind = ['newsletter', 'privacy'].includes(body.kind) ? body.kind : 'inquiry';
  const lead = {
    name: clean(body.name, MAX.name), company: clean(body.company, MAX.company), email: clean(body.email, MAX.email),
    interest: INTEREST[clean(body.interest, MAX.interest)] || '', workflow: clean(body.workflow || body.details, MAX.workflow), source: clean(body.source, MAX.source),
    request: REQUESTS.includes(clean(body.request, MAX.request)) ? clean(body.request, MAX.request) : '', state: clean(body.state, MAX.state),
  };
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(lead.email) || body.consent !== 'yes') return send(res, 400, { ok: false, error: 'fields' });
  if (kind === 'inquiry' && (!lead.name || !lead.company || lead.workflow.length < 10)) return send(res, 400, { ok: false, error: 'fields' });
  if (kind === 'privacy' && (!lead.name || !lead.request)) return send(res, 400, { ok: false, error: 'fields' });
  if (looksLikeSpam(lead.workflow) || looksLikeSpam(lead.name) || looksLikeSpam(lead.company)) return send(res, 200, { ok: true });
  const endpoint = process.env.GOOGLE_APPS_SCRIPT_URL;
  if (!endpoint) return send(res, 503, { ok: false, error: 'transport' });
  const workflow = kind === 'newsletter' ? 'Field Notes subscription request.'
    : kind === 'privacy' ? `PRIVACY REQUEST: ${lead.request}\nState: ${lead.state || 'not given'}\n\n${lead.workflow}` : lead.workflow;
  const payload = {
    kind: kind === 'privacy' ? 'inquiry' : kind === 'newsletter' ? 'newsletter' : 'inquiry',
    form: { name: lead.name, company: kind === 'privacy' ? 'Privacy request' : lead.company, email: lead.email, interest: kind === 'privacy' ? lead.request : lead.interest, workflow, source: lead.source },
  };
  try {
    const r = await fetch(endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify(payload), redirect: 'follow' });
    const j = await r.json().catch(() => ({}));
    if (!r.ok || j.ok !== true) return send(res, 502, { ok: false, error: 'upstream' });
    return send(res, 200, { ok: true });
  } catch (e) { return send(res, 502, { ok: false, error: 'upstream' }); }
};
