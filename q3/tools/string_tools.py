"""
String tools for the tool-enhanced reasoning script.
Provides string analysis operations that can be called by the LLM.
"""

import re
from typing import List, Dict, Union


def count_vowels(text: str, include_y: bool = False) -> int:
    """Count the number of vowels in a text."""
    vowels = "aeiouAEIOU"
    if include_y:
        vowels += "yY"
    
    return sum(1 for char in text if char in vowels)


def count_consonants(text: str, include_y: bool = True) -> int:
    """Count the number of consonants in a text."""
    vowels = "aeiouAEIOU"
    if not include_y:
        vowels += "yY"
    
    return sum(1 for char in text if char.isalpha() and char not in vowels)


def count_letters(text: str) -> int:
    """Count the number of letters (alphabetic characters) in a text."""
    return sum(1 for char in text if char.isalpha())


def count_words(text: str) -> int:
    """Count the number of words in a text."""
    return len(text.split())


def count_sentences(text: str) -> int:
    """Count the number of sentences in a text."""
    # Simple sentence counting based on sentence-ending punctuation
    sentence_endings = re.findall(r'[.!?]+', text)
    return len(sentence_endings)


def count_characters(text: str, include_spaces: bool = True) -> int:
    """Count the total number of characters in a text."""
    if include_spaces:
        return len(text)
    else:
        return len(text.replace(" ", ""))


def count_specific_character(text: str, character: str) -> int:
    """Count occurrences of a specific character in a text."""
    return text.count(character)


def count_uppercase_letters(text: str) -> int:
    """Count the number of uppercase letters in a text."""
    return sum(1 for char in text if char.isupper())


def count_lowercase_letters(text: str) -> int:
    """Count the number of lowercase letters in a text."""
    return sum(1 for char in text if char.islower())


def count_digits(text: str) -> int:
    """Count the number of digits in a text."""
    return sum(1 for char in text if char.isdigit())


def get_word_lengths(text: str) -> List[int]:
    """Get the length of each word in a text."""
    words = text.split()
    return [len(word.strip('.,!?;:"()[]{}')) for word in words]


def get_average_word_length(text: str) -> float:
    """Calculate the average word length in a text."""
    word_lengths = get_word_lengths(text)
    if not word_lengths:
        return 0.0
    return sum(word_lengths) / len(word_lengths)


def find_longest_word(text: str) -> str:
    """Find the longest word in a text."""
    words = text.split()
    if not words:
        return ""
    
    # Remove punctuation for length comparison
    clean_words = [word.strip('.,!?;:"()[]{}') for word in words]
    longest = max(clean_words, key=len)
    return longest


def find_shortest_word(text: str) -> str:
    """Find the shortest word in a text."""
    words = text.split()
    if not words:
        return ""
    
    # Remove punctuation for length comparison
    clean_words = [word.strip('.,!?;:"()[]{}') for word in words if word.strip('.,!?;:"()[]{}')]
    if not clean_words:
        return ""
    
    shortest = min(clean_words, key=len)
    return shortest


def count_unique_words(text: str, case_sensitive: bool = False) -> int:
    """Count the number of unique words in a text."""
    words = text.split()
    clean_words = [word.strip('.,!?;:"()[]{}') for word in words]
    
    if not case_sensitive:
        clean_words = [word.lower() for word in clean_words]
    
    return len(set(clean_words))


def get_character_frequency(text: str) -> Dict[str, int]:
    """Get the frequency of each character in a text."""
    frequency = {}
    for char in text:
        frequency[char] = frequency.get(char, 0) + 1
    return frequency


def is_palindrome(text: str, ignore_case: bool = True, ignore_spaces: bool = True) -> bool:
    """Check if a text is a palindrome."""
    processed_text = text
    
    if ignore_spaces:
        processed_text = processed_text.replace(" ", "")
    
    if ignore_case:
        processed_text = processed_text.lower()
    
    return processed_text == processed_text[::-1]


def reverse_string(text: str) -> str:
    """Reverse a string."""
    return text[::-1]


def count_substring(text: str, substring: str, case_sensitive: bool = True) -> int:
    """Count occurrences of a substring in a text."""
    if not case_sensitive:
        text = text.lower()
        substring = substring.lower()
    
    return text.count(substring)


def extract_numbers(text: str) -> List[float]:
    """Extract all numbers from a text."""
    # Find all numbers (including decimals)
    number_pattern = r'-?\d+\.?\d*'
    matches = re.findall(number_pattern, text)
    
    numbers = []
    for match in matches:
        try:
            if '.' in match:
                numbers.append(float(match))
            else:
                numbers.append(float(match))
        except ValueError:
            continue
    
    return numbers


# Tool registry for easy access
STRING_TOOLS = {
    "count_vowels": count_vowels,
    "count_consonants": count_consonants,
    "count_letters": count_letters,
    "count_words": count_words,
    "count_sentences": count_sentences,
    "count_characters": count_characters,
    "count_specific_character": count_specific_character,
    "count_uppercase_letters": count_uppercase_letters,
    "count_lowercase_letters": count_lowercase_letters,
    "count_digits": count_digits,
    "get_word_lengths": get_word_lengths,
    "get_average_word_length": get_average_word_length,
    "find_longest_word": find_longest_word,
    "find_shortest_word": find_shortest_word,
    "count_unique_words": count_unique_words,
    "get_character_frequency": get_character_frequency,
    "is_palindrome": is_palindrome,
    "reverse_string": reverse_string,
    "count_substring": count_substring,
    "extract_numbers": extract_numbers
}


def get_available_tools() -> List[str]:
    """Get a list of available string tools."""
    return list(STRING_TOOLS.keys())


def call_tool(tool_name: str, *args, **kwargs) -> Union[int, float, str, List, Dict, bool]:
    """Call a string tool by name with given arguments."""
    if tool_name not in STRING_TOOLS:
        raise ValueError(f"Unknown string tool: {tool_name}")
    
    try:
        return STRING_TOOLS[tool_name](*args, **kwargs)
    except Exception as e:
        raise ValueError(f"Error calling {tool_name}: {e}")
