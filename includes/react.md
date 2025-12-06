# React/TypeScript Environment Standards

## Specialist Agents
Leverage specialized agents from `~/.claude/agents/` for React/TypeScript work:

| Agent | Category | Use For |
|-------|----------|---------|
| `react-specialist` | 02-language-specialists | React patterns, hooks, state management |
| `typescript-pro` | 02-language-specialists | TypeScript types, generics, strict mode |
| `frontend-developer` | 01-core-development | Component architecture, UI implementation |
| `ui-designer` | 01-core-development | Design systems, styling, accessibility |
| `nextjs-developer` | 02-language-specialists | Next.js apps, SSR, API routes |

## Runtime & Package Management
- **Node.js**: 24 LTS (Krypton) or 22 LTS (Jod)
- **Package manager**: pnpm 11+ (NOT npm or yarn)
- **TypeScript**: 5.9+ with strict mode (TS 7.0 beta available with 10x speed)

### pnpm Commands
```bash
# Project setup
pnpm create vite@latest my-app --template react-ts
pnpm install

# Dependencies
pnpm add <package>            # Add dependency
pnpm add -D <package>         # Add dev dependency
pnpm remove <package>         # Remove dependency
pnpm update                   # Update all packages

# Running
pnpm dev                      # Development server
pnpm build                    # Production build
pnpm test                     # Run tests
pnpm lint                     # Run linter
```

## TypeScript Configuration (v5.9+, Strict)
```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2024",
    "lib": ["ES2024", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",

    // Strict type checking
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "exactOptionalPropertyTypes": true,
    "noPropertyAccessFromIndexSignature": true,

    // Module resolution
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src"],
  "exclude": ["node_modules"]
}
```

## ESLint Configuration (v9+, Flat Config)
```javascript
// eslint.config.js (flat config - default in ESLint 9+)
import js from '@eslint/js';
import tseslint from 'typescript-eslint';
import react from 'eslint-plugin-react';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';

export default tseslint.config(
  js.configs.recommended,
  ...tseslint.configs.strictTypeChecked,
  ...tseslint.configs.stylisticTypeChecked,
  {
    languageOptions: {
      parserOptions: {
        project: true,
        tsconfigRootDir: import.meta.dirname,
      },
    },
    plugins: {
      react,
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      'react-refresh/only-export-components': 'warn',
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    },
  }
);
```

## State Management: TanStack Query (v5.90+)
```typescript
// src/lib/query-client.ts
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      gcTime: 1000 * 60 * 30,   // 30 minutes
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

// Usage in components
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

function useUser(userId: string) {
  return useQuery({
    queryKey: ['user', userId],
    queryFn: () => fetchUser(userId),
    enabled: Boolean(userId),
  });
}

function useUpdateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: updateUser,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['user', data.id] });
    },
  });
}
```

## Styling: Tailwind CSS (v4.0+)
```css
/* src/index.css - Tailwind v4 uses CSS-first configuration */
@import "tailwindcss";

/* Custom theme configuration via CSS variables */
@theme {
  --color-brand: #3b82f6;
  --font-display: "Inter", sans-serif;
}
```

### Tailwind Patterns
```tsx
// Use cn() utility for conditional classes
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Usage
<button className={cn(
  'px-4 py-2 rounded-md font-medium',
  variant === 'primary' && 'bg-blue-600 text-white',
  variant === 'secondary' && 'bg-gray-200 text-gray-900',
  disabled && 'opacity-50 cursor-not-allowed'
)} />
```

## Testing: Vitest (v4.0+) + React Testing Library + Playwright (v1.57+)

### Vitest Configuration
```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/test/setup.ts',
    browser: {
      enabled: false, // Stable Browser Mode available in v4.0+
      provider: 'playwright',
    },
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      exclude: ['node_modules/', 'src/test/'],
      thresholds: { lines: 80, branches: 80 },
    },
  },
});
```

### Test Setup
```typescript
// src/test/setup.ts
import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';

afterEach(() => {
  cleanup();
});
```

### Component Test Pattern
```typescript
// src/components/Button.test.tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { Button } from './Button';

describe('Button', () => {
  it('calls onClick when clicked', async () => {
    const user = userEvent.setup();
    const handleClick = vi.fn();

    render(<Button onClick={handleClick}>Click me</Button>);

    await user.click(screen.getByRole('button', { name: /click me/i }));

    expect(handleClick).toHaveBeenCalledOnce();
  });
});
```

### Playwright E2E Configuration (v1.57+)
```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
  ],
  webServer: {
    command: 'pnpm dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
  },
});
```

## Project Structure
```
project-root/
├── index.html
├── package.json
├── pnpm-lock.yaml
├── tsconfig.json
├── vite.config.ts
├── vitest.config.ts
├── playwright.config.ts
├── tailwind.config.js
├── eslint.config.js
├── public/
├── e2e/                      # Playwright tests
│   └── home.spec.ts
└── src/
    ├── main.tsx              # Entry point
    ├── App.tsx
    ├── index.css             # Tailwind imports
    ├── vite-env.d.ts
    ├── components/           # Shared UI components
    │   ├── ui/               # Primitive components
    │   └── Button/
    │       ├── Button.tsx
    │       ├── Button.test.tsx
    │       └── index.ts
    ├── features/             # Feature-based modules
    │   └── auth/
    │       ├── components/
    │       ├── hooks/
    │       ├── api.ts
    │       └── types.ts
    ├── hooks/                # Shared hooks
    ├── lib/                  # Utilities, clients
    │   ├── query-client.ts
    │   └── utils.ts
    ├── pages/                # Route components
    └── test/
        └── setup.ts
```

## Component Patterns

### Functional Component with Props
```tsx
interface ButtonProps {
  variant?: 'primary' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
}

export function Button({
  variant = 'primary',
  size = 'md',
  disabled = false,
  children,
  onClick,
}: ButtonProps) {
  return (
    <button
      type="button"
      disabled={disabled}
      onClick={onClick}
      className={cn(
        'rounded-md font-medium transition-colors',
        sizeStyles[size],
        variantStyles[variant],
        disabled && 'opacity-50 cursor-not-allowed'
      )}
    >
      {children}
    </button>
  );
}
```

### Custom Hook Pattern
```tsx
import { useState, useCallback } from 'react';

export function useToggle(initialValue = false) {
  const [value, setValue] = useState(initialValue);

  const toggle = useCallback(() => setValue((v) => !v), []);
  const setTrue = useCallback(() => setValue(true), []);
  const setFalse = useCallback(() => setValue(false), []);

  return { value, toggle, setTrue, setFalse } as const;
}
```

### Suspense + Error Boundary Pattern
```tsx
import { Suspense } from 'react';
import { ErrorBoundary } from 'react-error-boundary';

function App() {
  return (
    <ErrorBoundary fallback={<ErrorFallback />}>
      <Suspense fallback={<LoadingSkeleton />}>
        <UserProfile />
      </Suspense>
    </ErrorBoundary>
  );
}

// With TanStack Query suspense
function UserProfile() {
  const { data } = useSuspenseQuery({
    queryKey: ['user'],
    queryFn: fetchUser,
  });

  return <div>{data.name}</div>;
}
```

## Barrel Exports
```typescript
// src/components/Button/index.ts
export { Button } from './Button';
export type { ButtonProps } from './Button';

// Usage
import { Button } from '@/components/Button';
```
