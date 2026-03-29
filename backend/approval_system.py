"""
AI Approval & Oversight System
Implements human-in-the-loop for AI-driven decisions

This is CRITICAL for production manufacturing where AI errors can cost millions.

Decision Framework:
- LOW RISK: Auto-approve (informational updates)
- MEDIUM RISK: Notify + Auto-approve with audit trail
- HIGH RISK: Require explicit approval before execution
- CRITICAL RISK: Require multi-level approval
"""
from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime
from database import get_db_connection, log_activity
import json


class RiskLevel(Enum):
    """Risk classification for AI decisions"""
    LOW = "low"              # Auto-approve: Analytics, forecasts
    MEDIUM = "medium"        # Notify + approve: Inventory adjustments < $10K
    HIGH = "high"            # Require approval: Production changes, large orders
    CRITICAL = "critical"    # Require multi-level: Major capital, plant shutdowns


class DecisionStatus(Enum):
    """Status of AI recommendation"""
    PENDING = "pending"           # Awaiting review
    APPROVED = "approved"         # Approved for execution
    REJECTED = "rejected"         # Rejected by human
    AUTO_APPROVED = "auto_approved"  # Low-risk, auto-approved
    EXECUTED = "executed"         # Already executed
    ROLLED_BACK = "rolled_back"   # Executed then reversed


class AIDecision:
    """Represents a single AI-driven decision requiring oversight"""

    def __init__(
        self,
        decision_type: str,
        action: str,
        description: str,
        risk_level: RiskLevel,
        impact_analysis: Dict,
        recommended_by: str = "AI System",
        requires_approval: bool = True
    ):
        self.id = None  # Set when saved to DB
        self.decision_type = decision_type
        self.action = action
        self.description = description
        self.risk_level = risk_level
        self.impact_analysis = impact_analysis
        self.recommended_by = recommended_by
        self.requires_approval = requires_approval
        self.status = DecisionStatus.PENDING
        self.created_at = datetime.now()
        self.reviewed_by = None
        self.reviewed_at = None
        self.rejection_reason = None
        self.executed_at = None
        self.payload = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "decision_type": self.decision_type,
            "action": self.action,
            "description": self.description,
            "risk_level": self.risk_level.value,
            "impact_analysis": self.impact_analysis,
            "recommended_by": self.recommended_by,
            "requires_approval": self.requires_approval,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "reviewed_by": self.reviewed_by,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "rejection_reason": self.rejection_reason,
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
            "payload": self.payload
        }


class ApprovalSystem:
    """
    Manages AI decision approvals with risk-based workflows

    Responsibilities:
    1. Classify decisions by risk level
    2. Auto-approve low-risk decisions
    3. Queue high-risk decisions for human review
    4. Track approval/rejection history
    5. Provide rollback capability
    """

    def __init__(self):
        self._init_approval_table()

    def _init_approval_table(self):
        """Create approval tracking table"""
        conn = get_db_connection()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ai_decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                decision_type TEXT NOT NULL,
                action TEXT NOT NULL,
                description TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                impact_analysis TEXT NOT NULL,
                recommended_by TEXT DEFAULT 'AI System',
                requires_approval INTEGER DEFAULT 1,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_by TEXT,
                reviewed_at TIMESTAMP,
                rejection_reason TEXT,
                executed_at TIMESTAMP,
                rollback_data TEXT
            )
        """)
        conn.commit()
        try:
            conn.execute("ALTER TABLE ai_decisions ADD COLUMN payload TEXT")
            conn.commit()
        except Exception:
            pass  # Column already exists
        conn.close()

    def classify_decision_risk(self, decision_type: str, impact: Dict) -> RiskLevel:
        """
        Classify decision risk based on type and financial impact

        Rules:
        - CRITICAL: Financial impact > $100K OR plant shutdown
        - HIGH: Financial impact $10K-$100K OR production schedule changes
        - MEDIUM: Financial impact $1K-$10K OR inventory adjustments
        - LOW: Financial impact < $1K OR read-only analytics
        """
        financial_impact = impact.get("financial_impact", 0)
        affects_production = impact.get("affects_production", False)
        affects_safety = impact.get("affects_safety", False)

        # Safety always critical
        if affects_safety:
            return RiskLevel.CRITICAL

        # Critical decisions
        if financial_impact > 100000:
            return RiskLevel.CRITICAL
        if decision_type in ["plant_shutdown", "major_capital_purchase", "supplier_contract"]:
            return RiskLevel.CRITICAL

        # High risk decisions
        if financial_impact > 10000:
            return RiskLevel.HIGH
        if affects_production:
            return RiskLevel.HIGH
        if decision_type in ["production_schedule_change", "machine_maintenance", "large_order"]:
            return RiskLevel.HIGH

        # Medium risk decisions
        if financial_impact > 1000:
            return RiskLevel.MEDIUM
        if decision_type in ["inventory_adjustment", "supplier_selection", "minor_order"]:
            return RiskLevel.MEDIUM

        # Low risk (analytics, forecasts)
        return RiskLevel.LOW

    def create_decision(
        self,
        decision_type: str,
        action: str,
        description: str,
        impact_analysis: Dict,
        auto_classify: bool = True,
        payload: Optional[Dict] = None
    ) -> AIDecision:
        """
        Create new AI decision for review

        Args:
            decision_type: Type of decision (e.g., "demand_forecast_update")
            action: Specific action to take (e.g., "Update demand forecast to 1,345 units/week")
            description: Human-readable explanation
            impact_analysis: Dict with financial_impact, affects_production, etc.
            auto_classify: Whether to auto-determine risk level
            payload: Full agent output to store for later execution

        Returns:
            AIDecision object
        """
        # Classify risk
        if auto_classify:
            risk_level = self.classify_decision_risk(decision_type, impact_analysis)
        else:
            risk_level = RiskLevel.HIGH  # Default to high if not auto-classifying

        # Create decision
        decision = AIDecision(
            decision_type=decision_type,
            action=action,
            description=description,
            risk_level=risk_level,
            impact_analysis=impact_analysis,
            requires_approval=(risk_level != RiskLevel.LOW)
        )

        # Attach payload for later execution
        decision.payload = payload

        # Auto-approve low-risk decisions
        if risk_level == RiskLevel.LOW:
            decision.status = DecisionStatus.AUTO_APPROVED
            decision.reviewed_by = "Auto-Approval System"
            decision.reviewed_at = datetime.now()

        # Save to database
        decision.id = self._save_decision(decision)

        # Log for audit
        log_activity(
            user="AI System",
            action=f"AI Decision Created ({risk_level.value})",
            details=f"{decision_type}: {description}"
        )

        return decision

    def _save_decision(self, decision: AIDecision) -> int:
        """Save decision to database"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ai_decisions
            (decision_type, action, description, risk_level, impact_analysis,
             recommended_by, requires_approval, status, reviewed_by, reviewed_at, payload)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            decision.decision_type,
            decision.action,
            decision.description,
            decision.risk_level.value,
            json.dumps(decision.impact_analysis),
            decision.recommended_by,
            1 if decision.requires_approval else 0,
            decision.status.value,
            decision.reviewed_by,
            decision.reviewed_at,
            json.dumps(decision.payload) if decision.payload is not None else None
        ))
        decision_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return decision_id

    def get_pending_decisions(self, risk_level: Optional[RiskLevel] = None) -> List[AIDecision]:
        """Get all pending decisions requiring approval"""
        conn = get_db_connection()
        cursor = conn.cursor()

        if risk_level:
            cursor.execute("""
                SELECT * FROM ai_decisions
                WHERE status = 'pending' AND risk_level = ?
                ORDER BY created_at DESC
            """, (risk_level.value,))
        else:
            cursor.execute("""
                SELECT * FROM ai_decisions
                WHERE status = 'pending'
                ORDER BY created_at DESC
            """)

        decisions = []
        for row in cursor.fetchall():
            decision = self._row_to_decision(dict(row))
            decisions.append(decision)

        conn.close()
        return decisions

    def approve_decision(self, decision_id: int, approved_by: str, notes: str = "") -> bool:
        """Approve AI decision"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE ai_decisions
            SET status = 'approved',
                reviewed_by = ?,
                reviewed_at = CURRENT_TIMESTAMP
            WHERE id = ? AND status = 'pending'
        """, (approved_by, decision_id))

        success = cursor.rowcount > 0
        conn.commit()
        conn.close()

        if success:
            log_activity(
                user=approved_by,
                action="AI Decision Approved",
                details=f"Decision #{decision_id} approved. Notes: {notes}"
            )

        return success

    def reject_decision(self, decision_id: int, rejected_by: str, reason: str) -> bool:
        """Reject AI decision"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE ai_decisions
            SET status = 'rejected',
                reviewed_by = ?,
                reviewed_at = CURRENT_TIMESTAMP,
                rejection_reason = ?
            WHERE id = ? AND status = 'pending'
        """, (rejected_by, reason, decision_id))

        success = cursor.rowcount > 0
        conn.commit()
        conn.close()

        if success:
            log_activity(
                user=rejected_by,
                action="AI Decision Rejected",
                details=f"Decision #{decision_id} rejected. Reason: {reason}"
            )

        return success

    def mark_executed(self, decision_id: int, rollback_data: Optional[Dict] = None) -> bool:
        """Mark decision as executed (stores rollback data)"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE ai_decisions
            SET status = 'executed',
                executed_at = CURRENT_TIMESTAMP,
                rollback_data = ?
            WHERE id = ? AND status IN ('approved', 'auto_approved')
        """, (json.dumps(rollback_data) if rollback_data else None, decision_id))

        success = cursor.rowcount > 0
        conn.commit()
        conn.close()

        return success

    def get_pending_as_dicts(self) -> list:
        """Return all pending decisions as plain dicts (for API responses)"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, decision_type, action, description, risk_level,
                   impact_analysis, status, created_at, payload
            FROM ai_decisions
            WHERE status = 'pending'
            ORDER BY created_at DESC
        """)
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        for row in rows:
            try:
                row['impact_analysis'] = json.loads(row['impact_analysis'])
            except Exception:
                pass
            try:
                row['payload'] = json.loads(row['payload']) if row['payload'] else None
            except Exception:
                pass
        return rows

    def _row_to_decision(self, row: Dict) -> AIDecision:
        """Convert database row to AIDecision object"""
        decision = AIDecision(
            decision_type=row["decision_type"],
            action=row["action"],
            description=row["description"],
            risk_level=RiskLevel(row["risk_level"]),
            impact_analysis=json.loads(row["impact_analysis"]),
            recommended_by=row["recommended_by"]
        )
        decision.id = row["id"]
        decision.status = DecisionStatus(row["status"])
        decision.requires_approval = bool(row["requires_approval"])
        decision.reviewed_by = row["reviewed_by"]
        decision.reviewed_at = row["reviewed_at"]
        decision.rejection_reason = row["rejection_reason"]
        decision.executed_at = row["executed_at"]
        return decision


# Global instance
_approval_system = None

def get_approval_system() -> ApprovalSystem:
    """Get singleton approval system"""
    global _approval_system
    if _approval_system is None:
        _approval_system = ApprovalSystem()
    return _approval_system
