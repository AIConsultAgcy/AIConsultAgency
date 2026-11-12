// Shared page behaviour for fands.io: menu, reveals, film loops, workflow demo, forms, consent, privacy choices and analytics events.
(function () {
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var track = function (event, params) {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push(Object.assign({ event: event }, params || {}));
  };
  var ICON = {
    arrowRight: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>',
    check: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>',
    checkSm: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>',
    layers: '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"/><path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/></svg>',
    shield: '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/></svg>',
    reset: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>'
  };
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  /* analytics: funnel events are sent to GTM; GA4 tags are configured in the container */
  document.addEventListener('click', function (e) {
    var link = e.target.closest('a[href]');
    if (!link) return;
    var href = link.href || '', text = (link.getAttribute('data-track') || link.getAttribute('aria-label') || link.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 120);
    if (/^(mailto|tel):/i.test(href)) return; // email clicks are reported as email_click below
    var isOutbound = link.origin && link.origin !== location.origin;
    var isCal = link.hasAttribute('data-cal-link') || /cal\.com/i.test(href) || /book a (free )?call/i.test(text);
    if (isCal) track('cal_open', { link_text: text, link_url: href, page_section: (link.closest('section,footer,header') || {}).className || '' });
    else if (isOutbound) track('outbound_click', { link_text: text, link_url: href });
    else if (link.matches('.button, .arrow-link, .text-link, .closing-link, .header-contact, .hub-card, .case-card, .related a, .leaks a, .lab-service, .link-btn')) track('cta_click', { link_text: text, link_url: href });
  }, { passive: true });

  /* booking links open the Cal popup in place; without Cal they fall through to /contact */
  document.addEventListener('click', function (e) { if (e.target.closest('a[data-cal-link]') && window.Cal && window.Cal.loaded) e.preventDefault(); });

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

  /* home services on phones: each practice starts collapsed with a "Show N services" button.
     The list stays in the page for search engines; CSS hides it only on small screens. */
  $$('.services .pillar').forEach(function (p, i) {
    var list = $('.svc-list', p), head = $('header', p); if (!list || !head) return;
    var n = $$('article', list).length, id = 'pillar-list-' + i;
    list.id = id; p.classList.add('can-collapse');
    var b = document.createElement('button');
    b.type = 'button'; b.className = 'pillar-toggle'; b.setAttribute('aria-controls', id); b.setAttribute('aria-expanded', 'false');
    var label = function (open) { return (open ? 'Hide services' : 'Show ' + n + ' service' + (n > 1 ? 's' : '')) + ' <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>'; };
    b.innerHTML = label(false);
    b.addEventListener('click', function () { var open = !p.classList.contains('open'); p.classList.toggle('open', open); b.setAttribute('aria-expanded', String(open)); b.innerHTML = label(open); });
    head.appendChild(b);
    // a link to one of this practice's services (#svc-...) opens it
    if (location.hash && list.querySelector(location.hash.replace(/[^#\w-]/g, ''))) b.click();
  });

  /* workflow demo: synthetic inputs, a draft, a human approval */
  var lab = $('.workflow-lab');
  if (lab) {
    // Each example: what arrives, the steps the system takes, the draft it produces, who approves, and a before/after.
    var examples = [
      { title: 'An inbox of invoices becomes clean books.', desc: 'Business process automation reads each invoice, matches it and drafts the entry for review.', source: 'Email with PDF attached', input: '“Invoice 4471 for October supplies, net 30. Reference PO 2291.”',
        steps: ['PDF read and fields extracted', 'Vendor matched to existing supplier', 'Purchase order 2291 checked', 'Bill entry drafted, not posted'],
        fields: [['Vendor', 'Matched to an existing supplier'], ['Amount', '$1,840.00, due in 30 days'], ['Check', 'PO 2291 found, quantities agree']], output: 'Draft bill entry', review: 'Finance approves before anything posts. Mismatches are flagged for a person.',
        before: 'Typed in by hand, one by one', after: 'Checked and approved in one click', metric: 'Minutes of handling per invoice', service: ['Business Process Automation', '/services/ai-operations#business-process-automation'] },
      { title: 'A weekend inquiry gets a reply in minutes.', desc: 'Lead-to-revenue automation replies right away, files the lead and schedules the follow-up.', source: 'Web form · Saturday 9:14 am', input: '“Looking for a quote on a kitchen remodel, about 200 square feet. Budget around $40K.”',
        steps: ['Inquiry captured from the website', 'Project, size and budget extracted', 'Lead created in the CRM pipeline', 'Personal first reply drafted'],
        fields: [['Lead', 'Kitchen remodel, 200 sq ft, ~$40K'], ['Reply', 'Text + email with two call times'], ['Pipeline', 'New lead, quote stage, follow-up set']], output: 'Draft first reply', review: 'The owner approves the first replies until the tone is right.',
        before: 'Reply on Monday, if remembered', after: 'Reply in under 5 minutes', metric: 'Minutes from inquiry to first reply', service: ['Lead-to-Revenue Automation', '/services/ai-operations#lead-to-revenue-automation'] },
      { title: 'One note becomes a week of content.', desc: 'The AI content engine turns a short brief into posts, an email and ads in your brand voice.', source: 'Owner note · Monday', input: '“We’re running a spring facial promo: 20% off through April. Let’s push it this week.”',
        steps: ['Brief read against the brand voice guide', 'Week planned across channels', 'Posts, email and ads drafted', 'Calendar queued for approval'],
        fields: [['Social', '3 posts + 1 short video script'], ['Email', 'Promo email to past clients'], ['Ads', '2 Meta ad variants']], output: 'Content week drafted', review: 'The owner approves the calendar before anything is published.',
        before: 'One post, if there’s time', after: 'A full week queued in one approval', metric: 'Pieces published on schedule', service: ['AI Content Engine', '/services/media-growth#ai-content-engine'] },
      { title: 'A buyer asks AI who to hire.', desc: 'AI search visibility checks how assistants answer today and drafts the fixes that help you get cited.', source: 'Question to an AI assistant', input: '“Who is the best HVAC repair company near Pasadena?”',
        steps: ['AI answers checked across assistants', 'Competitors that get cited identified', 'Missing signals found on your profile', 'Visibility fixes drafted'],
        fields: [['Today', 'Two competitors cited, you are not'], ['Gaps', 'Incomplete Google profile, no service FAQ'], ['Fixes', 'Profile update, schema, 3 answer pages']], output: 'Visibility plan drafted', review: 'You approve every page and profile change before it goes live.',
        before: 'Not mentioned in AI answers', after: 'Fixes shipped, mentions tracked monthly', metric: 'Monthly AI citations for your business', service: ['AI Search Visibility', '/services/media-growth#ai-search-visibility'] },
      { title: 'A call after closing becomes a booking.', desc: 'The AI receptionist answers, checks the calendar and books. Your team sees a finished booking in the morning.', source: 'Phone call · 7:42 pm', input: '“Hi, do you have anything Thursday afternoon? It’s for a cleaning.”',
        steps: ['Call answered and transcribed', 'Request understood: cleaning, Thursday pm', 'Calendar checked against booking rules', 'Confirmation text drafted'],
        fields: [['Caller needs', 'Cleaning, Thursday afternoon'], ['Offered', 'Thursday 2:30 pm, accepted'], ['Next step', 'Text confirmation + CRM record']], output: 'Booking drafted', review: 'Requests outside your booking rules go to a named person with the full transcript.',
        before: 'Voicemail until 9 am the next day', after: 'Booked during the call', metric: 'After-hours calls answered and booked', service: ['AI Receptionist', '/services/ai-assistants#ai-receptionist'] }
    ];
    // stage: 0 ready, 1 processing, 2 awaiting review, 3 approved
    var tabs = $$('[role=tab]', lab), body = $('#workflow-example', lab), choice = 0, stage = 0, timer = 0, run = 0;
    var stepsHtml = function (x, done) {
      return '<ol class="machine-steps">' + x.steps.map(function (s, i) {
        var st = i < done ? 'done' : i === done ? 'active' : '';
        return '<li class="' + st + '"><i>' + (i < done ? ICON.checkSm : '') + '</i>' + esc(s) + '</li>';
      }).join('') + '</ol>';
    };
    var draw = function () {
      var x = examples[choice];
      tabs.forEach(function (t, i) { t.setAttribute('aria-selected', String(i === choice)); t.tabIndex = i === choice ? 0 : -1; });
      body.setAttribute('aria-labelledby', 'workflow-tab-' + choice);
      $('.lab-copy h3', body).textContent = x.title;
      $('.lab-desc', body).textContent = x.desc;
      $('.lab-metric strong', body).textContent = x.metric;
      var sl = $('.lab-service', body); sl.href = x.service[1]; $('span', sl).textContent = x.service[0];
      $('.machine-status', body).textContent = ['Ready to process', 'Processing…', 'Ready for review', 'Approved in this demo'][stage];
      $('.source-note', body).classList.toggle('processed', stage > 0);
      $('.source-note span', body).textContent = x.source;
      $('.source-note p', body).textContent = x.input;
      var slot = $('.machine-slot', body);
      if (stage === 0) {
        slot.innerHTML = '<div class="machine-idle">' + ICON.layers + '<p>A structured draft starts here.</p><button type="button" class="button ink" data-go="1">Run the example ' + ICON.arrowRight + '</button></div>';
      } else if (stage === 1) {
        slot.innerHTML = '<div class="machine-result">' + stepsHtml(x, 0) + '</div>';
      } else {
        slot.innerHTML = '<div class="machine-result"><div class="result-title"><strong>' + esc(x.output) + '</strong>' + (stage === 3 ? '<span class="approved">' + ICON.checkSm + 'Approved</span>' : '<span>Awaiting review</span>') + '</div>' + stepsHtml(x, x.steps.length) + '<dl>' +
          x.fields.map(function (f) { return '<div><dt>' + esc(f[0]) + '</dt><dd>' + esc(f[1]) + '</dd></div>'; }).join('') +
          '</dl><p class="review-note">' + ICON.shield + esc(x.review) + '</p>' +
          (stage === 2 ? '<button type="button" class="button ink" data-go="3">Approve this demo ' + ICON.check + '</button>'
            : '<div class="compare"><div><span>Without the system</span><strong>' + esc(x.before) + '</strong></div><div class="on"><span>With the system</span><strong>' + esc(x.after) + '</strong></div></div><button type="button" class="reset-button" data-go="0">Reset example ' + ICON.reset + '</button>') + '</div>';
      }
      $('.machine-live', body).textContent = stage === 2 ? x.output + ', awaiting review.' : stage === 3 ? 'Approved.' : '';
    };
    // processing: tick the steps one by one, then show the draft. Reduced motion skips straight to the draft.
    var process = function () {
      var x = examples[choice], my = ++run, i = 0;
      if (reduce) { stage = 2; draw(); return; }
      var tick = function () {
        if (my !== run) return;
        i++;
        if (i > x.steps.length) { stage = 2; draw(); var b = $('.machine-slot button', body); if (b) b.focus(); return; }
        $('.machine-slot', body).innerHTML = '<div class="machine-result">' + stepsHtml(x, i) + '</div>';
        timer = setTimeout(tick, 520);
      };
      timer = setTimeout(tick, 420);
    };
    var go = function (n) {
      clearTimeout(timer); run++;
      stage = n; draw();
      if (n === 1) { process(); track('demo_run', { scenario: tabs[choice].textContent.trim() }); }
      else { var nb = $('.machine-slot button', body); if (nb) nb.focus(); }
    };
    lab.addEventListener('click', function (e) {
      var g = e.target.closest('[data-go]'); if (g) { go(+g.dataset.go); return; }
      var t = e.target.closest('[role=tab]'); if (t) { choice = tabs.indexOf(t); go(0); }
    });
    lab.addEventListener('keydown', function (e) {
      var t = e.target.closest('[role=tab]'); if (!t) return;
      var i = tabs.indexOf(t), n = i;
      if (e.key === 'ArrowRight') n = (i + 1) % tabs.length; else if (e.key === 'ArrowLeft') n = (i + tabs.length - 1) % tabs.length; else if (e.key === 'Home') n = 0; else if (e.key === 'End') n = tabs.length - 1; else return;
      e.preventDefault(); choice = n; go(0); tabs[n].focus(); tabs[n].scrollIntoView({ block: 'nearest', inline: 'nearest' });
    });
    draw();
  }

  /* floating booking button: lift it above the footer's last row so "Back to top" and legal links stay clear */
  var fab = $('.book-fab'), fb = $('.footer-bottom');
  if (fab && fb) {
    var lift = function () {
      var r = fb.getBoundingClientRect(), overlap = innerHeight - r.top;
      fab.style.transform = overlap > 0 ? 'translateY(' + (-Math.min(overlap, r.height + 12)) + 'px)' : '';
    };
    addEventListener('scroll', lift, { passive: true }); addEventListener('resize', lift); lift();
  }

  /* company film: swap the cover for the YouTube player on click (privacy-enhanced domain, autoplay once chosen) */
  $$('.film-player[data-yt]').forEach(function (box) {
    var btn = $('.film-cover', box); if (!btn) return;
    btn.addEventListener('click', function () {
      var id = box.getAttribute('data-yt'), f = document.createElement('iframe');
      f.src = 'https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1&rel=0&playsinline=1&modestbranding=1';
      f.title = box.getAttribute('data-title') || 'FANDS film';
      f.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
      f.setAttribute('allowfullscreen', ''); f.setAttribute('referrerpolicy', 'strict-origin-when-cross-origin');
      box.replaceChild(f, btn);
      track('video_play', { video_title: f.title, page_section: (box.closest('section') || {}).id || location.pathname });
    });
  });

  /* share button: opens the device's own share sheet; where there is none (most desktops), copies the link instead */
  $$('[data-share]').forEach(function (b) {
    b.addEventListener('click', function () {
      var url = location.origin + location.pathname; // clean address: no utm or other query tags
      // iPhone/iPad build a rich preview (site icon, title) only when the share holds the bare link; extra title/text
      // turns it into a plain text share with Safari's generic compass icon. Other systems get a title as well.
      var apple = /iP(hone|ad|od)/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
      var data = apple ? { url: url } : { title: 'FANDS — AI Systems & Media Agency', url: url };
      track('cta_click', { link_text: 'Share links page', link_url: url });
      if (navigator.share) { navigator.share(data).catch(function () {}); return; }
      var toast = $('.links-toast');
      var done = function (msg) { if (!toast) return; toast.textContent = msg; toast.hidden = false; clearTimeout(b._t); b._t = setTimeout(function () { toast.hidden = true; }, 2200); };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(data.url).then(function () { done('Link copied'); }, function () { done(data.url); });
      else done(data.url);
    });
  });

  /* legal switcher: on narrow screens it scrolls sideways, so bring the current document into view */
  var ln = $('.legal-nav'), cur = ln && $('[aria-current]', ln);
  if (cur && ln.scrollWidth > ln.clientWidth) ln.scrollLeft = cur.offsetLeft - (ln.clientWidth - cur.offsetWidth) / 2;

  /* privacy choices: analytics opt-out saved in this browser; a GPC signal always wins */
  var choice = $('[data-privacy-choice]');
  if (choice) {
    var sw = $('.switch', choice), status = $('.status', choice), gpc = !!navigator.globalPrivacyControl;
    var getOff = function () { try { return localStorage.getItem('fands-optout') === '1'; } catch (e) { return false; } };
    var paint = function () {
      var off = gpc || getOff();
      sw.setAttribute('aria-checked', String(!off)); $('span', sw).textContent = off ? 'Off' : 'On';
      sw.disabled = gpc;
      status.innerHTML = gpc ? 'Analytics is <b>off</b>: your browser sends a Global Privacy Control signal.' : off ? 'Analytics is <b>off</b> on this browser. You have opted out of sale and sharing.' : 'Analytics is on.';
    };
    sw.addEventListener('click', function () {
      window.fandsConsent(getOff() ? 'granted' : 'denied');
      var bn = $('.consent'); if (bn) { bn.hidden = true; document.documentElement.classList.remove('consent-open'); }
      paint();
    });
    paint();
  }

  /* forms: post to /api/lead; if the hand-off is unavailable, open a prefilled email so nothing is lost */
  var interest = new URLSearchParams(location.search).get('interest');
  var sel = $('#interest'); if (sel && interest && $$('option', sel).some(function (o) { return o.value === interest; })) sel.value = interest;
  // Three forms share one flow. Success and failure each show a clear notice; on failure the visitor gets a prefilled
  // email to send instead, so nothing is lost. Spam: a hidden honeypot field plus the time taken to fill the form.
  var FORMS = {
    inquiry: { name: 'workflow_inquiry', lead: 'workflow_review', ok: ['Request received.', 'Thanks — we’ll reply within two business days. Want to talk sooner? <a href="https://cal.com/fands/intro-call" data-cal-namespace="intro-call" data-cal-link="fands/intro-call">Book a free call</a>.'],
      mail: function (d) { var opt = $('#interest option:checked'); return ['Inquiry from ' + (d.company || 'the website'), 'Name: ' + d.name + '\nCompany: ' + d.company + '\nEmail: ' + d.email + (d.phone ? '\nPhone: ' + d.phone : '') + '\nService: ' + (opt ? opt.textContent : d.interest) + '\n\nWhere we are losing time or customers:\n' + d.workflow]; } },
    newsletter: { name: 'newsletter', lead: 'newsletter', ok: ['You’re on the list.', 'The first Field Note arrives on a Tuesday. You can unsubscribe from any email.'],
      mail: function (d) { return ['Field Notes: please add me', 'Please add ' + d.email + ' to Fands Field Notes.']; } },
    privacy: { name: 'privacy_request', lead: 'privacy_request', ok: ['Request received.', 'We’ll confirm within 10 business days and respond within 45 days. We may email you to verify your identity.'],
      mail: function (d) { return ['Privacy request: ' + d.request, 'Request: ' + d.request + '\nName: ' + d.name + '\nEmail: ' + d.email + '\nState: ' + d.state + '\n\nDetails:\n' + (d.details || '')]; } }
  };
  var ICO_OK = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/></svg>';
  var ICO_ERR = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M12 8v4"/><path d="M12 16h.01"/></svg>';
  $$('form[data-lead]').forEach(function (f) {
    var cfg = FORMS[f.dataset.lead] || FORMS.inquiry, btn = $('button[type=submit]', f), box = $('.form-notice', f);
    var started = false, opened = Date.now();
    var notice = function (kind, title, html) {
      box.className = 'form-notice ' + kind; box.setAttribute('role', kind === 'error' ? 'alert' : 'status');
      box.innerHTML = (kind === 'error' ? ICO_ERR : ICO_OK) + '<div><strong>' + title + '</strong><p>' + html + '</p></div>';
      box.scrollIntoView({ block: 'nearest', behavior: reduce ? 'auto' : 'smooth' });
    };
    f.addEventListener('focusin', function () { if (!started) { started = true; track('form_start', { form_name: cfg.name }); } });
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!f.checkValidity()) { f.reportValidity(); return; }
      var d = {}; new FormData(f).forEach(function (val, k) { d[k] = String(val).trim(); });
      d.kind = f.dataset.lead; d.source = location.pathname; d.elapsed = Date.now() - opened;
      var label = btn.innerHTML; btn.disabled = true; btn.textContent = 'Sending…'; box.className = 'form-notice'; box.innerHTML = '';
      var m = cfg.mail(d), mail = 'mailto:hello@fands.io?subject=' + encodeURIComponent(m[0]) + '&body=' + encodeURIComponent(m[1]);
      fetch('/api/lead', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(d) })
        .then(function (res) { return res.ok ? res.json() : Promise.reject(res.status); })
        .then(function (j) {
          if (!j.ok) throw 0;
          track('generate_lead', { form_name: cfg.name, lead_type: cfg.lead });
          notice('success', cfg.ok[0], cfg.ok[1]);
          f.reset(); opened = Date.now();
        })
        .catch(function () {
          track('form_error', { form_name: cfg.name });
          notice('error', 'We couldn’t send that.', 'Nothing was lost — your details are still in the form. <a href="' + esc(mail) + '">Send it by email instead</a>, or try again in a minute.');
        })
        .then(function () { btn.disabled = false; btn.innerHTML = label; });
    });
  });

  /* every email link reports a click, so GA4 can count contact intent */
  document.addEventListener('click', function (e) { var a = e.target.closest('a[href^="mailto:"]'); if (a) track('email_click', { link_url: a.getAttribute('href').split('?')[0] }); }, { passive: true });

  /* cookie consent: US notice-and-choice model. Analytics runs unless the visitor declines or sends Global Privacy Control.
     The choice is shared with /privacy-choices and read by the consent defaults in <head> on the next page. */
  var banner = $('.consent'), gpcOn = !!navigator.globalPrivacyControl;
  var stored = function () { try { return localStorage.getItem('fands-consent'); } catch (e) { return null; } };
  window.fandsConsent = function (v) {
    try { localStorage.setItem('fands-consent', v); if (v === 'granted') localStorage.removeItem('fands-optout'); else localStorage.setItem('fands-optout', '1'); } catch (e) {}
    if (typeof window.gtag === 'function') window.gtag('consent', 'update', { analytics_storage: v });
    track('consent_choice', { choice: v });
  };
  if (banner) {
    if (!stored() && !gpcOn) { banner.hidden = false; document.documentElement.classList.add('consent-open'); }
    banner.addEventListener('click', function (e) {
      var b = e.target.closest('[data-consent]'); if (!b) return;
      window.fandsConsent(b.dataset.consent); banner.hidden = true; document.documentElement.classList.remove('consent-open');
    });
  }
})();
