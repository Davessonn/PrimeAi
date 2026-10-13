# 🏃‍♂️ PrimeAi — AI-Powered Sports & Recovery Assistant

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-AsyncSQLAlchemy-336791?logo=postgresql)
![Google Gemini](https://img.shields.io/badge/AI-Google%20Gemini%202.0-8E44AD?logo=google)
![Discord](https://img.shields.io/badge/Interface-Discord%20Bot-5865F2?logo=discord)

**PrimeAi** is an automated personal endurance sports and sleep analysis assistant. It aggregates physiological and training metrics from **Intervals.icu** (fed by Apple Watch/AutoSleep and Strava/Garmin), calculates advanced recovery analytics against your individual 30-day baseline (HRV Z-Scores, Sleep Debt, Ramp Rate), and delivers daily personalized AI briefings directly to your **Discord** server.

---

## ✨ Key Features

- **🔄 Automatic Ingestion Pipeline:** Daily async sync of wellness data (HRV rMSSD, sleep duration/score, resting HR, CTL/ATL/TSB) and workouts (TSS, duration, avg HR) from Intervals.icu REST API.
- **📈 Advanced Recovery Analytics:**
  - **HRV Z-Score:** Evaluates today's HRV against your individual 30-day baseline and standard deviation to detect systemic fatigue or illness.
  - **Sleep Debt:** Tracks cumulative sleep deficits (hours) against your optimal target.
  - **TSB & Ramp Rate:** Monitors form and load acceleration to prevent overtraining and injury.
- **🧠 Personal AI Coach:** Powered by **Google Gemini 2.0 Flash** in structured JSON Mode. Combines objective physiological trends with subjective user notes to recommend workout zones, duration, and actionable lifestyle advice.
- **💬 Rich Discord Embeds:** Automatically posts a visually intuitive briefing card every morning at 07:00 AM.
- **📝 Interactive Slash Commands:** Use `/note` in Discord to report subjective context (e.g., *"Sore right calf"*, *"High stress day"*) that the AI accounts for in the next briefing.

---

## 🏗️ Tech Stack & Architecture

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        1. DATA COLLECTION (Devices)                    │
│  [ ⌚ Apple Watch / AutoSleep ]      [ 🚴 Strava / Garmin / Wahoo ]   │
└───────────────────────┬───────────────────────────────┬────────────────┘
                        │ (iOS Auto Sync)               │ (Auto Sync)
                        ▼                               ▼
┌────────────────────────────────────────────────────────────────────────┐
│                         2. INTERVALS.ICU (Cloud)                       │
│              Aggregated Workout, Sleep & Wellness Data                 │
└───────────────────────────────────────┬────────────────────────────────┘
                                        │ (REST API)
                                        ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        3. PYTHON BACKEND                               │
│                                                                        │
│   ┌──────────────────┐     ┌──────────────────┐    ┌───────────────┐   │
│   │   Sync Engine    │ ──► │ Analytics Engine │ ──►│   AI Engine   │   │
│   │  (Data Fetching) │     │  (Z-Score/Debt)  │    │(Prompt Builder)│  │
│   └────────┬─────────┘     └──────────────────┘    └───────┬───────┘   │
│            │                                               │           │
└────────────┼───────────────────────────────────────────────┼───────────┘
             │ (Save)                                        │
             ▼                                               ▼
┌──────────────────────────┐                    ┌──────────────────────────┐
│  4. POSTGRESQL DATABASE  │                    │ 5. GOOGLE GEMINI 2.0 AI  │
│   (Historical Storage)   │ ◄──────────────────┤   (JSON Mode Analysis)   │
└──────────────────────────┘                    └──────────────────────────┘
             ▲
             │ (Read & Save)
             ▼
┌────────────────────────────────────────────────────────────────────────┐
│                       6. DISCORD BOT & INTERFACE                       │
│                                                                        │
│  [ 💬 #daily-briefings ] ◄── (Embed Card) ────── [ 🤖 Discord Bot ]   │
│                                                            ▲           │
│  [ 👤 User ] ────────────── ( /note command ) ─────────────┘           │
└────────────────────────────────────────────────────────────────────────┘
```

- **Backend:** Python 3.11+, AsyncIO, `httpx`, `Pydantic v2`
- **Database:** PostgreSQL with `SQLAlchemy 2.0 (Async)` & `asyncpg`
- **AI Engine:** Google Gemini 2.0 Flash REST API (JSON Schema mode)
- **Interface:** `discord.py` (App Commands & Cogs)
- **Scheduler:** `APScheduler`

---

## 📁 Repository Structure

```text
primeAi/
├── config/             # Environment settings (Pydantic Settings)
├── database/           # Async engine, session setup, and ORM models
├── dto/                # Pydantic models for API payloads and AI JSON validation
├── repository/         # Data Access Layer (Async CRUD DB queries)
├── clients/            # Async HTTP clients (Intervals API & Gemini API)
├── services/           # Core business logic (Sync, Analytics, AI Engine)
├── bot/                # Discord Bot client and Slash Command Cogs
├── scheduler/          # APScheduler cron jobs (Daily 07:00 AM briefing)
├── docker-compose.yml  # Containerized production deployment
└── PROJECT_CONTEXT.md  # Architectural context file for AI coding assistants
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.11+ installed
- PostgreSQL 14+ database
- [Intervals.icu](https://intervals.icu) account with API key
- [Google AI Studio](https://aistudio.google.com) API Key (Gemini)
- [Discord Developer Portal](https://discord.com/developers) Bot Token

### 2. Environment Setup

Clone the repository and prepare the configuration:

```bash
git clone https://github.com/your-username/primeAi.git
cd primeAi

cp .env.example .env
```

Edit `.env` and supply your credentials:

```ini
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/primeAi_db

# Discord
DISCORD_TOKEN=your_discord_bot_token_here
DISCORD_CHANNEL_ID=1234567890123456789

# Intervals.icu
INTERVALS_API_KEY=your_intervals_api_key_here
INTERVALS_ATHLETE_ID=0

# Google Gemini
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Local Installation & Launch

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run main application (Initializes DB tables automatically on first launch)
python3 main.py
```

---

## 🐳 Docker Deployment

To run PrimeAi continuously on a home server:

```bash
docker compose up -d --build
```

To view real-time application logs:

```bash
docker compose logs -f
```

---

## 🤖 Discord Interface Preview

```text
🤖 PrimeAi — Today at 07:02 AM
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🟢 PrimeAi BRIEFING — 82 / 100                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  📊 Status Summary                                                           │
│  Your recovery is at a good level. Your HRV value (54 ms) is within your     │
│  normal baseline range, but sleep duration fell 40 minutes short of average. │
│                                                                              │
│  🏃 Recommended Daily Workout                                                │
│  • Type: Running (Easy Zone 2)                                               │
│  • Intensity: Zone 2 Aerobic                                                 │
│  • Duration: 45 minutes                                                      │
│  • Target HR Zone: 135 - 148 bpm                                             │
│                                                                              │
│  💡 Key AI Advice                                                            │
│  Yesterday's TSS load was low. Since your sleep was slightly short,          │
│  avoid caffeine in the evening hours and go to bed earlier tonight.          │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.
