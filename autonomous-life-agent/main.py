#!/usr/bin/env python3
"""
Autonomous Life Agent — Main Orchestrator
==========================================
Runs all 4 modules in sequence with user approval gates.

Usage:
    python main.py                  # Interactive mode (approve each module)
    python main.py --auto           # Auto-approve all modules
    python main.py --module gmail   # Run only one module
    python main.py --dry-run        # Preview mode — no changes made

Requires:
    1. credentials.json (Google OAuth2) in this directory
    2. .env file with CANVAS_API_TOKEN set
"""

import argparse
import json
import os
import sys
from datetime import datetime

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(__file__))

from utils.logger import get_logger
from config.settings import DRY_RUN

log = get_logger("orchestrator")


def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════╗
║            AUTONOMOUS LIFE AGENT v1.0                       ║
║            ─────────────────────────                        ║
║  Gmail · Calendar · Canvas · Opportunity Scout              ║
║  Built for UC Berkeley | Spring 2026                        ║
╚══════════════════════════════════════════════════════════════╝
    """)


def check_prerequisites():
    """Verify all required files and credentials are available."""
    issues = []

    creds_path = os.path.join(os.path.dirname(__file__), "credentials.json")
    if not os.path.exists(creds_path):
        issues.append(
            "❌ credentials.json not found.\n"
            "   → Download from: Google Cloud Console → APIs & Services → Credentials\n"
            "   → Create OAuth 2.0 Client ID (Desktop App) → Download JSON\n"
            f"   → Save to: {creds_path}"
        )

    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(env_path):
        issues.append(
            "❌ .env file not found.\n"
            "   → Copy .env.example to .env and fill in your Canvas API token\n"
            "   → Get token from: bcourses.berkeley.edu → Account → Settings → New Access Token"
        )

    if issues:
        print("\n⚠️  PREREQUISITES CHECK FAILED\n")
        for issue in issues:
            print(issue)
            print()
        print("Fix the above issues and re-run.\n")
        return False

    return True


def run_module(module_name: str, auto_approve: bool = False) -> dict:
    """Import and run a single module by name."""
    if module_name == "gmail":
        from agents.gmail_agent import GmailAgent
        agent = GmailAgent()
    elif module_name == "calendar":
        from agents.calendar_agent import CalendarAgent
        agent = CalendarAgent()
    elif module_name == "canvas":
        from agents.canvas_agent import CanvasAgent
        agent = CanvasAgent()
    elif module_name == "opportunity":
        from agents.opportunity_agent import OpportunityAgent
        agent = OpportunityAgent()
    else:
        log.error("Unknown module: %s", module_name)
        return {"status": "error", "reason": f"Unknown module: {module_name}"}

    try:
        return agent.run(auto_approve=auto_approve)
    except Exception as e:
        log.error("Module %s crashed: %s", module_name, e, exc_info=True)
        return {"status": "crashed", "error": str(e)}


def print_final_report(results: dict):
    """Print a comprehensive summary of everything done."""
    print("\n")
    print("=" * 70)
    print("  FINAL REPORT — Autonomous Life Agent")
    print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    for module_name, result in results.items():
        print(f"\n{'─' * 70}")
        print(f"  MODULE: {module_name.upper()}")
        print(f"{'─' * 70}")

        status = result.get("status", "unknown")
        print(f"  Status: {status}")

        if status == "completed":
            print(f"  Actions taken: {result.get('actions_taken', 0)}")
            print(f"  Errors: {result.get('errors', 0)}")

            details = result.get("details", {})
            if details:
                print("  Details:")
                for key, val in details.items():
                    if key == "top_opportunities":
                        print(f"    {key}:")
                        for opp in val:
                            if opp.get("type") == "arbitrage":
                                print(f"      • [{opp.get('type')}] {opp.get('title')} "
                                      f"— Margin: {opp.get('margin')}, "
                                      f"Startup: {opp.get('startup_cost')}")
                            else:
                                print(f"      • [{opp.get('type')}] {opp.get('title', '')[:60]} "
                                      f"(score: {opp.get('score')})")
                    else:
                        print(f"    {key}: {val}")

            flags = result.get("flags_for_review", [])
            if flags:
                print("\n  ⚠️  FLAGS FOR YOUR REVIEW:")
                for flag in flags:
                    print(f"    → {flag}")

        elif status == "skipped":
            print(f"  Reason: {result.get('reason', 'N/A')}")
        elif status == "crashed":
            print(f"  Error: {result.get('error', 'N/A')}")

    print(f"\n{'=' * 70}")
    print("  END OF REPORT")
    print(f"{'=' * 70}\n")

    # Save report to file
    report_path = os.path.join(
        os.path.dirname(__file__), "logs",
        f"report_{datetime.now():%Y%m%d_%H%M%S}.json"
    )
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"Full report saved to: {report_path}\n")


def main():
    parser = argparse.ArgumentParser(description="Autonomous Life Agent")
    parser.add_argument("--auto", action="store_true", help="Auto-approve all modules")
    parser.add_argument("--module", choices=["gmail", "calendar", "canvas", "opportunity"],
                        help="Run only a specific module")
    parser.add_argument("--dry-run", action="store_true", help="Preview mode — no changes made")
    args = parser.parse_args()

    if args.dry_run:
        os.environ["DRY_RUN"] = "true"
        # Reload settings
        import importlib
        import config.settings
        importlib.reload(config.settings)

    print_banner()

    if DRY_RUN or args.dry_run:
        print("🔍 DRY RUN MODE — No changes will be made\n")

    if not check_prerequisites():
        sys.exit(1)

    modules = ["gmail", "calendar", "canvas", "opportunity"]
    if args.module:
        modules = [args.module]

    results = {}
    for module_name in modules:
        print(f"\n{'━' * 70}")
        print(f"  Starting Module: {module_name.upper()}")
        print(f"{'━' * 70}\n")

        result = run_module(module_name, auto_approve=args.auto)
        results[module_name] = result

        if result.get("status") == "crashed":
            print(f"\n⚠️  Module {module_name} crashed. Continue with next module? [Y/n]: ", end="")
            if not args.auto:
                resp = input().strip().lower()
                if resp == "n":
                    break

    print_final_report(results)


if __name__ == "__main__":
    main()
