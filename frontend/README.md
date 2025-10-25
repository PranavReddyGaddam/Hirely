# Frontend

A modern React application built with Vite, TypeScript, and Tailwind CSS 3.4.2.

## Tech Stack

- **React 19** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS 3.4.2** - Utility-first CSS framework
- **shadcn/ui ready** - Pre-configured for shadcn/ui components

## Getting Started

### Install Dependencies

```bash
npm install
```

### Run Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm preview
```

## Adding shadcn/ui Components

The project is already configured for shadcn/ui. To add components:

```bash
npx shadcn@latest add button
npx shadcn@latest add card
# etc.
```

Components will be added to `src/components/ui/` and you can import them using the `@/` alias:

```tsx
import { Button } from "@/components/ui/button"
```

## Project Structure

```
frontend/
├── src/
│   ├── components/     # React components (shadcn/ui will add to ui/ subdirectory)
│   ├── lib/            # Utility functions (cn helper included)
│   ├── App.tsx         # Main app component
│   ├── main.tsx        # Entry point
│   └── index.css       # Global styles with Tailwind directives
├── components.json     # shadcn/ui configuration
├── tailwind.config.ts  # Tailwind configuration
├── vite.config.ts      # Vite configuration
└── tsconfig.json       # TypeScript configuration
```

## Features

- ✅ React 19 with TypeScript
- ✅ Vite for fast development
- ✅ Tailwind CSS 3.4.2
- ✅ Path aliases (`@/*` for `src/*`)
- ✅ Dark mode support
- ✅ shadcn/ui ready with `cn()` utility
- ✅ All config files in TypeScript
