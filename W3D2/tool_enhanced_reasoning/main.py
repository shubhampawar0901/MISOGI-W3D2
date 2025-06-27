#!/usr/bin/env python3
"""
Tool-Enhanced Reasoning Script

A Python script that takes natural language queries and uses an LLM to:
- Interpret the query using chain-of-thought (CoT) style reasoning
- Call external tools when necessary
- Combine results to produce a final answer
"""

import os
import sys
import json
import re
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import openai
from dotenv import load_dotenv

# Add tools directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))

from math_tools import MATH_TOOLS, call_tool as call_math_tool
from string_tools import STRING_TOOLS, call_tool as call_string_tool


@dataclass
class ReasoningResult:
    """Result of the reasoning process."""
    query: str
    reasoning_steps: str
    tool_used: Optional[str]
    tool_result: Optional[Any]
    final_answer: str
    success: bool
    error: Optional[str] = None


class ToolEnhancedReasoner:
    """Main class for tool-enhanced reasoning."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """Initialize the reasoner with OpenAI API."""
        load_dotenv()
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        
        openai.api_key = self.api_key
        self.model = model
        
        # Available tools
        self.available_tools = {
            **{f"math.{name}": func for name, func in MATH_TOOLS.items()},
            **{f"string.{name}": func for name, func in STRING_TOOLS.items()}
        }
    
    def get_reasoning_prompt(self, query: str) -> str:
        """Create a chain-of-thought prompt for the LLM."""
        tool_descriptions = self._get_tool_descriptions()
        
        prompt = f"""You are an AI assistant that can reason through problems step by step and use tools when needed.

Available Tools:
{tool_descriptions}

Your task is to analyze the following query and provide a step-by-step reasoning process.

Query: "{query}"

Please follow this format:

REASONING:
[Provide step-by-step reasoning about what the query is asking]

TOOL_NEEDED:
[If you need to use a tool, specify which one and why. If no tool is needed, write "NONE"]

TOOL_CALL:
[If a tool is needed, provide the exact function call in this format: tool_name(arguments)]

FINAL_ANSWER:
[Provide the final answer to the query]

Remember:
- Think step by step
- Only use tools when necessary for calculations or text analysis
- Be precise about which tool to use and how to call it
- Provide clear reasoning for your decisions
"""
        return prompt
    
    def _get_tool_descriptions(self) -> str:
        """Get descriptions of available tools."""
        descriptions = []
        
        # Math tools
        descriptions.append("MATH TOOLS:")
        descriptions.append("- math.add(a, b) - Add two numbers")
        descriptions.append("- math.subtract(a, b) - Subtract b from a")
        descriptions.append("- math.multiply(a, b) - Multiply two numbers")
        descriptions.append("- math.divide(a, b) - Divide a by b")
        descriptions.append("- math.square_root(number) - Calculate square root")
        descriptions.append("- math.average(numbers_list) - Calculate average of numbers")
        descriptions.append("- math.power(base, exponent) - Raise base to power")
        
        # String tools
        descriptions.append("\nSTRING TOOLS:")
        descriptions.append("- string.count_vowels(text) - Count vowels in text")
        descriptions.append("- string.count_letters(text) - Count letters in text")
        descriptions.append("- string.count_words(text) - Count words in text")
        descriptions.append("- string.count_consonants(text) - Count consonants in text")
        
        return "\n".join(descriptions)
    
    def call_llm(self, prompt: str) -> str:
        """Call the LLM with the given prompt."""
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant that can reason step by step and use tools when needed."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.1
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"Error calling LLM: {e}")
    
    def parse_llm_response(self, response: str) -> Dict[str, str]:
        """Parse the LLM response to extract reasoning, tool call, and answer."""
        sections = {
            "reasoning": "",
            "tool_needed": "",
            "tool_call": "",
            "final_answer": ""
        }
        
        # Extract sections using regex
        reasoning_match = re.search(r"REASONING:\s*(.*?)(?=TOOL_NEEDED:|$)", response, re.DOTALL)
        if reasoning_match:
            sections["reasoning"] = reasoning_match.group(1).strip()
        
        tool_needed_match = re.search(r"TOOL_NEEDED:\s*(.*?)(?=TOOL_CALL:|$)", response, re.DOTALL)
        if tool_needed_match:
            sections["tool_needed"] = tool_needed_match.group(1).strip()
        
        tool_call_match = re.search(r"TOOL_CALL:\s*(.*?)(?=FINAL_ANSWER:|$)", response, re.DOTALL)
        if tool_call_match:
            sections["tool_call"] = tool_call_match.group(1).strip()
        
        final_answer_match = re.search(r"FINAL_ANSWER:\s*(.*?)$", response, re.DOTALL)
        if final_answer_match:
            sections["final_answer"] = final_answer_match.group(1).strip()
        
        return sections
    
    def execute_tool_call(self, tool_call: str) -> Any:
        """Execute a tool call and return the result."""
        if not tool_call or tool_call.upper() == "NONE":
            return None
        
        # Parse tool call (simple parsing for demonstration)
        # Format: tool_name(arguments)
        match = re.match(r"(\w+\.\w+)\((.*?)\)", tool_call)
        if not match:
            raise ValueError(f"Invalid tool call format: {tool_call}")
        
        tool_name = match.group(1)
        args_str = match.group(2)
        
        if tool_name not in self.available_tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        # Parse arguments (simple parsing)
        args = []
        if args_str.strip():
            # Handle different argument types
            if tool_name.startswith("math."):
                # For math tools, parse numbers and lists
                if "[" in args_str and "]" in args_str:
                    # List of numbers
                    list_match = re.search(r"\[(.*?)\]", args_str)
                    if list_match:
                        numbers_str = list_match.group(1)
                        args = [[float(x.strip()) for x in numbers_str.split(",")]]
                else:
                    # Individual numbers
                    args = [float(x.strip()) for x in args_str.split(",")]
            else:
                # For string tools, treat as strings
                args = [arg.strip().strip('"\'') for arg in args_str.split(",")]
        
        # Call the appropriate tool
        if tool_name.startswith("math."):
            return call_math_tool(tool_name.split(".", 1)[1], *args)
        elif tool_name.startswith("string."):
            return call_string_tool(tool_name.split(".", 1)[1], *args)
        else:
            raise ValueError(f"Unknown tool category: {tool_name}")
    
    def reason(self, query: str) -> ReasoningResult:
        """Main reasoning function that processes a query."""
        try:
            # Get reasoning from LLM
            prompt = self.get_reasoning_prompt(query)
            llm_response = self.call_llm(prompt)
            
            # Parse the response
            parsed = self.parse_llm_response(llm_response)
            
            # Execute tool if needed
            tool_result = None
            tool_used = None
            
            if parsed["tool_needed"].upper() != "NONE" and parsed["tool_call"]:
                tool_used = parsed["tool_call"]
                tool_result = self.execute_tool_call(parsed["tool_call"])
                
                # Update final answer with tool result if needed
                if tool_result is not None:
                    final_answer = f"{parsed['final_answer']} (Tool result: {tool_result})"
                else:
                    final_answer = parsed["final_answer"]
            else:
                final_answer = parsed["final_answer"]
            
            return ReasoningResult(
                query=query,
                reasoning_steps=parsed["reasoning"],
                tool_used=tool_used,
                tool_result=tool_result,
                final_answer=final_answer,
                success=True
            )
            
        except Exception as e:
            return ReasoningResult(
                query=query,
                reasoning_steps="",
                tool_used=None,
                tool_result=None,
                final_answer="",
                success=False,
                error=str(e)
            )


def main():
    """Main function for command-line usage."""
    if len(sys.argv) < 2:
        print("Usage: python main.py '<query>'")
        print("\nExample queries:")
        print("- 'What's the square root of the average of 18 and 50?'")
        print("- 'How many vowels are in the word Multimodality?'")
        print("- 'Is the number of letters in machine greater than the number of vowels in reasoning?'")
        return
    
    query = sys.argv[1]
    
    try:
        reasoner = ToolEnhancedReasoner()
        result = reasoner.reason(query)
        
        print("=" * 60)
        print("TOOL-ENHANCED REASONING RESULT")
        print("=" * 60)
        print(f"Query: {result.query}")
        print("\nReasoning Steps:")
        print(result.reasoning_steps)
        
        if result.tool_used:
            print(f"\nTool Used: {result.tool_used}")
            print(f"Tool Result: {result.tool_result}")
        else:
            print("\nTool Used: None")
        
        print(f"\nFinal Answer: {result.final_answer}")
        print(f"Success: {result.success}")
        
        if result.error:
            print(f"Error: {result.error}")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
