"""
Workflow Recorder - Captures successful LangGraph agent workflows and generates standalone scripts
"""
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


class WorkflowRecorder:
    """Records successful workflow executions and generates standalone scripts"""
    
    def __init__(self, workflow_name: str = "grok_video_workflow"):
        self.workflow_name = workflow_name
        self.workflows_dir = Path("workflows")
        self.workflows_dir.mkdir(exist_ok=True)
        self.workflow_file = self.workflows_dir / f"{workflow_name}.json"
        self.script_file = self.workflows_dir / f"{workflow_name}_script.py"
    
    def save_workflow(self, action_history: List[Dict], task: str, success: bool):
        """Save a successful workflow execution"""
        if not success:
            print("⚠️  Workflow not successful, not saving")
            return
        
        # Extract only the tool calls (not results)
        steps = []
        for action in action_history:
            tool_call = action.get('tool_call', {})
            if tool_call.get('tool') != 'done':  # Skip the 'done' action
                steps.append(tool_call)
        
        workflow_data = {
            "name": self.workflow_name,
            "task": task,
            "created_at": datetime.now().isoformat(),
            "steps": steps,
            "total_steps": len(steps)
        }
        
        # Save JSON
        with open(self.workflow_file, 'w') as f:
            json.dump(workflow_data, f, indent=2)
        
        print(f"\n💾 Workflow saved to: {self.workflow_file}")
        print(f"   Total steps: {len(steps)}")
        
        # Generate script
        self._generate_script(workflow_data)
    
    def _escape_string(self, value: str) -> str:
        """Properly escape a string for Python code generation"""
        # If string contains single quotes, use double quotes for outer string
        if "'" in value and '"' not in value:
            return f'"{value}"'
        # If string contains double quotes, use single quotes and escape
        elif '"' in value:
            return f"'{value.replace(chr(39), chr(92) + chr(39))}'"
        # Default: use single quotes
        else:
            return f"'{value}'"
    
    def _generate_script(self, workflow_data: Dict):
        """Generate a standalone Python script from workflow data"""
        steps = workflow_data['steps']
        
        script_content = f'''"""
Auto-generated workflow script
Generated from: {self.workflow_name}
Created: {workflow_data['created_at']}
Task: {workflow_data['task'][:100]}...
"""
import time
import sys
from pathlib import Path

# Add parent directory to path so we can import dom_browser
sys.path.insert(0, str(Path(__file__).parent.parent))

from dom_browser import DOMBrowser


def run_workflow(
    prompt: str = "make it spin slowly",
    image_path: str = "./test_image.jpg",
    initial_url: str = "https://grok.com",
    headless: bool = False
) -> str:
    """
    Run the recorded workflow without AI
    
    Args:
        prompt: The text prompt for video generation
        image_path: Path to the image file to upload
        initial_url: Starting URL (default: https://grok.com)
        headless: Run browser in headless mode
    
    Returns:
        Path to downloaded video file, or None if failed
    """
    print("\\n" + "="*60)
    print("🤖 RECORDED WORKFLOW EXECUTION")
    print("="*60)
    print(f"📋 Workflow: {workflow_data['name']}")
    print(f"🔄 Steps: {len(steps)}")
    print(f"📝 Prompt: {{prompt}}")
    print(f"📸 Image: {{image_path}}")
    print("="*60)
    
    # Track downloads folder to find new video
    downloads_dir = Path(__file__).parent.parent / "grok_downloads"
    downloads_dir.mkdir(exist_ok=True)
    
    # Get existing videos before workflow
    existing_videos = set(downloads_dir.glob("*.mp4"))
    
    browser = DOMBrowser()
    
    try:
        # Start browser
        if not browser.start():
            print("❌ Failed to start browser")
            return None
        
        # Navigate to initial URL
        print(f"\\n🌐 Navigating to: {{initial_url}}")
        browser.navigate(initial_url)
        time.sleep(2)
        
        # Execute recorded steps (with parameter substitution)
'''
        
        # Add each step
        for i, step in enumerate(steps, 1):
            tool = step.get('tool', '')
            script_content += f"\n        # Step {i}: {tool}\n"
            script_content += f"        print(f'\\n⚡ Step {i}/{len(steps)}: {tool}')\n"
            
            if tool == 'click_by_text':
                text = self._escape_string(step.get('text', ''))
                element_type = self._escape_string(step.get('element_type', 'any'))
                script_content += f"        result = browser.click_element_by_text({text}, {element_type})\n"
            
            elif tool == 'click_by_selector':
                selector = self._escape_string(step.get('selector', ''))
                script_content += f"        result = browser.click_element_by_selector({selector})\n"
            
            elif tool == 'click_by_aria_label':
                aria_label = self._escape_string(step.get('aria_label', ''))
                script_content += f"        result = browser.click_element_by_aria_label({aria_label})\n"
            
            elif tool == 'upload_file':
                selector = self._escape_string(step.get('selector', 'auto'))
                # Use image_path parameter instead of hardcoded path
                script_content += f"        result = browser.upload_file({selector}, image_path)\n"
            
            elif tool == 'type_text':
                selector = self._escape_string(step.get('selector', ''))
                # Use prompt parameter instead of hardcoded text
                script_content += f"        result = browser.type_into_element({selector}, prompt)\n"
            
            elif tool == 'wait_for_text_change':
                selector = self._escape_string(step.get('selector', ''))
                timeout = step.get('timeout', 120)
                script_content += f"        result = browser.wait_for_text_change({selector}, timeout={timeout})\n"
            
            elif tool == 'wait_for_element':
                selector = self._escape_string(step.get('selector', ''))
                timeout = step.get('timeout', 30)
                condition = self._escape_string(step.get('condition', 'visible'))
                script_content += f"        result = browser.wait_for_element({selector}, timeout={timeout}, condition={condition})\n"
            
            elif tool == 'scroll':
                direction = self._escape_string(step.get('direction', 'down'))
                script_content += f"        result = browser.scroll_page({direction})\n"
            
            elif tool == 'press_enter':
                script_content += f"        result = browser.press_enter()\n"
            
            # Check result
            script_content += f"""        if not result.get('success'):
            print(f"   ❌ Failed: {{result.get('error', 'Unknown error')}}")
            return False
        print(f"   ✅ Success")
        time.sleep(1)
"""
        
        # Add completion check and video detection
        script_content += '''
        # Verify workflow completion
        print("\\n✅ Workflow completed successfully!")
        
        # Wait for download to complete
        print("\\n⏳ Waiting for video download...")
        time.sleep(5)
        
        # Find the new video
        current_videos = set(downloads_dir.glob("*.mp4"))
        new_videos = current_videos - existing_videos
        
        if new_videos:
            video_path = sorted(new_videos, key=lambda p: p.stat().st_mtime)[-1]
            print(f"\\n📹 Video downloaded: {video_path.name}")
            return str(video_path)
        else:
            print("\\n⚠️  Warning: No new video found in downloads folder")
            # Return latest video if any
            all_videos = list(downloads_dir.glob("*.mp4"))
            if all_videos:
                video_path = sorted(all_videos, key=lambda p: p.stat().st_mtime)[-1]
                print(f"📹 Returning latest video: {video_path.name}")
                return str(video_path)
            return None
        
    except Exception as e:
        print(f"\\n❌ Error during workflow execution: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    finally:
        browser.quit()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Grok video workflow")
    parser.add_argument("--prompt", default="make it spin slowly", help="Video generation prompt")
    parser.add_argument("--image", default="./test_image.jpg", help="Path to image file")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    
    args = parser.parse_args()
    
    video_path = run_workflow(
        prompt=args.prompt,
        image_path=args.image,
        headless=args.headless
    )
    
    if video_path:
        print("\\n" + "="*60)
        print("✅ WORKFLOW COMPLETED SUCCESSFULLY")
        print("="*60)
        print(f"📹 Video: {video_path}")
        sys.exit(0)
    else:
        print("\\n" + "="*60)
        print("❌ WORKFLOW FAILED")
        print("="*60)
        sys.exit(1)
'''
        
        # Write script
        with open(self.script_file, 'w') as f:
            f.write(script_content)
        
        print(f"📝 Script generated: {self.script_file}")
        print(f"   Run with: python {self.script_file}")
    
    def workflow_exists(self) -> bool:
        """Check if a saved workflow exists"""
        return self.workflow_file.exists() and self.script_file.exists()
    
    def get_workflow_info(self) -> Dict:
        """Get information about the saved workflow"""
        if not self.workflow_file.exists():
            return None
        
        with open(self.workflow_file, 'r') as f:
            return json.load(f)

