# 🏢 BizSim Enterprise: Strategy Simulator SaaS

> A production-grade, full-stack Business Strategy Simulator built with an enterprise-level architecture. Features a reactive AI simulation engine, real-time analytics, and a secure multi-user environment.

[![Frontend: React/Vite](https://img.shields.io/badge/Frontend-React%20%2F%20Vite-61DAFB?style=flat-square&logo=react)](https://vitejs.dev/)
[![Backend: FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Database: PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791?style=flat-square&logo=postgresql)](https://www.postgresql.org/)
[![Deployment: Railway/Vercel](https://img.shields.io/badge/Deployment-Railway%20%2F%20Vercel-000000?style=flat-square&logo=vercel)](https://vercel.com/)

---

## 🚀 Key Features

- **🧠 Advanced Simulation Engine**:
    - **Reactive AI Competitors**: Rival companies (RivalCorp, MegaCo) dynamically react to your market share and pricing strategies.
    - **Difficulty Scaling**: Choose between Easy, Medium, and Hard modes that affect market volatility and competitor aggression.
    - **Stateful Persistence**: Resume your CEO career across devices with DB-backed session management.
- **🔐 Enterprise Security**:
    - **JWT Authentication**: Secure login/register with token-based access and persistent sessions.
    - **Production Hardening**: Integrated Rate Limiting (SlowAPI), Input Sanitization, and CORS protection.
- **📊 Real-time Dashboards**:
    - **Interactive Analytics**: Powered by **Recharts** for visualizing revenue trends, profit margins, and market dominance.
    - **Global Leaderboard**: Compete with other users for the highest cumulative reward scores.
- **🛠️ Professional DevOps**:
    - **Alembic Migrations**: Robust database schema management.
    - **Dockerized Environment**: Full `docker-compose` setup for local development.
    - **CI/CD Ready**: Configured for seamless deployment to Railway (Backend) and Vercel (Frontend).

---

## 🏗️ Architecture & Stack

### **Backend (Python 3.12 + FastAPI)**
- **Modular Structure**: Service-based architecture with clean separation of concerns.
- **ORM**: SQLAlchemy 2.0 with PostgreSQL/SQLite support.
- **Migrations**: Alembic for version-controlled database schema.
- **Monitoring**: Structured JSON logging and request timing middleware.

### **Frontend (TypeScript + React + Vite)**
- **UI Framework**: Tailwind CSS for a modern, Google-inspired design system.
- **State Management**: Zustand for lightweight, high-performance global state.
- **Data Visualization**: Recharts for dynamic, interactive financial charts.
- **Routing**: React Router DOM with protected auth-based routes.

---

## 📁 Project Structure

```text
.
├── backend/
│   ├── app/
│   │   ├── api/v1/         # Versioned API Endpoints (Auth, Users, Sim)
│   │   ├── core/           # Security, JWT, Config (Pydantic Settings)
│   │   ├── db/             # SQLAlchemy Session & Base Classes
│   │   ├── models/         # Database Models (User, Session, History)
│   │   ├── schemas/        # Pydantic Validation Schemas
│   │   ├── services/       # Core Business & Simulation Logic
│   │   └── main.py         # FastAPI Entry Point & Middleware
│   └── tests/              # Pytest Suite (Auth & Simulation flows)
├── frontend/
│   ├── src/
│   │   ├── components/     # UI Components & Protected Routes
│   │   ├── services/       # API Integration (Axios)
│   │   ├── store/          # Zustand State Stores
│   │   └── App.tsx         # Main Dashboard UI
│   ├── vite.config.ts      # Vite & Proxy Config
│   └── tailwind.config.js  # Theme & Design Tokens
├── alembic/                # DB Migrations
├── docker-compose.yml      # Local Container Orchestration
└── Procfile                # Railway Start Command
```

---

## 📡 API Endpoints (v1)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/register` | Register a new user profile |
| `POST` | `/auth/login/access-token` | OAuth2 compatible token login |
| `GET`  | `/users/me` | Get current user details |
| `GET`  | `/simulation/state` | Fetch current active game state |
| `POST` | `/simulation/step` | Take a strategic action (marketing, R&D, etc.) |
| `POST` | `/simulation/reset` | Initialize a new session with difficulty/task |
| `GET`  | `/simulation/leaderboard` | Get global top strategist rankings |

---

## 🚀 Quick Start

### **1. Local Development (Docker)**
The easiest way to run the full stack locally:
```bash
docker-compose up --build
```
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

### **2. Manual Setup**

**Backend:**
```bash
cd backend
pip install -r ../requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## 🌍 Deployment

### **Railway (Backend & Database)**
1. Provision a **PostgreSQL** instance on Railway.
2. Link your GitHub repo to a new service.
3. Railway will auto-detect the `Procfile`.
4. Add Env Vars: `DATABASE_URL`, `SECRET_KEY`, `BACKEND_CORS_ORIGINS`.

### **Vercel (Frontend)**
1. Import the `frontend/` directory to Vercel.
2. Set `VITE_API_URL` to your Railway backend URL.
3. Deploy.

---

## 🧪 Testing
Run the backend test suite (Auth + Sim flows):
```bash
python -m pytest backend/tests -v
```

---

## 🏆 Final Note
This project was upgraded from a simple simulation into a **Production-Grade SaaS Platform**. It demonstrates best practices in full-stack engineering, secure API design, and cloud-native deployment.
