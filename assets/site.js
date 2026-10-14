// Shared page behaviour for fands.io: menu, type reveals, the workflow demo, the estimator, forms and film loops.
(function () {
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var ICON = {
    arrowRight: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>',
    check: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>',
    checkSm: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>',
    layers: '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"/><path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/></svg>',
    shield: '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/></svg>',
    reset: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>'
  };
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  /* menu: the plus opens a panel; Escape closes it and returns focus */
  var toggle = $('.menu-toggle'), panel = $('#site-menu');
  if (toggle && panel) {
    var setOpen = function (open) {
      panel.hidden = !open;
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
      $('.ico-plus', toggle).hidden = open; $('.ico-x', toggle).hidden = !open;
    };
    toggle.addEventListener('click', function () { setOpen(panel.hidden); });
    $$('a', panel).forEach(function (a) { a.addEventListener('click', function () { setOpen(false); }); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !panel.hidden) { setOpen(false); toggle.focus(); } });
  }

  /* type arrives as it scrolls in */
  if (!reduce && 'IntersectionObserver' in window) {
    var ro = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('is-seen'); ro.unobserve(e.target); } }); }, { threshold: .13 });
    $$('[data-reveal]').forEach(function (el) { ro.observe(el); });
  }

  /* film loops play only while on screen */
  var films = $$('.film video');
  if (films.length && 'IntersectionObserver' in window) {
    var fo = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { if (!reduce) e.target.play().catch(function () {}); } else e.target.pause(); }); }, { threshold: .2 });
    films.forEach(function (v) { fo.observe(v); });
  }

  /* workflow demo: synthetic inputs, a draft, a human approval */
  var lab = $('.workflow-lab');
  if (lab) {
    var examples = [
      { label: 'Client intake', title: 'An email becomes a useful brief.', input: '“We need a customer research sprint. Six interviews, findings by the 28th. Can you send a kickoff plan?”', fields: [['Service', 'Customer research'], ['Scope', '6 interviews + findings'], ['Due date', '28th — month to confirm']], output: 'Draft intake brief', review: 'Confirm the month and agree the scope before creating a project.', metric: 'Minutes spent preparing each brief' },
      { label: 'Project kickoff', title: 'An approved scope becomes a ready team.', input: 'Approved scope: discovery workshop, research synthesis, and a recommendations session. Project owner: Operations.', fields: [['Workstreams', 'Discovery / Research / Recommendations'], ['Owner', 'Operations'], ['Next step', 'Confirm dates and team availability']], output: 'Draft kickoff pack', review: 'A project owner reviews responsibilities and dates before tasks are created.', metric: 'Time from approved scope to kickoff' },
      { label: 'Delivery updates', title: 'Scattered progress becomes a clear update.', input: 'Workshop completed. Three interviews remaining. Analysis waiting for the client data export.', fields: [['Completed', 'Discovery workshop'], ['In progress', '3 remaining interviews'], ['Blocked', 'Client data export']], output: 'Draft status update', review: 'An account lead checks the update and source context before sending.', metric: 'Time spent preparing and checking updates' }
    ];
    var tabs = $$('[role=tab]', lab), body = $('#workflow-example', lab), choice = 0, stage = 0;
    var draw = function () {
      var x = examples[choice];
      tabs.forEach(function (t, i) { t.setAttribute('aria-selected', String(i === choice)); t.tabIndex = i === choice ? 0 : -1; });
      body.setAttribute('aria-labelledby', 'workflow-tab-' + choice);
      $('.lab-copy h3', body).textContent = x.title;
      $('.lab-metric strong', body).textContent = x.metric;
      $('.machine-status', body).textContent = stage === 0 ? 'Ready to process' : stage === 1 ? 'Ready for review' : 'Approved in this demo';
      $('.source-note', body).classList.toggle('processed', stage > 0);
      $('.source-note p', body).textContent = x.input;
      var slot = $('.machine-slot', body);
      if (stage === 0) {
        slot.innerHTML = '<div class="machine-idle">' + ICON.layers + '<p>A structured draft starts here.</p><button type="button" class="button ink" data-go="1">Run the example ' + ICON.arrowRight + '</button></div>';
      } else {
        slot.innerHTML = '<div class="machine-result" aria-live="polite"><div class="result-title"><strong>' + esc(x.output) + '</strong>' + (stage === 2 ? '<span class="approved">' + ICON.checkSm + 'Approved</span>' : '<span>Awaiting review</span>') + '</div><dl>' +
          x.fields.map(function (f) { return '<div><dt>' + esc(f[0]) + '</dt><dd>' + esc(f[1]) + '</dd></div>'; }).join('') +
          '</dl><p class="review-note">' + ICON.shield + esc(x.review) + '</p>' +
          (stage === 1 ? '<button type="button" class="button ink" data-go="2">Approve this demo ' + ICON.check + '</button>' : '<button type="button" class="reset-button" data-go="0">Reset example ' + ICON.reset + '</button>') + '</div>';
      }
    };
    lab.addEventListener('click', function (e) {
      var go = e.target.closest('[data-go]'); if (go) { stage = +go.dataset.go; draw(); var nb = $('.machine-slot button', body); if (nb) nb.focus(); return; }
      var t = e.target.closest('[role=tab]'); if (t) { choice = tabs.indexOf(t); stage = 0; draw(); }
    });
    lab.addEventListener('keydown', function (e) {
      var t = e.target.closest('[role=tab]'); if (!t) return;
      var i = tabs.indexOf(t), n = i;
      if (e.key === 'ArrowRight') n = (i + 1) % tabs.length; else if (e.key === 'ArrowLeft') n = (i + tabs.length - 1) % tabs.length; else if (e.key === 'Home') n = 0; else if (e.key === 'End') n = tabs.length - 1; else return;
      e.preventDefault(); choice = n; stage = 0; draw(); tabs[n].focus();
    });
    draw();
  }

  /* estimator: volume × minutes ÷ 60 × assumed reduction */
  var calc = $('.calc-panel');
  if (calc) {
    var v = $('#volume'), m = $('#minutes'), r = $('#reduction'), out = $('#calc-hours');
    var upd = function () {
      $('#volume-v').textContent = v.value; $('#minutes-v').textContent = m.value; $('#reduction-v').textContent = r.value + '%';
      out.textContent = (v.value * m.value / 60 * r.value / 100).toFixed(1);
    };
    [v, m, r].forEach(function (el) { el.addEventListener('input', upd); }); upd();
  }

  /* forms: post to /api/lead; if the hand-off is unavailable, open a prefilled email so nothing is lost */
  var interest = new URLSearchParams(location.search).get('interest');
  var sel = $('#interest'); if (sel && interest && /^(diagnostic|pilot|care)$/.test(interest)) sel.value = interest;
  $$('form[data-lead]').forEach(function (f) {
    var newsletter = f.dataset.lead === 'newsletter', btn = $('button', f), ok = $('.feedback', f), err = $('.feedback.error', f);
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!f.checkValidity()) { f.reportValidity(); return; }
      var d = {}; new FormData(f).forEach(function (val, k) { d[k] = String(val).trim(); });
      d.kind = newsletter ? 'newsletter' : 'inquiry'; d.source = location.pathname;
      var label = btn.textContent; btn.disabled = true; btn.textContent = 'Sending…'; ok.textContent = ''; err.hidden = true;
      var mail = newsletter
        ? 'mailto:hello@fands.io?subject=' + encodeURIComponent('Field Notes: please add me') + '&body=' + encodeURIComponent('Please add ' + d.email + ' to Fands Field Notes.')
        : 'mailto:hello@fands.io?subject=' + encodeURIComponent('Workflow review: ' + (d.company || '')) + '&body=' + encodeURIComponent('Name: ' + d.name + '\nCompany: ' + d.company + '\nEmail: ' + d.email + '\nStarting point: ' + d.interest + '\n\nThe handoff slowing us down:\n' + d.workflow);
      fetch('/api/lead', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(d) })
        .then(function (res) { return res.ok ? res.json() : Promise.reject(res.status); })
        .then(function (j) {
          if (!j.ok) throw 0;
          ok.textContent = newsletter ? 'You’re on the list. The first note arrives on a Tuesday.' : 'Got it. We’ll reply within two business days.';
          f.reset(); btn.disabled = false; btn.textContent = label;
        })
        .catch(function () { btn.disabled = false; btn.textContent = label; err.hidden = false; location.href = mail; });
    });
  });
})();
