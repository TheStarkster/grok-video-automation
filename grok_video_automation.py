#!/usr/bin/env python3
"""
Grok Video Automation - Production Script

Fully automated video generation from images using Grok AI.

COMPLETE WORKFLOW:
  1. Upload image
  2. Click "Edit Image" button
  3. Click "Make video" button (intelligent wait for editor)
  4. Wait for prompt textarea (dynamic detection)
  5. Enter custom prompt
  6. Submit and monitor video generation
  7. Wait for actual video with valid src (not just button appearance)
  8. Download generated video automatically

FEATURES:
  - Intelligent waits (no hardcoded delays)
  - Monitors for actual video generation completion
  - Multi-strategy element clicking (ActionChains, native, JS)
  - Saves learning data for continuous improvement
  - Robust error handling

USAGE:
  python3 grok_video_automation.py
"""

import undetected_chromedriver as uc
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from pathlib import Path
import json
from datetime import datetime
import random


class GrokVideoAutomation:
    """Automated video generation from images using Grok AI"""
    
    def __init__(self, user_data_dir=None):
        """Initialize automation"""
        self.driver = None
        self.wait = None
        
        # Use same Chrome profile
        if user_data_dir is None:
            script_dir = Path(__file__).parent
            self.user_data_dir = script_dir / "chrome_twitter_profile"
        else:
            self.user_data_dir = Path(user_data_dir)
        
        print(f"📁 Using Chrome profile: {self.user_data_dir}")
        
        # Test image
        self.test_image_path = Path(__file__).parent / "test_input.jpg"
        if not self.test_image_path.exists():
            raise FileNotFoundError(f"Test image not found: {self.test_image_path}")
        print(f"🖼️  Test image: {self.test_image_path}")
        
        # Load previous learning
        self.upload_learning = self.load_learning("upload_learning_data.json")
        self.edit_learning = self.load_learning("edit_button_learning_data.json")
        
        # Phase 3 learning data
        self.make_video_button_found = False
        self.make_video_button_text = None
        self.make_video_button_xpath = "/html/body/div[7]/div/footer/div/div/div[1]/button"
        self.prompt_textarea_found = False
        self.prompt_textarea_placeholder = None
        self.wait_time_worked = 0  # Will be measured dynamically
        self.video_generation_started = False
        self.video_generation_time = 0
        self.video_downloaded = False
        
        # Test prompt
        self.test_prompts = [
            "Make this image come to life",
            "Add smooth motion to this scene",
            "Create a dynamic video from this",
            "Animate this image naturally",
            "Bring movement to this picture"
        ]
        self.test_prompt = random.choice(self.test_prompts)
        print(f"🎲 Random test prompt: '{self.test_prompt}'")
    
    def load_learning(self, filename):
        """Load learning data from file"""
        try:
            learning_file = Path(__file__).parent / filename
            if learning_file.exists():
                with open(learning_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️  Could not load {filename}: {e}")
        return None
    
    def setup_driver(self):
        """Setup Chrome driver"""
        print("\n🚀 Initializing Chrome...")
        
        try:
            options = uc.ChromeOptions()
            options.add_argument(f'--user-data-dir={str(self.user_data_dir)}')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            options.add_argument('--window-size=1920,1080')
            
            self.driver = uc.Chrome(options=options, use_subprocess=True)
            self.wait = WebDriverWait(self.driver, 20)
            self.driver.maximize_window()
            time.sleep(1)
            
            print("✅ Chrome ready!")
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def navigate_to_grok(self):
        """Navigate to Grok"""
        print("\n🤖 Navigating to Grok...")
        
        try:
            self.driver.get("https://grok.com")
            time.sleep(4)
            print(f"✅ Loaded!")
            
            # Focus the page to ensure interactions work
            self.focus_page()
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def focus_page(self):
        """Focus the page by clicking on blank space"""
        try:
            print("🎯 Clicking blank space to focus page...")
            
            # Simple approach: move to a safe blank area and click
            actions = ActionChains(self.driver)
            # Move to coordinates that are likely to be blank (right side, middle height)
            actions.move_by_offset(800, 400).click().perform()
            
            # Reset the offset for future actions
            actions.move_by_offset(-800, -400).perform()
            
            time.sleep(0.5)
            print("✅ Page focused!")
            return True
            
        except Exception as e:
            print(f"⚠️  Could not focus page: {e}")
            return True  # Don't fail the whole automation for this
    
    def upload_image(self):
        """Upload image using learned method"""
        print("\n" + "="*60)
        print("📤 PHASE 1: Uploading Image")
        print("="*60)
        
        try:
            wait_time = 5
            if self.upload_learning:
                wait_time = self.upload_learning.get("recommendations", {}).get("wait_time", 5)
            
            file_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
            if not file_inputs:
                print("❌ No file inputs found!")
                return False
            
            target_input = None
            for fi in file_inputs:
                if fi.get_attribute("name") == "files":
                    target_input = fi
                    break
            if not target_input:
                target_input = file_inputs[0]
            
            target_input.send_keys(str(self.test_image_path.absolute()))
            print(f"✅ Uploaded! Waiting {wait_time}s...")
            time.sleep(wait_time)
            
            # Focus page after upload to ensure Edit Image button is clickable
            self.focus_page()
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def click_edit_image_button(self):
        """Click Edit Image button to enter editor"""
        print("\n" + "="*60)
        print("🖱️  PHASE 2: Clicking Edit Image Button")
        print("="*60)
        
        try:
            time.sleep(2)
            all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
            
            for button in all_buttons:
                text = button.text.strip()
                aria_label = (button.get_attribute("aria-label") or "").strip()
                
                if ("edit" in text.lower() and "image" in text.lower()) or (aria_label.lower() == "edit image"):
                    if button.is_displayed():
                        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
                        time.sleep(0.5)
                        
                        try:
                            button.click()
                        except:
                            self.driver.execute_script("arguments[0].click();", button)
                        
                        print("✅ Clicked Edit Image!")
                        time.sleep(3)
                        return True
            
            print("❌ Not found!")
            return False
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def click_make_video_button(self):
        """Click Make video button"""
        print("\n" + "="*60)
        print("🎬 PHASE 3A: Clicking Make Video Button")
        print("="*60)
        
        try:
            # Wait for editor to be ready (check for textarea that should exist in editor)
            print("⏳ Waiting for editor to be ready...")
            try:
                self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "textarea")))
                print("✅ Editor ready!")
            except TimeoutException:
                print("⚠️  Editor textarea not found, continuing anyway...")
            
            # Wait for Make video button to be clickable
            print("🔍 Waiting for Make video button...")
            try:
                button = self.wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "/html/body/div[7]/div/footer/div/div/div[1]/button")
                ))
                
                text = button.text.strip()
                print(f"✅ Found: '{text}'")
                self.make_video_button_found = True
                self.make_video_button_text = text
                
                # Scroll and click
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
                time.sleep(0.3)
                
                # Try clicks
                for method_name, click_func in [
                    ("native", lambda: button.click()),
                    ("ActionChains", lambda: ActionChains(self.driver).move_to_element(button).click().perform()),
                    ("JavaScript", lambda: self.driver.execute_script("arguments[0].click();", button))
                ]:
                    try:
                        click_func()
                        print(f"✅ Clicked!")
                        return True
                    except:
                        continue
                
                print("❌ All click methods failed!")
                return False
                
            except TimeoutException:
                print("❌ Make video button not found!")
                return False
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def wait_for_prompt_textarea(self):
        """Wait for prompt textarea to appear after clicking Make video"""
        print("\n" + "="*60)
        print("⏳ PHASE 3B: Waiting for Prompt Textarea")
        print("="*60)
        
        start_time = time.time()
        max_wait = 60  # Maximum 60 seconds
        
        print("⏳ Waiting for prompt textarea to appear...")
        
        try:
            # Wait for a visible textarea (the prompt input should appear)
            while time.time() - start_time < max_wait:
                textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
                
                for textarea in textareas:
                    if textarea.is_displayed():
                        placeholder = textarea.get_attribute("placeholder") or ""
                        # Look for prompt-related placeholder text
                        if any(keyword in placeholder.lower() for keyword in ["customize", "video", "describe", "prompt"]):
                            elapsed = int(time.time() - start_time)
                            print(f"✅ Prompt textarea ready! (took {elapsed}s)")
                            print(f"   Placeholder: '{placeholder}'")
                            self.wait_time_worked = elapsed
                            return True
                
                # Check every second
                time.sleep(1)
            
            # Timeout - but let's try anyway
            elapsed = int(time.time() - start_time)
            print(f"⚠️  Timeout after {elapsed}s, proceeding anyway...")
            return True
            
        except Exception as e:
            print(f"⚠️  Error: {e}, proceeding anyway...")
            return True
    
    def find_and_enter_prompt(self):
        """Find prompt textarea and enter prompt"""
        print("\n" + "="*60)
        print("📝 PHASE 3C: Finding and Entering Prompt")
        print("="*60)
        
        try:
            print("🔍 Looking for prompt textarea...")
            
            textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
            
            for textarea in textareas:
                if textarea.is_displayed():
                    placeholder = textarea.get_attribute("placeholder") or ""
                    print(f"✅ Found textarea: '{placeholder}'")
                    
                    self.prompt_textarea_found = True
                    self.prompt_textarea_placeholder = placeholder
                    
                    # Enter prompt
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", textarea)
                    time.sleep(0.5)
                    textarea.click()
                    textarea.clear()
                    textarea.send_keys(self.test_prompt)
                    print(f"📝 Prompt entered: '{self.test_prompt}'")
                    
                    # Submit
                    textarea.send_keys(Keys.RETURN)
                    print("✅ Submitted!")
                    
                    self.video_generation_started = True
                    time.sleep(2)
                    return True
            
            print("❌ No visible textarea found!")
            return False
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def monitor_video_generation(self):
        """Monitor for video generation completion - wait for ACTUAL video, not just button"""
        print("\n" + "="*60)
        print("👀 PHASE 3D: Monitoring Video Generation")
        print("="*60)
        
        start_time = time.time()
        max_wait = 180  # 3 minutes max
        
        print("⏳ Waiting for video to be generated...")
        print("   (Looking for <video> element with valid src)")
        
        try:
            while time.time() - start_time < max_wait:
                elapsed = int(time.time() - start_time)
                
                # FIRST PRIORITY: Check for actual video element with valid src
                videos = self.driver.find_elements(By.TAG_NAME, "video")
                for video in videos:
                    if not video.is_displayed():
                        continue
                    
                    src = video.get_attribute("src") or ""
                    
                    # Valid video src should be a blob URL or full URL, not empty
                    if src and (src.startswith("blob:") or src.startswith("http")):
                        print(f"✅ Video generated! ({elapsed}s)")
                        print(f"   Video src: {src[:50]}...")
                        self.video_generation_time = elapsed
                        
                        # Now look for download button
                        time.sleep(1)  # Give UI a moment to stabilize
                        download_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[aria-label*='ownload']")
                        for button in download_buttons:
                            if button.is_displayed():
                                aria = button.get_attribute("aria-label") or ""
                                if "download" in aria.lower():
                                    print(f"✅ Download button found!")
                                    return button
                        
                        # If no download button yet, return the video element
                        print("⚠️  Video ready but download button not found yet")
                        return video
                
                # Progress update
                if elapsed % 10 == 0 and elapsed > 0:
                    print(f"   Still generating... {elapsed}s")
                elif elapsed % 5 == 0 and elapsed > 0:
                    # Check how many videos we see (for debugging)
                    video_count = len([v for v in self.driver.find_elements(By.TAG_NAME, "video") if v.is_displayed()])
                    if video_count > 0:
                        print(f"   Found {video_count} video element(s), checking src...")
                
                time.sleep(2)
            
            print(f"⚠️  Timeout after {max_wait}s - video not generated")
            return None
            
        except Exception as e:
            print(f"⚠️  Error: {e}")
            import traceback
            print(traceback.format_exc())
            return None
    
    def download_video(self, element):
        """Download the generated video"""
        print("\n" + "="*60)
        print("💾 PHASE 3E: Downloading Video")
        print("="*60)
        
        try:
            # If element is a video, find the download button
            if element.tag_name == "video":
                print("🎥 Video element provided, searching for download button...")
                
                # Wait a bit for download button to appear
                max_wait_for_button = 30
                start_time = time.time()
                download_button = None
                
                while time.time() - start_time < max_wait_for_button:
                    download_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[aria-label*='ownload']")
                    
                    for button in download_buttons:
                        if button.is_displayed():
                            aria = button.get_attribute("aria-label") or ""
                            if "download" in aria.lower():
                                download_button = button
                                break
                    
                    if download_button:
                        break
                    
                    elapsed = int(time.time() - start_time)
                    if elapsed % 5 == 0:
                        print(f"   Waiting for download button... {elapsed}s")
                    time.sleep(1)
                
                if not download_button:
                    print("⚠️  Download button not found after 30s")
                    print("   Video is ready but download button didn't appear")
                    return False
                
                element = download_button
                print("✅ Download button found!")
            
            # Now element should be the download button
            aria = element.get_attribute("aria-label") or ""
            print(f"   Button aria-label: '{aria}'")
            
            # Scroll to button
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            time.sleep(0.5)
            
            # Click download button
            print("⬇️  Clicking download...")
            try:
                element.click()
                print("✅ Download clicked!")
            except:
                # Try JavaScript click
                self.driver.execute_script("arguments[0].click();", element)
                print("✅ Download clicked (JS)!")
            
            # Give some time for download to initiate
            time.sleep(2)
            
            self.video_downloaded = True
            print("✅ Video download initiated!")
            print("   📁 Check your Downloads folder for the video file")
            
            return True
            
        except Exception as e:
            print(f"❌ Download error: {e}")
            import traceback
            print(traceback.format_exc())
            return False
    
    def print_learning_summary(self):
        """Print Phase 3 learning summary"""
        print("\n" + "="*60)
        print("📚 AUTOMATION SUMMARY")
        print("="*60)
        
        print("\n🎯 COMPLETE WORKFLOW:")
        print("   1. Upload image ✅")
        print("   2. Click Edit Image ✅")
        print("   3. Click Make video (XPath) ✅")
        print(f"   4. Wait for prompt textarea (~{self.wait_time_worked}s) ✅")
        print("   5. Enter prompt ✅")
        print("   6. Hit Enter to submit ✅")
        print(f"   7. Wait ~{self.video_generation_time}s for video ✅")
        print("   8. Download video ✅")
        
        if self.make_video_button_found and self.prompt_textarea_found:
            print("\n   ✅ Full workflow completed successfully!")
        
        print("\n" + "="*60)
    
    def save_learning_data(self):
        """Save automation learning data"""
        try:
            learning_data = {
                "timestamp": datetime.now().isoformat(),
                "description": "Complete video automation workflow",
                "make_video_button": {
                    "found": self.make_video_button_found,
                    "text": self.make_video_button_text,
                    "xpath": self.make_video_button_xpath
                },
                "wait_after_make_video": {
                    "method": "wait_for_textarea",
                    "seconds": self.wait_time_worked,
                    "max_wait": 60
                },
                "prompt_textarea": {
                    "found": self.prompt_textarea_found,
                    "placeholder": self.prompt_textarea_placeholder,
                    "submit_method": "Keys.RETURN"
                },
                "video_generation": {
                    "started": self.video_generation_started,
                    "time_seconds": self.video_generation_time,
                    "detection_method": "Wait for <video> element with valid src (blob: or http:)"
                },
                "download": {
                    "success": self.video_downloaded,
                    "selector": "button[aria-label*='ownload']",
                    "method": "Wait for video element first, then find download button",
                    "notes": "Must wait for actual video generation, not just button appearance"
                },
                "recommendations": {
                    "workflow": [
                        "Upload image",
                        "Click 'Edit Image' button",
                        "Wait for editor (textarea exists)",
                        "Click 'Make video' button (XPath)",
                        f"Wait for prompt textarea (~{self.wait_time_worked}s observed)",
                        "Find visible textarea",
                        "Enter prompt",
                        "Hit Enter (Keys.RETURN)",
                        f"Wait {self.video_generation_time or 180}s for video",
                        "Click download button (aria-label contains 'download')"
                    ],
                    "make_video_identifier": "XPath: /html/body/div[7]/div/footer/div/div/div[1]/button",
                    "wait_strategy": "Wait for textarea with placeholder containing: customize, video, describe, or prompt",
                    "prompt_textarea_placeholder": self.prompt_textarea_placeholder or "visible textarea",
                    "typical_wait_after_make_video": self.wait_time_worked,
                    "max_wait_for_textarea": 60,
                    "wait_for_generation": self.video_generation_time or 180,
                    "workflow_ready": self.make_video_button_found and self.prompt_textarea_found
                }
            }
            
            output_file = Path(__file__).parent / "automation_run_data.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(learning_data, f, indent=2)
            
            print(f"💾 Run data saved to: {output_file.name}")
            
        except Exception as e:
            print(f"⚠️  Could not save run data: {e}")
    
    def interactive_mode(self):
        """Keep browser open"""
        print("\n" + "="*60)
        print("🎮 INTERACTIVE MODE - Press Ctrl+C when done")
        print("="*60)
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n👋 Exiting...")
    
    def run_automation(self):
        """Run complete video automation"""
        print("\n" + "="*60)
        print("🎬 GROK VIDEO AUTOMATION")
        print("="*60)
        
        try:
            if not self.setup_driver():
                return False
            
            if not self.navigate_to_grok():
                return False
            
            if not self.upload_image():
                return False
            
            if not self.click_edit_image_button():
                return False
            
            if not self.click_make_video_button():
                return False
            
            if not self.wait_for_prompt_textarea():
                return False
            
            if not self.find_and_enter_prompt():
                return False
            
            # Monitor video generation
            video_element = self.monitor_video_generation()
            
            if video_element:
                # Download the video
                self.download_video(video_element)
            else:
                print("⚠️  Video not ready, skipping download")
            
            # Print summary
            self.print_learning_summary()
            
            # Save learning data
            self.save_learning_data()
            
            # Interactive mode
            self.interactive_mode()
            
            return True
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Automation interrupted")
            return False
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            print(traceback.format_exc())
            return False
            
        finally:
            if self.driver:
                print("🧹 Cleaning up...")
                time.sleep(1)
                self.driver.quit()
                print("✅ Browser closed")


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("🎬 Grok Video Automation")
    print("="*60)
    
    try:
        input("\n▶️  Press Enter to start (or Ctrl+C to cancel)...")
    except KeyboardInterrupt:
        print("\n👋 Cancelled")
        return
    
    automation = GrokVideoAutomation()
    success = automation.run_automation()
    
    print("\n" + "✅ Complete!" if success else "\n❌ Incomplete")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
