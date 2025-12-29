"""
Hybrid Workflow Runner - Tries recorded script first, falls back to AI agent
"""
import subprocess
import sys
from pathlib import Path
from typing import Optional
from workflow_recorder import WorkflowRecorder
from langgraph_agent import LangGraphAgent


class HybridRunner:
    """
    Intelligent workflow runner that:
    1. Tries to run recorded script (fast, no tokens)
    2. Falls back to AI agent if script fails (intelligent recovery)
    3. Records new successful workflows for future use
    """
    
    def __init__(self, workflow_name: str = "grok_video_workflow"):
        self.workflow_name = workflow_name
        self.recorder = WorkflowRecorder(workflow_name)
    
    def run(self, task: str, initial_url: str, max_iterations: int = 30) -> bool:
        """
        Run workflow with hybrid approach
        Returns True if successful, False otherwise
        """
        print("\n" + "="*60)
        print("🚀 HYBRID WORKFLOW RUNNER")
        print("="*60)
        
        # Check if recorded workflow exists
        if self.recorder.workflow_exists():
            workflow_info = self.recorder.get_workflow_info()
            print(f"✅ Found recorded workflow:")
            print(f"   Created: {workflow_info['created_at']}")
            print(f"   Steps: {workflow_info['total_steps']}")
            print(f"\n📝 Attempting to run recorded script (no AI tokens)...")
            
            # Try running the recorded script
            success = self._run_recorded_script()
            
            if success:
                print("\n✅ Recorded script succeeded!")
                print("💰 Saved AI tokens by using recorded workflow")
                return True
            else:
                print("\n⚠️  Recorded script failed, falling back to AI agent...")
                print("💡 AI will figure out what changed and adapt")
        else:
            print("📭 No recorded workflow found")
            print("🤖 Running AI agent to learn the workflow...")
        
        # Fall back to AI agent
        return self._run_ai_agent(task, initial_url, max_iterations)
    
    def _run_recorded_script(self) -> bool:
        """
        Execute the recorded script
        Returns True if successful, False otherwise
        """
        script_file = self.recorder.script_file
        
        if not script_file.exists():
            return False
        
        try:
            # Run the script as a subprocess
            result = subprocess.run(
                [sys.executable, str(script_file)],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Print output
            if result.stdout:
                print(result.stdout)
            
            if result.stderr and result.returncode != 0:
                print(result.stderr)
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            print("❌ Script timeout (5 minutes)")
            return False
        except Exception as e:
            print(f"❌ Error running script: {e}")
            return False
    
    def _run_ai_agent(self, task: str, initial_url: str, max_iterations: int) -> bool:
        """
        Run the AI agent and record successful workflow
        Returns True if successful, False otherwise
        """
        print("\n" + "="*60)
        print("🤖 AI AGENT MODE")
        print("="*60)
        
        agent = LangGraphAgent(record_workflow=True, workflow_name=self.workflow_name)
        
        try:
            success = agent.run(
                task=task,
                initial_url=initial_url,
                max_iterations=max_iterations
            )
            
            if success:
                print("\n✅ Workflow recorded successfully!")
                print(f"   📄 JSON: {self.recorder.workflow_file}")
                print(f"   🐍 Script: {self.recorder.script_file}")
                print(f"\n💡 Next run will use the recorded script (no AI tokens!)")
                
                return True
            else:
                return False
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            agent.cleanup()


def main():
    """Example usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Hybrid Workflow Runner")
    parser.add_argument("--workflow", default="grok_video_workflow", help="Workflow name")
    parser.add_argument("--url", default="https://grok.com", help="Initial URL")
    parser.add_argument("--max-iter", type=int, default=30, help="Max iterations for AI agent")
    parser.add_argument("--force-ai", action="store_true", help="Force AI agent (skip recorded script)")
    
    args = parser.parse_args()
    
    # Default task for Grok video workflow
    task = """
1. Click on the 'Imagine' button in the left sidebar
2. Upload the image from test_image.jpg
3. Once redirected to the post page (URL contains '/imagine/post/'), type 'make it spin slowly' in the input field with placeholder 'Type to customize video...'
4. Click the 'Make video' button
5. IMPORTANT: Wait for video processing to complete by monitoring the button text. The button will show percentage progress (like "37%", "50%", "100%"). Use wait_for_text_change to wait until the text no longer contains "%" symbol, which means processing is complete.
6. After processing completes and text changes from percentage to something else, click the download button (aria-label='Download')
The goal is achieved when the video has been downloaded or the download button has been clicked AFTER video processing is complete.
"""
    
    runner = HybridRunner(args.workflow)
    
    if args.force_ai:
        print("🔧 Force AI mode enabled, skipping recorded script")
        runner.recorder.workflow_file.unlink(missing_ok=True)
        runner.recorder.script_file.unlink(missing_ok=True)
    
    success = runner.run(task, args.url, args.max_iter)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

