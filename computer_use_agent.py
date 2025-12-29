"""
Computer Use Agent - Main orchestrator combining AI vision and browser control
"""
import time
from typing import Optional
from ai_agent import AIAgent
from browser_controller import BrowserController


class ComputerUseAgent:
    """Main agent that orchestrates AI vision and browser automation"""
    
    def __init__(self, headless: bool = False):
        """
        Initialize the computer use agent
        
        Args:
            headless: Run browser in headless mode
        """
        self.ai_agent = AIAgent()
        self.browser = BrowserController(headless=headless)
        self.max_iterations = 50  # Safety limit
        self.screenshot_dir = "screenshots"
        
        # Create screenshots directory
        from pathlib import Path
        Path(self.screenshot_dir).mkdir(exist_ok=True)
    
    def execute_task(self, task: str, initial_url: Optional[str] = None) -> bool:
        """
        Execute a task using AI vision and browser automation
        
        Args:
            task: Task description (e.g., "Open Grok and click the Imagine button")
            initial_url: Optional starting URL
            
        Returns:
            True if task completed successfully
        """
        print("\n" + "="*60)
        print("🤖 AI COMPUTER USE AGENT")
        print("="*60)
        print(f"📋 Task: {task}")
        print("="*60)
        
        # Start browser
        if not self.browser.start():
            print("❌ Failed to start browser")
            return False
        
        try:
            # Navigate to initial URL if provided
            if initial_url:
                if not self.browser.navigate(initial_url):
                    print("❌ Failed to navigate to initial URL")
                    return False
            
            # Main execution loop
            iteration = 0
            while iteration < self.max_iterations:
                iteration += 1
                print(f"\n--- Iteration {iteration} ---")
                
                # Take screenshot (with optional grid for better accuracy)
                screenshot_path = self.browser.take_screenshot(
                    f"{self.screenshot_dir}/step_{iteration}.png",
                    add_grid=False  # Set to True to help AI with coordinates
                )
                
                # Get viewport size for context
                viewport_size = self.browser.get_viewport_size()
                
                # Analyze screenshot with AI
                print("\n🧠 AI analyzing screenshot...")
                try:
                    analysis = self.ai_agent.analyze_screenshot(
                        screenshot_path,
                        task,
                        viewport_size
                    )
                    
                    print(f"💭 Reasoning: {analysis['reasoning']}")
                    print(f"🎯 Action: {analysis['action']}")
                    print(f"📊 Confidence: {analysis['confidence']:.2f}")
                    
                except Exception as e:
                    print(f"❌ AI analysis error: {e}")
                    return False
                
                # Parse and execute action
                parsed_action = self.ai_agent.parse_action(analysis['action'])
                action_type = parsed_action['type']
                
                if action_type == "DONE":
                    print("\n✅ Task completed!")
                    return True
                
                elif action_type == "CLICK":
                    x = parsed_action['params']['x']
                    y = parsed_action['params']['y']
                    self.browser.click_at_coordinates(x, y)
                    time.sleep(1)  # Wait for page to react
                
                elif action_type == "TYPE":
                    text = parsed_action['params']['text']
                    self.browser.type_text(text)
                    time.sleep(0.5)
                
                elif action_type == "SCROLL":
                    direction = parsed_action['params']['direction']
                    self.browser.scroll(direction)
                    time.sleep(1)
                
                elif action_type == "WAIT":
                    seconds = parsed_action['params']['seconds']
                    print(f"⏳ Waiting {seconds} seconds...")
                    time.sleep(seconds)
                
                else:
                    print(f"⚠️  Unknown action type: {action_type}")
                    time.sleep(1)
                
                # Brief pause between iterations
                time.sleep(0.5)
            
            print(f"\n⚠️  Reached maximum iterations ({self.max_iterations})")
            return False
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Task interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ Error during task execution: {e}")
            import traceback
            print(traceback.format_exc())
            return False
    
    def interactive_mode(self):
        """Keep browser open for manual inspection"""
        print("\n" + "="*60)
        print("🎮 INTERACTIVE MODE - Press Ctrl+C when done")
        print("="*60)
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n👋 Exiting...")
    
    def cleanup(self):
        """Clean up resources"""
        self.browser.quit()

