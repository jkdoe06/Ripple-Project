"""
Module 1: Gmail Agent
- Auto-label emails into categories
- Auto-trash known junk senders
- Star professional emails from real humans
- Flag emails needing response after 48h
- Protect emails from VIP senders
"""

import base64
import email.utils
from datetime import datetime, timedelta, timezone
from googleapiclient.discovery import build

from agents.base_agent import BaseAgent
from auth.google_auth import get_google_credentials
from config.settings import (
    GMAIL_LABELS,
    AUTO_TRASH_SENDERS,
    PROTECTED_SENDERS,
    LABEL_KEYWORDS,
    RESPONSE_TIMEOUT_HOURS,
    DRY_RUN,
)
from utils.retry import with_retry


class GmailAgent(BaseAgent):
    def __init__(self):
        super().__init__("GmailAgent")
        creds = get_google_credentials()
        self.service = build("gmail", "v1", credentials=creds)
        self.label_map: dict[str, str] = {}  # name → id

    # ── Helpers ──────────────────────────────────────────────────────────

    def _ensure_labels_exist(self):
        """Create any missing labels, populate self.label_map."""
        existing = self.service.users().labels().list(userId="me").execute()
        existing_map = {l["name"]: l["id"] for l in existing.get("labels", [])}

        for label_name in GMAIL_LABELS:
            if label_name in existing_map:
                self.label_map[label_name] = existing_map[label_name]
                self.log.info("Label exists: %s (%s)", label_name, existing_map[label_name])
            else:
                body = {
                    "name": label_name,
                    "labelListVisibility": "labelShow",
                    "messageListVisibility": "show",
                }
                if not DRY_RUN:
                    result = self.service.users().labels().create(
                        userId="me", body=body
                    ).execute()
                    self.label_map[label_name] = result["id"]
                    self.record_action("create_label", label_name)
                else:
                    self.log.info("[DRY RUN] Would create label: %s", label_name)

    def _get_sender_domain(self, headers: list[dict]) -> str:
        for h in headers:
            if h["name"].lower() == "from":
                addr = email.utils.parseaddr(h["value"])[1]
                return addr.split("@")[-1].lower() if "@" in addr else ""
        return ""

    def _get_sender_address(self, headers: list[dict]) -> str:
        for h in headers:
            if h["name"].lower() == "from":
                return email.utils.parseaddr(h["value"])[1].lower()
        return ""

    def _get_subject(self, headers: list[dict]) -> str:
        for h in headers:
            if h["name"].lower() == "subject":
                return h["value"]
        return ""

    def _is_automated(self, headers: list[dict]) -> bool:
        """Check if email is from an automated sender (noreply, etc.)."""
        addr = self._get_sender_address(headers)
        auto_indicators = ["noreply", "no-reply", "donotreply", "notifications", "mailer-daemon"]
        return any(ind in addr for ind in auto_indicators)

    def _is_protected(self, headers: list[dict]) -> bool:
        addr = self._get_sender_address(headers)
        domain = self._get_sender_domain(headers)
        return any(p in addr or p in domain for p in PROTECTED_SENDERS)

    def _classify_email(self, subject: str, snippet: str) -> str | None:
        """Return the best matching label name, or None."""
        text = f"{subject} {snippet}".lower()
        best_label = None
        best_score = 0
        for label, keywords in LABEL_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > best_score:
                best_score = score
                best_label = label
        return best_label if best_score > 0 else None

    def _has_been_replied_to(self, thread_id: str) -> bool:
        """Check if a thread has a sent message (i.e., user replied)."""
        thread = self.service.users().threads().get(
            userId="me", id=thread_id, format="metadata",
            metadataHeaders=["From"]
        ).execute()
        messages = thread.get("messages", [])
        for msg in messages:
            label_ids = msg.get("labelIds", [])
            if "SENT" in label_ids:
                return True
        return False

    @with_retry
    def _modify_message(self, msg_id: str, add_labels=None, remove_labels=None):
        body = {}
        if add_labels:
            body["addLabelIds"] = add_labels
        if remove_labels:
            body["removeLabelIds"] = remove_labels
        if body and not DRY_RUN:
            self.service.users().messages().modify(
                userId="me", id=msg_id, body=body
            ).execute()

    @with_retry
    def _trash_message(self, msg_id: str):
        if not DRY_RUN:
            self.service.users().messages().trash(userId="me", id=msg_id).execute()

    @with_retry
    def _star_message(self, msg_id: str):
        self._modify_message(msg_id, add_labels=["STARRED"])

    # ── Lifecycle ────────────────────────────────────────────────────────

    def audit(self) -> dict:
        """Count inbox messages, existing labels."""
        results = self.service.users().labels().list(userId="me").execute()
        label_names = [l["name"] for l in results.get("labels", [])]

        inbox = self.service.users().messages().list(
            userId="me", labelIds=["INBOX"], maxResults=1
        ).execute()
        total = inbox.get("resultSizeEstimate", 0)

        return {
            "existing_labels": label_names,
            "inbox_estimate": total,
        }

    def plan(self) -> list[str]:
        actions = []
        actions.append(f"Create missing labels from: {GMAIL_LABELS}")
        actions.append(f"Scan inbox emails and classify into {len(GMAIL_LABELS)} categories")
        actions.append(f"Auto-trash emails from {len(AUTO_TRASH_SENDERS)} junk senders")
        actions.append("Star professional emails from real humans")
        actions.append(f"Flag unreplied emails older than {RESPONSE_TIMEOUT_HOURS}h")
        actions.append(f"Protect emails from: {PROTECTED_SENDERS}")
        return actions

    def execute(self) -> dict:
        stats = {
            "labeled": 0,
            "trashed": 0,
            "starred": 0,
            "flagged_for_response": 0,
            "skipped_uncertain": 0,
            "protected": 0,
        }

        # Step 1: Ensure labels exist
        self._ensure_labels_exist()

        # Step 2: Fetch inbox messages (last 500)
        self.log.info("Fetching inbox messages...")
        messages = []
        page_token = None
        while len(messages) < 500:
            resp = self.service.users().messages().list(
                userId="me", labelIds=["INBOX"],
                maxResults=100, pageToken=page_token,
            ).execute()
            messages.extend(resp.get("messages", []))
            page_token = resp.get("nextPageToken")
            if not page_token:
                break

        self.log.info("Processing %d inbox messages...", len(messages))
        cutoff = datetime.now(timezone.utc) - timedelta(hours=RESPONSE_TIMEOUT_HOURS)

        for msg_stub in messages:
            try:
                msg = self.service.users().messages().get(
                    userId="me", id=msg_stub["id"], format="metadata",
                    metadataHeaders=["From", "Subject", "Date"],
                ).execute()
                headers = msg.get("payload", {}).get("headers", [])
                msg_id = msg["id"]
                thread_id = msg.get("threadId", "")
                subject = self._get_subject(headers)
                snippet = msg.get("snippet", "")
                domain = self._get_sender_domain(headers)

                # ── Protected sender check ──
                if self._is_protected(headers):
                    stats["protected"] += 1

                # ── Auto-trash junk ──
                if domain in AUTO_TRASH_SENDERS:
                    # Safety: never trash protected senders
                    if not self._is_protected(headers):
                        self._trash_message(msg_id)
                        self.record_action("trash", f"Junk from {domain}: {subject[:60]}")
                        stats["trashed"] += 1
                        continue

                # ── Classify and label ──
                label = self._classify_email(subject, snippet)
                if label and label in self.label_map:
                    self._modify_message(msg_id, add_labels=[self.label_map[label]])
                    self.record_action("label", f"{label}: {subject[:60]}")
                    stats["labeled"] += 1
                elif not label:
                    # Uncertain — log for review, don't touch
                    self.flag_for_review(f"Unclassified: {subject[:80]} (from {domain})")
                    stats["skipped_uncertain"] += 1

                # ── Star professional emails from real humans ──
                if not self._is_automated(headers) and not domain in AUTO_TRASH_SENDERS:
                    classified = self._classify_email(subject, snippet)
                    if classified in ("Professional", "Jobs & Internships"):
                        self._star_message(msg_id)
                        self.record_action("star", f"Professional: {subject[:60]}")
                        stats["starred"] += 1

                # ── Flag unreplied emails needing response ──
                internal_date = int(msg.get("internalDate", "0")) / 1000
                msg_time = datetime.fromtimestamp(internal_date, tz=timezone.utc)
                if msg_time < cutoff:
                    if not self._is_automated(headers) and not self._has_been_replied_to(thread_id):
                        self._modify_message(msg_id, add_labels=["STARRED"])
                        self.flag_for_review(
                            f"NEEDS RESPONSE (>{RESPONSE_TIMEOUT_HOURS}h): "
                            f"{subject[:60]} from {self._get_sender_address(headers)}"
                        )
                        stats["flagged_for_response"] += 1

            except Exception as e:
                self.record_error("process_message", f"{msg_stub['id']}: {e}")

        return stats
