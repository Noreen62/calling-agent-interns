# main.py (single file version)
import json
import math
from datetime import datetime
from typing import Dict, Any, List, Optional

# ============ TOOLS IMPLEMENTATION ============
def get_weather(location: str, unit: str = "celsius") -> Dict[str, Any]:
    weather_data = {
        "New York": {"temp": 22, "condition": "Sunny", "humidity": 65},
        "London": {"temp": 15, "condition": "Cloudy", "humidity": 78},
        "Tokyo": {"temp": 28, "condition": "Rainy", "humidity": 82},
        "Paris": {"temp": 18, "condition": "Partly Cloudy", "humidity": 70}
    }
    
    city = location.split(',')[0].title()
    if city in weather_data:
        data = weather_data[city].copy()
        if unit == "fahrenheit":
            data["temp"] = (data["temp"] * 9/5) + 32
        data["location"] = location
        data["unit"] = unit
        return {"status": "success", "data": data}
    else:
        return {"status": "error", "message": f"Weather data not found for {location}"}

def calculate(expression: str) -> Dict[str, Any]:
    try:
        allowed_chars = set("0123456789+-*/().% ")
        if not all(c in allowed_chars for c in expression):
            return {"status": "error", "message": "Invalid characters in expression"}
        
        result = eval(expression, {"__builtins__": {}}, math.__dict__)
        return {"status": "success", "result": result, "expression": expression}
    except ZeroDivisionError:
        return {"status": "error", "message": "Division by zero error"}
    except Exception as e:
        return {"status": "error", "message": f"Calculation error: {str(e)}"}

def get_current_time(timezone: str = "UTC") -> Dict[str, Any]:
    try:
        now = datetime.utcnow()
        return {
            "status": "success",
            "timezone": timezone,
            "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp": now.timestamp()
        }
    except Exception as e:
        return {"status": "error", "message": f"Time error: {str(e)}"}

def search(query: str, limit: int = 3) -> Dict[str, Any]:
    sample_results = {
        "python": ["Python is a high-level language", "Python has extensive libraries"],
        "default": [f"Result {i+1} for '{query}'" for i in range(limit)]
    }
    results = sample_results.get(query.lower(), sample_results["default"])
    return {"status": "success", "query": query, "results": results[:limit]}

AVAILABLE_TOOLS = {
    "get_weather": {"function": get_weather},
    "calculate": {"function": calculate},
    "get_current_time": {"function": get_current_time},
    "search": {"function": search}
}

# ============ AGENT IMPLEMENTATION ============
class ToolCallingAgent:
    def __init__(self):
        self.tools = AVAILABLE_TOOLS
    
    def parse_tool_call(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if "function" not in tool_call:
                return {"status": "error", "error_message": "Invalid tool call format"}
            
            function_name = tool_call["function"]["name"]
            arguments = json.loads(tool_call["function"]["arguments"])
            
            if function_name not in self.tools:
                return {"status": "error", "error_message": f"Unknown tool: {function_name}"}
            
            result = self.tools[function_name]["function"](**arguments)
            return {"status": "success", "tool": function_name, "result": result}
            
        except json.JSONDecodeError as e:
            return {"status": "error", "error_message": f"Invalid JSON: {str(e)}"}
        except Exception as e:
            return {"status": "error", "error_message": str(e)}
    
    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if task.get("type") == "single_tool":
                return self.parse_tool_call(task.get("tool_call", {}))
            else:
                return {"status": "error", "error_message": "Unknown task type"}
        except Exception as e:
            return {"status": "error", "error_message": str(e)}

# ============ MAIN DEMO ============
def main():
    print("\n🚀 TOOL-CALLING AI AGENT DEMO")
    print("="*50)
    
    agent = ToolCallingAgent()
    print(f"✅ Agent initialized with {len(agent.tools)} tools\n")
    
    # Test different tool calls
    test_cases = [
        ("Weather", {"type": "single_tool", "tool_call": {"function": {"name": "get_weather", "arguments": '{"location": "London"}'}}}),
        ("Calculator", {"type": "single_tool", "tool_call": {"function": {"name": "calculate", "arguments": '{"expression": "15 * 8"}'}}}),
        ("Time", {"type": "single_tool", "tool_call": {"function": {"name": "get_current_time", "arguments": '{}'}}}),
        ("Search", {"type": "single_tool", "tool_call": {"function": {"name": "search", "arguments": '{"query": "python"}'}}}),
    ]
    
    for name, task in test_cases:
        print(f"\n📋 Testing {name}:")
        response = agent.process_task(task)
        print(json.dumps(response, indent=2))
    
    print("\n✨ Demo completed!")

if __name__ == "__main__":
    main()