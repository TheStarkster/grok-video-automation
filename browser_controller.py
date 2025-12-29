"""
Browser Controller - Selenium wrapper with screenshot and coordinate-click capabilities
"""
import time
from pathlib import Path
from typing import Optional, Tuple
import undetected_chromedriver as uc
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from PIL import Image, ImageDraw, ImageFont
import io


class BrowserController:
    """Browser automation controller with AI-friendly methods"""
    
    def __init__(self, user_data_dir: Optional[Path] = None, headless: bool = False):
        """
        Initialize browser controller
        
        Args:
            user_data_dir: Path to Chrome user data directory
            headless: Run browser in headless mode
        """
        self.driver = None
        self.wait = None
        self.headless = headless
        
        # Use existing Chrome profile if available
        if user_data_dir is None:
            script_dir = Path(__file__).parent
            self.user_data_dir = script_dir / "chrome_twitter_profile"
        else:
            self.user_data_dir = Path(user_data_dir)
    
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
            
            if self.headless:
                options.add_argument('--headless=new')
            
            self.driver = uc.Chrome(options=options, use_subprocess=True)
            self.wait = WebDriverWait(self.driver, 20)
            
            # Maximize window if not headless
            if not self.headless:
                self.driver.maximize_window()
                time.sleep(1)
            
            print("✅ Chrome ready!")
            return True
            
        except Exception as e:
            print(f"❌ Error starting Chrome: {e}")
            return False
    
    def navigate(self, url: str) -> bool:
        """
        Navigate to URL
        
        Args:
            url: URL to navigate to
            
        Returns:
            True if successful
        """
        try:
            print(f"\n🌐 Navigating to: {url}")
            self.driver.get(url)
            time.sleep(2)  # Wait for page load
            print("✅ Page loaded!")
            return True
        except Exception as e:
            print(f"❌ Navigation error: {e}")
            return False
    
    def take_screenshot(self, filepath: Optional[str] = None, add_grid: bool = False) -> str:
        """
        Take screenshot of current viewport
        
        Args:
            filepath: Optional path to save screenshot. If None, generates temp path.
            add_grid: If True, adds coordinate grid overlay for AI reference
            
        Returns:
            Path to saved screenshot
        """
        if filepath is None:
            timestamp = int(time.time())
            filepath = f"screenshot_{timestamp}.png"
        
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Take screenshot using Selenium
        self.driver.save_screenshot(str(filepath))
        
        # Optionally add coordinate grid
        if add_grid:
            self._add_coordinate_grid(filepath)
        
        print(f"📸 Screenshot saved: {filepath}")
        return str(filepath)
    
    def _add_coordinate_grid(self, filepath: Path, grid_spacing: int = 100):
        """Add coordinate grid overlay to screenshot for AI reference"""
        try:
            img = Image.open(filepath)
            draw = ImageDraw.Draw(img)
            width, height = img.size
            
            # Draw grid lines
            for x in range(0, width, grid_spacing):
                draw.line([(x, 0), (x, height)], fill=(255, 0, 0, 50), width=1)
                # Add x coordinate label
                draw.text((x + 2, 2), str(x), fill=(255, 0, 0))
            
            for y in range(0, height, grid_spacing):
                draw.line([(0, y), (width, y)], fill=(255, 0, 0, 50), width=1)
                # Add y coordinate label
                draw.text((2, y + 2), str(y), fill=(255, 0, 0))
            
            img.save(filepath)
        except Exception as e:
            print(f"⚠️  Could not add grid: {e}")
    
    def get_viewport_size(self) -> Tuple[int, int]:
        """
        Get current viewport size
        
        Returns:
            (width, height) tuple
        """
        size = self.driver.get_window_size()
        return (size['width'], size['height'])
    
    def click_at_coordinates(self, x: int, y: int, debug: bool = True) -> bool:
        """
        Click at specific pixel coordinates
        
        Args:
            x: X coordinate (pixels from left)
            y: Y coordinate (pixels from top)
            debug: If True, shows visual indicator before clicking
            
        Returns:
            True if successful
        """
        try:
            print(f"🖱️  Clicking at coordinates: ({x}, {y})")
            
            # Debug: Show what element is at these coordinates
            if debug:
                element_info = self.driver.execute_script(f"""
                    var element = document.elementFromPoint({x}, {y});
                    if (element) {{
                        return {{
                            tag: element.tagName,
                            text: element.innerText ? element.innerText.substring(0, 50) : '',
                            class: element.className,
                            id: element.id
                        }};
                    }}
                    return null;
                """)
                if element_info:
                    print(f"   Target element: <{element_info['tag']}> class='{element_info['class'][:30]}' text='{element_info['text'][:30]}'")
                
                # Add visual indicator (red dot) at click location
                self.driver.execute_script(f"""
                    var dot = document.createElement('div');
                    dot.style.position = 'fixed';
                    dot.style.left = '{x}px';
                    dot.style.top = '{y}px';
                    dot.style.width = '20px';
                    dot.style.height = '20px';
                    dot.style.borderRadius = '50%';
                    dot.style.backgroundColor = 'red';
                    dot.style.zIndex = '999999';
                    dot.style.pointerEvents = 'none';
                    dot.style.border = '2px solid white';
                    document.body.appendChild(dot);
                    setTimeout(() => dot.remove(), 1000);
                """)
                time.sleep(0.5)  # Brief pause to see the indicator
            
            # Click using JavaScript
            script = f"""
            var element = document.elementFromPoint({x}, {y});
            if (element) {{
                element.click();
                return true;
            }}
            return false;
            """
            result = self.driver.execute_script(script)
            
            if result:
                time.sleep(0.5)  # Brief pause after click
                print("✅ Click executed!")
                return True
            else:
                print("⚠️  No element found at coordinates")
                return False
            
        except Exception as e:
            print(f"❌ Click error: {e}")
            return False
    
    def type_text(self, text: str) -> bool:
        """
        Type text into currently focused element
        
        Args:
            text: Text to type
            
        Returns:
            True if successful
        """
        try:
            print(f"⌨️  Typing: {text[:50]}...")
            
            actions = ActionChains(self.driver)
            actions.send_keys(text).perform()
            
            time.sleep(0.3)
            print("✅ Text entered!")
            return True
            
        except Exception as e:
            print(f"❌ Type error: {e}")
            return False
    
    def press_key(self, key: str) -> bool:
        """
        Press a key (e.g., Keys.RETURN, Keys.ESCAPE)
        
        Args:
            key: Key to press (from selenium.webdriver.common.keys.Keys)
            
        Returns:
            True if successful
        """
        try:
            print(f"⌨️  Pressing key: {key}")
            
            actions = ActionChains(self.driver)
            actions.send_keys(key).perform()
            
            time.sleep(0.3)
            return True
            
        except Exception as e:
            print(f"❌ Key press error: {e}")
            return False
    
    def scroll(self, direction: str, pixels: int = 500) -> bool:
        """
        Scroll the page
        
        Args:
            direction: "up", "down", "left", "right"
            pixels: Number of pixels to scroll
            
        Returns:
            True if successful
        """
        try:
            direction = direction.lower()
            print(f"📜 Scrolling {direction} by {pixels}px")
            
            if direction == "down":
                self.driver.execute_script(f"window.scrollBy(0, {pixels});")
            elif direction == "up":
                self.driver.execute_script(f"window.scrollBy(0, -{pixels});")
            elif direction == "right":
                self.driver.execute_script(f"window.scrollBy({pixels}, 0);")
            elif direction == "left":
                self.driver.execute_script(f"window.scrollBy(-{pixels}, 0);")
            else:
                print(f"⚠️  Unknown scroll direction: {direction}")
                return False
            
            time.sleep(0.5)
            print("✅ Scroll executed!")
            return True
            
        except Exception as e:
            print(f"❌ Scroll error: {e}")
            return False
    
    def wait_for_page_load(self, timeout: int = 10) -> bool:
        """
        Wait for page to finish loading
        
        Args:
            timeout: Maximum wait time in seconds
            
        Returns:
            True if page loaded
        """
        try:
            self.wait.until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            return True
        except TimeoutException:
            return False
    
    def get_current_url(self) -> str:
        """Get current page URL"""
        return self.driver.current_url
    
    def quit(self):
        """Close browser"""
        if self.driver:
            print("\n🧹 Closing browser...")
            self.driver.quit()
            print("✅ Browser closed")

