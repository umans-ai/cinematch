import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  if (request.nextUrl.pathname.startsWith('/api/')) {
    const apiUrl = process.env.API_URL || 'http://localhost:8000';
    const rewrittenUrl = new URL(
      request.nextUrl.pathname + request.nextUrl.search,
      apiUrl
    );
    return NextResponse.rewrite(rewrittenUrl);
  }
  return NextResponse.next();
}

export const config = {
  matcher: '/api/:path*',
};
