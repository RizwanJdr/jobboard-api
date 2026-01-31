#!/usr/bin/env python3
"""
Muslim Mathematician PhD Job Scraper
Uses RSS feeds that work from GitHub Actions
"""

import requests
import xml.etree.ElementTree as ET
import json
import re
from datetime import datetime, timezone
from typing import List, Dict
import time

# =============================================================================
# CONFIGURATION
# =============================================================================

KEYWORDS = [
    "math", "mathematician", "postdoc", "professor", "lecturer",
    "research", "quantitative", "statistics", "algebra", "geometry",
    "topology", "analysis", "probability", "combinatorics", "computational",
    "applied math", "pure math", "numerical", "optimization"
]

EXCLUDE = ["senior manager", "director of operations", "sales", "marketing"]

MUSLIM_FRIENDLY = {
    # Score 5 - Muslim majority
    "dubai": 5, "abu dhabi": 5, "doha": 5, "qatar": 5, "riyadh": 5,
    "saudi": 5, "kuala lumpur": 5, "malaysia": 5, "istanbul": 5,
    "turkey": 5, "jakarta": 5, "indonesia": 5, "cairo": 5, "egypt": 5,
    "kuwait": 5, "bahrain": 5, "oman": 5, "jordan": 5, "uae": 5,
    "brunei": 5, "morocco": 5, "tunisia": 5, "pakistan": 5,
    # Score 4 - Large Muslim communities
    "london": 4, "birmingham": 4, "manchester": 4, "uk": 4, "united kingdom": 4,
    "toronto": 4, "canada": 4, "berlin": 4, "germany": 4,
    "paris": 4, "france": 4, "amsterdam": 4, "netherlands": 4,
    "new york": 4, "chicago": 4, "houston": 4, "singapore": 4,
    "brussels": 4, "belgium": 4, "detroit": 4,
    # Score 3 - Moderate communities
    "sydney": 3, "melbourne": 3, "australia": 3, "vienna": 3, "austria": 3,
    "zurich": 3, "switzerland": 3, "boston": 3, "california": 3,
    "spain": 3, "italy": 3, "sweden": 3, "norway": 3, "denmark": 3,
    "los angeles": 3, "san francisco": 3, "seattle": 3,
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

# =============================================================================
# RSS FEED FETCHERS
# =============================================================================

def fetch_with_retry(url: str, retries: int = 3, delay: float = 2.0) -> requests.Response:
    """Fetch URL with retries"""
    for i in range(retries):
        try:
            r = requests.get(url, timeout=30, headers=HEADERS)
            r.raise_for_status()
            return r
        except Exception as e:
            if i == retries - 1:
                raise e
            time.sleep(delay)
    raise Exception("Max retries exceeded")


def fetch_jobs_ac_uk() -> List[Dict]:
    """jobs.ac.uk Mathematics RSS"""
    jobs = []
    urls = [
        "https://www.jobs.ac.uk/atom/mathematics-and-statistics",
        "https://www.jobs.ac.uk/atom/academic",
    ]
    
    for url in urls:
        try:
            r = fetch_with_retry(url)
            root = ET.fromstring(r.content)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            
            for entry in root.findall("atom:entry", ns):
                title = entry.findtext("atom:title", "", ns)
                link_elem = entry.find("atom:link", ns)
                link = link_elem.get("href", "") if link_elem is not None else ""
                summary = entry.findtext("atom:summary", "", ns) or entry.findtext("atom:content", "", ns)
                
                if title:
                    jobs.append({
                        "title": clean(title),
                        "url": link,
                        "description": clean(summary)[:200],
                        "source": "jobs.ac.uk",
                        "location": extract_loc(title + " " + str(summary)),
                    })
            print(f"✓ jobs.ac.uk ({url.split('/')[-1]}): {len(jobs)} items")
        except Exception as e:
            print(f"✗ jobs.ac.uk: {str(e)[:80]}")
    
    return jobs


def fetch_mathjobs() -> List[Dict]:
    """MathJobs.org RSS"""
    jobs = []
    url = "https://www.mathjobs.org/jobs/rss"
    
    try:
        r = fetch_with_retry(url)
        root = ET.fromstring(r.content)
        
        for item in root.findall(".//item"):
            title = item.findtext("title", "")
            link = item.findtext("link", "")
            desc = item.findtext("description", "")
            
            if title:
                jobs.append({
                    "title": clean(title),
                    "url": link,
                    "description": clean(desc)[:200],
                    "source": "MathJobs.org",
                    "location": extract_loc(title + " " + desc),
                })
        print(f"✓ MathJobs.org: {len(jobs)}")
    except Exception as e:
        print(f"✗ MathJobs.org: {str(e)[:80]}")
    
    return jobs


def fetch_higheredjobs() -> List[Dict]:
    """HigherEdJobs Math RSS"""
    jobs = []
    urls = [
        "https://www.higheredjobs.com/rss/categoryFeed.cfm?catID=91",  # Math
        "https://www.higheredjobs.com/rss/categoryFeed.cfm?catID=92",  # Statistics
    ]
    
    for url in urls:
        try:
            r = fetch_with_retry(url)
            root = ET.fromstring(r.content)
            
            for item in root.findall(".//item"):
                title = item.findtext("title", "")
                link = item.findtext("link", "")
                desc = item.findtext("description", "")
                
                if title:
                    jobs.append({
                        "title": clean(title),
                        "url": link,
                        "description": clean(desc)[:200],
                        "source": "HigherEdJobs",
                        "location": extract_loc(title + " " + desc),
                    })
            print(f"✓ HigherEdJobs: {len(jobs)}")
        except Exception as e:
            print(f"✗ HigherEdJobs: {str(e)[:80]}")
    
    return jobs


def fetch_euraxess() -> List[Dict]:
    """EURAXESS European research jobs"""
    jobs = []
    urls = [
        "https://euraxess.ec.europa.eu/jobs/search/rss?keywords=mathematics",
        "https://euraxess.ec.europa.eu/jobs/search/rss?keywords=mathematician",
    ]
    
    for url in urls:
        try:
            r = fetch_with_retry(url)
            root = ET.fromstring(r.content)
            
            for item in root.findall(".//item"):
                title = item.findtext("title", "")
                link = item.findtext("link", "")
                desc = item.findtext("description", "")
                
                if title:
                    jobs.append({
                        "title": clean(title),
                        "url": link,
                        "description": clean(desc)[:200],
                        "source": "EURAXESS",
                        "location": extract_loc(title + " " + desc),
                    })
            print(f"✓ EURAXESS: {len(jobs)}")
        except Exception as e:
            print(f"✗ EURAXESS: {str(e)[:80]}")
    
    return jobs


def fetch_times_higher_ed() -> List[Dict]:
    """Times Higher Education jobs"""
    jobs = []
    url = "https://www.timeshighereducation.com/unijobs/rss"
    
    try:
        r = fetch_with_retry(url)
        root = ET.fromstring(r.content)
        
        for item in root.findall(".//item"):
            title = item.findtext("title", "")
            link = item.findtext("link", "")
            desc = item.findtext("description", "")
            
            # Only include math-related
            combined = (title + " " + desc).lower()
            if any(kw in combined for kw in ["math", "statistic", "quantitative"]):
                jobs.append({
                    "title": clean(title),
                    "url": link,
                    "description": clean(desc)[:200],
                    "source": "THE Jobs",
                    "location": extract_loc(title + " " + desc),
                })
        print(f"✓ Times Higher Ed: {len(jobs)}")
    except Exception as e:
        print(f"✗ Times Higher Ed: {str(e)[:80]}")
    
    return jobs


def fetch_academictransfer() -> List[Dict]:
    """AcademicTransfer (Netherlands/EU)"""
    jobs = []
    url = "https://www.academictransfer.com/en/rss/jobs/"
    
    try:
        r = fetch_with_retry(url)
        root = ET.fromstring(r.content)
        
        for item in root.findall(".//item"):
            title = item.findtext("title", "")
            link = item.findtext("link", "")
            desc = item.findtext("description", "")
            
            combined = (title + " " + desc).lower()
            if any(kw in combined for kw in ["math", "statistic", "quantitative", "computational"]):
                jobs.append({
                    "title": clean(title),
                    "url": link,
                    "description": clean(desc)[:200],
                    "source": "AcademicTransfer",
                    "location": extract_loc(title + " " + desc),
                })
        print(f"✓ AcademicTransfer: {len(jobs)}")
    except Exception as e:
        print(f"✗ AcademicTransfer: {str(e)[:80]}")
    
    return jobs


def fetch_nature_careers() -> List[Dict]:
    """Nature Careers RSS"""
    jobs = []
    url = "https://www.nature.com/naturecareers/rss/jobs"
    
    try:
        r = fetch_with_retry(url)
        root = ET.fromstring(r.content)
        
        for item in root.findall(".//item"):
            title = item.findtext("title", "")
            link = item.findtext("link", "")
            desc = item.findtext("description", "")
            
            combined = (title + " " + desc).lower()
            if any(kw in combined for kw in ["math", "statistic", "quantitative", "computational"]):
                jobs.append({
                    "title": clean(title),
                    "url": link,
                    "description": clean(desc)[:200],
                    "source": "Nature Careers",
                    "location": extract_loc(title + " " + desc),
                })
        print(f"✓ Nature Careers: {len(jobs)}")
    except Exception as e:
        print(f"✗ Nature Careers: {str(e)[:80]}")
    
    return jobs


def fetch_indeed_rss() -> List[Dict]:
    """Indeed RSS (multiple regions)"""
    jobs = []
    feeds = [
        ("Indeed UK", "https://www.indeed.co.uk/rss?q=mathematician"),
        ("Indeed CA", "https://www.indeed.ca/rss?q=mathematician"),
        ("Indeed AU", "https://au.indeed.com/rss?q=mathematician"),
        ("Indeed SG", "https://www.indeed.com.sg/rss?q=mathematician"),
        ("Indeed UAE", "https://www.indeed.ae/rss?q=mathematician"),
    ]
    
    for name, url in feeds:
        try:
            r = fetch_with_retry(url)
            root = ET.fromstring(r.content)
            count = 0
            
            for item in root.findall(".//item"):
                title = item.findtext("title", "")
                link = item.findtext("link", "")
                
                if title:
                    jobs.append({
                        "title": clean(title),
                        "url": link,
                        "description": "",
                        "source": name,
                        "location": extract_loc(title + " " + name),
                    })
                    count += 1
            print(f"✓ {name}: {count}")
        except Exception as e:
            print(f"✗ {name}: {str(e)[:60]}")
    
    return jobs


# =============================================================================
# HELPERS
# =============================================================================

def clean(text: str) -> str:
    """Clean HTML and whitespace"""
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'&[a-zA-Z]+;', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_loc(text: str) -> str:
    """Extract location from text"""
    if not text:
        return "Unknown"
    
    text = text.lower()
    
    # Countries (check first for more specific matches)
    countries = {
        "united arab emirates": "UAE", "uae": "UAE", "dubai": "UAE", "abu dhabi": "UAE",
        "qatar": "Qatar", "doha": "Qatar",
        "saudi arabia": "Saudi Arabia", "saudi": "Saudi Arabia", "riyadh": "Saudi Arabia",
        "malaysia": "Malaysia", "kuala lumpur": "Malaysia",
        "turkey": "Turkey", "türkiye": "Turkey", "istanbul": "Turkey",
        "egypt": "Egypt", "cairo": "Egypt",
        "indonesia": "Indonesia", "jakarta": "Indonesia",
        "united kingdom": "UK", " uk ": "UK", "england": "UK", "scotland": "UK", "wales": "UK",
        "united states": "USA", " usa ": "USA", "u.s.a": "USA", "u.s.": "USA",
        "germany": "Germany", "deutschland": "Germany",
        "france": "France",
        "canada": "Canada",
        "australia": "Australia",
        "netherlands": "Netherlands", "holland": "Netherlands",
        "switzerland": "Switzerland",
        "singapore": "Singapore",
        "belgium": "Belgium",
        "austria": "Austria",
        "sweden": "Sweden",
        "norway": "Norway",
        "denmark": "Denmark",
        "spain": "Spain",
        "italy": "Italy",
        "japan": "Japan",
        "china": "China",
        "hong kong": "Hong Kong",
    }
    
    for pattern, name in countries.items():
        if pattern in text:
            return name
    
    # Cities
    cities = [
        "london", "oxford", "cambridge", "manchester", "edinburgh", "birmingham",
        "new york", "boston", "chicago", "los angeles", "berkeley", "princeton",
        "toronto", "vancouver", "montreal",
        "sydney", "melbourne", "brisbane",
        "berlin", "munich", "frankfurt", "hamburg",
        "paris", "lyon", "marseille",
        "amsterdam", "rotterdam", "leiden",
        "zurich", "geneva", "basel",
        "vienna", "graz",
        "stockholm", "gothenburg",
        "copenhagen",
        "brussels",
        "dubai", "abu dhabi", "doha",
        "singapore",
        "hong kong",
        "tokyo", "kyoto",
        "beijing", "shanghai",
    ]
    
    for city in cities:
        if city in text:
            return city.title()
    
    return "Unknown"


def get_score(location: str) -> int:
    """Get Muslim-friendly score"""
    if not location:
        return 2
    loc = location.lower()
    for place, score in MUSLIM_FRIENDLY.items():
        if place in loc:
            return score
    return 2


def filter_jobs(jobs: List[Dict]) -> List[Dict]:
    """Filter and dedupe jobs"""
    filtered = []
    seen = set()
    
    for job in jobs:
        title = job.get("title", "")
        desc = job.get("description", "")
        text = (title + " " + desc).lower()
        
        # Must have keyword
        if not any(kw in text for kw in KEYWORDS):
            continue
        
        # Exclude unwanted
        if any(ex in text for ex in EXCLUDE):
            continue
        
        # Dedupe by title prefix
        key = title.lower()[:50]
        if key in seen:
            continue
        seen.add(key)
        
        job["score"] = get_score(job.get("location", ""))
        filtered.append(job)
    
    return filtered


# =============================================================================
# OUTPUT
# =============================================================================

def make_markdown(jobs: List[Dict]) -> str:
    """Generate Markdown report"""
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')
    
    md = f"""# 🎓 Math PhD Job Listings

**Last Updated:** {now} UTC  
**Total Positions:** {len(jobs)}

---

## 📊 Summary by Region

| Muslim-Friendly Score | Count |
|-----------------------|-------|
"""
    
    # Count by score
    for s in [5, 4, 3, 2]:
        count = len([j for j in jobs if j.get("score", 2) == s])
        if count:
            stars = "★" * s + "☆" * (5 - s)
            md += f"| {stars} | {count} |\n"
    
    md += "\n---\n\n"
    
    # Jobs grouped by score
    labels = {
        5: "Muslim-Majority Regions",
        4: "Large Muslim Communities", 
        3: "Moderate Communities",
        2: "Other Locations"
    }
    
    for score in [5, 4, 3, 2]:
        group = [j for j in jobs if j.get("score", 2) == score]
        if not group:
            continue
        
        stars = "★" * score + "☆" * (5 - score)
        md += f"## {stars} {labels[score]} ({len(group)})\n\n"
        
        for j in group[:30]:
            title = j.get("title", "")[:70]
            url = j.get("url", "#")
            loc = j.get("location", "Unknown")
            src = j.get("source", "")
            
            md += f"- **[{title}]({url})**  \n"
            md += f"  📍 {loc} | 🔗 {src}\n\n"
        
        if len(group) > 30:
            md += f"*...and {len(group) - 30} more positions*\n\n"
    
    md += """---

## ℹ️ Score Guide

| Score | Meaning |
|-------|---------|
| ★★★★★ | Muslim-majority (UAE, Qatar, Malaysia, Turkey, Egypt, Saudi Arabia) |
| ★★★★☆ | Large communities (UK, Germany, Canada, France, Singapore) |
| ★★★☆☆ | Moderate (Australia, Scandinavia, Spain, Italy) |
| ★★☆☆☆ | Other locations |

---

**Data Sources:** MathJobs.org, jobs.ac.uk, HigherEdJobs, EURAXESS, Times Higher Education, Indeed  
**Auto-updated daily via GitHub Actions**
"""
    
    return md


# =============================================================================
# MAIN
# =============================================================================

def main():
    now = datetime.now(timezone.utc)
    print(f"🔄 Job scraper started: {now.isoformat()}")
    print("=" * 50)
    
    all_jobs = []
    
    print("\n📡 Fetching from RSS feeds...\n")
    
    # Fetch from all sources
    all_jobs.extend(fetch_mathjobs())
    all_jobs.extend(fetch_jobs_ac_uk())
    all_jobs.extend(fetch_higheredjobs())
    all_jobs.extend(fetch_euraxess())
    all_jobs.extend(fetch_times_higher_ed())
    all_jobs.extend(fetch_academictransfer())
    all_jobs.extend(fetch_nature_careers())
    all_jobs.extend(fetch_indeed_rss())
    
    print(f"\n📥 Total fetched: {len(all_jobs)}")
    
    # Filter and sort
    filtered = filter_jobs(all_jobs)
    filtered.sort(key=lambda x: (-x.get("score", 0), x.get("title", "")))
    
    print(f"✅ After filtering: {len(filtered)}")
    
    # Save outputs
    md = make_markdown(filtered)
    with open("JOBS.md", "w", encoding="utf-8") as f:
        f.write(md)
    print(f"\n💾 Saved JOBS.md")
    
    output = {
        "updated": now.isoformat(),
        "count": len(filtered),
        "jobs": filtered
    }
    with open("jobs.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved jobs.json")
    
    # Summary
    print(f"\n{'=' * 50}")
    print(f"✨ COMPLETE: {len(filtered)} jobs found")
    
    for s in [5, 4, 3, 2]:
        c = len([j for j in filtered if j.get("score") == s])
        if c:
            print(f"   {'★' * s}{'☆' * (5-s)}: {c} positions")
    
    return filtered


if __name__ == "__main__":
    main()
