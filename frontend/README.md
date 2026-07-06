# CareerOS Frontend

This is the Vite React frontend for CareerOS.

## Stack

- Vite
- React
- TypeScript
- React Router
- Axios
- Lucide React icons
- Framer Motion
- React Hot Toast

## Scripts

```powershell
npm install
npm run dev
npm.cmd run build
npm run lint
npm run preview
```

Use `npm.cmd` on Windows if PowerShell blocks `npm.ps1`.

## API URL

The API client defaults to:

```text
http://127.0.0.1:8000/api
```

Override it with `frontend/.env` when needed:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

## Main Files

```text
src/lib/api.ts                 Axios API client and auth token interceptor
src/context/AuthContext.tsx    Login, registration, logout, session hydration
src/context/JobsContext.tsx    Jobs, stats, scraping, and auto-apply state
src/pages/Login.tsx            Sign-in and registration screen
src/pages/Dashboard.tsx        Application stats overview
src/pages/Jobs.tsx             Job scraper and tracker UI
src/pages/Profile.tsx          Profile and base resume editor
```
