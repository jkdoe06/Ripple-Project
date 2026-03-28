"""
Central configuration for the Autonomous Life Agent.
All rules, labels, colors, and domain knowledge live here.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ─── Google OAuth2 Scopes ───────────────────────────────────────────────────
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.labels",
    "https://www.googleapis.com/auth/calendar",
]

# ─── Canvas LMS ─────────────────────────────────────────────────────────────
CANVAS_API_URL = os.getenv("CANVAS_API_URL", "https://bcourses.berkeley.edu/api/v1")
CANVAS_API_TOKEN = os.getenv("CANVAS_API_TOKEN", "")

# ─── Gmail: Label Definitions ───────────────────────────────────────────────
GMAIL_LABELS = [
    "Travel",
    "Finance",
    "School & Greek Life",
    "Jobs & Internships",
    "Housing",
    "Professional",
    "Social",
]

# ─── Gmail: Auto-Trash Senders ──────────────────────────────────────────────
AUTO_TRASH_SENDERS = [
    "babbel.com",
    "walgreens.com",
    "ryanairemail.com",
    "staples.com",
    "kinguin.net",
    "big5sportinggoods.com",
    "skool.com",
    "hostelworld.com",
    "feverup.com",
    "fandango.com",
    "e.goat.com",
    "bandsintown.com",
    "pinterest.com",
]

# ─── Gmail: Protected Senders (never delete) ────────────────────────────────
PROTECTED_SENDERS = [
    "amaris.charton@gmail.com",
    "sigmachi.org",
    "berkeley.edu",
    "delta.com",
    "booking.com",
]

# ─── Gmail: Classification Keywords ─────────────────────────────────────────
LABEL_KEYWORDS = {
    "Travel": [
        "flight", "booking", "hotel", "airbnb", "delta", "united", "reservation",
        "itinerary", "check-in", "boarding pass", "trip", "travel", "hostel",
    ],
    "Finance": [
        "invoice", "payment", "bank", "credit", "debit", "transaction", "statement",
        "venmo", "zelle", "paypal", "tax", "financial aid", "scholarship", "refund",
    ],
    "School & Greek Life": [
        "berkeley", "bcourses", "canvas", "assignment", "lecture", "exam", "midterm",
        "final", "professor", "gsi", "office hours", "sigma chi", "fraternity",
        "greek", "chapter", "rush", "philanthropy", "sorority",
    ],
    "Jobs & Internships": [
        "internship", "job", "career", "recruiting", "handshake", "linkedin",
        "application", "interview", "offer", "resume", "cover letter", "hiring",
    ],
    "Housing": [
        "lease", "rent", "apartment", "housing", "roommate", "landlord", "move-in",
        "move-out", "deposit", "utilities",
    ],
    "Professional": [
        "meeting", "conference", "networking", "mentor", "startup", "founder",
        "investor", "pitch", "studyforge", "partnership",
    ],
    "Social": [
        "party", "event", "hangout", "dinner", "lunch", "concert", "festival",
        "game", "tailgate", "date",
    ],
}

# ─── Google Calendar: Color Mapping ─────────────────────────────────────────
# Google Calendar colorId values:
# 1=Lavender, 2=Sage, 3=Grape, 4=Flamingo, 5=Banana,
# 6=Tangerine, 7=Peacock, 8=Graphite, 9=Blueberry, 10=Basil, 11=Tomato
CALENDAR_COLORS = {
    # New calendars to create
    "Professional": {"color": "10", "create": True},   # Basil
    "Travel": {"color": "2", "create": True},           # Sage

    # Existing calendars to recolor
    "COMPSCI 47B": {"color": "9"},    # Blueberry
    "MATH 55": {"color": "9"},        # Blueberry
    "SCANDIN R5B": {"color": "9"},    # Blueberry
    "UGBA 135": {"color": "9"},       # Blueberry
    "INDENG 162": {"color": "9"},     # Blueberry
    "FUN!!": {"color": "4"},          # Flamingo
    "Family": {"color": "2"},         # Sage
}

# Primary + Holidays → Graphite (handled separately since they use special IDs)
PRIMARY_CALENDAR_COLOR = "8"   # Graphite
HOLIDAYS_CALENDAR_COLOR = "8"  # Graphite

# ─── Calendar: Event Classification Keywords ────────────────────────────────
CALENDAR_EVENT_KEYWORDS = {
    "Professional": [
        "meeting", "interview", "networking", "conference", "pitch", "startup",
        "studyforge", "mentor", "office hours", "career fair",
    ],
    "Travel": [
        "flight", "airport", "hotel", "trip", "travel", "vacation", "road trip",
    ],
}

# ─── Canvas: Courses (Spring 2026) ──────────────────────────────────────────
CANVAS_COURSES = [
    "SCANDIN R5B",
    "MATH 55",
    "INDENG 162",
    "UGBA 135",
]

# ─── Opportunity Scout: Search Terms ────────────────────────────────────────
OPPORTUNITY_SEARCH_TERMS = [
    "berkeley student freelance gig",
    "CS student paid research study",
    "beta testing program paid",
    "AI startup micro tasks",
    "tutoring platform sign up bonus",
    "sell digital products student",
    "paid survey sites legitimate 2026",
    "upwork data science entry level",
]

# ─── General Settings ───────────────────────────────────────────────────────
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
MAX_RETRIES = 3
RETRY_BASE_DELAY = 2  # seconds, exponential backoff: 2, 4, 8
RESPONSE_TIMEOUT_HOURS = 48  # flag emails needing response after this
