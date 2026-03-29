# 🧪 Agent Negotiation - Testing Guide

## Quick Start (5 minutes)

### Step 1: Start Backend Server

```bash
cd backend
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 2: Start Frontend

```bash
cd frontend
npm run dev
```

You should see:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
```

### Step 3: Open AMIS in Browser

1. Go to `http://localhost:5173`
2. Login with:
   - Username: `admin`
   - Password: `admin123`

### Step 4: Navigate to Agent Negotiation

1. Click **"Agent Negotiation"** in the sidebar (has Users icon 👥)
2. You'll see 4 scenario options:
   - **Demand Spike Crisis** (blue)
   - **Supplier Failure** (orange)
   - **Machine Breakdown** (red)
   - **Cost Reduction Pressure** (green)

### Step 5: Run Your First Negotiation

1. Select **"Demand Spike Crisis"** (default)
2. Review scenario details:
   - Customer wants: 2,000 units
   - Timeline: 3 days
   - Normal capacity: 1,500 units
   - Gap: 500 units SHORT
3. Click **"Start Agent Negotiation"** button
4. Watch the magic! 🎭

---

## What You'll See

### Round 1: Proposals (2 seconds)
```
🤖 Demand Agent: "Accept order - customer is high-value"
🤖 Production Agent: "Reject - cannot meet capacity"
🤖 Inventory Agent: "Use buffer + overtime"
```

### Round 2: Critiques (2 seconds)
```
💬 Demand → Production: "Rejecting loses $500K customer"
💬 Production → Inventory: "Overtime costs $6K"
💬 Inventory → Demand: "Buffer usage safe"
```

### Round 3: Consensus (2 seconds)
```
🎯 Synthesizing final recommendation...
```

### Final Result
```
✅ Consensus Reached

Final Decision:
[AI-generated comprehensive recommendation]

Agent Participation:
🔵 Demand Agent
🟣 Production Agent
🟢 Inventory Agent

All 3 agents contributed to this decision
```

---

## Testing Each Scenario

### 1. Demand Spike Crisis (Blue)
**What it simulates:**
- Customer emergency order
- Exceeds production capacity
- Tight deadline (3 days)
- Competitor bidding

**Expected outcome:**
- Agents debate accept vs. reject
- Production raises capacity concerns
- Inventory suggests buffer usage
- Final: Hybrid solution (buffer + overtime)

**Test this when:**
- Demonstrating multi-agent debate
- Showing capacity planning
- Illustrating trade-off analysis

---

### 2. Supplier Failure (Orange)
**What it simulates:**
- Primary supplier can't deliver
- Missing critical components
- Production at risk
- Alternative suppliers available (but more expensive)

**Expected outcome:**
- Agents evaluate alternative suppliers
- Cost vs. time trade-off analysis
- Production impact assessment
- Final: Multi-sourcing strategy

**Test this when:**
- Showing supply chain resilience
- Demonstrating risk mitigation
- Illustrating procurement decisions

---

### 3. Machine Breakdown (Red)
**What it simulates:**
- Critical equipment failure
- 5-day repair time
- $40K repair cost
- Alternative machine at 60% capacity

**Expected outcome:**
- Production impact analysis
- Repair vs. workaround debate
- Customer commitment evaluation
- Final: Parallel approach (repair + alternative)

**Test this when:**
- Showing crisis management
- Demonstrating contingency planning
- Illustrating maintenance decisions

---

### 4. Cost Reduction Pressure (Green)
**What it simulates:**
- Need to cut costs by 15%
- Must maintain quality
- Volume unchanged
- Multiple reduction levers available

**Expected outcome:**
- Agents propose different cost reduction areas
- Quality impact assessment
- Feasibility analysis
- Final: Multi-pronged cost reduction plan

**Test this when:**
- Showing strategic planning
- Demonstrating cost optimization
- Illustrating quality-cost balance

---

## Troubleshooting

### Error: "Negotiation Failed"
**Cause:** Backend server not running or wrong port

**Solution:**
```bash
# Check if backend is running
curl http://localhost:8000/api/products

# If error, restart backend
cd backend
python main.py
```

---

### Error: "Cannot read properties of undefined"
**Cause:** API response format mismatch

**Solution:**
Check browser console (F12) for actual error. Usually means:
- Agent returned unexpected format
- Need to update prompt structure

---

### Negotiation takes too long (>30 seconds)
**Cause:** Claude API slowness or complex prompts

**Solution:**
- Check your internet connection
- Verify Anthropic API key is valid
- Check API rate limits

---

### Agents return generic responses
**Cause:** Prompts not specific enough

**Solution:**
Edit `backend/agent_negotiation.py` and make prompts more specific:
```python
def _build_proposal_prompt(self, agent_name: str, scenario: Dict) -> str:
    # Add more context
    # Add specific constraints
    # Add expected format
```

---

## Advanced Testing

### Test Backend Directly (Without UI)

```bash
cd backend
curl -X POST http://localhost:8000/api/negotiation/run \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_type": "demand_spike",
    "product_id": "PROD-A",
    "customer_order": 2000,
    "timeline_days": 3
  }'
```

Expected response:
```json
{
  "status": "completed",
  "negotiation_id": "...",
  "scenario_type": "demand_spike",
  "result": {
    "round_1_proposals": {...},
    "round_2_critiques": {...},
    "round_3_consensus": {...}
  }
}
```

---

### Test with Custom Scenario

```javascript
// In browser console (F12) while on Negotiation page
fetch('http://localhost:8000/api/negotiation/run', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    scenario_type: 'custom',
    product_id: 'PROD-A',
    custom_constraints: {
      problem: 'Custom crisis scenario',
      deadline: '2 days',
      budget: 10000
    }
  })
})
.then(r => r.json())
.then(console.log)
```

---

## Demo Presentation Tips

### For Hackathon Judges

**Opening (30 sec):**
> "Traditional manufacturing decisions involve 5 departments meeting for hours.
> What if AI agents could debate these decisions in minutes? Let me show you."

**Demo (2 min):**
1. Show scenario selection (4 options)
2. Select "Demand Spike Crisis"
3. Click "Start Negotiation"
4. Narrate each round:
   - "Round 1: Each agent proposes from their perspective"
   - "Round 2: Agents critique each other - see the debate"
   - "Round 3: Consensus emerges - best of all perspectives"
5. Show final decision

**Key Points to Emphasize:**
- ✅ This is TRUE multi-agent collaboration (not sequential)
- ✅ Agents influence each other through debate
- ✅ Solves real manufacturing crisis scenarios
- ✅ Demonstrates cutting-edge agentic AI

**Closing:**
> "This shows how specialized AI agents can collaborate on complex decisions,
> just like human experts - but in minutes, not hours."

---

## Success Checklist

Before your presentation, verify:

- [ ] Backend starts without errors
- [ ] Frontend starts and connects to backend
- [ ] Can login successfully
- [ ] "Agent Negotiation" appears in sidebar
- [ ] All 4 scenarios are selectable
- [ ] At least one scenario completes successfully
- [ ] Final result displays properly
- [ ] Can run negotiation multiple times
- [ ] UI animations work smoothly
- [ ] No console errors (check F12)

---

## Known Limitations (Be Ready to Explain)

**Q: "Why do all scenarios take the same time?"**
A: "The timing is simulated for demo purposes. Real-world would depend on Claude API response time."

**Q: "Can you show the actual agent prompts?"**
A: "Yes! They're in `backend/agent_negotiation.py`. Each round has specific prompts for proposal, critique, and consensus."

**Q: "What if agents never reach consensus?"**
A: "Good question! In production, we'd add timeout and fallback to human decision. For demo, orchestrator synthesizes even from disagreement."

**Q: "How does this scale to 100 agents?"**
A: "Current implementation is 3 agents (manageable rounds). Scaling would need hierarchical negotiation or tournament-style debate."

---

## Performance Metrics

Expected performance:

| Metric | Target | Actual (measure yours) |
|--------|--------|------------------------|
| Time to start negotiation | < 1 second | ___ seconds |
| Round 1 completion | ~5-10 seconds | ___ seconds |
| Round 2 completion | ~5-10 seconds | ___ seconds |
| Round 3 completion | ~5-10 seconds | ___ seconds |
| Total negotiation time | ~20-30 seconds | ___ seconds |
| UI responsiveness | Smooth animations | ✅ / ❌ |
| Error rate | 0% (on retry) | ___ % |

---

## Next Steps After Testing

Once basic negotiation works:

1. **Polish UI animations** (make rounds more visual)
2. **Add more scenarios** (specific to your industry)
3. **Improve prompts** (get better agent responses)
4. **Add agent memory** (agents remember past negotiations)
5. **Create demo video** (for async judging)

---

## Quick Fixes for Common Issues

### Fix 1: CORS Error
```python
# In backend/main.py, verify CORS settings:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Must match frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Fix 2: Missing Icon
```bash
# If Users icon doesn't show, install lucide-react
cd frontend
npm install lucide-react
```

### Fix 3: Backend Not Found
```bash
# Check if process is running
# Windows:
netstat -ano | findstr :8000

# Mac/Linux:
lsof -i :8000

# If nothing, restart backend
cd backend
python main.py
```

---

## You're Ready! 🚀

Your agent negotiation system is now fully implemented and ready to demo!

**Final Pre-Demo Checklist:**
- ✅ Run both servers
- ✅ Test one complete negotiation
- ✅ Practice your narrative
- ✅ Have backup plan (video recording)
- ✅ Know your talking points
- ✅ Be ready for Q&A

**Good luck with your hackathon!** 🏆
