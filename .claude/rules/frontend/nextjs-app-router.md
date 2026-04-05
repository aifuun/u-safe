---
category: frontend
title: Nextjs App Router
description: Next.js 15 app router
tags:
- nextjs
- react
- typescript
profiles:
- nextjs-aws
- tauri
paths:
- '**/*.{ts,tsx}'
version: 1.0.0
last_updated: '2026-03-27'
---

---
paths:
  - "app/**"
  - "src/app/**"
---
# Next.js App Router Rules

> Next.js 13+ App Router patterns. Server-first with client opt-in.

## Quick Check

### Route Structure
- [ ] Use `app/` directory (not `pages/`)
- [ ] Routes defined by folder structure: `app/users/[id]/page.tsx`
- [ ] Special files: `page.tsx`, `layout.tsx`, `loading.tsx`, `error.tsx`
- [ ] Route groups for organization: `app/(marketing)/about/page.tsx`

### Server vs Client Components
- [ ] Components are Server Components by default (no 'use client')
- [ ] Add 'use client' ONLY when needed (interactivity, hooks, browser APIs)
- [ ] Server Components at the top of the tree
- [ ] Client Components as leaves

### Data Fetching
- [ ] Fetch in Server Components (no useEffect)
- [ ] Use async/await directly in components
- [ ] Leverage automatic request deduplication
- [ ] Cache with `revalidate` or `cache` options

### Layouts
- [ ] Root layout in `app/layout.tsx` (required)
- [ ] Nested layouts for shared UI
- [ ] Layouts preserve state on navigation
- [ ] Use `<Suspense>` for streaming

## Core Patterns

### 1. Page Component (Server Component)

```tsx
// app/users/[id]/page.tsx
// Server Component - fetch data directly
interface PageProps {
  params: { id: string };
  searchParams: { [key: string]: string | string[] | undefined };
}

export default async function UserPage({ params, searchParams }: PageProps) {
  // ✅ Fetch directly - no useEffect needed
  const user = await getUserById(params.id);

  // ✅ Multiple parallel requests
  const [posts, comments] = await Promise.all([
    getUserPosts(params.id),
    getUserComments(params.id),
  ]);

  return (
    <div>
      <h1>{user.name}</h1>
      <PostList posts={posts} />
      <CommentList comments={comments} />
    </div>
  );
}

// ✅ Generate static params for SSG
export async function generateStaticParams() {
  const users = await getAllUsers();
  return users.map((user) => ({ id: user.id }));
}

// ✅ Metadata for SEO
export async function generateMetadata({ params }: PageProps) {
  const user = await getUserById(params.id);
  return {
    title: `${user.name} - Profile`,
    description: user.bio,
  };
}
```

### 2. Layout Component

```tsx
// app/dashboard/layout.tsx
// Shared layout for all dashboard pages
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="dashboard">
      {/* ✅ Shared UI - rendered once, preserved on navigation */}
      <DashboardNav />
      <main>{children}</main>
      <DashboardFooter />
    </div>
  );
}
```

### 3. Loading State

```tsx
// app/users/loading.tsx
// Automatic loading UI with Suspense
export default function Loading() {
  return (
    <div className="animate-pulse">
      <div className="h-8 bg-gray-200 rounded w-1/3 mb-4" />
      <div className="h-4 bg-gray-200 rounded w-2/3 mb-2" />
      <div className="h-4 bg-gray-200 rounded w-1/2" />
    </div>
  );
}
```

### 4. Error Boundary

```tsx
// app/users/error.tsx
'use client'; // ✅ Error boundaries must be Client Components

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="error-container">
      <h2>Something went wrong!</h2>
      <p>{error.message}</p>
      <button onClick={reset}>Try again</button>
    </div>
  );
}
```

### 5. Route Groups (Organization)

```tsx
// app/(marketing)/about/page.tsx
// Parentheses create logical groups without affecting URL
// URL: /about (not /marketing/about)

export default function AboutPage() {
  return <div>About Us</div>;
}
```

### 6. Parallel Routes

```tsx
// app/dashboard/@analytics/page.tsx
// app/dashboard/@team/page.tsx
// app/dashboard/layout.tsx

export default function DashboardLayout({
  children,
  analytics,
  team,
}: {
  children: React.ReactNode;
  analytics: React.ReactNode;
  team: React.ReactNode;
}) {
  return (
    <div>
      <div className="main">{children}</div>
      <div className="sidebar">
        {analytics}
        {team}
      </div>
    </div>
  );
}
```

### 7. Intercepting Routes (Modals)

```tsx
// app/photos/[id]/page.tsx - Full page
export default function PhotoPage({ params }: { params: { id: string } }) {
  return <FullPhoto id={params.id} />;
}

// app/@modal/(.)photos/[id]/page.tsx - Modal intercept
export default function PhotoModal({ params }: { params: { id: string } }) {
  return (
    <Modal>
      <FullPhoto id={params.id} />
    </Modal>
  );
}
```

## Anti-Patterns

### ❌ Using Client Components Unnecessarily

```tsx
// ❌ BAD - Entire page is client-side
'use client';

export default async function UsersPage() {
  const users = await getUsers(); // Won't work - async not allowed in client
  return <UserList users={users} />;
}

// ✅ GOOD - Server Component at top
export default async function UsersPage() {
  const users = await getUsers();
  return <UserList users={users} />; // Can be client if needed
}
```

### ❌ Using useEffect for Data Fetching

```tsx
// ❌ BAD - Old Pages Router pattern
'use client';
import { useEffect, useState } from 'react';

export default function UserPage({ params }: any) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    fetch(`/api/users/${params.id}`)
      .then(res => res.json())
      .then(setUser);
  }, [params.id]);

  if (!user) return <div>Loading...</div>;
  return <div>{user.name}</div>;
}

// ✅ GOOD - Server Component async fetch
export default async function UserPage({
  params
}: {
  params: { id: string }
}) {
  const user = await getUserById(params.id);
  return <div>{user.name}</div>;
}
```

### ❌ Mixing Pages and App Router

```tsx
// ❌ BAD - Don't mix pages/ and app/ directories
// Choose one routing system

// ✅ GOOD - Use app/ directory exclusively
// Migrate incrementally if needed, but commit to App Router
```

## Caching & Revalidation

### Static Data (Build Time)

```tsx
// ✅ Generate at build time, cache forever
export default async function StaticPage() {
  const data = await fetch('https://api.example.com/data', {
    cache: 'force-cache', // Default - static
  });
  return <div>{data.title}</div>;
}
```

### Revalidate Periodically (ISR)

```tsx
// ✅ Revalidate every 60 seconds
export default async function RevalidatedPage() {
  const data = await fetch('https://api.example.com/data', {
    next: { revalidate: 60 },
  });
  return <div>{data.title}</div>;
}
```

### Dynamic (Per Request)

```tsx
// ✅ Fetch fresh data on every request
export default async function DynamicPage() {
  const data = await fetch('https://api.example.com/data', {
    cache: 'no-store', // Always fresh
  });
  return <div>{data.title}</div>;
}
```

## Streaming with Suspense

```tsx
// app/dashboard/page.tsx
import { Suspense } from 'react';

export default function DashboardPage() {
  return (
    <div>
      {/* ✅ Fast content renders immediately */}
      <UserGreeting />

      {/* ✅ Slow content streams in when ready */}
      <Suspense fallback={<AnalyticsSkeleton />}>
        <Analytics />
      </Suspense>

      <Suspense fallback={<ChartsSkeleton />}>
        <Charts />
      </Suspense>
    </div>
  );
}

async function Analytics() {
  const data = await getAnalytics(); // Slow query
  return <div>{/* Render analytics */}</div>;
}
```

## Migration from Pages Router

### Key Differences

| Pages Router | App Router |
|--------------|------------|
| `pages/` directory | `app/` directory |
| `_app.tsx` | `layout.tsx` |
| `_document.tsx` | `layout.tsx` (root) |
| `getServerSideProps` | `async` Server Component |
| `getStaticProps` | `async` Server Component + `generateStaticParams` |
| `getStaticPaths` | `generateStaticParams` |
| `useRouter()` | `useRouter()` from `next/navigation` |
| `<Link>` auto-wraps `<a>` | `<Link>` IS the anchor |

### Migration Strategy

1. **Incremental**: Keep `pages/` for existing routes
2. **Add `app/` directory** for new features
3. **Migrate route by route** when ready
4. **Remove `pages/` when complete**

---

**Version**: 1.0.0
**Next.js Version**: 13.4+ (App Router stable)
**See Also**: nextjs-server-components.md, nextjs-api-routes.md
