# Tool-Enhanced Reasoning Script

A Python script that uses Large Language Models (LLMs) to interpret natural language queries, apply chain-of-thought reasoning, and automatically call external tools when needed to solve complex problems.

## Features

- 🧠 **Chain-of-Thought Reasoning**: Uses structured prompting to break down complex queries
- 🔧 **Automatic Tool Selection**: Intelligently decides when and which tools to use
- 🧮 **Math Tools**: Calculator functions for mathematical operations
- 📝 **String Tools**: Text analysis and string manipulation functions
- 🤖 **LLM Integration**: Works with OpenAI's GPT models
- 📊 **Detailed Output**: Shows reasoning steps, tool usage, and final answers

## Installation

1. **Clone or download the project**:
   ```bash
   cd tool_enhanced_reasoning
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env file with your OpenAI API key
   ```

## Configuration

### API Key Setup

1. Get your OpenAI API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Copy `.env.example` to `.env`
3. Replace `your_openai_api_key_here` with your actual API key

```env
OPENAI_API_KEY=sk-your-actual-api-key-here
```

## Usage

### Command Line

```bash
python main.py "Your question here"
```

### Examples

Here are 5+ test queries and their expected outputs:

#### 1. Mathematical Calculation
```bash
python main.py "What's the square root of the average of 18 and 50?"
```

**Expected Output:**
```
TOOL-ENHANCED REASONING RESULT
============================================================
Query: What's the square root of the average of 18 and 50?

Reasoning Steps:
I need to find the square root of the average of 18 and 50.
First, I'll calculate the average of 18 and 50: (18 + 50) / 2 = 34
Then, I'll find the square root of 34.

Tool Used: math.average([18, 50])
Tool Result: 34.0

Final Answer: The square root of the average of 18 and 50 is approximately 5.83 (Tool result: 34.0, then sqrt(34) ≈ 5.83)
```

#### 2. String Analysis
```bash
python main.py "How many vowels are in the word 'Multimodality'?"
```

**Expected Output:**
```
TOOL-ENHANCED REASONING RESULT
============================================================
Query: How many vowels are in the word 'Multimodality'?

Reasoning Steps:
I need to count the vowels in the word "Multimodality".
Vowels are a, e, i, o, u (and sometimes y).

Tool Used: string.count_vowels("Multimodality")
Tool Result: 6

Final Answer: The word "Multimodality" contains 6 vowels (Tool result: 6)
```

#### 3. Comparison Query
```bash
python main.py "Is the number of letters in 'machine' greater than the number of vowels in 'reasoning'?"
```

#### 4. Complex Mathematical Query
```bash
python main.py "What is 15 squared plus the square root of 144?"
```

#### 5. Text Analysis Query
```bash
python main.py "How many consonants are in the word 'programming'?"
```

#### 6. Simple Query (No Tools Needed)
```bash
python main.py "What is the capital of France?"
```

## How Tool Selection Works

The script uses a structured prompt that guides the LLM through a decision-making process:

1. **Analysis Phase**: The LLM analyzes the query to understand what's being asked
2. **Tool Decision**: Based on the query type, it decides if tools are needed:
   - Mathematical operations → Math tools
   - Text analysis → String tools
   - General knowledge → No tools needed
3. **Tool Execution**: If a tool is needed, the script parses the LLM's tool call and executes it
4. **Result Integration**: The tool result is incorporated into the final answer

### Prompt Strategy

The prompt includes:
- Clear instructions for step-by-step reasoning
- Descriptions of available tools
- Structured output format (REASONING, TOOL_NEEDED, TOOL_CALL, FINAL_ANSWER)
- Examples of when to use tools vs. when to rely on general knowledge

## Available Tools

### Math Tools
- `math.add(a, b)` - Add two numbers
- `math.subtract(a, b)` - Subtract b from a
- `math.multiply(a, b)` - Multiply two numbers
- `math.divide(a, b)` - Divide a by b
- `math.square_root(number)` - Calculate square root
- `math.average(numbers_list)` - Calculate average
- `math.power(base, exponent)` - Raise to power
- `math.factorial(n)` - Calculate factorial
- `math.absolute_value(number)` - Get absolute value

### String Tools
- `string.count_vowels(text)` - Count vowels in text
- `string.count_letters(text)` - Count letters in text
- `string.count_words(text)` - Count words in text
- `string.count_consonants(text)` - Count consonants in text
- `string.find_longest_word(text)` - Find longest word
- `string.reverse_string(text)` - Reverse a string

## Project Structure

```
tool_enhanced_reasoning/
├── main.py                 # Main script with LLM integration
├── tools/
│   ├── math_tools.py      # Mathematical operations
│   └── string_tools.py    # String analysis functions
├── README.md              # This file
├── requirements.txt       # Python dependencies
└── .env.example          # Environment variables template
```

## Error Handling

The script includes comprehensive error handling for:
- Missing API keys
- Invalid tool calls
- Mathematical errors (division by zero, negative square roots)
- Network issues with OpenAI API
- Malformed queries

## Limitations

- Uses simple string parsing for tool calls (production systems would use more robust parsing)
- Limited to predefined tools (extensible architecture allows easy addition of new tools)
- Requires OpenAI API access (could be adapted for other LLM providers)

## Extending the System

To add new tools:

1. Create a new tool module in the `tools/` directory
2. Follow the same pattern as `math_tools.py` or `string_tools.py`
3. Register tools in the `TOOL_REGISTRY` dictionary
4. Update the tool descriptions in `main.py`

## License

This project is for educational purposes as part of the MISOGI Week 3 Day 2 assignment.
