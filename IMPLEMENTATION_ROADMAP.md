# AMIS - Production Implementation Roadmap
**Goal:** Fix all critical gaps to make AMIS production-ready
**Timeline:** 4-6 weeks
**Team:** 2-3 developers

---

## CRITICAL GAPS TO IMPLEMENT

### **Priority 1: Security & Authentication (Week 1-2)**
### **Priority 2: Notifications & Alerts (Week 2-3)**
### **Priority 3: Data Export (Week 3-4)**
### **Priority 4: Mobile Responsiveness (Week 4-6)**

---

# PRIORITY 1: USER AUTHENTICATION & AUTHORIZATION

## Overview
**Current State:** Anyone can access all pages, no login required, no audit trail
**Target State:** Role-based access control (RBAC) with user management
**Timeline:** 1.5-2 weeks
**Complexity:** HIGH

## Implementation Approach

### Backend: JWT Authentication with FastAPI

**Step 1: Install Dependencies**
```bash
pip install python-jose[cryptography] passlib[bcrypt] python-multipart
```

**Step 2: Create Authentication Module**

File: `backend/auth.py`
```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

# Configuration
SECRET_KEY = "your-secret-key-here-change-in-production"  # Store in .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# User model
class User(BaseModel):
    username: str
    email: str
    full_name: str
    role: str  # admin, manager, operator, viewer
    disabled: bool = False

class UserInDB(User):
    hashed_password: str

# Token models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Password hashing
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# JWT token creation
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Get current user from token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Role-based authorization
def require_role(required_roles: list):
    def role_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {required_roles}"
            )
        return current_user
    return role_checker
```

**Step 3: Create User Database Schema**

File: `backend/database.py` (add these functions)
```python
def create_users_table():
    """Create users table for authentication"""
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            hashed_password TEXT NOT NULL,
            role TEXT NOT NULL,
            disabled BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def create_default_users():
    """Create default admin user"""
    conn = get_db_connection()
    from auth import get_password_hash

    # Default admin user
    conn.execute("""
        INSERT OR IGNORE INTO users (username, email, full_name, hashed_password, role)
        VALUES (?, ?, ?, ?, ?)
    """, ("admin", "admin@amis.com", "System Administrator",
          get_password_hash("admin123"), "admin"))

    # Default manager user
    conn.execute("""
        INSERT OR IGNORE INTO users (username, email, full_name, hashed_password, role)
        VALUES (?, ?, ?, ?, ?)
    """, ("manager", "manager@amis.com", "Plant Manager",
          get_password_hash("manager123"), "manager"))

    conn.commit()
    conn.close()

def get_user(username: str):
    """Get user by username"""
    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()
    conn.close()

    if user:
        return {
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"],
            "hashed_password": user["hashed_password"],
            "role": user["role"],
            "disabled": bool(user["disabled"])
        }
    return None

def update_last_login(username: str):
    """Update last login timestamp"""
    conn = get_db_connection()
    conn.execute(
        "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE username = ?",
        (username,)
    )
    conn.commit()
    conn.close()
```

**Step 4: Add Authentication Endpoints to main.py**

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from auth import (
    create_access_token, get_current_active_user, verify_password,
    require_role, Token, User, ACCESS_TOKEN_EXPIRE_MINUTES
)
from datetime import timedelta

# Login endpoint
@app.post("/api/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )

    update_last_login(user["username"])

    return {"access_token": access_token, "token_type": "bearer"}

# Get current user info
@app.get("/api/auth/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

# Protected endpoint example
@app.post("/api/inventory/{product_id}/adjust")
async def adjust_inventory_protected(
    product_id: str,
    adjustment: dict,
    current_user: User = Depends(require_role(["admin", "manager"]))
):
    # Only admin and manager can adjust inventory
    # Rest of the function...
```

**Step 5: Frontend Login Page**

File: `frontend/src/pages/Login.jsx`
```jsx
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Lock, User, AlertCircle } from 'lucide-react'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const formData = new FormData()
      formData.append('username', username)
      formData.append('password', password)

      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Invalid credentials')
      }

      const data = await response.json()

      // Store token in localStorage
      localStorage.setItem('access_token', data.access_token)

      // Fetch user info
      const userResponse = await fetch('http://localhost:8000/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${data.access_token}`
        }
      })

      const userData = await userResponse.json()
      localStorage.setItem('user', JSON.stringify(userData))

      // Redirect to dashboard
      navigate('/dashboard')
    } catch (err) {
      setError('Invalid username or password')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-block p-3 bg-indigo-100 rounded-full mb-4">
            <Lock className="w-8 h-8 text-indigo-600" />
          </div>
          <h1 className="text-3xl font-bold text-gray-800">AMIS Login</h1>
          <p className="text-gray-600 mt-2">Autonomous Manufacturing Intelligence System</p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Username
            </label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="Enter your username"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="Enter your password"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div className="mt-8 pt-6 border-t border-gray-200">
          <p className="text-center text-sm text-gray-600">
            Default credentials:<br />
            <span className="font-mono text-xs">admin / admin123</span> or{' '}
            <span className="font-mono text-xs">manager / manager123</span>
          </p>
        </div>
      </div>
    </div>
  )
}
```

**Step 6: Protected API Client**

File: `frontend/src/api/client.js` (modify to include auth)
```javascript
const getAuthToken = () => localStorage.getItem('access_token')

const authFetch = async (url, options = {}) => {
  const token = getAuthToken()

  const headers = {
    ...options.headers,
    ...(token && { 'Authorization': `Bearer ${token}` })
  }

  const response = await fetch(url, { ...options, headers })

  if (response.status === 401) {
    // Token expired, redirect to login
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    window.location.href = '/login'
    throw new Error('Unauthorized')
  }

  return response
}

// Update all API calls to use authFetch instead of fetch
export const apiClient = {
  getDashboardSummary: () => authFetch(`${API_BASE_URL}/dashboard/summary`).then(r => r.json()),
  getMachines: () => authFetch(`${API_BASE_URL}/machines`).then(r => r.json()),
  // ... rest of API calls
}
```

---

# PRIORITY 2: NOTIFICATION SYSTEM

## Overview
**Current State:** Alerts only visible in dashboard, easy to miss
**Target State:** Real-time browser notifications + optional email alerts
**Timeline:** 3-5 days
**Complexity:** MEDIUM

## Implementation Approach

### Backend: Alert Management System

File: `backend/notifications.py`
```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from datetime import datetime
import os

# Email configuration (from .env)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@amis.com")

def send_email_alert(to_emails: List[str], subject: str, body: str, html_body: Optional[str] = None):
    """Send email alert to recipients"""
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        print("Email credentials not configured, skipping email send")
        return False

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = FROM_EMAIL
        msg['To'] = ', '.join(to_emails)

        # Add plain text body
        part1 = MIMEText(body, 'plain')
        msg.attach(part1)

        # Add HTML body if provided
        if html_body:
            part2 = MIMEText(html_body, 'html')
            msg.attach(part2)

        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)

        print(f"Email sent successfully to {to_emails}")
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False

def create_machine_failure_alert_email(machine_id: str, failure_risk: float):
    """Generate email for machine failure alert"""
    subject = f"🚨 URGENT: Machine {machine_id} High Failure Risk ({failure_risk}%)"

    body = f"""
CRITICAL ALERT - AMIS Manufacturing Intelligence System

Machine: {machine_id}
Failure Risk: {failure_risk}%
Status: CRITICAL - IMMEDIATE ACTION REQUIRED
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This machine has exceeded the critical failure risk threshold and requires immediate attention.

Recommended Actions:
1. Schedule maintenance within 48 hours
2. Review machine sensor data for anomalies
3. Prepare backup production capacity
4. Contact maintenance team immediately

Login to AMIS for detailed analysis: http://localhost:5173/machine-health

This is an automated alert from AMIS. Do not reply to this email.
"""

    html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9fafb;">
        <div style="background-color: #dc2626; color: white; padding: 20px; border-radius: 8px 8px 0 0;">
            <h1 style="margin: 0; font-size: 24px;">🚨 CRITICAL ALERT</h1>
            <p style="margin: 10px 0 0 0;">Machine Failure Risk Detected</p>
        </div>

        <div style="background-color: white; padding: 30px; border-radius: 0 0 8px 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                <tr>
                    <td style="padding: 10px; background-color: #f3f4f6; font-weight: bold;">Machine ID:</td>
                    <td style="padding: 10px; background-color: #fff;">{machine_id}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; background-color: #f3f4f6; font-weight: bold;">Failure Risk:</td>
                    <td style="padding: 10px; background-color: #fff;"><span style="color: #dc2626; font-weight: bold; font-size: 18px;">{failure_risk}%</span></td>
                </tr>
                <tr>
                    <td style="padding: 10px; background-color: #f3f4f6; font-weight: bold;">Status:</td>
                    <td style="padding: 10px; background-color: #fff;"><span style="color: #dc2626; font-weight: bold;">CRITICAL</span></td>
                </tr>
                <tr>
                    <td style="padding: 10px; background-color: #f3f4f6; font-weight: bold;">Timestamp:</td>
                    <td style="padding: 10px; background-color: #fff;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td>
                </tr>
            </table>

            <div style="background-color: #fef2f2; border-left: 4px solid #dc2626; padding: 15px; margin-bottom: 20px;">
                <strong>⚠️ IMMEDIATE ACTION REQUIRED</strong>
                <p style="margin: 10px 0 0 0;">This machine has exceeded the critical failure risk threshold and requires immediate attention.</p>
            </div>

            <h3 style="color: #1f2937; margin-top: 20px;">Recommended Actions:</h3>
            <ol style="color: #4b5563;">
                <li>Schedule maintenance within 48 hours</li>
                <li>Review machine sensor data for anomalies</li>
                <li>Prepare backup production capacity</li>
                <li>Contact maintenance team immediately</li>
            </ol>

            <div style="text-align: center; margin-top: 30px;">
                <a href="http://localhost:5173/machine-health" style="display: inline-block; background-color: #4f46e5; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; font-weight: bold;">View Detailed Analysis</a>
            </div>
        </div>

        <div style="text-align: center; margin-top: 20px; color: #6b7280; font-size: 12px;">
            <p>This is an automated alert from AMIS. Do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
"""

    return subject, body, html_body
```

### Backend: WebSocket for Real-Time Notifications

File: `backend/main.py` (add WebSocket support)
```python
from fastapi import WebSocket, WebSocketDisconnect
from typing import List
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                # Connection closed, remove it
                self.disconnect(connection)

manager = ConnectionManager()

@app.websocket("/ws/notifications")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Echo back (optional)
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Function to send real-time notification
async def send_realtime_notification(severity: str, title: str, category: str):
    notification = {
        "severity": severity,
        "title": title,
        "category": category,
        "created_at": datetime.now().isoformat()
    }
    await manager.broadcast(notification)
```

### Frontend: Notification Component

File: `frontend/src/components/NotificationCenter.jsx`
```jsx
import { useState, useEffect } from 'react'
import { Bell, X, AlertCircle, AlertTriangle, Info } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

export default function NotificationCenter() {
  const [notifications, setNotifications] = useState([])
  const [showPanel, setShowPanel] = useState(false)
  const [ws, setWs] = useState(null)

  useEffect(() => {
    // Request browser notification permission
    if ('Notification' in window) {
      Notification.requestPermission()
    }

    // Connect to WebSocket for real-time notifications
    const websocket = new WebSocket('ws://localhost:8000/ws/notifications')

    websocket.onmessage = (event) => {
      const notification = JSON.parse(event.data)

      // Add to notification list
      setNotifications(prev => [notification, ...prev].slice(0, 50))

      // Show browser notification
      if (Notification.permission === 'granted' && notification.severity === 'critical') {
        new Notification(notification.title, {
          body: `Category: ${notification.category}`,
          icon: '/amis-icon.png',
          tag: notification.created_at
        })
      }

      // Play alert sound for critical notifications
      if (notification.severity === 'critical') {
        const audio = new Audio('/alert-sound.mp3')
        audio.play().catch(() => {})
      }
    }

    setWs(websocket)

    return () => {
      if (websocket) {
        websocket.close()
      }
    }
  }, [])

  const unreadCount = notifications.filter(n => !n.read).length

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical':
        return <AlertCircle className="w-5 h-5 text-red-600" />
      case 'high':
        return <AlertTriangle className="w-5 h-5 text-orange-600" />
      default:
        return <Info className="w-5 h-5 text-blue-600" />
    }
  }

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-50 border-red-200'
      case 'high':
        return 'bg-orange-50 border-orange-200'
      default:
        return 'bg-blue-50 border-blue-200'
    }
  }

  return (
    <>
      {/* Notification Bell Icon */}
      <button
        onClick={() => setShowPanel(!showPanel)}
        className="relative p-2 rounded-lg hover:bg-gray-100 transition-colors"
      >
        <Bell className="w-6 h-6 text-gray-700" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-600 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-semibold">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {/* Notification Panel */}
      <AnimatePresence>
        {showPanel && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            className="absolute right-0 top-16 w-96 bg-white rounded-lg shadow-2xl border border-gray-200 z-50"
          >
            <div className="p-4 border-b border-gray-200 flex items-center justify-between">
              <h3 className="font-semibold text-gray-800">Notifications</h3>
              <button
                onClick={() => setShowPanel(false)}
                className="p-1 hover:bg-gray-100 rounded"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="max-h-96 overflow-y-auto">
              {notifications.length === 0 ? (
                <div className="p-8 text-center text-gray-500">
                  <Bell className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                  <p>No notifications</p>
                </div>
              ) : (
                notifications.map((notif, idx) => (
                  <div
                    key={idx}
                    className={`p-4 border-b border-gray-100 ${getSeverityColor(notif.severity)} ${
                      !notif.read ? 'bg-opacity-100' : 'bg-opacity-50'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      {getSeverityIcon(notif.severity)}
                      <div className="flex-1">
                        <p className="font-medium text-sm text-gray-800">{notif.title}</p>
                        <p className="text-xs text-gray-600 mt-1">{notif.category}</p>
                        <p className="text-xs text-gray-500 mt-1">
                          {new Date(notif.created_at).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}
```

---

# PRIORITY 3: DATA EXPORT TO CSV/EXCEL

## Overview
**Current State:** No way to export data for external analysis
**Target State:** Export buttons on all major pages
**Timeline:** 1-2 days per page
**Complexity:** LOW-MEDIUM

## Implementation Approach

### Backend: Export Endpoints

File: `backend/main.py` (add export endpoints)
```python
from fastapi.responses import StreamingResponse
import csv
import io

@app.get("/api/machines/export")
async def export_machines_csv():
    """Export all machines to CSV"""
    machines = get_all_machines()

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        'ID', 'Name', 'Type', 'Line', 'Status', 'OEE',
        'Availability', 'Performance', 'Quality', 'Failure Risk',
        'Capacity', 'Utilization', 'Last Maintenance', 'Next Maintenance'
    ])

    # Write data
    for machine in machines:
        writer.writerow([
            machine['id'], machine['name'], machine['type'], machine['line'],
            machine['status'], machine['oee'], machine['availability'],
            machine['performance'], machine['quality'], machine['failure_risk'],
            machine['production_capacity'], machine['current_utilization'],
            machine['last_maintenance'], machine['next_maintenance']
        ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=machines_export.csv"}
    )

@app.get("/api/inventory/export")
async def export_inventory_csv():
    """Export all inventory to CSV"""
    products = get_all_products()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        'Product ID', 'Product Name', 'Current Stock', 'Reorder Point',
        'Lead Time', 'Avg Daily Usage', 'Days Supply', 'Stockout Risk %',
        'Unit Cost', 'Total Value'
    ])

    for product in products:
        inventory = get_inventory(product['id'])
        if inventory:
            writer.writerow([
                product['id'], product['name'], inventory.get('current_stock', 0),
                inventory.get('reorder_point', 0), inventory.get('lead_time', 0),
                inventory.get('avg_daily_usage', 0), inventory.get('days_supply', 0),
                inventory.get('stockout_risk', 0), product.get('unit_cost', 0),
                inventory.get('current_stock', 0) * product.get('unit_cost', 0)
            ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=inventory_export.csv"}
    )
```

### Frontend: Export Button Component

File: `frontend/src/components/ExportButton.jsx`
```jsx
import { Download } from 'lucide-react'
import { useState } from 'react'

export default function ExportButton({ endpoint, filename, label = "Export to CSV" }) {
  const [loading, setLoading] = useState(false)

  const handleExport = async () => {
    setLoading(true)
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`http://localhost:8000/api/${endpoint}/export`, {
        headers: {
          ...(token && { 'Authorization': `Bearer ${token}` })
        }
      })

      if (!response.ok) {
        throw new Error('Export failed')
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename || 'export.csv'
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      alert('Failed to export data. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <button
      onClick={handleExport}
      disabled={loading}
      className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
    >
      <Download className="w-4 h-4" />
      {loading ? 'Exporting...' : label}
    </button>
  )
}
```

---

# PRIORITY 4: MOBILE RESPONSIVENESS

## Overview
**Current State:** Desktop-only, doesn't work on tablets/phones
**Target State:** Fully responsive for all screen sizes
**Timeline:** 1-2 weeks
**Complexity:** MEDIUM

## Implementation Approach

Update Tailwind CSS classes to use responsive breakpoints:

```jsx
// Before (Desktop only)
<div className="grid grid-cols-4 gap-6">

// After (Responsive)
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6">

// Before (Fixed width)
<div className="w-64">

// After (Responsive width)
<div className="w-full sm:w-64">

// Before (Large padding)
<div className="p-8">

// After (Responsive padding)
<div className="p-4 md:p-6 lg:p-8">
```

Add mobile navigation menu:

File: `frontend/src/components/MobileNav.jsx`
```jsx
import { useState } from 'react'
import { Menu, X } from 'lucide-react'
import { Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'

export default function MobileNav({ navItems }) {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div className="lg:hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="p-2 rounded-lg hover:bg-gray-100"
      >
        {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="absolute top-16 left-0 right-0 bg-white shadow-lg border-t border-gray-200 z-50"
          >
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setIsOpen(false)}
                className="block px-6 py-4 hover:bg-gray-50 border-b border-gray-100"
              >
                <div className="flex items-center gap-3">
                  {item.icon}
                  <span className="font-medium">{item.label}</span>
                </div>
              </Link>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
```

---

# TESTING CHECKLIST

## Authentication Testing
- [ ] Login with valid credentials
- [ ] Login with invalid credentials
- [ ] Token expiration handling
- [ ] Role-based access control (admin vs manager vs operator)
- [ ] Protected endpoints reject unauthenticated requests
- [ ] Logout functionality

## Notification Testing
- [ ] WebSocket connection establishes
- [ ] Browser notifications appear for critical alerts
- [ ] Email notifications sent (if configured)
- [ ] Notification panel shows all alerts
- [ ] Alert sound plays for critical notifications
- [ ] Unread count updates correctly

## Export Testing
- [ ] CSV export downloads correctly
- [ ] Export includes all relevant columns
- [ ] Export works with authentication
- [ ] File naming is appropriate
- [ ] Data accuracy matches UI display

## Mobile Testing
- [ ] Navigation menu works on mobile
- [ ] Charts render correctly on small screens
- [ ] Tables scroll horizontally on mobile
- [ ] Forms are usable on mobile
- [ ] Touch interactions work properly
- [ ] Layout doesn't break on different screen sizes

---

# DEPLOYMENT INSTRUCTIONS

## Step 1: Install Backend Dependencies
```bash
cd backend
pip install python-jose[cryptography] passlib[bcrypt] python-multipart
```

## Step 2: Initialize User Database
```python
# Run once to create users table and default users
python -c "from database import create_users_table, create_default_users; create_users_table(); create_default_users()"
```

## Step 3: Configure Email (Optional)
Add to `backend/.env`:
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@amis.com
```

## Step 4: Update Frontend Routes
Add login route to `frontend/src/App.jsx`:
```jsx
import Login from './pages/Login'

// In Routes:
<Route path="/login" element={<Login />} />
```

## Step 5: Restart Services
```bash
# Backend
cd backend
python main.py

# Frontend
cd frontend
npm run dev
```

## Step 6: Test Login
1. Navigate to http://localhost:5173/login
2. Login with: `admin` / `admin123`
3. Verify redirect to dashboard
4. Test protected endpoints

---

# TIMELINE SUMMARY

| Priority | Feature | Timeline | Status |
|----------|---------|----------|--------|
| 1 | Authentication & Authorization | 1.5-2 weeks | Code provided ✅ |
| 2 | Notification System | 3-5 days | Code provided ✅ |
| 3 | Data Export (CSV) | 1-2 days | Code provided ✅ |
| 4 | Mobile Responsiveness | 1-2 weeks | Guidelines provided ✅ |

**Total Estimated Timeline:** 4-6 weeks for full implementation

---

# NEXT STEPS

1. **Review this implementation guide**
2. **Start with Priority 1 (Authentication)** - Most critical for security
3. **Test thoroughly** - Use the testing checklist
4. **Deploy in stages** - Don't deploy all at once
5. **Get user feedback** - Iterate based on real usage
6. **Plan for Priority 2** - Notifications are the next most valuable feature

---

**Document Version:** 1.0
**Last Updated:** March 1, 2026
**Contact:** AMIS Development Team
