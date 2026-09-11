# Voyager AI Travel Planner

Voyager AI is a travel-focused conversational planner with a React/Vite frontend and a stateless FastAPI backend. The browser keeps conversation context in `sessionStorage`; Google and weather credentials stay on the backend.

## Local Run

Start the backend with mock providers:

```bash
cd backend
LLM_PROVIDER=mock WEATHER_PROVIDER=mock uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Start the frontend in a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

For Google AI Studio, create `backend/.env` locally and set `GOOGLE_API_KEY`, `LLM_PROVIDER=google`, and `MODEL_NAME=gemma-4-26b-a4b-it`. Never commit `.env` files or put provider keys in frontend configuration.

## GitHub Pages

The Pages workflow deploys the Vite frontend from `main` to:

`https://i2807.github.io/capstone-travel-iternary-planner/`

GitHub Pages cannot run FastAPI. Deploy the backend separately, then create this repository variable under **Settings -> Secrets and variables -> Actions -> Variables**:

- `VITE_API_BASE_URL`: the public URL of the deployed FastAPI service, without a trailing slash

The Pages build passes that variable to Vite. If it is not set, the frontend falls back to `/api`, which is useful locally but will not reach a backend on GitHub Pages.

Configure the backend CORS setting to allow the Pages origin:

```env
CORS_ORIGINS=https://i2807.github.io
```

Then push to `main` or run **Actions -> Deploy frontend to GitHub Pages -> Run workflow**. In **Settings -> Pages**, select **GitHub Actions** as the source if Pages has not been enabled for the repository yet.

## Validation

Backend:

```bash
cd backend
ruff check .
pytest
```

Frontend:

```bash
cd frontend
npm run lint
npm run type-check
npm run test:run
npm run build
```
