import { rewrite } from '@vercel/functions';

// Static index.html wins over vercel.json rewrites on "/", so the
// subdomain landing pages are mapped here, before the filesystem.
const MAP = {
  'links.fands.io': '/links',
  'seimur.fands.io': '/seimur',
  'faris.fands.io': '/faris',
  'pitch.fands.io': '/pitch'
};

export const config = { matcher: '/' };

export default function middleware(request) {
  const host = (request.headers.get('host') || '').toLowerCase().split(':')[0];
  const target = MAP[host];
  if (!target) return;
  return rewrite(new URL(target, request.url));
}
