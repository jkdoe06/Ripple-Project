"""
Base agent class — all modules inherit from this.
Provides: logging, audit trail, run lifecycle, summary generation.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from utils.logger import get_logger


class BaseAgent(ABC):
    """Base class for all life-agent modules."""

    def __init__(self, name: str):
        self.name = name
        self.log = get_logger(name)
        self.actions: list[dict] = []  # audit trail
        self.errors: list[dict] = []
        self.flags: list[str] = []     # items needing user review

    def record_action(self, action: str, detail: str = ""):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": self.name,
            "action": action,
            "detail": detail,
        }
        self.actions.append(entry)
        self.log.info("ACTION: %s — %s", action, detail)

    def record_error(self, action: str, error: str):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": self.name,
            "action": action,
            "error": error,
        }
        self.errors.append(entry)
        self.log.error("ERROR in %s: %s", action, error)

    def flag_for_review(self, item: str):
        self.flags.append(item)
        self.log.warning("FLAGGED FOR REVIEW: %s", item)

    @abstractmethod
    def audit(self) -> dict:
        """Return current state audit before making changes."""

    @abstractmethod
    def plan(self) -> list[str]:
        """Return a list of planned actions for user approval."""

    @abstractmethod
    def execute(self) -> dict:
        """Execute the module's tasks. Returns a summary dict."""

    def run(self, auto_approve: bool = False) -> dict:
        """Full lifecycle: audit → plan → (approve) → execute → summarize."""
        self.log.info("=" * 60)
        self.log.info("Starting %s", self.name)
        self.log.info("=" * 60)

        # Step 1: Audit current state
        self.log.info("Phase 1: Auditing current state...")
        audit_result = self.audit()
        self.log.info("Audit complete: %s", audit_result)

        # Step 2: Generate plan
        self.log.info("Phase 2: Generating plan...")
        planned_actions = self.plan()
        for i, action in enumerate(planned_actions, 1):
            self.log.info("  [%d] %s", i, action)

        # Step 3: Approval gate
        if not auto_approve:
            print(f"\n{'=' * 60}")
            print(f"  {self.name} — PLANNED ACTIONS")
            print(f"{'=' * 60}")
            for i, action in enumerate(planned_actions, 1):
                print(f"  [{i}] {action}")
            print(f"{'=' * 60}")
            response = input("Approve and execute? [y/N]: ").strip().lower()
            if response != "y":
                self.log.info("User declined execution. Skipping %s.", self.name)
                return {"status": "skipped", "reason": "user_declined"}

        # Step 4: Execute
        self.log.info("Phase 3: Executing...")
        result = self.execute()

        # Step 5: Summary
        summary = {
            "agent": self.name,
            "status": "completed",
            "actions_taken": len(self.actions),
            "errors": len(self.errors),
            "flags_for_review": self.flags,
            "details": result,
        }
        self.log.info("Completed %s: %d actions, %d errors, %d flags",
                       self.name, len(self.actions), len(self.errors), len(self.flags))
        return summary
