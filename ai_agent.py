"""
AI Vision Agent - Multi-step reasoning agent using GPT-4.1 Vision on Azure
"""
import os
import json
import base64
from typing import Dict, List, Optional, Tuple
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()


class AIAgent:
    """AI-powered computer use agent with vision capabilities"""
    
    def __init__(self):
        """Initialize Azure OpenAI client"""
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://primary-az-ai-foundary.cognitiveservices.azure.com/")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
        
        if not self.api_key:
            raise ValueError(
                "Missing Azure OpenAI API key. Set AZURE_OPENAI_API_KEY in .env file"
            )
        
        self.client = AzureOpenAI(
            api_key=self.api_key,
            api_version=self.api_version,
            azure_endpoint=self.endpoint
        )
        
        self.conversation_history: List[Dict] = []
        self.system_prompt = self._get_system_prompt()
        
        print(f"🔧 Azure OpenAI initialized:")
        print(f"   Endpoint: {self.endpoint}")
        print(f"   Deployment: {self.deployment}")
        print(f"   API Version: {self.api_version}")
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the AI agent"""
        return """You are an AI computer use agent that controls a web browser by analyzing screenshots and performing actions.

AVAILABLE ACTIONS:
1. CLICK(x, y) - Click at pixel coordinates (x, y). Coordinates are relative to the viewport.
2. TYPE(text) - Type the specified text into the currently focused element.
3. SCROLL(direction) - Scroll the page. Direction can be: "up", "down", "left", "right".
4. WAIT(seconds) - Wait for the specified number of seconds.
5. DONE - Task is complete.

RESPONSE FORMAT:
You must respond with a JSON object containing:
{
    "reasoning": "Your step-by-step reasoning about what you see and what to do next",
    "action": "CLICK(120, 450)" | "TYPE(text)" | "SCROLL(down)" | "WAIT(2)" | "DONE",
    "confidence": 0.0-1.0
}

COORDINATE SYSTEM:
- The screenshot shows the EXACT browser viewport you will interact with
- Coordinates are in pixels: (0, 0) is the TOP-LEFT corner of the viewport
- X increases to the RIGHT, Y increases DOWNWARD
- IMPORTANT: Click on the CENTER of buttons/elements, not edges
- Double-check button boundaries before providing coordinates

BEST PRACTICES:
- Analyze the screenshot carefully and identify the EXACT center point of clickable elements
- Always explain your reasoning, including the visual position you're targeting
- For buttons, aim for the text center, not the icon or edge
- If you see multiple similar elements, carefully distinguish them by position
- Use TYPE action AFTER clicking an input field
- Use WAIT when pages are loading or animations are in progress
- Return DONE when the task objective is clearly achieved

COORDINATE ACCURACY:
- Describe the element's position (e.g., "left sidebar, 200px from top")
- Estimate the element's size and calculate the center point
- Verify your coordinates are within the viewport bounds
- Be conservative - it's better to click slightly inside an element than on its edge

Be PRECISE with coordinates and DETAILED with your reasoning."""

    def analyze_screenshot(
        self, 
        screenshot_path: str, 
        task: str,
        viewport_size: Optional[Tuple[int, int]] = None
    ) -> Dict:
        """
        Analyze screenshot and determine next action
        
        Args:
            screenshot_path: Path to screenshot image
            task: Current task description
            viewport_size: Optional (width, height) tuple for context
            
        Returns:
            Dict with 'reasoning', 'action', and 'confidence'
        """
        # Encode screenshot to base64
        with open(screenshot_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Build user message with context
        viewport_info = ""
        if viewport_size:
            viewport_info = f"\nViewport size: {viewport_size[0]}x{viewport_size[1]} pixels."
        
        user_message = f"""Current task: {task}
{viewport_info}

Analyze this screenshot and determine the next action to complete the task. 
Provide your reasoning and the exact action to take."""

        # Prepare messages
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Add conversation history (last 3 exchanges for context)
        messages.extend(self.conversation_history[-6:])
        
        # Add current screenshot and task
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": user_message
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{base64_image}"
                    }
                }
            ]
        })
        
        try:
            # Call Azure OpenAI with GPT-4.1
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                max_completion_tokens=2000,  # GPT-4.1 uses max_completion_tokens
                temperature=0.1,  # Lower temperature for more consistent actions
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            ai_response = response.choices[0].message.content
            
            # Parse JSON response
            try:
                # Extract JSON from response (handle markdown code blocks)
                if "```json" in ai_response:
                    json_start = ai_response.find("```json") + 7
                    json_end = ai_response.find("```", json_start)
                    json_str = ai_response[json_start:json_end].strip()
                elif "```" in ai_response:
                    json_start = ai_response.find("```") + 3
                    json_end = ai_response.find("```", json_start)
                    json_str = ai_response[json_start:json_end].strip()
                else:
                    json_str = ai_response.strip()
                
                result = json.loads(json_str)
                
                # Validate result structure
                if "action" not in result:
                    raise ValueError("Missing 'action' in AI response")
                
                # Add full response to conversation history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": ai_response
                })
                
                return {
                    "reasoning": result.get("reasoning", ""),
                    "action": result["action"],
                    "confidence": result.get("confidence", 0.5),
                    "raw_response": ai_response
                }
                
            except json.JSONDecodeError as e:
                print(f"⚠️  Failed to parse JSON from AI response: {e}")
                print(f"Raw response: {ai_response}")
                # Try to extract action from text
                return self._parse_action_from_text(ai_response)
                
        except Exception as e:
            print(f"❌ Error calling Azure OpenAI: {e}")
            raise
    
    def _parse_action_from_text(self, text: str) -> Dict:
        """Fallback: try to extract action from unstructured text"""
        text_lower = text.lower()
        
        if "done" in text_lower or "complete" in text_lower:
            action = "DONE"
        elif "click" in text_lower:
            # Try to extract coordinates
            import re
            coords = re.findall(r'\((\d+),\s*(\d+)\)', text)
            if coords:
                x, y = coords[0]
                action = f"CLICK({x}, {y})"
            else:
                action = "WAIT(1)"  # Fallback
        elif "type" in text_lower or "enter" in text_lower:
            action = "WAIT(1)"  # Need more context
        else:
            action = "WAIT(1)"
        
        return {
            "reasoning": text,
            "action": action,
            "confidence": 0.3,
            "raw_response": text
        }
    
    def parse_action(self, action_str: str) -> Dict:
        """
        Parse action string into structured format
        
        Args:
            action_str: Action string like "CLICK(120, 450)" or "TYPE(hello)"
            
        Returns:
            Dict with 'type', 'params'
        """
        action_str = action_str.strip().upper()
        
        if action_str == "DONE":
            return {"type": "DONE", "params": {}}
        
        if action_str.startswith("CLICK"):
            # Extract coordinates: CLICK(120, 450)
            import re
            match = re.search(r'CLICK\((\d+),\s*(\d+)\)', action_str)
            if match:
                return {
                    "type": "CLICK",
                    "params": {"x": int(match.group(1)), "y": int(match.group(2))}
                }
        
        if action_str.startswith("TYPE"):
            # Extract text: TYPE(hello world)
            import re
            match = re.search(r'TYPE\((.*?)\)', action_str)
            if match:
                return {
                    "type": "TYPE",
                    "params": {"text": match.group(1)}
                }
        
        if action_str.startswith("SCROLL"):
            # Extract direction: SCROLL(down)
            import re
            match = re.search(r'SCROLL\((up|down|left|right)\)', action_str, re.IGNORECASE)
            if match:
                return {
                    "type": "SCROLL",
                    "params": {"direction": match.group(1).lower()}
                }
        
        if action_str.startswith("WAIT"):
            # Extract seconds: WAIT(2)
            import re
            match = re.search(r'WAIT\((\d+)\)', action_str)
            if match:
                return {
                    "type": "WAIT",
                    "params": {"seconds": int(match.group(1))}
                }
        
        # Unknown action
        return {"type": "UNKNOWN", "params": {}}
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []

