"""
DOM-Based Browser Controller - No coordinates, pure DOM interactions
"""
import time
import hashlib
from pathlib import Path
from typing import Optional, Tuple, Dict, List, Any
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from PIL import Image
import imagehash


class DOMBrowser:
    """Browser controller using DOM-based interactions - no coordinate guessing"""
    
    def __init__(self, user_data_dir: Optional[Path] = None):
        """Initialize browser controller"""
        self.driver = None
        self.wait = None
        
        if user_data_dir is None:
            script_dir = Path(__file__).parent
            self.user_data_dir = script_dir / "chrome_twitter_profile"
        else:
            self.user_data_dir = Path(user_data_dir)
        
        # State tracking for feedback loop
        self.previous_url = None
        self.previous_screenshot_hash = None
        self.screenshot_dir = Path("screenshots")
        self.screenshot_dir.mkdir(exist_ok=True)
    
    def start(self) -> bool:
        """Start the browser"""
        print("\n🚀 Initializing Chrome...")
        
        try:
            options = uc.ChromeOptions()
            
            if self.user_data_dir.exists():
                options.add_argument(f'--user-data-dir={str(self.user_data_dir)}')
                print(f"📁 Using Chrome profile: {self.user_data_dir}")
            
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--start-maximized')
            
            self.driver = uc.Chrome(options=options, use_subprocess=True)
            self.wait = WebDriverWait(self.driver, 10)
            self.driver.maximize_window()
            time.sleep(1)
            
            print("✅ Chrome ready!")
            return True
            
        except Exception as e:
            print(f"❌ Error starting Chrome: {e}")
            return False
    
    def navigate(self, url: str) -> Dict[str, Any]:
        """Navigate to URL and return state"""
        try:
            print(f"\n🌐 Navigating to: {url}")
            self.driver.get(url)
            time.sleep(2)
            
            # Capture initial state
            self._update_state()
            
            return {
                "success": True,
                "url": self.driver.current_url,
                "title": self.driver.title
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _update_state(self):
        """Update state tracking for feedback loop"""
        self.previous_url = self.driver.current_url
        screenshot_path = self.take_screenshot()
        self.previous_screenshot_hash = self._get_image_hash(screenshot_path)
    
    def _get_image_hash(self, image_path: str) -> str:
        """Get perceptual hash of image for comparison"""
        try:
            img = Image.open(image_path)
            return str(imagehash.phash(img))
        except Exception:
            return ""
    
    def take_screenshot(self, name: Optional[str] = None) -> str:
        """Take screenshot and return path"""
        if name is None:
            name = f"step_{int(time.time())}"
        
        filepath = self.screenshot_dir / f"{name}.png"
        self.driver.save_screenshot(str(filepath))
        return str(filepath)
    
    def get_page_state(self) -> Dict[str, Any]:
        """Get comprehensive page state for AI analysis"""
        try:
            return {
                "url": self.driver.current_url,
                "title": self.driver.title,
                "clickable_elements": self._get_clickable_elements(),
                "input_elements": self._get_input_elements(),
                "visible_text_summary": self._get_visible_text_summary()
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _get_clickable_elements(self) -> List[Dict]:
        """Get all clickable elements with their selectors"""
        elements = []
        
        # Find buttons
        for btn in self.driver.find_elements(By.TAG_NAME, "button"):
            if btn.is_displayed():
                elements.append({
                    "type": "button",
                    "text": btn.text.strip()[:50],
                    "aria_label": btn.get_attribute("aria-label") or "",
                    "selector": self._get_unique_selector(btn),
                    "visible": True
                })
        
        # Find links
        for link in self.driver.find_elements(By.TAG_NAME, "a"):
            if link.is_displayed():
                text = link.text.strip()[:50]
                if text:  # Only include links with visible text
                    elements.append({
                        "type": "link",
                        "text": text,
                        "href": link.get_attribute("href") or "",
                        "selector": self._get_unique_selector(link),
                        "visible": True
                    })
        
        # Find clickable divs/spans with role="button"
        for elem in self.driver.find_elements(By.CSS_SELECTOR, "[role='button']"):
            if elem.is_displayed() and elem.tag_name not in ["button", "a"]:
                elements.append({
                    "type": "role_button",
                    "text": elem.text.strip()[:50],
                    "aria_label": elem.get_attribute("aria-label") or "",
                    "selector": self._get_unique_selector(elem),
                    "visible": True
                })
        
        return elements[:30]  # Limit to top 30 elements
    
    def _get_input_elements(self) -> List[Dict]:
        """Get all input elements"""
        elements = []
        
        for inp in self.driver.find_elements(By.CSS_SELECTOR, "input, textarea"):
            if inp.is_displayed():
                elements.append({
                    "type": inp.get_attribute("type") or "text",
                    "placeholder": inp.get_attribute("placeholder") or "",
                    "name": inp.get_attribute("name") or "",
                    "selector": self._get_unique_selector(inp),
                    "visible": True
                })
        
        return elements[:20]
    
    def _get_visible_text_summary(self) -> str:
        """Get summary of visible text on page"""
        try:
            body = self.driver.find_element(By.TAG_NAME, "body")
            text = body.text[:1000]  # First 1000 chars
            return text.replace("\n", " ").strip()
        except Exception:
            return ""
    
    def _get_unique_selector(self, element) -> str:
        """Generate a unique CSS selector for an element"""
        try:
            # Try ID first
            elem_id = element.get_attribute("id")
            if elem_id:
                return f"#{elem_id}"
            
            # Try data-testid
            test_id = element.get_attribute("data-testid")
            if test_id:
                return f"[data-testid='{test_id}']"
            
            # Try aria-label
            aria = element.get_attribute("aria-label")
            if aria:
                tag = element.tag_name
                return f"{tag}[aria-label='{aria}']"
            
            # Build path-based selector
            return self._build_xpath_selector(element)
            
        except Exception:
            return ""
    
    def _build_xpath_selector(self, element) -> str:
        """Build XPath selector for element"""
        try:
            script = """
            function getXPath(element) {
                if (element.id !== '') {
                    return '//*[@id="' + element.id + '"]';
                }
                if (element === document.body) {
                    return '/html/body';
                }
                var ix = 0;
                var siblings = element.parentNode.childNodes;
                for (var i = 0; i < siblings.length; i++) {
                    var sibling = siblings[i];
                    if (sibling === element) {
                        return getXPath(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
                    }
                    if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                        ix++;
                    }
                }
            }
            return getXPath(arguments[0]);
            """
            return self.driver.execute_script(script, element)
        except Exception:
            return ""
    
    # ========== DOM INTERACTION METHODS ==========
    
    def click_element_by_text(self, text: str, element_type: str = "any") -> Dict[str, Any]:
        """Click element by its visible text"""
        try:
            print(f"🖱️  Clicking element with text: '{text}'")
            
            # Build XPath based on element type
            if element_type == "button":
                xpath = f"//button[contains(., '{text}')]"
            elif element_type == "link":
                xpath = f"//a[contains(., '{text}')]"
            else:
                xpath = f"//*[contains(text(), '{text}')]"
            
            # Find and click
            elements = self.driver.find_elements(By.XPATH, xpath)
            
            for elem in elements:
                if elem.is_displayed():
                    self._scroll_to_element(elem)
                    elem.click()
                    time.sleep(1)
                    return self._get_action_result("click", f"Clicked '{text}'")
            
            return {"success": False, "error": f"No visible element found with text '{text}'"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def click_element_by_selector(self, selector: str) -> Dict[str, Any]:
        """Click element by CSS selector or XPath"""
        try:
            print(f"🖱️  Clicking element: {selector[:50]}...")
            
            # Determine if it's XPath or CSS
            if selector.startswith("//") or selector.startswith("/html"):
                elem = self.driver.find_element(By.XPATH, selector)
            else:
                elem = self.driver.find_element(By.CSS_SELECTOR, selector)
            
            if elem.is_displayed():
                self._scroll_to_element(elem)
                elem.click()
                time.sleep(1)
                return self._get_action_result("click", f"Clicked selector: {selector[:30]}")
            else:
                return {"success": False, "error": "Element not visible"}
                
        except NoSuchElementException:
            return {"success": False, "error": f"Element not found: {selector[:50]}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def click_element_by_aria_label(self, aria_label: str) -> Dict[str, Any]:
        """Click element by aria-label attribute"""
        try:
            print(f"🖱️  Clicking element with aria-label: '{aria_label}'")
            
            elem = self.driver.find_element(By.CSS_SELECTOR, f"[aria-label='{aria_label}']")
            
            if elem.is_displayed():
                self._scroll_to_element(elem)
                elem.click()
                time.sleep(1)
                return self._get_action_result("click", f"Clicked aria-label: {aria_label}")
            else:
                return {"success": False, "error": "Element not visible"}
                
        except NoSuchElementException:
            return {"success": False, "error": f"No element with aria-label '{aria_label}'"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def type_into_element(self, selector: str, text: str) -> Dict[str, Any]:
        """Type text into an input element"""
        try:
            print(f"⌨️  Typing into: {selector[:30]}...")
            
            if selector.startswith("//"):
                elem = self.driver.find_element(By.XPATH, selector)
            else:
                elem = self.driver.find_element(By.CSS_SELECTOR, selector)
            
            elem.clear()
            elem.send_keys(text)
            time.sleep(0.5)
            
            return self._get_action_result("type", f"Typed '{text[:20]}...'")
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def press_enter(self) -> Dict[str, Any]:
        """Press Enter key"""
        try:
            actions = ActionChains(self.driver)
            actions.send_keys(Keys.RETURN).perform()
            time.sleep(1)
            return self._get_action_result("key", "Pressed Enter")
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def scroll_page(self, direction: str = "down") -> Dict[str, Any]:
        """Scroll the page"""
        try:
            if direction == "down":
                self.driver.execute_script("window.scrollBy(0, 500);")
            elif direction == "up":
                self.driver.execute_script("window.scrollBy(0, -500);")
            time.sleep(0.5)
            return self._get_action_result("scroll", f"Scrolled {direction}")
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def execute_js(self, code: str) -> Dict[str, Any]:
        """Execute arbitrary JavaScript code"""
        try:
            print(f"📜 Executing JS: {code[:50]}...")
            result = self.driver.execute_script(code)
            time.sleep(0.5)
            return self._get_action_result("js", f"Executed JS", {"result": result})
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def upload_file(self, selector: str, file_path: str) -> Dict[str, Any]:
        """Upload a file to a file input element (works with hidden inputs)"""
        try:
            print(f"📤 Uploading file: {file_path}")
            
            # Validate file exists
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return {"success": False, "error": f"File not found: {file_path}"}
            
            # Get absolute path
            abs_file_path = str(file_path_obj.absolute())
            
            # If selector is "auto", find any file input on the page
            if selector.lower() == "auto":
                print("   🔍 Auto-detecting file input element...")
                file_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
                if not file_inputs:
                    return {"success": False, "error": "No file input elements found on page"}
                elem = file_inputs[0]  # Use the first one
                print(f"   ✅ Found file input element")
            else:
                # Find the file input element by selector
                if selector.startswith("//") or selector.startswith("/html"):
                    elem = self.driver.find_element(By.XPATH, selector)
                else:
                    elem = self.driver.find_element(By.CSS_SELECTOR, selector)
            
            # For hidden file inputs, make them visible temporarily
            # This is a common workaround for modern web apps that hide file inputs
            if not elem.is_displayed():
                print("   📝 Note: File input is hidden, making it temporarily visible")
                self.driver.execute_script(
                    "arguments[0].style.display = 'block'; "
                    "arguments[0].style.visibility = 'visible'; "
                    "arguments[0].style.opacity = '1'; "
                    "arguments[0].style.position = 'relative';",
                    elem
                )
                time.sleep(0.2)
            
            # Upload the file
            elem.send_keys(abs_file_path)
            time.sleep(2)  # Wait for file to be processed
            
            return self._get_action_result("upload", f"Uploaded file: {file_path_obj.name}")
            
        except NoSuchElementException:
            return {"success": False, "error": f"File input element not found: {selector[:50]}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def wait_for_element(self, selector: str, timeout: int = 30, condition: str = "visible") -> Dict[str, Any]:
        """Wait for an element to appear/become visible"""
        try:
            print(f"⏳ Waiting for element: {selector[:50]}... (timeout: {timeout}s, condition: {condition})")
            
            # Create a wait instance with custom timeout
            wait = WebDriverWait(self.driver, timeout)
            
            # Determine which condition to use
            if selector.startswith("//") or selector.startswith("/html"):
                by_method = By.XPATH
            else:
                by_method = By.CSS_SELECTOR
            
            if condition == "visible":
                expected_condition = EC.visibility_of_element_located((by_method, selector))
            elif condition == "present":
                expected_condition = EC.presence_of_element_located((by_method, selector))
            elif condition == "clickable":
                expected_condition = EC.element_to_be_clickable((by_method, selector))
            else:
                expected_condition = EC.visibility_of_element_located((by_method, selector))
            
            # Wait for element
            element = wait.until(expected_condition)
            
            time.sleep(0.5)  # Brief pause after element appears
            return self._get_action_result("wait", f"Element appeared: {selector[:30]}", {
                "element_found": True,
                "timeout": timeout,
                "condition": condition
            })
            
        except TimeoutException:
            return {
                "success": False,
                "error": f"Element did not appear within {timeout} seconds: {selector[:50]}",
                "element_found": False,
                "timeout": timeout,
                "condition": condition
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def check_element_exists(self, selector: str) -> bool:
        """Quick boolean check if element exists on page"""
        try:
            if selector.startswith("//") or selector.startswith("/html"):
                self.driver.find_element(By.XPATH, selector)
            else:
                self.driver.find_element(By.CSS_SELECTOR, selector)
            return True
        except NoSuchElementException:
            return False
        except Exception:
            return False
    
    def get_element_text(self, selector: str) -> Dict[str, Any]:
        """Get text content of an element"""
        try:
            if selector.startswith("//") or selector.startswith("/html"):
                elem = self.driver.find_element(By.XPATH, selector)
            else:
                elem = self.driver.find_element(By.CSS_SELECTOR, selector)
            
            text = elem.text.strip()
            return {
                "success": True,
                "text": text,
                "selector": selector
            }
        except NoSuchElementException:
            return {"success": False, "error": f"Element not found: {selector[:50]}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def wait_for_text_change(self, selector: str, initial_text: str = None, timeout: int = 120) -> Dict[str, Any]:
        """Wait for an element's text to change from initial value or stop containing certain patterns"""
        try:
            print(f"⏳ Waiting for text change in: {selector[:50]}... (timeout: {timeout}s)")
            
            # Determine selector type
            if selector.startswith("//") or selector.startswith("/html"):
                by_method = By.XPATH
            else:
                by_method = By.CSS_SELECTOR
            
            start_time = time.time()
            last_text = initial_text
            elem_found_once = False
            
            while time.time() - start_time < timeout:
                try:
                    elem = self.driver.find_element(by_method, selector)
                    elem_found_once = True
                    current_text = elem.text.strip()
                    
                    # If checking for percentage completion (text contains %)
                    if "%" in current_text:
                        print(f"   📊 Progress: {current_text}")
                        last_text = current_text
                        time.sleep(2)  # Check every 2 seconds
                        continue
                    
                    # If we get here, text no longer contains % - processing might be done
                    if last_text and "%" in last_text and "%" not in current_text:
                        print(f"   ✅ Text changed from '{last_text}' to '{current_text}'")
                        time.sleep(2)  # Wait a bit more for stability
                        return self._get_action_result("wait_text", f"Text changed to: {current_text}", {
                            "previous_text": last_text,
                            "current_text": current_text
                        })
                    
                    last_text = current_text
                    time.sleep(2)
                    
                except NoSuchElementException:
                    # If selector not found, try to find any button with percentage
                    if not elem_found_once:
                        print(f"   ⚠️  Selector not found, trying generic percentage button...")
                        result = self._wait_for_percentage_generic(timeout - (time.time() - start_time))
                        if result.get('success'):
                            return result
                    time.sleep(1)
                    continue
            
            return {
                "success": False,
                "error": f"Text did not change within {timeout} seconds",
                "last_text": last_text
            }
            
        except KeyboardInterrupt:
            raise
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _wait_for_percentage_generic(self, timeout: int = 120) -> Dict[str, Any]:
        """Wait for any button with percentage text to complete (fallback for dynamic selectors)"""
        try:
            print(f"   🔍 Looking for any button with percentage...")
            start_time = time.time()
            last_text = None
            
            while time.time() - start_time < timeout:
                try:
                    # Find all buttons on the page
                    buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    
                    for button in buttons:
                        text = button.text.strip()
                        if "%" in text:
                            print(f"   📊 Progress: {text}")
                            last_text = text
                            time.sleep(2)
                            break
                    else:
                        # No button with % found - might be done!
                        if last_text and "%" in last_text:
                            print(f"   ✅ Processing complete (no more percentage buttons)")
                            time.sleep(2)
                            return self._get_action_result("wait_text", "Processing complete", {
                                "previous_text": last_text,
                                "current_text": "Complete"
                            })
                    
                    time.sleep(2)
                    
                except Exception:
                    time.sleep(1)
                    continue
            
            return {
                "success": False,
                "error": f"Percentage did not complete within {timeout} seconds",
                "last_text": last_text
            }
            
        except KeyboardInterrupt:
            raise
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _scroll_to_element(self, element):
        """Scroll element into view"""
        self.driver.execute_script(
            "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
            element
        )
        time.sleep(0.3)
    
    def _get_action_result(self, action_type: str, description: str, extra: Dict = None) -> Dict[str, Any]:
        """Get result of action including change detection"""
        current_url = self.driver.current_url
        screenshot_path = self.take_screenshot()
        current_hash = self._get_image_hash(screenshot_path)
        
        url_changed = current_url != self.previous_url
        screen_changed = current_hash != self.previous_screenshot_hash
        
        result = {
            "success": True,
            "action": action_type,
            "description": description,
            "url_changed": url_changed,
            "screen_changed": screen_changed,
            "current_url": current_url,
            "previous_url": self.previous_url,
            "screenshot": screenshot_path
        }
        
        if extra:
            result.update(extra)
        
        # Update state
        self.previous_url = current_url
        self.previous_screenshot_hash = current_hash
        
        if url_changed:
            print(f"   📍 URL changed: {self.previous_url} → {current_url}")
        if screen_changed:
            print(f"   🖼️  Screen content changed")
        
        return result
    
    def check_goal_achieved(self, goal_indicators: List[str]) -> bool:
        """Check if goal is achieved based on URL or page content"""
        current_url = self.driver.current_url
        page_source = self.driver.page_source.lower()
        
        for indicator in goal_indicators:
            if indicator.lower() in current_url.lower():
                return True
            if indicator.lower() in page_source:
                return True
        
        return False
    
    def quit(self):
        """Close browser"""
        if self.driver:
            print("\n🧹 Closing browser...")
            self.driver.quit()
            print("✅ Browser closed")

