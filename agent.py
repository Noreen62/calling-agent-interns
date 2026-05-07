import json
import openai
from typing import Dict, Any, List

# Initialize the OpenAI client (Ensure OPENAI_API_KEY is in your environment variables)
client = openai.OpenAI(api_key="-")

class ToolCallError(Exception):
    """Custom exception for tool-related errors."""
    pass

class ToolCallingAgent:
    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt
        self.messages = [{"role": "system", "content": system_prompt}]
        
        # Define available tools in strict OpenAI JSON schema format
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "reverse_string",
                    "description": "Reverses a given string.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "The string to reverse."
                            }
                        },
                        "required": ["text"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "string_utils",
                    "description": "A legacy tool for advanced string manipulation.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string"},
                            "text": {"type": "string"}
                        },
                        "required": ["action", "text"]
                    }
                }
            }
        ]
        
        # Simulate a scenario where a specific tool is disabled (like your previous error)
        self.disabled_tools = {"string_utils"}

    def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Executes the local tool and returns a JSON string result."""
        
        # --- ERROR HANDLING 1: Disabled Tools ---
        if tool_name in self.disabled_tools:
            raise ToolCallError(f'Tool "{tool_name}" is currently disabled. Enable it from the toolbar.')
        
        # --- Tool Logic ---
        if tool_name == "reverse_string":
            text = arguments.get("text", "")
            reversed_text = text[::-1]
            return json.dumps({"status": "success", "reversed_string": reversed_text})
        
        # --- ERROR HANDLING 2: Unknown Tool ---
        raise ToolCallError(f'Unknown tool requested: "{tool_name}"')

    def _handle_tool_calls(self, tool_calls: List[Any]) -> List[Dict[str, str]]:
        """Processes tool calls requested by the LLM, with bulletproof error handling."""
        tool_messages = []
        
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = tool_call.function.arguments
            tool_call_id = tool_call.id
            
            try:
                # --- ERROR HANDLING 3: Malformed JSON from LLM ---
                args_dict = json.loads(function_args)
                
                # Execute the tool
                result_json = self._execute_tool(function_name, args_dict)
                tool_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": result_json
                })
                
            except json.JSONDecodeError:
                # Feed the JSON error back to the LLM so it can self-correct
                error_msg = json.dumps({"error": f"Invalid JSON arguments provided: {function_args}"})
                tool_messages.append({"role": "tool", "tool_call_id": tool_call_id, "content": error_msg})
                
            except ToolCallError as e:
                # Feed the tool error (e.g., Disabled Tool) back to the LLM
                error_msg = json.dumps({"error": str(e)})
                tool_messages.append({"role": "tool", "tool_call_id": tool_call_id, "content": error_msg})
                
            except Exception as e:
                # --- ERROR HANDLING 4: Catch-all for unexpected crashes ---
                error_msg = json.dumps({"error": f"Internal server error executing tool: {str(e)}"})
                tool_messages.append({"role": "tool", "tool_call_id": tool_call_id, "content": error_msg})
                
        return tool_messages

    def run(self, user_input: str) -> Dict[str, Any]:
        """Main agent loop. Returns a strict JSON response."""
        self.messages.append({"role": "user", "content": user_input})
        
        try:
            while True:
                response = client.chat.completions.create(
                    model="gpt-4o-mini", # or gpt-4o
                    messages=self.messages,
                    tools=self.tools,
                    tool_choice="auto"
                )
                
                assistant_message = response.choices[0].message
                self.messages.append(assistant_message)
                
                # Check if the LLM wants to call a tool
                if assistant_message.tool_calls:
                    # Process tools and append errors/successes to messages
                    tool_results = self._handle_tool_calls(assistant_message.tool_calls)
                    self.messages.extend(tool_results)
                    # Loop again to let the LLM process the tool results
                    continue 
                
                # If no tool calls, the LLM has generated the final text response
                break
                
        except openai.AuthenticationError:
            return {"error": "Authentication failed. Check your OPENAI_API_KEY."}
        except openai.RateLimitError:
            return {"error": "Rate limit exceeded. Please wait and try again."}
        except Exception as e:
            return {"error": f"Unexpected API error: {str(e)}"}
            
        # --- JSON RESPONSE FORMATTING ---
        # Wrap the final text output in a strict JSON structure
        return {
            "status": "success",
            "response": assistant_message.content,
            "message_history_length": len(self.messages)
        }


# ==========================================
# ASSIGNMENT TEST RUNNER
# ==========================================
if __name__ == "__main__":
    agent = ToolCallingAgent(
        system_prompt="You are a helpful assistant. If a tool fails or is disabled, apologize and do the task manually if possible."
    )
    
    print("--- TEST 1: Working Tool ---")
    result1 = agent.run("Reverse the string 'hello world'")
    print(json.dumps(result1, indent=2))
    
    print("\n--- TEST 2: Disabled Tool (Simulating your previous error) ---")
    result2 = agent.run("Use the string_utils tool to reverse 'goodbye world'")
    print(json.dumps(result2, indent=2))