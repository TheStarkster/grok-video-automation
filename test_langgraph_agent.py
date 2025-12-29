"""
Test Script: LangGraph Agent clicking Grok Imagine button
"""
from pathlib import Path
from langgraph_agent import LangGraphAgent


def main():
    """Test the LangGraph agent by clicking the Imagine button on Grok"""
    print("\n" + "="*60)
    print("🧪 TEST: LangGraph Agent - Grok Imagine Button")
    print("="*60)
    
    # Create screenshots directory
    Path("screenshots").mkdir(exist_ok=True)
    
    # Initialize agent
    agent = LangGraphAgent()
    
    try:
        # Execute task with 10 max iterations
        task = "Click on the 'Imagine' button in the left sidebar. The goal is achieved when you see the Imagine page or the URL changes to include 'imagine'."
        
        success = agent.run(
            task=task,
            initial_url="https://grok.com",
            max_iterations=10
        )
        
        if success:
            print("\n" + "="*60)
            print("✅ TEST PASSED!")
            print("="*60)
        else:
            print("\n" + "="*60)
            print("⚠️  TEST INCOMPLETE")
            print("="*60)
        
        # Interactive mode to inspect results
        agent.interactive_mode()
        
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        agent.cleanup()


if __name__ == "__main__":
    main()

