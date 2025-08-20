#!/usr/bin/env python3
"""
OSINT Username Hunter - Social Media Username Investigation Tool
Developer: ErenTechLabs
Enhanced version with improved detection algorithms
"""

import requests
import argparse
import time
from colorama import init, Fore, Back, Style
from concurrent.futures import ThreadPoolExecutor
import json
from urllib.parse import urlparse

# Initialize colorama
init()


def generate_username_variants(username):
    """Generate different case combinations of the username"""
    variants = [username, username.lower(), username.upper(), username.capitalize()]  # Original

    # Different combinations

    # If multi-character, add mixed combinations
    if len(username) > 1:
        variants.append(username[0].upper() + username[1:].lower())  # Eren
        if len(username) > 2:
            variants.append(username[0].lower() + username[1:].upper())  # eREN

    # Remove duplicates
    return list(set(variants))


class OSINTHunter:
    def __init__(self):
        self.platforms = {
            "Instagram": {
                "url": "https://www.instagram.com/{}",
                "error_indicators": [
                    "Sorry, this page isn't available",
                    "The link you followed may be broken",
                    "Page Not Found"
                ],
                "success_indicators": ["followers", "following", "posts"]
            },
            "Twitter": {
                "url": "https://twitter.com/{}",
                "error_indicators": [
                    "This account doesn't exist",
                    "Account suspended",
                    "Something went wrong"
                ],
                "success_indicators": ["Tweets", "Following", "Followers"]
            },
            "GitHub": {
                "url": "https://github.com/{}",
                "error_indicators": ["Not Found", "404"],
                "success_indicators": ["repositories", "contributions", "profile"]
            },
            "Facebook": {
                "url": "https://www.facebook.com/{}",
                "error_indicators": [
                    "Content Not Found",
                    "This content isn't available right now",
                    "Page not found"
                ],
                "success_indicators": ["timeline", "about", "photos"]
            },
            "LinkedIn": {
                "url": "https://www.linkedin.com/in/{}",
                "error_indicators": [
                    "Page not found",
                    "This profile was not found",
                    "Member not found"
                ],
                "success_indicators": ["experience", "connections", "profile"]
            },
            "TikTok": {
                "url": "https://www.tiktok.com/@{}",
                "error_indicators": [
                    "Couldn't find this account",
                    "User not found",
                    "Something went wrong"
                ],
                "success_indicators": ["Following", "Followers", "Likes"]
            },
            "YouTube": {
                "url": "https://www.youtube.com/c/{}",
                "error_indicators": [
                    "This channel does not exist",
                    "404 Not Found"
                ],
                "success_indicators": ["subscribers", "videos", "channel"]
            },
            "Pinterest": {
                "url": "https://www.pinterest.com/{}",
                "error_indicators": [
                    "Sorry, we couldn't find that page",
                    "User not found"
                ],
                "success_indicators": ["followers", "following", "pins"]
            },
            "Reddit": {
                "url": "https://www.reddit.com/user/{}",
                "error_indicators": [
                    "Sorry, nobody on Reddit goes by that name",
                    "page not found"
                ],
                "success_indicators": ["karma", "cake day", "post karma"]
            },
            "Telegram": {
                "url": "https://t.me/{}",
                "error_indicators": [
                    "If you have Telegram, you can contact",
                    "User not found"
                ],
                "success_indicators": ["members", "online", "channel"]
            },
            "Steam": {
                "url": "https://steamcommunity.com/id/{}",
                "error_indicators": [
                    "The specified profile could not be found",
                    "No profile could be found"
                ],
                "success_indicators": ["level", "games", "friends"]
            },
            "Spotify": {
                "url": "https://open.spotify.com/user/{}",
                "error_indicators": [
                    "User not found",
                    "Spotify - Page not found"
                ],
                "success_indicators": ["playlist", "followers", "following"]
            },
            "Twitch": {
                "url": "https://www.twitch.tv/{}",
                "error_indicators": [
                    "Sorry. Unless you've got a time machine",
                    "This channel does not exist"
                ],
                "success_indicators": ["followers", "views", "stream"]
            },
            "VKontakte": {
                "url": "https://vk.com/{}",
                "error_indicators": [
                    "Page not found",
                    "Access denied"
                ],
                "success_indicators": ["friends", "photos", "posts"]
            },
            "Snapchat": {
                "url": "https://www.snapchat.com/add/{}",
                "error_indicators": [
                    "Oh snap! Something went wrong",
                    "User not found"
                ],
                "success_indicators": ["snapcode", "add friend"]
            },
            "Medium": {
                "url": "https://medium.com/@{}",
                "error_indicators": [
                    "Page not found",
                    "User not found"
                ],
                "success_indicators": ["stories", "followers", "following"]
            },
            "DeviantArt": {
                "url": "https://{}.deviantart.com",
                "error_indicators": [
                    "The page you're looking for cannot be found",
                    "User not found"
                ],
                "success_indicators": ["deviations", "watchers", "pageviews"]
            },
            "Flickr": {
                "url": "https://www.flickr.com/people/{}",
                "error_indicators": [
                    "Flickr User Not Found",
                    "Person not found"
                ],
                "success_indicators": ["photos", "photostream", "contacts"]
            },
            "Tumblr": {
                "url": "https://{}.tumblr.com",
                "error_indicators": [
                    "There's nothing here",
                    "This Tumblr may contain sensitive media"
                ],
                "success_indicators": ["posts", "archive", "followers"]
            },
            "Behance": {
                "url": "https://www.behance.net/{}",
                "error_indicators": [
                    "Oops! We can't find that page",
                    "User not found"
                ],
                "success_indicators": ["projects", "followers", "following"]
            },
            "Patreon": {
                "url": "https://www.patreon.com/{}",
                "error_indicators": [
                    "Sorry, the page you are looking for could not be found",
                    "Creator not found"
                ],
                "success_indicators": ["patrons", "posts", "creating"]
            },
            "SoundCloud": {
                "url": "https://soundcloud.com/{}",
                "error_indicators": [
                    "Sorry! Something went wrong",
                    "User not found"
                ],
                "success_indicators": ["tracks", "followers", "following"]
            },
            "Dribbble": {
                "url": "https://dribbble.com/{}",
                "error_indicators": [
                    "Whoops, that page is gone",
                    "User not found"
                ],
                "success_indicators": ["shots", "followers", "following"]
            },
            "About.me": {
                "url": "https://about.me/{}",
                "error_indicators": [
                    "Uh oh. This page doesn't exist",
                    "Page not found"
                ],
                "success_indicators": ["about", "contact", "links"]
            },
            "BitBucket": {
                "url": "https://bitbucket.org/{}",
                "error_indicators": [
                    "There is no such user",
                    "404"
                ],
                "success_indicators": ["repositories", "snippets", "downloads"]
            },
            "CashApp": {
                "url": "https://cash.app/${}",
                "error_indicators": [
                    "404 - Page not found",
                    "This $Cashtag doesn't exist"
                ],
                "success_indicators": ["$cashtag", "pay", "request"]
            },
            "Etsy": {
                "url": "https://www.etsy.com/shop/{}",
                "error_indicators": [
                    "Sorry, we couldn't find that page",
                    "Shop not found"
                ],
                "success_indicators": ["items", "reviews", "shop policies"]
            },
            "Gravatar": {
                "url": "https://en.gravatar.com/{}",
                "error_indicators": [
                    "User not found",
                    "No such user"
                ],
                "success_indicators": ["profile", "avatar", "about"]
            },
            "HackerNews": {
                "url": "https://news.ycombinator.com/user?id={}",
                "error_indicators": [
                    "No such user",
                    "User not found"
                ],
                "success_indicators": ["karma", "submissions", "comments"]
            },
            "Keybase": {
                "url": "https://keybase.io/{}",
                "error_indicators": [
                    "User not found",
                    "404"
                ],
                "success_indicators": ["proofs", "public key", "followers"]
            },
            "Last.fm": {
                "url": "https://www.last.fm/user/{}",
                "error_indicators": [
                    "User not found",
                    "Sorry, we can't find that user"
                ],
                "success_indicators": ["scrobbles", "artists", "tracks"]
            },
            "Quora": {
                "url": "https://www.quora.com/profile/{}",
                "error_indicators": [
                    "Page Not Found",
                    "User not found"
                ],
                "success_indicators": ["answers", "questions", "followers"]
            },
            "WeHeartIt": {
                "url": "https://weheartit.com/{}",
                "error_indicators": [
                    "Sorry, this page isn't available",
                    "User not found",
                    "page not found",
                    "404",
                    "oops! we can't find that page"
                ],
                "success_indicators": ["hearts", "collections", "followers", "inspiring images"]
            },
            "Wattpad": {
                "url": "https://www.wattpad.com/user/{}",
                "error_indicators": [
                    "Sorry, that page doesn't exist",
                    "User not found"
                ],
                "success_indicators": ["stories", "followers", "following"]
            }
        }

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

        self.found = []
        self.not_found = []
        self.errors = []

    def advanced_username_check(self, platform_name, platform_data, username):
        """Advanced username checking with multiple validation methods"""
        url = platform_data["url"].format(username)

        try:
            # Make a request with timeout
            response = requests.get(url, headers=self.headers, timeout=15, allow_redirects=True)

            # Get response content
            content = response.text.lower()
            original_content = response.text  # Keep the original case for some checks

            # If the status code is 404 or similar, it's definitely not found
            if response.status_code in [404, 403, 410, 500]:
                return False, f"HTTP {response.status_code}"

            # If the status code is not 200, it might be rate limiting or other issues
            if response.status_code != 200:
                return None, f"HTTP {response.status_code} - Uncertain"

            # Check for explicit error indicators first (most reliable)
            for error_indicator in platform_data["error_indicators"]:
                if error_indicator.lower() in content:
                    return False, f"Error indicator found: {error_indicator}"

            # Special checks for specific platforms
            if platform_name == "WeHeartIt":
                # WeHeartIt specific checks
                if "create account" in content and "sign up" in content and "log in" in content:
                    # If we see signup/login prompts without profile content, likely not found
                    if not any(indicator in content for indicator in ["hearts", "collections", "followers"]):
                        return False, "WeHeartIt: Shows signup page instead of profile"

                # Check if redirected to the main page
                if response.url.endswith("weheartit.com/") or response.url.endswith("weheartit.com"):
                    return False, "WeHeartIt: Redirected to main page"

            elif platform_name == "Instagram":
                # Instagram-specific checks
                if '"ProfilePage"' not in original_content and '"User"' not in original_content:
                    return False, "Instagram: No profile data found"

            elif platform_name == "Twitter":
                # Twitter/ X-specific checks
                if '"screen_name"' not in original_content and 'data-screen-name' not in original_content:
                    return False, "Twitter: No user data found"

            elif platform_name == "GitHub":
                # GitHub-specific checks
                if '"login":' not in original_content and 'data-login=' not in original_content:
                    return False, "GitHub: No user login data found"

            # Check if we were redirected to a different path (might indicate not found)
            expected_path = f"/{username}" if platform_name not in ["DeviantArt", "Tumblr"] else ""
            if urlparse(response.url).path.lower() == "/" and expected_path:
                return False, "Redirected to homepage - user likely not found"

            # Check for success indicators with a higher threshold
            success_count = 0
            for success_indicator in platform_data["success_indicators"]:
                if success_indicator.lower() in content:
                    success_count += 1

            # Require at least 1 success indicator for most platforms
            if success_count >= 1:
                return True, f"Found {success_count} success indicators"

            # Additional content analysis
            if len(content) < 500:  # Very short content might be an error page
                return False, "Content too short - likely error/redirect page"

            # Check for common "not found" patterns in any language
            not_found_patterns = [
                "not found", "404", "page not found", "user not found",
                "doesn't exist", "not available", "can't find", "no such",
                "sorry", "oops", "error", "bulunamadı", "mevcut değil"
            ]

            not_found_count = sum(1 for pattern in not_found_patterns if pattern in content)
            if not_found_count >= 2:  # Multiple not-found indicators
                return False, f"Multiple not-found patterns detected ({not_found_count})"

            # If we reach here with no success indicators, it's likely not found
            return False, "No success indicators found - likely not found"

        except requests.exceptions.Timeout:
            return None, "Request timeout"
        except requests.exceptions.ConnectionError:
            return None, "Connection error"
        except requests.exceptions.RequestException as e:
            return None, f"Request error: {str(e)}"

    def search_username(self, username, use_variants=False):
        """Main search function"""
        usernames_to_check = [username]

        if use_variants:
            usernames_to_check = generate_username_variants(username)
            print(f"{Fore.YELLOW}[INFO] Generating username variants: {', '.join(usernames_to_check)}{Style.RESET_ALL}")

        print(f"{Fore.CYAN}[INFO] Starting search across {len(self.platforms)} platforms...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[INFO] Target usernames: {', '.join(usernames_to_check)}{Style.RESET_ALL}")
        print("-" * 80)

        total_checks = len(self.platforms) * len(usernames_to_check)
        completed = 0

        # Check each platform for each username variant
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = []

            for platform_name, platform_data in self.platforms.items():
                for user in usernames_to_check:
                    future = executor.submit(self.advanced_username_check, platform_name, platform_data, user)
                    futures.append((future, platform_name, platform_data, user))

            for future, platform_name, platform_data, user in futures:
                completed += 1
                try:
                    result, reason = future.result()
                    progress = (completed / total_checks) * 100

                    if result is True:
                        url = platform_data["url"].format(user)
                        self.found.append((platform_name, user, url, reason))
                        print(f"{Fore.GREEN}[✓] {platform_name}: {user} - {url} ({reason}){Style.RESET_ALL}")
                    elif result is False:
                        self.not_found.append((platform_name, user, reason))
                    else:  # the result is None (uncertain)
                        self.errors.append(f"{platform_name} ({user}): {reason}")

                    # Progress indicator
                    if completed % 15 == 0:
                        print(
                            f"{Fore.BLUE}[INFO] Progress: {progress:.1f}% ({completed}/{total_checks}){Style.RESET_ALL}")

                except Exception as e:
                    self.errors.append(f"{platform_name} ({user}): {str(e)}")

                # Rate limiting
                time.sleep(0.2)

    def print_results(self):
        """Print search results"""
        print("\n" + "=" * 80)
        print(
            f"{Fore.CYAN}{Back.BLACK}                         SEARCH RESULTS                          {Style.RESET_ALL}")
        print("=" * 80)

        if self.found:
            print(f"\n{Fore.GREEN}[FOUND PROFILES] ({len(self.found)} found):{Style.RESET_ALL}")
            print("-" * 60)
            for platform, username, url, reason in self.found:
                print(f"{Fore.GREEN}• {platform:15} | {username:20} | {url}{Style.RESET_ALL}")
                print(f"  {Fore.CYAN}└─ Reason: {reason}{Style.RESET_ALL}")

        if self.not_found:
            print(f"\n{Fore.RED}[NOT FOUND] ({len(self.not_found)} platforms):{Style.RESET_ALL}")
            print("-" * 60)
            not_found_platforms = list(set([platform for platform, _, _ in self.not_found]))
            for platform in not_found_platforms[:10]:
                print(f"{Fore.RED}• {platform}{Style.RESET_ALL}")
            if len(not_found_platforms) > 10:
                print(f"{Fore.RED}• ... and {len(not_found_platforms) - 10} more platforms{Style.RESET_ALL}")

        if self.errors:
            print(f"\n{Fore.YELLOW}[ERRORS/UNCERTAIN] ({len(self.errors)} cases):{Style.RESET_ALL}")
            print("-" * 60)
            for error in self.errors[:8]:
                print(f"{Fore.YELLOW}• {error}{Style.RESET_ALL}")
            if len(self.errors) > 8:
                print(f"{Fore.YELLOW}• ... and {len(self.errors) - 8} more errors{Style.RESET_ALL}")

        print(f"\n{Fore.CYAN}[SUMMARY]{Style.RESET_ALL}")
        print(f"Total profiles found: {Fore.GREEN}{len(self.found)}{Style.RESET_ALL}")
        print(f"Platforms checked: {len(self.platforms)}")
        print(f"Not found/Errors: {Fore.YELLOW}{len(self.not_found) + len(self.errors)}{Style.RESET_ALL}")

    def save_results(self, filename):
        """Save results to a JSON file"""
        data = {
            "found_profiles": [
                {"platform": platform, "username": username, "url": url, "detection_reason": reason}
                for platform, username, url, reason in self.found
            ],
            "not_found_platforms": [
                {"platform": platform, "username": username, "reason": reason}
                for platform, username, reason in self.not_found
            ],
            "errors": self.errors,
            "summary": {
                "total_found": len(self.found),
                "total_platforms_checked": len(self.platforms),
                "total_not_found": len(self.not_found),
                "total_errors": len(self.errors),
                "confidence_level": "high" if len(self.errors) < len(self.found) else "medium"
            }
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"{Fore.GREEN}[INFO] Results saved to {filename}{Style.RESET_ALL}")


def main():
    print(f"""{Fore.RED}
    ╔═══════════════════════════════════════════════════════════════╗
    ║                    OSINT USERNAME HUNTER                      ║
    ║                 Social Media Investigation Tool               ║
    ║                     Developer: ErenTechLabs                   ║
    ║                      Enhanced Detection v2.0                 ║
    ╚═══════════════════════════════════════════════════════════════╝
    {Style.RESET_ALL}""")

    parser = argparse.ArgumentParser(description="OSINT Username Hunter - Social Media Username Investigation Tool")
    parser.add_argument("username", help="Target username to search for")
    parser.add_argument("-a", "--allcase", action="store_true",
                        help="Search all case combinations of username (eren, Eren, EREN, etc.)")
    parser.add_argument("-o", "--output", help="Save results to JSON file")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    if not args.username:
        print(f"{Fore.RED}[ERROR] Please provide a username to search for.{Style.RESET_ALL}")
        return

    # Validate username
    if len(args.username) < 2:
        print(f"{Fore.RED}[ERROR] Username must be at least 2 characters long.{Style.RESET_ALL}")
        return

    hunter = OSINTHunter()

    print(f"{Fore.CYAN}[INFO] Target username: {args.username}{Style.RESET_ALL}")
    if args.allcase:
        print(f"{Fore.CYAN}[INFO] All case combinations will be searched{Style.RESET_ALL}")
    if args.verbose:
        print(f"{Fore.CYAN}[INFO] Verbose mode enabled{Style.RESET_ALL}")

    start_time = time.time()

    try:
        hunter.search_username(args.username, args.allcase)
        hunter.print_results()

        if args.output:
            hunter.save_results(args.output)

        end_time = time.time()
        print(f"\n{Fore.CYAN}[INFO] Search completed in {end_time - start_time:.2f} seconds{Style.RESET_ALL}")

        # Provide recommendation
        if len(hunter.found) > 0:
            print(f"{Fore.GREEN}[RECOMMENDATION] Manual verification recommended for found profiles{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}[RECOMMENDATION] Try different username variations or check spelling{Style.RESET_ALL}")

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[INFO] Search interrupted by user.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[ERROR] Unexpected error occurred: {str(e)}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()