# OSINT Username Hunter
Social media username investigation tool that checks a target handle across 30+ platforms in parallel, using multiple detection strategies to identify likely matches and flag uncertain or error cases.
Developer: ErenTechLabs
Version: Enhanced Detection v2.0
## Features
- Parallel checks across 30+ platforms (currently 34 preset targets)
- Multiple detection signals:
    - HTTP status codes
    - Platform-specific “not found” and “success” indicators
    - Redirect and content-length heuristics
    - Special-case diagnostics for certain platforms

- Optional case-variant searching (e.g., eren, EREN, Eren)
- Colorized, human-friendly CLI output with progress updates
- JSON export with a structured summary and confidence level
- Rate-limited requests and robust error handling

## Requirements
- Python 3.8+ recommended
- Dependencies:
    - requests
    - colorama

Install with pip:
``` bash
# Using a virtual environment is recommended
pip install requests colorama
```
Alternatively, if a requirements file exists:
``` bash
pip install -r requirements.txt
```
## Quick Start
``` bash
python osint_tool.py <username>
```
Examples:
``` bash
# Basic search
python osint_tool.py erentech

# Search with case variants
python osint_tool.py erentech -a

# Save results to JSON
python osint_tool.py erentech -o results.json

# Verbose mode (adds info logs)
python osint_tool.py erentech -v

# Combine options
python osint_tool.py erentech -a -o results.json -v
```
Exit early at any time with Ctrl+C.
## Command-Line Options
- username (positional): Target handle to search for
- -a, --allcase: Search common case combinations of the username
- -o, --output FILE: Save results to a JSON file
- -v, --verbose: Enable extra informational output

## What It Checks
The tool includes a curated dictionary of platforms (e.g., Instagram, Twitter/X, GitHub, Facebook, LinkedIn, TikTok, YouTube, Reddit, Twitch, Steam, Bitbucket, CashApp, etc.) and for each:
- A profile URL pattern
- Error indicators (strings typical of “not found” pages)
- Success indicators (strings typical of legitimate profile pages)
- Special-case logic for certain sites

Currently configured: 34 platforms.
## How Detection Works
For each platform:
- Build profile URL for the username (and case variants if enabled)
- Fetch page with browser-like headers
- Evaluate:
    - Definitive HTTP errors (e.g., 404, 403, 410, 500) → Not Found
    - Non-200 status codes → Uncertain
    - Explicit error indicators in HTML → Not Found
    - Special-case rules for certain platforms (e.g., homepage redirects, absence of profile data keys)
    - Count “success indicators” (≥1 implies Found)
    - Heuristics: short pages, multiple generic “not found” phrases → Not Found

Results are categorized as:
- Found: Platform, username tested, direct URL, reason
- Not Found: Platform, username tested, reason
- Errors/Uncertain: Platform + diagnostic

## Output
CLI summary includes:
- Found profiles with their URLs
- Not found platforms (collapsed list)
- Errors/Uncertain list (truncated)
- Totals and quick recommendation

When saving to JSON:
``` json
{
  "found_profiles": [
    {
      "platform": "PlatformName",
      "username": "handle",
      "url": "https://platform.example/handle",
      "detection_reason": "Found X success indicators"
    }
  ],
  "not_found_platforms": [
    {
      "platform": "PlatformName",
      "username": "handle",
      "reason": "Error indicator found: ..."
    }
  ],
  "errors": [
    "PlatformName (handle): HTTP 429 - Uncertain"
  ],
  "summary": {
    "total_found": 3,
    "total_platforms_checked": 34,
    "total_not_found": 28,
    "total_errors": 3,
    "confidence_level": "high"
  }
}
```
## Tips and Best Practices
- Try -a/--allcase to catch platforms with case-sensitive or normalized usernames.
- Use -o to persist results and review later.
- Found results should be manually verified in a browser.
- Consider retries later if many platforms return uncertain due to rate limits or transient errors.

## Troubleshooting
- Many “Uncertain” results:
    - You may be rate-limited. Wait and retry.
    - Try a different network or use a rotating IP/proxy solution in your environment.

- Some platforms always return Not Found for legit users:
    - Sites can change HTML structure; update platform indicators as needed.

- Timeouts:
    - Check your connectivity and DNS.
    - Some platforms are slower; re-run or reduce parallelism by editing the worker count if you customize the code.

## Ethics and Legal
- Use responsibly for research, security testing, or account recovery with proper authorization.
- Respect each platform’s Terms of Service and robots policies.
- Do not use the tool for harassment, stalking, or unlawful activity.
