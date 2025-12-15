#!/usr/bin/env python3
"""
Standalone Twitter Automation Test Script using Selenium with Undetected Chrome

This script is designed to test Twitter's automation detection capabilities.
It uses undetected-chromedriver to bypass common automation detection methods.

Features:
- Uses undetected_chromedriver to avoid bot detection
- Runs in headed mode (visible browser window)
- Waits for manual user login
- Opens random tweets after user confirmation
- Implements human-like behavior patterns
- Robust error handling

Requirements:
- undetected-chromedriver
- selenium
- Chrome browser installed
"""

import undetected_chromedriver as uc
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import sys
import os
from pathlib import Path


class TwitterAutomationTester:
    """A robust Twitter automation tester using undetected Chrome"""
    
    def __init__(self, user_data_dir=None):
        """Initialize the tester with Chrome driver
        
        Args:
            user_data_dir: Path to Chrome user data directory for persistent login.
                          If None, creates one in the script directory.
        """
        self.driver = None
        self.wait = None
        
        # Set up persistent user data directory
        if user_data_dir is None:
            # Create a chrome_profile directory in the script's directory
            script_dir = Path(__file__).parent
            self.user_data_dir = script_dir / "chrome_twitter_profile"
        else:
            self.user_data_dir = Path(user_data_dir)
        
        # Create the directory if it doesn't exist
        self.user_data_dir.mkdir(exist_ok=True)
        print(f"📁 Using Chrome profile: {self.user_data_dir}")
        
    def setup_driver(self):
        """Setup undetected Chrome driver with anti-detection options and persistent profile"""
        print("\n" + "="*60)
        print("🚀 Initializing Undetected Chrome Driver...")
        print("="*60)
        
        try:
            # Configure Chrome options for maximum stealth
            # Note: undetected_chromedriver already handles most anti-detection
            # We just need to add a few basic options
            options = uc.ChromeOptions()
            
            # IMPORTANT: Use persistent user data directory for login persistence
            options.add_argument(f'--user-data-dir={str(self.user_data_dir)}')
            
            # Basic options for stability
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            
            # Set a realistic window size
            options.add_argument('--window-size=1920,1080')
            
            # Set user agent to look like a real browser
            options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            print("📁 Using persistent Chrome profile (login will be saved)")
            
            # Initialize undetected Chrome driver
            # undetected_chromedriver handles most anti-detection automatically
            # use_subprocess=True can help with stability
            self.driver = uc.Chrome(options=options, use_subprocess=True)
            
            # Set up WebDriverWait for explicit waits
            self.wait = WebDriverWait(self.driver, 20)
            
            # Maximize window for better visibility
            self.driver.maximize_window()
            
            # Small delay to let browser fully initialize
            time.sleep(1)
            
            # Execute CDP commands to further hide automation
            try:
                self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                    "userAgent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                })
            except Exception as cdp_error:
                print(f"⚠️  CDP command warning: {cdp_error}")
                # This is not critical, continue anyway
            
            # Override the navigator.webdriver flag (extra protection)
            try:
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            except Exception as script_error:
                print(f"⚠️  Script injection warning: {script_error}")
                # This is not critical, continue anyway
            
            print("✅ Chrome driver initialized successfully!")
            print("   Browser is running in HEADED mode (visible)")
            print("   Anti-detection measures activated")
            print("   Using PERSISTENT profile (cookies & login saved)")
            
            return True
            
        except Exception as e:
            print(f"❌ Error setting up Chrome driver: {e}")
            print("\n💡 Troubleshooting:")
            print("   1. Make sure Chrome browser is installed")
            print("   2. Try: pip install --upgrade undetected-chromedriver")
            print("   3. Try: pip install --upgrade selenium")
            print("   4. If Chrome version mismatch, let undetected-chromedriver auto-download")
            print("   5. If profile is corrupted, delete: {self.user_data_dir}")
            return False
    
    def human_delay(self, min_seconds=1, max_seconds=3):
        """Simulate human-like delay with random timing"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def smooth_scroll(self, pixels=None):
        """Perform smooth scrolling like a human would"""
        if pixels is None:
            pixels = random.randint(100, 500)
        
        try:
            # Smooth scroll with small increments
            scroll_script = f"""
                window.scrollBy({{
                    top: {pixels},
                    left: 0,
                    behavior: 'smooth'
                }});
            """
            self.driver.execute_script(scroll_script)
            self.human_delay(0.5, 1.5)
        except Exception as e:
            print(f"⚠️  Scroll warning: {e}")
    
    def move_mouse_naturally(self, element=None):
        """Move mouse to element in a natural way"""
        try:
            actions = ActionChains(self.driver)
            if element:
                actions.move_to_element(element).perform()
                self.human_delay(0.2, 0.5)
        except Exception as e:
            print(f"⚠️  Mouse movement warning: {e}")
    
    def check_if_logged_in(self):
        """Check if user is already logged in to Twitter
        
        Returns:
            bool: True if logged in, False otherwise
        """
        print("\n" + "-"*60)
        print("🔍 Checking if already logged in to Twitter...")
        print("-"*60)
        
        try:
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()
            
            # Multiple indicators of being logged in
            logged_in_indicators = [
                '/home' in current_url,
                'x.com/home' in current_url,
                'twitter.com/home' in current_url,
                'compose tweet' in page_source,
                'what is happening' in page_source,
                'data-testid="SideNav_NewTweet_Button"' in self.driver.page_source,
            ]
            
            # Also check for login page indicators (means NOT logged in)
            login_indicators = [
                '/login' in current_url,
                '/flow/login' in current_url,
                'sign in to x' in page_source,
                'sign in to twitter' in page_source,
            ]
            
            if any(login_indicators):
                print("❌ Not logged in (on login page)")
                return False
            
            if any(logged_in_indicators):
                print("✅ Already logged in to Twitter!")
                print(f"   Current URL: {current_url}")
                return True
            
            # If unclear, check for tweet button or other UI elements
            try:
                # Try to find elements that only exist when logged in
                self.driver.find_element(By.CSS_SELECTOR, '[data-testid="SideNav_NewTweet_Button"]')
                print("✅ Already logged in to Twitter! (Found tweet button)")
                return True
            except NoSuchElementException:
                pass
            
            # Default to not logged in if we can't confirm
            print("⚠️  Login status unclear, assuming not logged in")
            return False
            
        except Exception as e:
            print(f"⚠️  Error checking login status: {e}")
            return False
    
    def open_twitter(self):
        """Navigate to Twitter homepage"""
        print("\n" + "-"*60)
        print("🐦 Opening Twitter...")
        print("-"*60)
        
        try:
            self.driver.get("https://twitter.com")
            print("✅ Twitter loaded successfully")
            
            # Random delay to simulate human reading the page
            self.human_delay(2, 4)
            
            # Perform some natural scrolling
            self.smooth_scroll(random.randint(50, 150))
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading Twitter: {e}")
            return False
    
    def wait_for_manual_login(self):
        """Wait for user to manually log in to Twitter"""
        print("\n" + "="*60)
        print("⏳ MANUAL LOGIN REQUIRED")
        print("="*60)
        print("\n📋 Instructions:")
        print("   1. Please log in to Twitter manually in the browser window")
        print("   2. Complete any verification steps if prompted")
        print("   3. Wait until you see your Twitter home feed")
        print("   4. Once logged in, come back here and type: ready")
        print("\n💡 Note: Your login will be saved for future script runs!")
        print("-"*60)
        
        # Wait for user confirmation
        while True:
            user_input = input("\n👤 Type 'ready' when you're logged in: ").strip().lower()
            
            if user_input == 'ready':
                print("\n✅ Great! Proceeding with automation...")
                break
            else:
                print("⚠️  Please type 'ready' to continue (or Ctrl+C to exit)")
        
        # Give a moment to ensure page is stable
        self.human_delay(1, 2)
        
        # Verify we're logged in by checking the current URL
        current_url = self.driver.current_url
        print(f"📍 Current URL: {current_url}")
        
        if "twitter.com" in current_url or "x.com" in current_url:
            print("✅ Login verification passed!")
            print("✅ Login saved! Next time you won't need to log in again.")
            return True
        else:
            print("⚠️  Warning: URL doesn't look like Twitter, but continuing...")
            return True
    
    def find_and_open_random_tweet(self):
        """Find and open a random tweet on the page"""
        print("\n" + "-"*60)
        print("🎲 Searching for tweets to open...")
        print("-"*60)
        
        try:
            # Scroll a bit to load more tweets
            print("📜 Scrolling to load tweets...")
            self.smooth_scroll(random.randint(300, 600))
            self.human_delay(2, 3)
            
            # Try multiple selectors to find tweet links
            tweet_selectors = [
                "article[data-testid='tweet']",
                "div[data-testid='tweet']",
                "article[role='article']",
                "div[data-testid='cellInnerDiv']"
            ]
            
            tweets = []
            for selector in tweet_selectors:
                try:
                    found_tweets = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if found_tweets:
                        tweets.extend(found_tweets)
                        print(f"   ✓ Found {len(found_tweets)} tweets using selector: {selector}")
                        break
                except Exception as e:
                    continue
            
            if not tweets:
                print("⚠️  No tweets found with standard selectors. Trying alternative method...")
                # Try to find any clickable links that look like tweets
                tweets = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/status/']")
            
            if tweets:
                print(f"\n✅ Found {len(tweets)} potential tweet elements")
                
                # Select a random tweet
                random_tweet = random.choice(tweets)
                
                # Scroll to the tweet
                print("📍 Scrolling to selected tweet...")
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", random_tweet)
                self.human_delay(1, 2)
                
                # Move mouse to the tweet naturally
                print("🖱️  Moving mouse to tweet...")
                self.move_mouse_naturally(random_tweet)
                
                # Try to find a link within the tweet
                try:
                    # Look for the tweet link (usually contains /status/)
                    tweet_link = random_tweet.find_element(By.CSS_SELECTOR, "a[href*='/status/']")
                    tweet_url = tweet_link.get_attribute('href')
                    
                    print(f"🔗 Tweet URL found: {tweet_url}")
                    
                    # Human-like delay before clicking
                    self.human_delay(0.5, 1.5)
                    
                    # Click on the tweet
                    print("👆 Clicking on tweet...")
                    
                    # Try JavaScript click for better reliability
                    self.driver.execute_script("arguments[0].click();", tweet_link)
                    
                    print("✅ Tweet opened successfully!")
                    
                    # Wait for tweet to load
                    self.human_delay(2, 4)
                    
                    # Scroll on the tweet page to appear more human
                    self.smooth_scroll(random.randint(100, 300))
                    
                    return True
                    
                except NoSuchElementException:
                    # If we can't find a link, try clicking the article itself
                    print("🔄 Trying alternative click method...")
                    self.driver.execute_script("arguments[0].click();", random_tweet)
                    self.human_delay(2, 4)
                    return True
                    
            else:
                print("❌ No tweets found on the page")
                print("💡 You may need to scroll manually or refresh the page")
                return False
                
        except Exception as e:
            print(f"❌ Error opening tweet: {e}")
            print(f"   Error type: {type(e).__name__}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
            return False
    
    def perform_human_like_actions(self):
        """Perform various human-like actions on the current page"""
        print("\n" + "-"*60)
        print("🤖 Performing human-like actions...")
        print("-"*60)
        
        try:
            # Random scrolling
            print("📜 Random scrolling...")
            for _ in range(random.randint(2, 4)):
                self.smooth_scroll(random.randint(-200, 500))
                self.human_delay(1, 2)
            
            # Move mouse around
            print("🖱️  Moving mouse naturally...")
            actions = ActionChains(self.driver)
            for _ in range(random.randint(2, 4)):
                x_offset = random.randint(-100, 100)
                y_offset = random.randint(-100, 100)
                actions.move_by_offset(x_offset, y_offset).perform()
                self.human_delay(0.3, 0.7)
                # Reset position
                actions.move_by_offset(-x_offset, -y_offset).perform()
            
            print("✅ Human-like actions completed")
            
        except Exception as e:
            print(f"⚠️  Warning during human-like actions: {e}")
    
    def check_for_automation_detection(self):
        """Check if Twitter has detected automation"""
        print("\n" + "-"*60)
        print("🔍 Checking for automation detection...")
        print("-"*60)
        
        try:
            # Check page title
            page_title = self.driver.title
            print(f"📄 Page title: {page_title}")
            
            # Check current URL
            current_url = self.driver.current_url
            print(f"📍 Current URL: {current_url}")
            
            # Check for common automation detection indicators
            page_source = self.driver.page_source.lower()
            
            detection_keywords = [
                "automation",
                "suspicious",
                "unusual activity",
                "verify you're human",
                "captcha",
                "blocked"
            ]
            
            detected = []
            for keyword in detection_keywords:
                if keyword in page_source:
                    detected.append(keyword)
            
            if detected:
                print(f"⚠️  Potential detection keywords found: {', '.join(detected)}")
                print("   Note: This doesn't necessarily mean you're blocked")
            else:
                print("✅ No obvious automation detection indicators found!")
            
            # Check for webdriver flag
            webdriver_value = self.driver.execute_script("return navigator.webdriver")
            print(f"🔧 Navigator.webdriver value: {webdriver_value}")
            
            if webdriver_value is None or webdriver_value is False:
                print("✅ Webdriver flag successfully hidden!")
            else:
                print("⚠️  Webdriver flag is exposed (may indicate detection)")
            
            return len(detected) == 0
            
        except Exception as e:
            print(f"⚠️  Error during detection check: {e}")
            return False
    
    def run_test(self):
        """Run the complete Twitter automation test"""
        print("\n" + "="*60)
        print("🚀 TWITTER AUTOMATION DETECTION TEST")
        print("="*60)
        print("\nThis script will:")
        print("  1. Open Twitter in Chrome (visible window)")
        print("  2. Check if you're already logged in")
        print("  3. If not logged in, wait for you to log in manually")
        print("  4. Open a random tweet")
        print("  5. Perform human-like actions")
        print("  6. Check for automation detection")
        print("\n💡 Your login will be saved - you only need to log in once!")
        print("="*60)
        
        try:
            # Setup driver with persistent profile
            if not self.setup_driver():
                return False
            
            # Open Twitter
            if not self.open_twitter():
                return False
            
            # Check if already logged in
            is_logged_in = self.check_if_logged_in()
            
            if not is_logged_in:
                # Not logged in, need manual login
                print("\n🔐 Not logged in to Twitter")
                if not self.wait_for_manual_login():
                    return False
                
                # Verify login was successful
                if not self.check_if_logged_in():
                    print("\n❌ Login verification failed!")
                    print("   Please make sure you're on the Twitter home feed")
                    return False
            else:
                # Already logged in!
                print("\n🎉 You're already logged in! Skipping login step.")
                self.human_delay(1, 2)
            
            # Find and open a random tweet
            if not self.find_and_open_random_tweet():
                print("\n⚠️  Could not open a tweet automatically.")
                print("   The browser will remain open for manual inspection.")
            
            # Perform human-like actions
            self.perform_human_like_actions()
            
            # Check for automation detection
            self.check_for_automation_detection()
            
            # Keep browser open for inspection
            print("\n" + "="*60)
            print("✅ TEST COMPLETED")
            print("="*60)
            print("\n📋 Next Steps:")
            print("   1. Inspect the browser window for any detection messages")
            print("   2. Try interacting with Twitter manually")
            print("   3. Check if you can perform normal actions")
            print("\n💾 Your login session is saved in: chrome_twitter_profile/")
            print("⏸️  Browser will remain open. Press Ctrl+C to close...")
            
            # Keep the browser open
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\n👋 Closing browser...")
            
            return True
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Test interrupted by user")
            return False
            
        except Exception as e:
            print(f"\n❌ Error during test: {e}")
            import traceback
            print(traceback.format_exc())
            return False
            
        finally:
            # Cleanup
            if self.driver:
                print("🧹 Cleaning up...")
                self.human_delay(1, 2)
                self.driver.quit()
                print("✅ Browser closed")
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("🐦 Twitter Automation Detection Test - Undetected Chrome")
    print("="*60)
    
    # Check if user wants to continue
    print("\nℹ️  This script uses undetected-chromedriver to test")
    print("   Twitter's automation detection capabilities.")
    print("\n✨ NEW: Persistent login - you only need to log in once!")
    print("   Your session will be saved in 'chrome_twitter_profile/'")
    print("\n⚠️  Use responsibly and in accordance with Twitter's ToS")
    
    try:
        input("\n▶️  Press Enter to start (or Ctrl+C to cancel)...")
    except KeyboardInterrupt:
        print("\n\n👋 Cancelled by user")
        return
    
    # Create and run tester
    tester = TwitterAutomationTester()
    success = tester.run_test()
    
    if success:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed or was interrupted")
    
    print("\n" + "="*60)
    print("Done!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()

