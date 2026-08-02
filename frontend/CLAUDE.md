# Frontend — Behavioral Risk Assessment

React + TypeScript + TailwindCSS single-page application that consumes the FastAPI backend at `http://localhost:8000`.

## Tech Stack

| Tool | Version | Purpose |
|------|---------|---------|
| React | 18 | UI framework |
| TypeScript | 5 | Type safety |
| Vite | 5 | Build tool / dev server |
| TailwindCSS | 3 | Utility-first styling |
| Radix UI | latest | Headless component primitives |
| Recharts | 2 | Charts (gauge, bar, pie, line) |
| Axios | 1 | HTTP client |
| React Router | 6 | Client-side routing |
| React Hook Form | 7 | Form state management |
| Zod | 3 | Schema validation |
| Lucide React | latest | Icons |

## Project Structure

```
src/
  api/
    client.ts          # Axios instance → http://localhost:8000
    assessments.ts     # Typed API functions (postPredict, getAssessment, etc.)
  components/
    Navbar.tsx         # Sticky nav, active route, dark mode toggle
  contexts/
    ThemeContext.tsx    # System-preference dark mode + localStorage
  pages/
    Landing.tsx        # Hero, feature cards, CTA
    Assessment.tsx     # 4-step form with per-step Zod validation
    Results.tsx        # Risk gauge, SHAP chart, scores, biases, recommendations
    History.tsx        # Past assessments table, click → Results
    Analytics.tsx      # Aggregate charts (pie, bar, line)
  types/
    index.ts           # All TypeScript types for API shapes
  App.tsx              # Router setup
  main.tsx             # Entry point
```

## Routes

| Path | Page | Description |
|------|------|-------------|
| `/` | Landing | Hero + CTA |
| `/assessment` | Assessment | 4-step behavioral questionnaire |
| `/results/:id` | Results | Full prediction breakdown |
| `/history` | History | Past assessments list |
| `/analytics` | Analytics | Aggregate dashboard |

## API Contract

**Single source of truth:** [`../docs/api-contract.json`](../docs/api-contract.json)

Before making any API change:
1. Update `../docs/api-contract.json` first — agree on the shape
2. Update `src/types/index.ts` to match exactly
3. Update `src/api/assessments.ts` if URL or envelope changes
4. Run `npm run build` — zero TypeScript errors required

The backend wraps responses in `{ "success": true, "data": { ... } }`. The `src/api/assessments.ts` functions unwrap the envelope — components receive the inner payload directly.

## Key Conventions

- **No business logic in the frontend.** All computation happens in the backend. The frontend only renders what the API returns.
- All API calls go through `src/api/assessments.ts` — never call axios directly from a component.
- All API request/response shapes are typed in `src/types/index.ts`. Update types there when the backend contract changes.
- Dark mode is controlled by `ThemeContext` — use `useTheme()` hook, never set `document.classList` directly.
- Form steps in `Assessment.tsx` are validated by Zod schemas before advancing. Add new fields to the matching schema first.

## Development

```bash
npm install
npm run dev          # http://localhost:5173
npm run build        # Production build → dist/
npm run preview      # Preview production build
```

## Environment

The backend URL is hardcoded in `src/api/client.ts` as `http://localhost:8000`. To change it for a different environment, update that file (or extract to a `.env` variable using `VITE_API_URL`).

## API Contract Summary

All endpoints are on the backend at port 8000. The predict endpoint returns:

```typescript
{
  risk_category: 'Low' | 'Medium' | 'High'
  risk_confidence: number           // 0–1
  risk_probabilities: Record<string, number>
  investment_preference: string
  investment_confidence: number
  financial_decision_score: number  // 0–100
  behavioral_composite_score: number
  financial_discipline_score: number
  shap_values: Record<string, number>   // top 10 features
  feature_importance: Record<string, number>
  recommendations: string[]
  behavioral_biases: string[]
}
```

## Docker

```bash
# Built and served via nginx on port 3000
docker build -t risk-frontend .
docker run -p 3000:80 risk-frontend
```

The nginx config at `nginx.conf` proxies `/api/` → backend and handles SPA routing with `try_files`.

---

## Agents

### agent:frontend-dev
**Role:** Frontend feature development and bug fixes.

**Scope:** All files under `src/`. Do not touch backend, ML, or database files.

**Capabilities:**
- Add new pages under `src/pages/` and register the route in `App.tsx`
- Add/modify components in `src/components/`
- Update API types in `src/types/index.ts` when the backend contract changes
- Add new Recharts visualizations to existing pages
- Fix styling, responsiveness, and dark mode issues
- Add form fields to `Assessment.tsx` steps (update Zod schema + API type simultaneously)

**Must not:**
- Add business logic or ML computation to the frontend
- Call the backend URL directly — always go through `src/api/assessments.ts`
- Modify `backend/`, `ml/`, or `data/` directories

**How to verify changes:** Run `npm run build` — zero TypeScript errors required. Then `npm run dev` and exercise the changed page in the browser.

---

### agent:ui-reviewer
**Role:** Visual QA and accessibility review.

**Scope:** Read-only review of `src/` files. Reports issues but does not edit.

**Focus areas:**
- Dark mode contrast and color consistency
- Responsive layout on mobile (375px) and desktop (1440px)
- Loading and error states on all async operations
- Form field labels and ARIA attributes
- Chart readability and axis labels

---

### agent:api-contract-sync
**Role:** Keep frontend types in sync when the backend API changes.

**Scope:** `src/types/index.ts` and `src/api/assessments.ts`.

**Trigger:** Run this agent after any backend schema change.

**Task:** Compare the backend Pydantic schemas in `../backend/app/schemas/assessment.py` against `src/types/index.ts` and update the TypeScript types to match. Then check all usages of changed types across `src/pages/` and fix any type errors.
