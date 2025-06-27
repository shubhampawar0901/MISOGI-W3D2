"""Command-line interface for the model comparison tool."""

import sys
from typing import Dict, List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text

from config import Config
from model_manager import ModelManager
from visualization import Visualizer


class ModelComparisonCLI:
    """Command-line interface for model comparison."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the CLI with configuration."""
        self.console = Console()
        self.config = Config(config_path)
        self.model_manager = ModelManager(self.config)
        self.visualizer = Visualizer(self.config)
    
    def run_interactive(self):
        """Run the tool in interactive mode."""
        self.console.print(Panel.fit(
            "[bold blue]Model Comparison Tool[/bold blue]\n"
            "Compare AI models from OpenAI, Anthropic, and Hugging Face",
            title="Welcome"
        ))
        
        # Validate API keys
        self._check_api_keys()
        
        while True:
            try:
                # Get user query
                query = Prompt.ask("\n[bold green]Enter your query[/bold green]")
                if not query.strip():
                    continue
                
                # Get model selection preferences
                provider = self._select_provider()
                model_type = self._select_model_type()
                
                # Show visualization option
                visualize = Confirm.ask("Show visualization?", default=True)
                
                # Run comparison
                self.run_single_query(query, model_type, provider, visualize)
                
                # Ask if user wants to continue
                if not Confirm.ask("\nRun another comparison?", default=True):
                    break
                    
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Goodbye![/yellow]")
                break
            except Exception as e:
                self.console.print(f"[red]Error: {str(e)}[/red]")
    
    def run_single_query(
        self,
        query: str,
        model_type: str = "all",
        provider: str = "all",
        visualize: bool = False
    ):
        """Run a single query comparison."""
        self.console.print(f"\n[bold]Query:[/bold] {query}")
        self.console.print(f"[bold]Model Type:[/bold] {model_type}")
        self.console.print(f"[bold]Provider:[/bold] {provider}")
        
        # Get responses from models
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Generating responses...", total=None)
            
            responses = self.model_manager.compare_models(
                query=query,
                model_type=model_type,
                provider=provider
            )
            
            progress.update(task, completed=True)
        
        # Display results
        self._display_responses(responses)
        
        # Show visualization if requested
        if visualize and responses:
            self.visualizer.create_comparison_visualization(responses)
    
    def _check_api_keys(self):
        """Check and display API key validation status."""
        validation_results = self.config.validate_api_keys()
        
        table = Table(title="API Key Status")
        table.add_column("Provider", style="cyan")
        table.add_column("Status", style="green")
        
        for provider, is_valid in validation_results.items():
            status = "✓ Valid" if is_valid else "✗ Missing/Invalid"
            style = "green" if is_valid else "red"
            table.add_row(provider.title(), f"[{style}]{status}[/{style}]")
        
        self.console.print(table)
        
        # Warn if no API keys are valid
        if not any(validation_results.values()):
            self.console.print(
                "[red]Warning: No valid API keys found. "
                "Please check your .env file or environment variables.[/red]"
            )
    
    def _select_provider(self) -> str:
        """Interactive provider selection."""
        providers = ["all", "openai", "anthropic", "huggingface"]
        
        self.console.print("\n[bold]Available Providers:[/bold]")
        for i, provider in enumerate(providers, 1):
            self.console.print(f"  {i}. {provider.title()}")
        
        while True:
            try:
                choice = Prompt.ask(
                    "Select provider",
                    choices=[str(i) for i in range(1, len(providers) + 1)],
                    default="1"
                )
                return providers[int(choice) - 1]
            except (ValueError, IndexError):
                self.console.print("[red]Invalid choice. Please try again.[/red]")
    
    def _select_model_type(self) -> str:
        """Interactive model type selection."""
        model_types = ["all", "base", "instruct", "fine_tuned"]
        
        self.console.print("\n[bold]Available Model Types:[/bold]")
        for i, model_type in enumerate(model_types, 1):
            description = {
                "all": "Compare all available model types",
                "base": "Base models (pre-training only)",
                "instruct": "Instruction-tuned models",
                "fine_tuned": "Fine-tuned models"
            }
            self.console.print(f"  {i}. {model_type.title()} - {description[model_type]}")
        
        while True:
            try:
                choice = Prompt.ask(
                    "Select model type",
                    choices=[str(i) for i in range(1, len(model_types) + 1)],
                    default="1"
                )
                return model_types[int(choice) - 1]
            except (ValueError, IndexError):
                self.console.print("[red]Invalid choice. Please try again.[/red]")
    
    def _display_responses(self, responses: List):
        """Display model responses in a formatted table."""
        if not responses:
            self.console.print("[yellow]No responses generated.[/yellow]")
            return
        
        for response in responses:
            # Create a panel for each response
            title = f"{response.provider.title()} - {response.model_name} ({response.model_type})"
            
            # Prepare metadata
            metadata_text = (
                f"Response Time: {response.response_time:.2f}s\n"
                f"Tokens: {response.token_usage['total_tokens']} "
                f"(prompt: {response.token_usage['prompt_tokens']}, "
                f"completion: {response.token_usage['completion_tokens']})\n"
                f"Context Window: {response.context_window:,}"
            )
            
            # Create content with metadata
            content = f"{response.content}\n\n[dim]{metadata_text}[/dim]"
            
            panel = Panel(
                content,
                title=title,
                border_style="blue" if "error" not in response.metadata else "red"
            )
            
            self.console.print(panel)
            self.console.print()  # Add spacing
    
    def list_available_models(self):
        """List all available models."""
        self.console.print("[bold]Available Models:[/bold]\n")
        
        for provider_name in ["openai", "anthropic", "huggingface"]:
            models = self.model_manager.get_available_models(provider_name)
            
            if models:
                table = Table(title=f"{provider_name.title()} Models")
                table.add_column("Model Name", style="cyan")
                table.add_column("Type", style="green")
                table.add_column("Context Window", style="yellow")
                table.add_column("Description", style="white")
                
                for model in models:
                    table.add_row(
                        model.name,
                        model.model_type,
                        f"{model.context_window:,}",
                        model.description
                    )
                
                self.console.print(table)
                self.console.print()
    
    def show_help(self):
        """Show help information."""
        help_text = """
[bold]Model Comparison Tool Help[/bold]

[green]Usage:[/green]
  python main.py --query "Your question" --model-type instruct --provider openai
  python main.py --interactive

[green]Model Types:[/green]
  • base: Pre-trained models without instruction tuning
  • instruct: Models fine-tuned to follow instructions
  • fine_tuned: Custom fine-tuned models

[green]Providers:[/green]
  • openai: GPT models from OpenAI
  • anthropic: Claude models from Anthropic
  • huggingface: Open-source models from Hugging Face

[green]Configuration:[/green]
  • Copy .env.example to .env and add your API keys
  • Modify config.yaml to customize model settings
        """
        
        self.console.print(Panel(help_text, title="Help", border_style="green"))
