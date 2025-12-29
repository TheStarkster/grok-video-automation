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
from pathlib import Path
from dom_browser import DOMBrowser


def run_workflow(initial_url: str = "https://grok.com", headless: bool = False) -> bool:
    """
    Run the recorded workflow without AI
    Returns True if successful, False if failed
    """
    print("\\n" + "="*60)
    print("🤖 RECORDED WORKFLOW EXECUTION")
    print("="*60)
    print(f"📋 Workflow: {workflow_data['name']}")
    print(f"🔄 Steps: {len(steps)}")
    print("="*60)
    
    browser = DOMBrowser()
    
    try:
        # Start browser
        if not browser.start():
            print("❌ Failed to start browser")
            return False
        
        # Navigate to initial URL
        print(f"\\n🌐 Navigating to: {{initial_url}}")
        browser.navigate(initial_url)
        time.sleep(2)
        
        # Execute recorded steps
'''
        
        # Add each step
        for i, step in enumerate(steps, 1):
            tool = step.get('tool', '')
            script_content += f"\n        # Step {i}: {tool}\n"
            script_content += f"        print(f'\\n⚡ Step {i}/{len(steps)}: {tool}')\n"
            
            if tool == 'click_by_text':
                text = step.get('text', '')
                element_type = step.get('element_type', 'any')
                script_content += f"        result = browser.click_element_by_text('{text}', '{element_type}')\n"
            
            elif tool == 'click_by_selector':
                selector = step.get('selector', '')
                script_content += f"        result = browser.click_element_by_selector('{selector}')\n"
            
            elif tool == 'click_by_aria_label':
                aria_label = step.get('aria_label', '')
                script_content += f"        result = browser.click_element_by_aria_label('{aria_label}')\n"
            
            elif tool == 'upload_file':
                selector = step.get('selector', 'auto')
                file_path = step.get('file_path', '')
                script_content += f"        result = browser.upload_file('{selector}', '{file_path}')\n"
            
            elif tool == 'type_text':
                selector = step.get('selector', '')
                text = step.get('text', '')
                # Escape quotes in text
                text = text.replace("'", "\\'")
                script_content += f"        result = browser.type_into_element('{selector}', '{text}')\n"
            
            elif tool == 'wait_for_text_change':
                selector = step.get('selector', '')
                timeout = step.get('timeout', 120)
                script_content += f"        result = browser.wait_for_text_change('{selector}', timeout={timeout})\n"
            
            elif tool == 'wait_for_element':
                selector = step.get('selector', '')
                timeout = step.get('timeout', 30)
                condition = step.get('condition', 'visible')
                script_content += f"        result = browser.wait_for_element('{selector}', timeout={timeout}, condition='{condition}')\n"
            
            elif tool == 'scroll':
                direction = step.get('direction', 'down')
                script_content += f"        result = browser.scroll_page('{direction}')\n"
            
            elif tool == 'press_enter':
                script_content += f"        result = browser.press_enter()\n"
            
            # Check result
            script_content += f"""        if not result.get('success'):
            print(f"   ❌ Failed: {{result.get('error', 'Unknown error')}}")
            return False
        print(f"   ✅ Success")
        time.sleep(1)
"""
        
        # Add completion check
        script_content += '''
        # Verify workflow completion
        print("\\n✅ Workflow completed successfully!")
        
        # Keep browser open for verification
        print("\\n🎮 Browser will stay open for 5 seconds for verification...")
        time.sleep(5)
        
        return True
        
    except Exception as e:
        print(f"\\n❌ Error during workflow execution: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        browser.quit()


if __name__ == "__main__":
    import sys
    
    # Check if we should run in headless mode
    headless = "--headless" in sys.argv
    
    success = run_workflow(headless=headless)
    
    if success:
        print("\\n" + "="*60)
        print("✅ WORKFLOW COMPLETED SUCCESSFULLY")
        print("="*60)
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

