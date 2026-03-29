# 🚀 AMIS Hackathon Setup Guide

## Complete Production-Grade React + FastAPI Setup

This guide will get your **Autonomous Manufacturing Intelligence System** running with a professional React frontend and FastAPI backend.

---

## 📋 Prerequisites

- **Python 3.9+**
- **Node.js 18+** and npm
- **Anthropic API Key** ([Get one here](https://console.anthropic.com/))

---

## ⚡ Quick Start (5 minutes)

### Step 1: Fix API Key Security

```bash
# Create .env file in project root
cd amis_phase_final
echo "ANTHROPIC_API_KEY=your-key-here" > .env
```

Edit `config.py`:
```python
import os
from dotenv import load_dotenv

load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not ANTHROPIC_API_KEY:
    raise ValueError("Set ANTHROPIC_API_KEY in .env file")
```

### Step 2: Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 3: Install Frontend Dependencies

```bash
cd ../frontend
npm install
```

### Step 4: Start Backend Server

```bash
# From backend/ directory
python main.py
```

Backend will run on **http://localhost:8000**

### Step 5: Start Frontend Dev Server

```bash
# From frontend/ directory (new terminal)
npm run dev
```

Frontend will run on **http://localhost:5173**

### Step 6: Open Browser

Navigate to **http://localhost:5173** and you'll see the AMIS dashboard!

---

## 🎯 What You'll See

### 1. **Dashboard** (Command Center)
- System health score with circular progress
- 4 key metric cards (Demand, Inventory, Machines, Production)
- Active alerts list with severity indicators
- Real-time updates every 30 seconds

### 2. **Pipeline Runner**
- Execute full 5-agent analysis with one click
- Live progress tracking for each agent
- Beautiful animations showing agent execution
- Results display with export option
- Recent runs history

### 3. **Demand Intelligence**
- Multi-scenario forecast visualization
- Interactive charts (Recharts)
- AI insights and anomaly detection
- Trend analysis with recommendations

### 4. **Ask AMIS** (Chat Interface)
- Natural language queries
- AI routes to correct agent automatically
- Suggested questions to get started
- Live response streaming
- Beautiful conversation UI

---

## 🏗️ Project Structure

```
amis_phase_final/
├── backend/
│   ├── main.py                 # FastAPI application
│   └── requirements.txt        # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   │   ├── Layout.jsx      # Main layout with sidebar
│   │   │   ├── Card.jsx        # Card components
│   │   │   └── Badge.jsx       # Badge component
│   │   ├── pages/              # Page components
│   │   │   ├── Dashboard.jsx   # Main dashboard
│   │   │   ├── Pipeline.jsx    # Pipeline runner
│   │   │   ├── DemandIntelligence.jsx
│   │   │   ├── InventoryControl.jsx
│   │   │   ├── MachineHealth.jsx
│   │   │   ├── ProductionPlanning.jsx
│   │   │   ├── SupplierManagement.jsx
│   │   │   └── Chat.jsx        # AI chat interface
│   │   ├── lib/
│   │   │   ├── api.js          # API client
│   │   │   └── utils.js        # Utility functions
│   │   ├── App.jsx             # Main app component
│   │   ├── main.jsx            # Entry point
│   │   └── index.css           # Global styles
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── agents/                     # AI agents (existing)
├── tools/                      # Agent tools (existing)
├── data/                       # Sample data (existing)
├── prompts/                    # Agent prompts (existing)
└── .env                        # API key (create this!)
```

---

## 🎨 Tech Stack

### Frontend
- **React 18** - Modern UI framework
- **Vite** - Lightning-fast build tool
- **Tailwind CSS** - Utility-first styling
- **Framer Motion** - Smooth animations
- **Recharts** - Beautiful data visualization
- **React Query** - API data management
- **React Router** - Client-side routing
- **Lucide Icons** - Beautiful icons
- **Axios** - HTTP client

### Backend
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **LangChain** - AI agent framework
- **Anthropic Claude** - LLM reasoning

---

## 🔥 Key Features

### ✅ Production-Grade UI
- Responsive design (mobile, tablet, desktop)
- Smooth animations and transitions
- Professional color scheme
- Loading states and error handling
- Real-time data updates

### ✅ Professional Layout
- Collapsible sidebar navigation
- Top header with breadcrumbs
- Notification bell (with badge)
- Settings menu
- User avatar

### ✅ Advanced Components
- Animated metric cards
- Interactive charts
- Live progress tracking
- Chat interface with streaming
- Alert system with severity levels

### ✅ API Integration
- RESTful backend
- Async agent execution
- Background tasks
- Polling for results
- Error handling

---

## 🎪 Demo Flow for Hackathon

### 1. **Start with Dashboard** (30 seconds)
"Here's our manufacturing intelligence command center. You can see the system health score is 68/100 - we're at risk."

### 2. **Show Alerts** (15 seconds)
"The AI has detected 2 critical issues: Machine 002 has a 47% failure risk, and Product C is below reorder point."

### 3. **Run Pipeline** (90 seconds)
"Let's run a full analysis. Watch as 5 AI agents work together..."
- Click "Run Analysis"
- Show agents executing in real-time
- Display final orchestrator synthesis

### 4. **Show Demand Forecast** (30 seconds)
"The demand agent created a multi-scenario forecast with 3 possible outcomes..."

### 5. **Ask a Question** (45 seconds)
"You can ask AMIS anything in natural language..."
- Type: "Why is production attainment lower this week?"
- Show AI routing to correct agent
- Display intelligent response

**Total demo time: ~3.5 minutes**

---

## 🚀 Deployment Options

### Option A: Render.com (Recommended)

1. Push code to GitHub
2. Create new Web Service on Render
3. Connect GitHub repo
4. Set environment variables:
   - `ANTHROPIC_API_KEY=your-key`
5. Deploy!

### Option B: Streamlit Cloud (Backup)

If you want simpler deployment, we kept the Streamlit app:
```bash
cd amis_phase_final
streamlit run app.py
```

Then deploy to share.streamlit.io

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Make sure you're in backend/ directory
cd backend
python -m pip install -r requirements.txt
python main.py
```

### Frontend won't start
```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### CORS errors
Make sure backend is running on port 8000 and frontend on 5173. Check `backend/main.py` CORS settings.

### API key error
Double-check `.env` file exists in project root with:
```
ANTHROPIC_API_KEY=sk-ant-...
```

---

## 📝 Environment Variables

Create `.env` in project root:

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-api03-...

# Optional (for production)
VITE_API_URL=http://localhost:8000
```

---

## 🎯 Next Steps After Hackathon

1. **Add Real Data** - Connect to PostgreSQL instead of sample data
2. **Add Authentication** - JWT auth for multi-tenant
3. **Expand Charts** - More interactive visualizations
4. **Add Notifications** - Email/Slack alerts
5. **Mobile App** - React Native version
6. **ERP Connectors** - SAP, Oracle integration

---

## 📚 API Endpoints

### Health
- `GET /` - Health check
- `GET /api/health` - Detailed health

### Dashboard
- `GET /api/dashboard/summary` - Dashboard data

### Agents
- `POST /api/agents/run` - Run single agent
- `GET /api/agents/runs/{run_id}` - Get agent results

### Pipeline
- `POST /api/pipeline/run` - Run full pipeline
- `GET /api/pipeline/runs/{run_id}` - Get pipeline results
- `GET /api/pipeline/runs` - List recent runs

### Chat
- `POST /api/chat` - Send message to AI

---

## 🏆 Hackathon Pitch Deck Outline

### Slide 1: Problem
"Manufacturing plants lose $111K/year from stockouts because humans can't process data from 5 different systems fast enough"

### Slide 2: Solution
"AMIS uses 6 AI agents that reason across demand, inventory, machines, production, and suppliers simultaneously"

### Slide 3: Demo
[Show live dashboard]

### Slide 4: Magic Moment
"Watch the agents discover a hidden risk that no single system would catch"

### Slide 5: Tech
- Multi-agent AI with Claude Sonnet
- Cross-domain reasoning
- Explainable recommendations
- Production-ready React + FastAPI

### Slide 6: Market
- $50M revenue manufacturers
- $280K-$900K annual value per customer
- $3K-$8K/month SaaS pricing

---

## 💡 Tips for Success

1. **Practice the demo** - Know your flow cold
2. **Have backup** - Screenshots if API is slow
3. **Show the AI reasoning** - That's your differentiator
4. **Emphasize cross-domain** - No other tool does this
5. **Be confident** - You built something genuinely impressive

---

## 🤝 Support

If you run into issues during setup:
1. Check all paths are correct (Windows backslashes!)
2. Verify Python and Node versions
3. Make sure both servers are running
4. Check browser console for errors

---

## 🎉 You're Ready!

You now have a production-grade manufacturing AI system that would take most teams 6+ months to build. Your agents are the hard part - the UI just makes them shine.

**Good luck at the hackathon! 🚀**
