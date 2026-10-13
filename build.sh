#!/bin/bash
# page.html is the page body (what the Claude artifact publishes). This wraps it into index.html for hosting,
# adding the <head> the artifact platform supplies itself: metadata, icons, social cards, schema and analytics.
cd "$(dirname "$0")"
{
cat <<'HEAD'
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Fands · AI systems with measurable outcomes for local business</title>
<meta name="description" content="Fands builds and deploys AI systems that create measurable outcomes for owner-led businesses in West Hollywood and Los Angeles. A free in-person walk-through, a starter system from $1,000, one number agreed before we build.">
<link rel="canonical" href="https://fands.io/">
<meta name="theme-color" content="#121521">
<meta name="color-scheme" content="light">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Sans:ital,wght@0,400;0,500;0,600;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="icon" href="/brand/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/brand/favicon.ico" sizes="32x32">
<link rel="apple-touch-icon" href="/brand/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Fands">
<meta property="og:title" content="Fands · Measured, not promised.">
<meta property="og:description" content="AI systems that create measurable outcomes for owner-led businesses. Practical, affordable, measured monthly, and in person. West Hollywood, CA.">
<meta property="og:url" content="https://fands.io/">
<meta property="og:image" content="https://fands.io/brand/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Fands: Measured, not promised. AI systems that create measurable outcomes for owner-led businesses.">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Fands · Measured, not promised.">
<meta name="twitter:description" content="AI systems that create measurable outcomes for owner-led businesses. West Hollywood, CA.">
<meta name="twitter:image" content="https://fands.io/brand/og.png">
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"ProfessionalService","@id":"https://fands.io/#org","name":"Fands","url":"https://fands.io/","logo":"https://fands.io/brand/icon-512.png","image":"https://fands.io/brand/og.png","email":"hello@fands.io","description":"AI implementation studio for owner-led businesses. We build and deploy AI systems that create measurable outcomes: AI receptionists, booking and follow-up automation, websites and apps, local marketing, content, dashboards and reporting.","slogan":"Measured, not promised.","priceRange":"$1,000 – $3,000 starter systems; $500 – $2,000 per month","areaServed":[{"@type":"City","name":"West Hollywood"},{"@type":"City","name":"Los Angeles"}],"address":{"@type":"PostalAddress","addressLocality":"West Hollywood","addressRegion":"CA","addressCountry":"US"},"openingHours":"Mo-Sa 09:00-19:00","knowsAbout":["AI automation","AI phone receptionist","booking automation","local SEO","Google Business Profile","dashboards and reporting","AI training"],"makesOffer":[{"@type":"Offer","name":"Walk-through","price":"0","priceCurrency":"USD","description":"Sixty minutes on site to find the first task worth automating."},{"@type":"Offer","name":"Starter system","priceSpecification":{"@type":"PriceSpecification","minPrice":"1000","maxPrice":"3000","priceCurrency":"USD"},"description":"One AI system built, connected and launched with your team in two to three weeks."},{"@type":"Offer","name":"Run and measure","priceSpecification":{"@type":"PriceSpecification","minPrice":"500","maxPrice":"2000","priceCurrency":"USD","unitText":"month"},"description":"Monthly in-person review of the agreed number, tuning, and the next system when the first pays for itself."}]}
</script>
</head>
<body style="margin:0">
HEAD
grep -v -e '^<title>' -e '^<link rel="preconnect"' -e '^<link rel="stylesheet" href="https://fonts.googleapis.com' page.html
cat <<'TAIL'
<script>window.va=window.va||function(){(window.vaq=window.vaq||[]).push(arguments)};</script>
<script defer src="/_vercel/insights/script.js"></script>
</body>
</html>
TAIL
} > index.html
echo "built index.html ($(wc -c < index.html) bytes)"
