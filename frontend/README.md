# Cronos Frontend

React + Vite + TypeScript + Zustand + Tailwind CSS frontend for Cronos, the Colombian labor law-compliant shift management system.

## Setup

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

```bash
npm install
```

### Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000
```

For production, update with your backend URL:

```env
VITE_API_URL=https://api.cronos.example.com
```

### Development

Start the Vite dev server:

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Build

```bash
npm run build
```

Output will be in the `dist/` directory.

### Preview

Preview the production build locally:

```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── api/              # API client & endpoints
│   ├── components/       # Reusable React components
│   ├── hooks/            # Custom React hooks
│   ├── layouts/          # Page layouts (Dashboard, etc.)
│   ├── pages/            # Page components
│   ├── stores/           # Zustand stores (auth, shifts, etc.)
│   ├── utils/            # Utility functions
│   ├── App.tsx           # Main App component
│   ├── main.tsx          # React entry point
│   └── index.css         # Global styles + Tailwind
├── index.html            # HTML entry point
├── vite.config.ts        # Vite config
├── tsconfig.json         # TypeScript config
├── tailwind.config.js    # Tailwind CSS config
└── postcss.config.js     # PostCSS config
```

## Features (Phase 2)

### Completed (Sprint 2.1)
- ✅ React + Vite + Zustand + Tailwind setup
- ✅ API client with JWT interceptors
- ✅ Login page with form validation
- ✅ Auth store (Zustand)
- ✅ Dashboard layout with sidebar navigation

### TODO (Sprint 2.2+)
- FE-006: Shift Calendar Component
- FE-007: Shift Assignment Form
- FE-008: Payroll Breakdown Table
- FE-009: CSV/XML Export Feature
- FE-010: Payroll Summary (Manager/HR view)

## API Integration

The frontend connects to the backend at `VITE_API_URL`. See `src/api/client.ts` for the Axios client with automatic token refresh logic.

### Endpoints

- Auth: `/auth/login`, `/auth/refresh`, `/auth/logout`
- Shifts: `/shifts/templates`, `/shifts/assignments`
- Holidays: `/holidays`
- Payroll: `/payroll/worker/{id}`, `/payroll/daily/{id}`, `/payroll/summary`

## Testing (TODO)

```bash
npm run test
```

## Contributing

Follow the project's TypeScript conventions and component structure.
