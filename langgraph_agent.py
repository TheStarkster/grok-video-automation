"""
LangGraph-based Computer Use Agent with DOM interactions and feedback loop
"""
import os
import json
import base64
from typing import TypedDict, Annotated, List, Dict, Any, Literal
from pathlib import Path
from openai import AzureOpenAI
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from dom_browser import DOMBrowser

load_dotenv()


# ========== STATE DEFINITION ==========

class AgentState(TypedDict):
    """State for the agent"""
    task: str  # The goal to achieve
    messages: Annotated[List[Dict], add_messages]  # Conversation history
    page_state: Dict  # Current page DOM state
    screenshot_path: str  # Path to current screenshot
    action_history: List[Dict]  # History of actions taken
    iteration: int  # Current iteration count
    max_iterations: int  # Maximum iterations allowed
    goal_achieved: bool  # Whether the goal is achieved
    last_action_result: Dict  # Result of last action
    error: str  # Any error message
    pending_tool_call: Dict  # Tool call to execute in next step


# ========== AGENT CLASS ==========

class LangGraphAgent:
    """LangGraph-based agent for browser automation"""
    
    def __init__(self):
        """Initialize the agent"""
        # Azure OpenAI setup
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://primary-az-ai-foundary.cognitiveservices.azure.com/")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
        
        if not self.api_key:
            raise ValueError("Missing AZURE_OPENAI_API_KEY in .env file")
        
        self.client = AzureOpenAI(
            api_key=self.api_key,
            api_version=self.api_version,
            azure_endpoint=self.endpoint
        )
        
        # Browser
        self.browser = DOMBrowser()
        
        # Build the graph
        self.graph = self._build_graph()
        
        print(f"🤖 LangGraph Agent initialized")
        print(f"   Model: {self.deployment}")
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state graph"""
        
        # Create graph
        graph = StateGraph(AgentState)
        
        # Add nodes
        graph.add_node("analyze", self._analyze_node)
        graph.add_node("execute", self._execute_node)
        graph.add_node("evaluate", self._evaluate_node)
        
        # Set entry point
        graph.set_entry_point("analyze")
        
        # Add edges
        graph.add_edge("analyze", "execute")
        graph.add_edge("execute", "evaluate")
        
        # Conditional edge from evaluate
        graph.add_conditional_edges(
            "evaluate",
            self._should_continue,
            {
                "continue": "analyze",
                "end": END
            }
        )
        
        return graph.compile()
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the AI"""
        return """You are an intelligent browser automation agent. You interact with web pages using DOM-based methods - NO coordinate clicking.

AVAILABLE TOOLS (call ONE at a time):

1. click_by_text(text, element_type)
   - Clicks element containing the specified text
   - element_type: "button", "link", or "any"
   - Example: {"tool": "click_by_text", "text": "Imagine", "element_type": "any"}

2. click_by_selector(selector)
   - Clicks element by CSS selector or XPath
   - Example: {"tool": "click_by_selector", "selector": "button[aria-label='Imagine']"}

3. click_by_aria_label(aria_label)
   - Clicks element by its aria-label attribute
   - Example: {"tool": "click_by_aria_label", "aria_label": "Imagine"}

4. type_text(selector, text)
   - Types text into an input field
   - Example: {"tool": "type_text", "selector": "textarea", "text": "Hello"}

5. press_enter()
   - Presses the Enter key
   - Example: {"tool": "press_enter"}

6. scroll(direction)
   - Scrolls the page: "up" or "down"
   - Example: {"tool": "scroll", "direction": "down"}

7. done(reason)
   - Call when goal is achieved
   - Example: {"tool": "done", "reason": "Successfully clicked Imagine button"}

8. upload_file(selector, file_path)
   - Uploads a file to a file input element (works with hidden inputs)
   - Use selector "auto" to auto-detect the file input element
   - Example: {"tool": "upload_file", "selector": "auto", "file_path": "./test_image.png"}

9. wait_for_element(selector, timeout, condition)
   - Waits for an element to appear (for polling)
   - condition: "visible", "present", or "clickable"
   - timeout: seconds to wait (default: 30)
   - Example: {"tool": "wait_for_element", "selector": "button[aria-label='Download']", "timeout": 60, "condition": "visible"}

10. wait_for_text_change(selector, timeout)
   - Waits for element text to change, especially for percentage completion (e.g., "37%" -> "100%" -> "Download")
   - Monitors text and waits until it stops containing "%" symbol
   - timeout: seconds to wait (default: 120)
   - Example: {"tool": "wait_for_text_change", "selector": "button", "timeout": 120}

11. get_element_text(selector)
   - Gets the text content of an element
   - Example: {"tool": "get_element_text", "selector": "button"}

RESPONSE FORMAT:
Return a JSON object with:
{
    "reasoning": "Your analysis of the current state and what to do next",
    "tool_call": {<tool parameters>}
}

IMPORTANT RULES:
- Look at the clickable_elements list to find elements you can interact with
- Use exact text matches when possible
- If an element has aria-label, prefer click_by_aria_label
- For file uploads: Use upload_file with selector "auto" - do NOT click upload buttons that open system dialogs
- For video processing: Use wait_for_text_change to monitor percentage progress - do NOT click download until processing completes (text no longer contains "%")
- After each action, you'll see if URL or screen changed
- Call "done" when you see evidence the goal is achieved
- Be efficient - don't repeat failed actions"""

    def _analyze_node(self, state: AgentState) -> AgentState:
        """Analyze current page and decide next action"""
        print(f"\n🧠 [Analyze] Iteration {state['iteration'] + 1}/{state['max_iterations']}")
        
        # Get current page state
        page_state = self.browser.get_page_state()
        screenshot_path = self.browser.take_screenshot(f"step_{state['iteration'] + 1}")
        
        # Build context for AI
        context = self._build_context(state, page_state, screenshot_path)
        
        # Call AI
        try:
            response = self._call_ai(context, screenshot_path)
            
            # Parse response
            ai_decision = self._parse_ai_response(response)
            
            print(f"   💭 Reasoning: {ai_decision.get('reasoning', 'N/A')[:100]}...")
            print(f"   🎯 Tool call: {ai_decision.get('tool_call', {})}")
            
            # Update state
            state['page_state'] = page_state
            state['screenshot_path'] = screenshot_path
            state['messages'].append({
                "role": "assistant",
                "content": json.dumps(ai_decision)
            })
            
            # Store the tool call for execution
            state['pending_tool_call'] = ai_decision.get('tool_call', {})
            
        except Exception as e:
            print(f"   ❌ AI Error: {e}")
            state['error'] = str(e)
            state['_pending_tool_call'] = {"tool": "done", "reason": f"Error: {e}"}
        
        return state
    
    def _execute_node(self, state: AgentState) -> AgentState:
        """Execute the decided action"""
        tool_call = state.get('pending_tool_call', {})
        tool = tool_call.get('tool', '')
        
        print(f"\n⚡ [Execute] Running: {tool}")
        
        result = {"success": False, "error": "Unknown tool"}
        
        if tool == "click_by_text":
            result = self.browser.click_element_by_text(
                tool_call.get('text', ''),
                tool_call.get('element_type', 'any')
            )
        
        elif tool == "click_by_selector":
            result = self.browser.click_element_by_selector(
                tool_call.get('selector', '')
            )
        
        elif tool == "click_by_aria_label":
            result = self.browser.click_element_by_aria_label(
                tool_call.get('aria_label', '')
            )
        
        elif tool == "type_text":
            result = self.browser.type_into_element(
                tool_call.get('selector', ''),
                tool_call.get('text', '')
            )
        
        elif tool == "press_enter":
            result = self.browser.press_enter()
        
        elif tool == "scroll":
            result = self.browser.scroll_page(tool_call.get('direction', 'down'))
        
        elif tool == "upload_file":
            result = self.browser.upload_file(
                tool_call.get('selector', ''),
                tool_call.get('file_path', '')
            )
        
        elif tool == "wait_for_element":
            result = self.browser.wait_for_element(
                tool_call.get('selector', ''),
                tool_call.get('timeout', 30),
                tool_call.get('condition', 'visible')
            )
        
        elif tool == "wait_for_text_change":
            result = self.browser.wait_for_text_change(
                tool_call.get('selector', ''),
                tool_call.get('initial_text', None),
                tool_call.get('timeout', 120)
            )
        
        elif tool == "get_element_text":
            result = self.browser.get_element_text(
                tool_call.get('selector', '')
            )
        
        elif tool == "done":
            result = {
                "success": True,
                "action": "done",
                "reason": tool_call.get('reason', 'Goal achieved')
            }
            state['goal_achieved'] = True
        
        # Record result
        state['last_action_result'] = result
        state['action_history'].append({
            "iteration": state['iteration'] + 1,
            "tool_call": tool_call,
            "result": result
        })
        
        if result.get('success'):
            print(f"   ✅ {result.get('description', 'Action completed')}")
        else:
            print(f"   ❌ {result.get('error', 'Action failed')}")
        
        return state
    
    def _evaluate_node(self, state: AgentState) -> AgentState:
        """Evaluate the result and update state"""
        print(f"\n📊 [Evaluate]")
        
        result = state['last_action_result']
        
        # Check for changes
        url_changed = result.get('url_changed', False)
        screen_changed = result.get('screen_changed', False)
        
        if url_changed:
            print(f"   📍 URL changed to: {result.get('current_url', 'unknown')}")
        if screen_changed:
            print(f"   🖼️  Screen content changed")
        if not url_changed and not screen_changed:
            print(f"   ⚠️  No visible changes detected")
        
        # Increment iteration
        state['iteration'] += 1
        
        # Add feedback to messages
        feedback = {
            "role": "user",
            "content": f"Action result: {json.dumps(result)}"
        }
        state['messages'].append(feedback)
        
        return state
    
    def _should_continue(self, state: AgentState) -> Literal["continue", "end"]:
        """Decide whether to continue or end"""
        
        # Check if goal achieved
        if state['goal_achieved']:
            print(f"\n✅ Goal achieved!")
            return "end"
        
        # Check iteration limit
        if state['iteration'] >= state['max_iterations']:
            print(f"\n⚠️  Max iterations ({state['max_iterations']}) reached")
            return "end"
        
        # Check for errors
        if state.get('error'):
            print(f"\n❌ Error: {state['error']}")
            return "end"
        
        return "continue"
    
    def _build_context(self, state: AgentState, page_state: Dict, screenshot_path: str) -> str:
        """Build context string for AI"""
        
        context = f"""TASK: {state['task']}

CURRENT PAGE STATE:
- URL: {page_state.get('url', 'unknown')}
- Title: {page_state.get('title', 'unknown')}

CLICKABLE ELEMENTS:
{json.dumps(page_state.get('clickable_elements', []), indent=2)}

INPUT ELEMENTS:
{json.dumps(page_state.get('input_elements', []), indent=2)}

VISIBLE TEXT (summary):
{page_state.get('visible_text_summary', '')[:500]}

ITERATION: {state['iteration'] + 1}/{state['max_iterations']}

PREVIOUS ACTIONS:
{json.dumps(state['action_history'][-3:], indent=2) if state['action_history'] else 'None yet'}

What is your next action? Analyze the page and call one tool."""

        return context
    
    def _call_ai(self, context: str, screenshot_path: str) -> str:
        """Call Azure OpenAI with context and screenshot"""
        
        # Encode screenshot
        with open(screenshot_path, "rb") as f:
            base64_image = base64.b64encode(f.read()).decode('utf-8')
        
        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": context},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                    }
                ]
            }
        ]
        
        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=messages,
            max_completion_tokens=1000,
            temperature=0.1
        )
        
        return response.choices[0].message.content
    
    def _parse_ai_response(self, response: str) -> Dict:
        """Parse AI response to extract tool call"""
        try:
            # Try to extract JSON
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_str = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                json_str = response[start:end].strip()
            elif "{" in response:
                start = response.find("{")
                end = response.rfind("}") + 1
                json_str = response[start:end]
            else:
                json_str = response
            
            return json.loads(json_str)
            
        except json.JSONDecodeError:
            # Fallback: try to extract tool call manually
            return {
                "reasoning": response,
                "tool_call": {"tool": "done", "reason": "Could not parse response"}
            }
    
    def run(self, task: str, initial_url: str, max_iterations: int = 10) -> bool:
        """Run the agent to complete a task"""
        
        print("\n" + "="*60)
        print("🤖 LANGGRAPH BROWSER AGENT")
        print("="*60)
        print(f"📋 Task: {task}")
        print(f"🌐 URL: {initial_url}")
        print(f"🔄 Max iterations: {max_iterations}")
        print("="*60)
        
        # Start browser
        if not self.browser.start():
            print("❌ Failed to start browser")
            return False
        
        try:
            # Navigate to initial URL
            self.browser.navigate(initial_url)
            
            # Initial state
            initial_state: AgentState = {
                "task": task,
                "messages": [],
                "page_state": {},
                "screenshot_path": "",
                "action_history": [],
                "iteration": 0,
                "max_iterations": max_iterations,
                "goal_achieved": False,
                "last_action_result": {},
                "error": "",
                "pending_tool_call": {}
            }
            
            # Run the graph
            final_state = self.graph.invoke(initial_state)
            
            # Print summary
            print("\n" + "="*60)
            print("📊 EXECUTION SUMMARY")
            print("="*60)
            print(f"   Iterations: {final_state['iteration']}")
            print(f"   Goal achieved: {final_state['goal_achieved']}")
            print(f"   Actions taken: {len(final_state['action_history'])}")
            
            if final_state['action_history']:
                print("\n   Action history:")
                for action in final_state['action_history']:
                    status = "✅" if action['result'].get('success') else "❌"
                    print(f"      {status} {action['tool_call']}")
            
            return final_state['goal_achieved']
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def interactive_mode(self):
        """Keep browser open for inspection"""
        print("\n🎮 Interactive mode - Press Ctrl+C to exit")
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Exiting...")
    
    def cleanup(self):
        """Clean up resources"""
        self.browser.quit()

