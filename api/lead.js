// Lead capture for fands.io. Receives the workflow-review and Field Notes forms, validates them,
// and forwards them to the configured Google Apps Script Web App.
const MAX = { name: 120, company: 200, email: 254, interest: 40, workflow: 2000, source: 120 };
const INTEREST = { diagnostic: 'Workflow diagnostic', pilot: 'Workflow pilot', care: 'Ongoing system care', unsure: 'Help me find the right starting point' };

function clean(v, max) { return String(v || '').replace(/[\u0000-\u001f]+/g, ' ').trim().slice(0, max); }
function send(res, code, body) { res.statusCode = code; res.setHeader('Content-Type', 'application/json'); return res.end(JSON.stringify(body)); }

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method !== 'POST') return send(res, 405, { ok: false, error: 'method' });
  let body = req.body;
  if (typeof body === 'string') { try { body = JSON.parse(body); } catch (e) { body = {}; } }
  body = body || {};
  if (body.website) return send(res, 200, { ok: true }); // honeypot: pretend success
  const newsletter = body.kind === 'newsletter';
  const lead = {
    name: clean(body.name, MAX.name), company: clean(body.company, MAX.company), email: clean(body.email, MAX.email),
    interest: INTEREST[clean(body.interest, MAX.interest)] || '', workflow: clean(body.workflow, MAX.workflow), source: clean(body.source, MAX.source),
  };
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(lead.email) || body.consent !== 'yes') return send(res, 400, { ok: false, error: 'fields' });
  if (!newsletter && (!lead.name || !lead.company || lead.workflow.length < 10)) return send(res, 400, { ok: false, error: 'fields' });
  const endpoint = process.env.GOOGLE_APPS_SCRIPT_URL;
  if (!endpoint) return send(res, 503, { ok: false, error: 'transport' });
  const payload = {
    kind: newsletter ? 'newsletter' : 'inquiry',
    form: {
      name: lead.name,
      company: lead.company,
      email: lead.email,
      interest: lead.interest,
      workflow: newsletter ? 'Field Notes subscription request.' : lead.workflow,
      source: lead.source,
    },
  };
  try {
    const r = await fetch(endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify(payload), redirect: 'follow' });
    const j = await r.json().catch(() => ({}));
    if (!r.ok || j.ok !== true) return send(res, 502, { ok: false, error: 'upstream' });
    return send(res, 200, { ok: true });
  } catch (e) { return send(res, 502, { ok: false, error: 'upstream' }); }
};
