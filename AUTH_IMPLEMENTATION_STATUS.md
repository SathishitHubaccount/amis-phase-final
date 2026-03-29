# Authentication Implementation Status

## ✅ COMPLETED

1. **Installed Dependencies** ✅
   - `python-jose[cryptography]` - JWT token handling
   - `passlib[bcrypt]` - Password hashing
   - `python-multipart` - Form data handling

2. **Created auth.py Module** ✅
   - Location: `backend/auth.py`
   - JWT token creation and validation
   - Password hashing (bcrypt)
   - Role-based access control functions
   - OAuth2 password bearer scheme

## ⏳ REMAINING TASKS

### 1. Update database.py (15 minutes)

Add these functions to `backend/database.py`:

```python
# Add at the end of the file

# ============================================================================
# USER AUTHENTICATION OPERATIONS
# ============================================================================

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
    print("[OK] Users table created")

def create_default_users():
    """Create default admin and manager users"""
    from auth import get_password_hash

    conn = get_db_connection()

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

    # Default operator user
    conn.execute("""
        INSERT OR IGNORE INTO users (username, email, full_name, hashed_password, role)
        VALUES (?, ?, ?, ?, ?)
    """, ("operator", "operator@amis.com", "Production Operator",
          get_password_hash("operator123"), "operator"))

    conn.commit()
    conn.close()
    print("[OK] Default users created: admin, manager, operator")

def get_user(username: str) -> Optional[Dict]:
    """Get user by username"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return dict(user)
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

### 2. Initialize Users Table (5 minutes)

Run this command once:

```bash
cd backend
python -c "from database import create_users_table, create_default_users; create_users_table(); create_default_users()"
```

This creates:
- `admin` / `admin123` (admin role)
- `manager` / `manager123` (manager role)
- `operator` / `operator123` (operator role)

### 3. Add Auth Endpoints to main.py (10 minutes)

Add these imports at the top of `backend/main.py`:

```python
from fastapi.security import OAuth2PasswordRequestForm
from auth import (
    create_access_token, get_current_active_user, verify_password,
    require_role, Token, User, ACCESS_TOKEN_EXPIRE_MINUTES
)
from datetime import timedelta
from database import get_user, update_last_login
```

Add these endpoints before the machine endpoints:

```python
# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.post("/api/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login endpoint - returns JWT token

    Default users:
    - admin / admin123
    - manager / manager123
    - operator / operator123
    """
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

@app.get("/api/auth/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current logged-in user info"""
    return current_user

@app.get("/api/auth/health")
async def auth_health():
    """Check if authentication system is working"""
    return {"status": "ok", "auth_enabled": True}
```

### 4. Protect Sensitive Endpoints (Optional - 10 minutes)

Add authentication to sensitive operations like inventory adjustment:

```python
# Example: Protect inventory adjustment
@app.post("/api/inventory/{product_id}/adjust")
async def adjust_inventory_endpoint(
    product_id: str,
    adjustment: dict,
    current_user: User = Depends(require_role(["admin", "manager"]))  # ADD THIS
):
    # Only admin and manager can adjust inventory
    # Rest of function...
```

### 5. Frontend Login Page (20 minutes)

Create `frontend/src/pages/Login.jsx` - copy the code from IMPLEMENTATION_ROADMAP.md (lines 365-470)

### 6. Update Frontend Routing (5 minutes)

Add to `frontend/src/App.jsx`:

```jsx
import Login from './pages/Login'

// In the Routes section:
<Route path="/login" element={<Login />} />
```

### 7. Test Authentication (10 minutes)

1. Restart backend
2. Go to http://localhost:5173/login
3. Try logging in with `admin` / `admin123`
4. Should see JWT token in browser console
5. Should redirect to dashboard

---

## QUICK START (90 minutes total)

```bash
# Step 1: Update database.py (copy functions from above)
# ... add functions to database.py ...

# Step 2: Initialize users table
cd backend
python -c "from database import create_users_table, create_default_users; create_users_table(); create_default_users()"

# Step 3: Update main.py (copy auth endpoints from above)
# ... add imports and endpoints to main.py ...

# Step 4: Kill all old processes and restart
taskkill //F //IM python.exe //T
cd backend
python main.py

# Step 5: Create Login page
# ... create frontend/src/pages/Login.jsx ...

# Step 6: Update App.jsx routing
# ... add login route ...

# Step 7: Restart frontend
cd frontend
npm run dev

# Step 8: Test
# Go to http://localhost:5173/login
# Login with admin / admin123
```

---

## FILES TO MODIFY

1. ✅ `backend/auth.py` - DONE
2. ⏳ `backend/database.py` - ADD user functions
3. ⏳ `backend/main.py` - ADD auth endpoints
4. ⏳ `frontend/src/pages/Login.jsx` - CREATE new file
5. ⏳ `frontend/src/App.jsx` - ADD login route

---

## TESTING CHECKLIST

- [ ] Users table created in database
- [ ] Default users (admin, manager, operator) created
- [ ] Login endpoint returns JWT token
- [ ] `/api/auth/me` returns user info with valid token
- [ ] Login page loads at `/login`
- [ ] Can login with admin/admin123
- [ ] Token stored in localStorage
- [ ] Redirects to dashboard after login
- [ ] Invalid credentials show error message

---

## NEXT PHASE (After Auth Works)

Once authentication is working, implement:

1. **Notification System** (3-5 days)
2. **CSV Export** (1-2 days)
3. **Mobile Responsiveness** (1-2 weeks)

All code is ready in IMPLEMENTATION_ROADMAP.md!

---

## CURRENT STATUS: 30% COMPLETE

- ✅ Dependencies installed
- ✅ auth.py created
- ⏳ database.py needs user functions
- ⏳ main.py needs auth endpoints
- ⏳ Frontend Login page needed
- ⏳ Testing required

**Estimated Time to Finish:** 60-75 minutes of focused work
