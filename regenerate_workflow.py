"""
Quick script to regenerate workflow with updated generator
"""
from pathlib import Path
from langgraph_agent import LangGraphAgent


def main():
    print("\n" + "="*60)
    print("🔄 REGENERATING WORKFLOW")
    print("="*60)
    print("This will create a new parameterized workflow script")
    print("="*60)
    
    # Check for test image
    test_image = Path("test_image.jpg")
    if not test_image.exists():
        test_image = Path("test_image.png")
    
    if not test_image.exists():
        print(f"\n❌ Error: No test image found")
        return
    
    print(f"\n📸 Using test image: {test_image}")
    
    # Initialize agent with recording enabled
    agent = LangGraphAgent(record_workflow=True, workflow_name="grok_video_workflow")
    
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
            max_iterations=30
        )
        
        if success:
            print("\n" + "="*60)
            print("✅ WORKFLOW REGENERATED!")
            print("="*60)
            print("\nYou can now use the parameterized script:")
            print("  python workflows/grok_video_workflow_script.py --prompt 'your prompt' --image path/to/image.jpg")
        else:
            print("\n⚠️  Workflow incomplete")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        agent.cleanup()


if __name__ == "__main__":
    main()

