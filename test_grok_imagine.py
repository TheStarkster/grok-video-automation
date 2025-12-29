"""
Test Script: Click "Imagine" button on Grok
"""
from pathlib import Path
from computer_use_agent import ComputerUseAgent


def main():
    """Test the AI agent by clicking the Imagine button on Grok"""
    print("\n" + "="*60)
    print("🧪 TEST: Grok Imagine Button Click")
    print("="*60)
    
    # Create screenshots directory
    Path("screenshots").mkdir(exist_ok=True)
    
    # Initialize agent
    agent = ComputerUseAgent(headless=False)
    
    try:
        # Execute task
        task = "Open Grok and click on the 'Imagine' button which is on the left sidebar"
        success = agent.execute_task(
            task=task,
            initial_url="https://grok.com"
        )
        
        if success:
            print("\n" + "="*60)
            print("✅ TEST PASSED: Imagine button clicked successfully!")
            print("="*60)
        else:
            print("\n" + "="*60)
            print("⚠️  TEST INCOMPLETE: Task may not have completed")
            print("="*60)
        
        # Interactive mode to inspect results
        agent.interactive_mode()
        
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        print(traceback.format_exc())
    
    finally:
        agent.cleanup()


if __name__ == "__main__":
    main()

