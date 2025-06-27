#!/usr/bin/env python3
"""
Model Comparison Tool
A command-line tool for comparing Base, Instruct, and Fine-tuned models
from popular providers (OpenAI, Anthropic, Hugging Face).
"""

import argparse
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent / "src"))

from cli import ModelComparisonCLI


def main():
    """Main entry point for the model comparison tool."""
    parser = argparse.ArgumentParser(
        description="Compare AI models from different providers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --query "Explain quantum computing" --model-type instruct
  python main.py --query "Write a poem" --provider openai --model-type base
  python main.py --interactive
        """
    )
    
    parser.add_argument(
        "--query", "-q",
        type=str,
        help="Query to send to the models"
    )
    
    parser.add_argument(
        "--model-type", "-t",
        choices=["base", "instruct", "fine-tuned", "all"],
        default="all",
        help="Type of model to use (default: all)"
    )
    
    parser.add_argument(
        "--provider", "-p",
        choices=["openai", "anthropic", "huggingface", "all"],
        default="all",
        help="Model provider to use (default: all)"
    )
    
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode"
    )
    
    parser.add_argument(
        "--visualize", "-v",
        action="store_true",
        help="Show token usage and context window visualization"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to configuration file (default: config.yaml)"
    )
    
    args = parser.parse_args()
    
    # Initialize and run the CLI
    cli = ModelComparisonCLI(config_path=args.config)
    
    if args.interactive:
        cli.run_interactive()
    else:
        if not args.query:
            parser.error("--query is required when not in interactive mode")
        
        cli.run_single_query(
            query=args.query,
            model_type=args.model_type,
            provider=args.provider,
            visualize=args.visualize
        )


if __name__ == "__main__":
    main()
