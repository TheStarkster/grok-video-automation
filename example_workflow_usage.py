"""
Example: How to use the Hybrid Workflow System

This demonstrates the token-saving workflow system
"""
from pathlib import Path
from hybrid_runner import HybridRunner
from workflow_recorder import WorkflowRecorder


def example_1_basic_usage():
    """Example 1: Basic hybrid runner usage"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Hybrid Runner")
    print("="*60)
    
    # Create runner
    runner = HybridRunner("grok_video_workflow")
    
    # Define task
    task = """
    1. Click Imagine button
    2. Upload image
    3. Type prompt
    4. Generate video
    5. Wait for completion
    6. Download video
    """
    
    # Run (tries script first, falls back to AI)
    success = runner.run(
        task=task,
        initial_url="https://grok.com",
        max_iterations=30
    )
    
    print(f"\nResult: {'Success' if success else 'Failed'}")


def example_2_check_workflow():
    """Example 2: Check if workflow exists"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Check Workflow Status")
    print("="*60)
    
    recorder = WorkflowRecorder("grok_video_workflow")
    
    if recorder.workflow_exists():
        info = recorder.get_workflow_info()
        print(f"✅ Workflow exists!")
        print(f"   Name: {info['name']}")
        print(f"   Created: {info['created_at']}")
        print(f"   Steps: {info['total_steps']}")
        print(f"\n   Steps breakdown:")
        for i, step in enumerate(info['steps'], 1):
            print(f"      {i}. {step.get('tool', 'unknown')}")
    else:
        print("❌ No workflow found - run AI agent first")


def example_3_cost_comparison():
    """Example 3: Calculate cost savings"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Cost Comparison")
    print("="*60)
    
    # Assumptions
    ai_cost_per_run = 0.20  # $0.20 per AI run
    script_cost_per_run = 0.00  # Free!
    
    runs = [1, 10, 50, 100, 500, 1000]
    
    print(f"\n{'Runs':<10} {'AI Only':<15} {'Hybrid':<15} {'Savings':<15}")
    print("-" * 55)
    
    for num_runs in runs:
        ai_total = num_runs * ai_cost_per_run
        hybrid_total = ai_cost_per_run + (num_runs - 1) * script_cost_per_run
        savings = ai_total - hybrid_total
        savings_pct = (savings / ai_total * 100) if ai_total > 0 else 0
        
        print(f"{num_runs:<10} ${ai_total:<14.2f} ${hybrid_total:<14.2f} ${savings:<10.2f} ({savings_pct:.1f}%)")


def example_4_workflow_management():
    """Example 4: Manage multiple workflows"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Multiple Workflows")
    print("="*60)
    
    workflows = [
        "grok_video_workflow",
        "grok_image_workflow",
        "grok_chat_workflow"
    ]
    
    print("\nWorkflow Status:")
    for workflow_name in workflows:
        recorder = WorkflowRecorder(workflow_name)
        status = "✅ Exists" if recorder.workflow_exists() else "❌ Not found"
        print(f"   {workflow_name}: {status}")


def main():
    """Run examples"""
    import sys
    
    examples = {
        "1": ("Basic Usage", example_1_basic_usage),
        "2": ("Check Workflow", example_2_check_workflow),
        "3": ("Cost Comparison", example_3_cost_comparison),
        "4": ("Workflow Management", example_4_workflow_management),
        "all": ("All Examples", lambda: [
            example_2_check_workflow(),
            example_3_cost_comparison(),
            example_4_workflow_management()
        ])
    }
    
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        print("\n" + "="*60)
        print("HYBRID WORKFLOW SYSTEM - EXAMPLES")
        print("="*60)
        print("\nAvailable examples:")
        for key, (name, _) in examples.items():
            print(f"   {key}. {name}")
        print("\nUsage: python example_workflow_usage.py [1|2|3|4|all]")
        print("   or: python example_workflow_usage.py  (shows this menu)")
        return
    
    if choice in examples:
        name, func = examples[choice]
        print(f"\n🎯 Running: {name}")
        func()
    else:
        print(f"❌ Unknown example: {choice}")
        print("   Choose from: 1, 2, 3, 4, or all")


if __name__ == "__main__":
    main()

