"""
Test Script: LangGraph Agent - Full Grok Video Creation Workflow
"""
from pathlib import Path
from langgraph_agent import LangGraphAgent


def main():
    """Test the LangGraph agent with full video creation workflow"""
    print("\n" + "="*60)
    print("🧪 TEST: LangGraph Agent - Full Grok Video Workflow")
    print("="*60)
    
    # Create screenshots directory
    Path("screenshots").mkdir(exist_ok=True)
    
    # Check for test image file
    test_image = Path("test_image.jpg")
    if not test_image.exists():
        test_image = Path("test_image.png")
    
    if not test_image.exists():
        print(f"\n❌ Error: No test image found (test_image.jpg or test_image.png)")
        print("   Please place a test image in the project root.")
        return
    
    print(f"📸 Using test image: {test_image}")
    
    # Initialize agent
    agent = LangGraphAgent()
    
    try:
        # Full workflow task
        task = f"""
1. Click on the 'Imagine' button in the left sidebar
2. Upload the image from {test_image}
3. Once redirected to the post page (URL contains '/imagine/post/'), type 'make it spin slowly' in the input field with placeholder 'Type to customize video...'
4. Click the 'Make video' button
5. IMPORTANT: Wait for video processing to complete by monitoring the button text. The button will show percentage progress (like "37%", "50%", "100%"). Use wait_for_text_change to wait until the text no longer contains "%" symbol, which means processing is complete.
6. After processing completes and text changes from percentage to something else, click the download button (aria-label='Download')
The goal is achieved when the video has been downloaded or the download button has been clicked AFTER video processing is complete.
"""
        
        success = agent.run(
            task=task,
            initial_url="https://grok.com",
            max_iterations=30  # Increased for full workflow
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

