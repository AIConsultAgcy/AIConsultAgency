#!/bin/bash
# page.html is the page body (what the Claude artifact publishes). This wraps it into index.html for hosting.
cd "$(dirname "$0")"
{ printf '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n<meta name="description" content="We build and deploy AI systems that create measurable outcomes for your business. Practical, affordable, measurable. West Hollywood.">\n</head>\n<body style="margin:0">\n'; cat page.html; printf '\n</body>\n</html>\n'; } > index.html
echo "built index.html ($(wc -c < index.html) bytes)"
