# 🚀 START HERE - Complete Setup Instructions

## Current Status
✅ Python 3.13.5 installed
❌ Node.js needs to be installed
❌ .env file needs to be created

---

## Step 1: Install Node.js (5 minutes)

### Option A: Using Installer (Recommended)
1. Go to: https://nodejs.org/
2. Download the **LTS version** (Long Term Support)
3. Run the installer
4. Check "Automatically install necessary tools" box
5. Complete installation
6. **Restart your terminal/command prompt**

### Option B: Using Chocolatey (Windows)
```bash
choco install nodejs-lts
```

### Verify Installation
Open a **NEW** terminal and run:
```bash
node --version
npm --version
```

You should see version numbers (e.g., v20.x.x and 10.x.x)

---

## Step 2: Create .env File with Your API Key (1 minute)

### Get Your Anthropic API Key
1. Go to: https://console.anthropic.com/
2. Sign in or create account
3. Go to **API Keys** section
4. Create a new API key
5. Copy the key (starts with `sk-ant-api03-...`)

### Create .env File
**Option A: Using Notepad (Easy)**
1. Open Notepad
2. Type this (replace with YOUR key):
   ```
   ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
   ```
3. Save As: `.env` (with the dot!)
4. Save in: `C:\Users\user\Downloads\amis_phase1__data_flow_crises_output\amis_phase_final\`
5. Save as type: **All Files** (not .txt!)

**Option B: Using Command Line**
```bash
# In project root directory
echo ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here > .env
```

### Verify .env File
```bash
cat .env
# Should show: ANTHROPIC_API_KEY=sk-ant-...
```

---

## Step 3: Install Backend Dependencies (2 minutes)

```bash
# Make sure you're in project root
cd C:\Users\user\Downloads\amis_phase1__data_flow_crises_output\amis_phase_final

# Install Python packages
cd backend
pip install -r requirements.txt

# Go back to root
cd ..
```

If you get errors, try:
```bash
pip install --upgrade pip
pip install -r backend/requirements.txt
```

---

## Step 4: Install Frontend Dependencies (3 minutes)

```bash
# From project root
cd frontend
npm install
```

**Note:** This will take 2-3 minutes. That's normal! It's installing ~500 packages.

If you see warnings, that's usually okay. Errors are problems, warnings are just notices.

---

## Step 5: Start Backend Server (Terminal 1)

Open a terminal and run:
```bash
cd C:\Users\user\Downloads\amis_phase1__data_flow_crises_output\amis_phase_final\backend
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

✅ **Backend is running!** Leave this terminal open.

---

## Step 6: Start Frontend Server (Terminal 2)

Open a **NEW** terminal window and run:
```bash
cd C:\Users\user\Downloads\amis_phase1__data_flow_crises_output\amis_phase_final\frontend
npm run dev
```

You should see:
```
  VITE v5.0.11  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

✅ **Frontend is running!** Leave this terminal open too.

---

## Step 7: Open in Browser

1. Open your web browser
2. Go to: **http://localhost:5173**
3. You should see the AMIS Dashboard! 🎉

---

## 🎯 Quick Test

### Test the Pipeline:
1. Click **"Run Pipeline"** in the sidebar
2. Click the **"Run Analysis"** button
3. Watch the 5 agents execute (takes ~30-60 seconds)
4. See the results!

### Test the Chat:
1. Click **"Ask AMIS"** in the sidebar
2. Type: "What is the stockout risk for Product A?"
3. Watch the AI respond!

---

## 🐛 Troubleshooting

### Problem: "Cannot find module"
**Solution:**
```bash
cd backend
pip install python-dotenv fastapi uvicorn
```

### Problem: "ANTHROPIC_API_KEY not found"
**Solution:** Check your .env file:
```bash
# Should be in project root (amis_phase_final/)
cat .env
# Should show: ANTHROPIC_API_KEY=sk-ant-...
```

### Problem: "Port 8000 already in use"
**Solution:** Kill the existing process:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F

# Or just change the port in backend/main.py
# Line at bottom: uvicorn.run(app, host="0.0.0.0", port=8001)
```

### Problem: Frontend won't start
**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Problem: "npm command not found"
**Solution:** Node.js didn't install correctly. Try:
1. Uninstall Node.js
2. Reinstall from nodejs.org
3. **Restart your computer**
4. Try again

---

## 📁 Quick Reference

### Project Structure
```
amis_phase_final/
├── .env                    ← YOUR API KEY HERE!
├── backend/
│   └── main.py            ← Backend server
└── frontend/
    └── src/               ← React app
```

### Important Commands
```bash
# Check if .env exists
cat .env

# Start backend
cd backend && python main.py

# Start frontend (new terminal)
cd frontend && npm run dev

# View in browser
http://localhost:5173
```

---

## ✅ Success Checklist

Before demo/hackathon, verify:

- [ ] Node.js installed (`node --version` works)
- [ ] .env file exists with valid API key
- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Browser shows AMIS dashboard
- [ ] Pipeline runs successfully
- [ ] Chat responds to questions

---

## 🎉 You're Ready!

Once everything is running, check out:
- **HACKATHON_SETUP.md** - Full documentation
- **PHASE1_COMPLETE.md** - What we built
- **README_REACT.md** - Technical details

---

## 💡 Pro Tips

1. **Keep both terminals open** while working
2. **Backend logs** show what agents are doing
3. **Browser console** (F12) shows frontend errors
4. **Refresh browser** if something looks weird
5. **Restart servers** if things stop working

---

## 🆘 Still Stuck?

1. Check both terminals for error messages
2. Verify .env file is in the **root** directory (not in backend/)
3. Make sure ports 8000 and 5173 aren't blocked
4. Try running in **PowerShell as Administrator**

---

**Good luck with your hackathon! 🚀**
