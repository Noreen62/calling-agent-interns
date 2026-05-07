# tools.py
import json
import math
from datetime import datetime
from typing import Dict, Any

# Tool implementations
def get_weather(location: str, unit: str = "celsius") -> Dict[str, Any]:
    """Get weather information for a location"""
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
    """Perform mathematical calculations"""
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
    """Get current time"""
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
    """Search for information"""
    sample_results = {
        "python": [
            "Python is a high-level programming language",
            "Python is known for its simplicity and readability",
            "Python has extensive libraries for AI and data science"
        ],
        "weather": [
            "Weather is the state of the atmosphere",
            "Weather forecasting uses mathematical models",
            "Extreme weather events are increasing"
        ],
        "default": [
            f"Search result 1 for '{query}'",
            f"Search result 2 for '{query}'",
            f"Search result 3 for '{query}'"
        ]
    }
    
    results = sample_results.get(query.lower(), sample_results["default"])
    return {
        "status": "success",
        "query": query,
        "results": results[:limit],
        "total_results": len(results[:limit])
    }

# Tool registry
AVAILABLE_TOOLS = {
    "get_weather": {
        "function": get_weather,
        "description": "Get weather information for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City name"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
            },
            "required": ["location"]
        }
    },
    "calculate": {
        "function": calculate,
        "description": "Perform mathematical calculations",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "Math expression"}
            },
            "required": ["expression"]
        }
    },
    "get_current_time": {
        "function": get_current_time,
        "description": "Get current time",
        "parameters": {
            "type": "object",
            "properties": {
                "timezone": {"type": "string", "description": "Timezone"}
            },
            "required": []
        }
    },
    "search": {
        "function": search,
        "description": "Search for information",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "limit": {"type": "integer", "description": "Number of results"}
            },
            "required": ["query"]
        }
    }
}