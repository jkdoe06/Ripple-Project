"""
Module 4: Opportunity Scout + Arbitrage Agent
- Search for legitimate income opportunities matching user profile
- Scan freelance platforms, research studies, tutoring, beta testing
- Identify geographic/market arbitrage opportunities (buy low, sell high)
- Log everything, never auto-execute account creation
- Present findings for user review with estimated ROI
"""

import json
import re
from datetime import datetime
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup

from agents.base_agent import BaseAgent
from config.settings import OPPORTUNITY_SEARCH_TERMS, DRY_RUN
from utils.retry import with_retry

# User profile for matching
USER_PROFILE = {
    "school": "UC Berkeley",
    "year": "Undergrad Spring 2026",
    "skills": ["Python", "AI/ML", "data science", "web development", "entrepreneurship"],
    "courses": ["CS", "Math", "IEOR", "Business Administration"],
    "interests": ["AI", "electronic music", "gaming", "entrepreneurship"],
    "project": "StudyForge (AI study tool)",
    "fraternity": "Sigma Chi",
}

# ── Arbitrage Opportunity Database ───────────────────────────────────────
# Real-world arbitrage patterns: buy low in one market, sell high in another.
# These are well-known, legal strategies.
ARBITRAGE_STRATEGIES = [
    {
        "name": "Textbook Arbitrage",
        "description": (
            "Buy used textbooks at end-of-semester buyback (campus bookstores sell for $5-15) "
            "or thrift stores. Resell on Amazon/Chegg at market price. "
            "Berkeley-specific: check ASUC bookswap, Free & For Sale groups."
        ),
        "buy_channels": ["campus bookstore buyback", "thrift stores", "ASUC bookswap", "estate sales"],
        "sell_channels": ["Amazon FBA", "Chegg", "eBay", "Berkeley Free & For Sale"],
        "estimated_margin": "200-500% per book",
        "startup_cost": "$20-50",
        "risk": "low",
        "time_investment": "2-4 hours/week",
        "legal": True,
    },
    {
        "name": "Wine Arbitrage (Travel-Based)",
        "description": (
            "When traveling to wine regions (France, Italy, Spain), buy bottles at local "
            "prices (€5-15/bottle). Legally bring back 1 bottle in carry-on per person. "
            "Resell to collectors/enthusiasts or at local wine tastings. "
            "Burgundy, Bordeaux, and Rioja regions have the best margins."
        ),
        "buy_channels": ["local vineyards in wine regions", "duty-free shops"],
        "sell_channels": ["wine collector groups", "local wine bars (consignment)", "private sales"],
        "estimated_margin": "100-400% per bottle",
        "startup_cost": "$10-50 per bottle",
        "risk": "low (1 bottle carry-on is fully legal)",
        "time_investment": "piggyback on existing travel",
        "legal": True,
        "notes": (
            "US Customs allows 1 liter duty-free per person. "
            "Additional bottles incur ~$1-2 duty. "
            "Check state laws on resale — most allow private sales under threshold."
        ),
    },
    {
        "name": "Electronics Arbitrage (Japan/Asia Travel)",
        "description": (
            "Japanese electronics, vinyl records, and collectibles are significantly cheaper "
            "in Akihabara/Nakano Broadway. Retro games, limited-edition tech accessories, "
            "and anime merchandise have strong US resale markets."
        ),
        "buy_channels": ["Akihabara shops", "Book Off", "Hard Off", "Nakano Broadway"],
        "sell_channels": ["eBay", "Mercari", "Reddit r/GameSale", "Depop"],
        "estimated_margin": "50-300%",
        "startup_cost": "$50-200",
        "risk": "low-medium",
        "time_investment": "piggyback on travel",
        "legal": True,
    },
    {
        "name": "Concert/Event Ticket Arbitrage",
        "description": (
            "Monitor presale codes for concerts and events in the Bay Area. "
            "Buy at face value, resell on StubHub/Vivid Seats when sold out. "
            "Electronic music events and tech conferences have strong demand."
        ),
        "buy_channels": ["presale links", "artist fan clubs", "credit card presales"],
        "sell_channels": ["StubHub", "Vivid Seats", "SeatGeek"],
        "estimated_margin": "30-200%",
        "startup_cost": "$50-500",
        "risk": "medium (event might not sell out)",
        "time_investment": "1-2 hours/week monitoring",
        "legal": True,
        "notes": "Check California ticket resale laws — legal with no price cap since 2019.",
    },
    {
        "name": "Thrift Store / Estate Sale Flip",
        "description": (
            "Bay Area thrift stores (Goodwill, Salvation Army) and estate sales often have "
            "underpriced electronics, vintage clothing, and furniture. "
            "Use eBay sold listings to verify value before buying."
        ),
        "buy_channels": ["Goodwill", "estate sales", "garage sales", "flea markets"],
        "sell_channels": ["eBay", "Poshmark", "Facebook Marketplace", "Depop"],
        "estimated_margin": "100-1000%",
        "startup_cost": "$10-50",
        "risk": "low",
        "time_investment": "3-5 hours/week",
        "legal": True,
    },
    {
        "name": "Domain Name Flipping",
        "description": (
            "Register expiring or undervalued domain names related to trending topics, "
            "AI tools, or Berkeley/student niches. Sell on Afternic, Sedo, or directly. "
            "AI-related domains are currently high demand."
        ),
        "buy_channels": ["Namecheap ($8-12/domain)", "GoDaddy auctions", "ExpiredDomains.net"],
        "sell_channels": ["Afternic", "Sedo", "Flippa", "direct outreach"],
        "estimated_margin": "500-10000%",
        "startup_cost": "$8-50 per domain",
        "risk": "medium (not all domains sell)",
        "time_investment": "1-2 hours/week",
        "legal": True,
    },
    {
        "name": "Digital Product Arbitrage",
        "description": (
            "Create simple digital products (Notion templates, study guides, AI prompt packs) "
            "targeted at Berkeley students. Sell on Gumroad, Etsy, or directly. "
            "StudyForge could be a distribution channel."
        ),
        "buy_channels": ["your own time/skills (zero cost)"],
        "sell_channels": ["Gumroad", "Etsy", "Notion Marketplace", "StudyForge"],
        "estimated_margin": "near 100% (digital goods)",
        "startup_cost": "$0-20",
        "risk": "low",
        "time_investment": "5-10 hours to create, then passive",
        "legal": True,
    },
]


class OpportunityAgent(BaseAgent):
    def __init__(self):
        super().__init__("OpportunityAgent")
        self.opportunities: list[dict] = []
        self.arbitrage_matches: list[dict] = []

    # ── Web Search Helpers ───────────────────────────────────────────────

    @with_retry
    def _search_web(self, query: str) -> list[dict]:
        """
        Search the web for opportunities. Uses a simple scraping approach.
        In production, you'd use a proper search API (SerpAPI, Google Custom Search, etc.)
        """
        results = []
        try:
            url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
            }
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                for result in soup.select(".result__body")[:5]:
                    title_el = result.select_one(".result__title")
                    snippet_el = result.select_one(".result__snippet")
                    link_el = result.select_one(".result__url")
                    if title_el:
                        results.append({
                            "title": title_el.get_text(strip=True),
                            "snippet": snippet_el.get_text(strip=True) if snippet_el else "",
                            "url": link_el.get_text(strip=True) if link_el else "",
                            "query": query,
                        })
        except Exception as e:
            self.record_error("web_search", f"Query '{query}': {e}")
        return results

    def _score_opportunity(self, result: dict) -> int:
        """Score an opportunity based on profile match (0-100)."""
        text = f"{result.get('title', '')} {result.get('snippet', '')}".lower()
        score = 0
        # Skill match
        for skill in USER_PROFILE["skills"]:
            if skill.lower() in text:
                score += 15
        # Interest match
        for interest in USER_PROFILE["interests"]:
            if interest.lower() in text:
                score += 10
        # Student-friendly indicators
        student_terms = ["student", "college", "university", "remote", "flexible", "part-time"]
        for term in student_terms:
            if term in text:
                score += 5
        # Red flags (reduce score)
        red_flags = ["scam", "mlm", "pyramid", "get rich", "guaranteed income", "no experience needed"]
        for flag in red_flags:
            if flag in text:
                score -= 30
        return max(0, min(100, score))

    def _evaluate_arbitrage_strategies(self) -> list[dict]:
        """Evaluate which arbitrage strategies match the user's current situation."""
        matches = []
        for strategy in ARBITRAGE_STRATEGIES:
            if not strategy["legal"]:
                continue
            relevance_score = 0
            reasons = []

            # Check profile fit
            if "digital" in strategy["name"].lower() or "domain" in strategy["name"].lower():
                relevance_score += 30
                reasons.append("Matches CS/tech skills")
            if "textbook" in strategy["name"].lower():
                relevance_score += 25
                reasons.append("Berkeley student — high textbook volume")
            if "thrift" in strategy["name"].lower() or "estate" in strategy["name"].lower():
                relevance_score += 15
                reasons.append("Bay Area has great thrift/estate scene")
            if "wine" in strategy["name"].lower() or "travel" in strategy["name"].lower():
                relevance_score += 20
                reasons.append("Travel-based — piggyback on existing trips")
            if "concert" in strategy["name"].lower() or "ticket" in strategy["name"].lower():
                relevance_score += 20
                reasons.append("Electronic music interest — know the market")
            if "electronic" in strategy["name"].lower() and "japan" in strategy.get("description", "").lower():
                relevance_score += 15
                reasons.append("Gaming interest — know collectible market")

            # Low startup cost bonus
            cost_str = strategy.get("startup_cost", "")
            if "$0" in cost_str or "$10" in cost_str or "$20" in cost_str:
                relevance_score += 10
                reasons.append("Very low startup cost")

            strategy["_relevance_score"] = relevance_score
            strategy["_match_reasons"] = reasons
            matches.append(strategy)

        return sorted(matches, key=lambda s: s["_relevance_score"], reverse=True)

    # ── Lifecycle ────────────────────────────────────────────────────────

    def audit(self) -> dict:
        return {
            "profile": USER_PROFILE,
            "search_terms": len(OPPORTUNITY_SEARCH_TERMS),
            "arbitrage_strategies": len(ARBITRAGE_STRATEGIES),
        }

    def plan(self) -> list[str]:
        actions = [
            f"Search {len(OPPORTUNITY_SEARCH_TERMS)} queries for freelance/gig opportunities",
            "Score each result against your profile (skills, interests, student status)",
            f"Evaluate {len(ARBITRAGE_STRATEGIES)} arbitrage strategies for profile fit",
            "Rank all opportunities by relevance and estimated ROI",
            "Compile a prioritized report of top opportunities",
            "NOTE: Will NOT auto-create accounts or execute transactions — report only",
        ]
        return actions

    def execute(self) -> dict:
        stats = {
            "queries_run": 0,
            "raw_results": 0,
            "qualified_opportunities": 0,
            "arbitrage_strategies_matched": 0,
            "top_opportunities": [],
        }

        # ── Step 1: Web search for opportunities ──
        self.log.info("Searching for opportunities...")
        all_results = []
        for query in OPPORTUNITY_SEARCH_TERMS:
            results = self._search_web(query)
            all_results.extend(results)
            stats["queries_run"] += 1
            self.record_action("web_search", f"Query: {query} → {len(results)} results")

        stats["raw_results"] = len(all_results)

        # ── Step 2: Score and filter ──
        scored = []
        for result in all_results:
            score = self._score_opportunity(result)
            if score >= 25:
                result["_score"] = score
                scored.append(result)

        scored.sort(key=lambda r: r["_score"], reverse=True)
        self.opportunities = scored[:20]  # Top 20
        stats["qualified_opportunities"] = len(self.opportunities)

        for opp in self.opportunities[:10]:
            self.record_action(
                "opportunity_found",
                f"[Score: {opp['_score']}] {opp.get('title', '')[:80]}"
            )

        # ── Step 3: Evaluate arbitrage strategies ──
        self.log.info("Evaluating arbitrage strategies...")
        self.arbitrage_matches = self._evaluate_arbitrage_strategies()
        stats["arbitrage_strategies_matched"] = len(
            [s for s in self.arbitrage_matches if s["_relevance_score"] >= 20]
        )

        for strat in self.arbitrage_matches:
            self.record_action(
                "arbitrage_evaluated",
                f"[Score: {strat['_relevance_score']}] {strat['name']}: {strat['estimated_margin']}"
            )

        # ── Step 4: Compile top opportunities ──
        top = []

        # Top freelance/gig opportunities
        for opp in self.opportunities[:5]:
            top.append({
                "type": "freelance/gig",
                "title": opp.get("title", ""),
                "url": opp.get("url", ""),
                "score": opp["_score"],
                "snippet": opp.get("snippet", "")[:200],
            })

        # Top arbitrage strategies
        for strat in self.arbitrage_matches[:5]:
            top.append({
                "type": "arbitrage",
                "title": strat["name"],
                "description": strat["description"],
                "margin": strat["estimated_margin"],
                "startup_cost": strat["startup_cost"],
                "risk": strat["risk"],
                "score": strat["_relevance_score"],
                "match_reasons": strat.get("_match_reasons", []),
            })

        stats["top_opportunities"] = top

        # Flag best immediate actions
        for strat in self.arbitrage_matches:
            if strat["_relevance_score"] >= 25:
                self.flag_for_review(
                    f"HIGH-VALUE ARBITRAGE: {strat['name']} — "
                    f"Margin: {strat['estimated_margin']}, "
                    f"Startup: {strat['startup_cost']}, "
                    f"Risk: {strat['risk']}"
                )

        return stats
