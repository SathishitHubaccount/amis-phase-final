# ⚡ AMIS Quick Start - 5 Minutes to Running

## Step-by-Step Setup

### 1️⃣ Get Your API Key
Get an Anthropic API key from: https://console.anthropic.com/

### 2️⃣ Create .env File
```bash
# In the project root (amis_phase_final/)
echo ANTHROPIC_API_KEY=your-key-here > .env
```

### 3️⃣ Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 4️⃣ Install Frontend Dependencies
```bash
cd ../frontend
npm install
```

### 5️⃣ Start Backend (Terminal 1)
```bash
cd backend
python main.py
```
✅ Backend running on http://localhost:8000

### 6️⃣ Start Frontend (Terminal 2)
```bash
cd frontend
npm run dev
```
✅ Frontend running on http://localhost:5173

### 7️⃣ Open Browser
Navigate to: **http://localhost:5173**

## 🎉 You're Done!

You should see:
- ✅ Beautiful dashboard with system health score
- ✅ Sidebar navigation
- ✅ Working Pipeline Runner
- ✅ AI Chat interface

## 🔥 Try This First

1. **Click "Run Pipeline"** on sidebar
2. **Click "Run Analysis"** button
3. **Watch agents execute in real-time** (takes ~30-60 seconds)
4. **See the orchestrator synthesis**

Then try:
- **Go to "Ask AMIS"**
- **Type:** "Why is Machine 2 at risk?"
- **Hit Enter** and watch AI respond!

## 🐛 Something Not Working?

### Backend won't start?
```bash
pip install python-dotenv
```

### Frontend won't start?
```bash
npm install --legacy-peer-deps
```

### Can't find API key?
Make sure `.env` file is in `amis_phase_final/` root directory (not in backend/)

---

**Need more help?** See `HACKATHON_SETUP.md` for detailed instructions.
