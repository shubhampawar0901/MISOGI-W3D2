"""Visualization module for model comparison results."""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
from rich.console import Console
from rich.table import Table

from providers.base import ModelResponse
from config import Config


class Visualizer:
    """Handles visualization of model comparison results."""
    
    def __init__(self, config: Config):
        """Initialize visualizer with configuration."""
        self.config = config
        self.console = Console()
        
        # Set up matplotlib style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Create output directory if needed
        if self.config.should_save_plots():
            output_dir = Path(self.config.get_plot_output_dir())
            output_dir.mkdir(exist_ok=True)
    
    def create_comparison_visualization(self, responses: List[ModelResponse]):
        """Create comprehensive visualization of model comparison."""
        if not responses:
            self.console.print("[yellow]No responses to visualize.[/yellow]")
            return
        
        # Create DataFrame for easier manipulation
        df = self._responses_to_dataframe(responses)
        
        # Create visualizations
        self._create_response_time_chart(df)
        self._create_token_usage_chart(df)
        self._create_context_window_chart(df)
        self._create_summary_table(responses)
        
        if self.config.should_save_plots():
            self.console.print(f"[green]Plots saved to {self.config.get_plot_output_dir()}[/green]")
        else:
            plt.show()
    
    def _responses_to_dataframe(self, responses: List[ModelResponse]) -> pd.DataFrame:
        """Convert responses to pandas DataFrame."""
        data = []
        
        for response in responses:
            data.append({
                'provider': response.provider,
                'model_name': response.model_name,
                'model_type': response.model_type,
                'response_time': response.response_time,
                'prompt_tokens': response.token_usage['prompt_tokens'],
                'completion_tokens': response.token_usage['completion_tokens'],
                'total_tokens': response.token_usage['total_tokens'],
                'context_window': response.context_window,
                'content_length': len(response.content),
                'has_error': 'error' in response.metadata
            })
        
        return pd.DataFrame(data)
    
    def _create_response_time_chart(self, df: pd.DataFrame):
        """Create response time comparison chart."""
        plt.figure(figsize=(12, 6))
        
        # Create subplot for response times
        plt.subplot(1, 2, 1)
        sns.barplot(data=df, x='provider', y='response_time', hue='model_type')
        plt.title('Response Time by Provider and Model Type')
        plt.ylabel('Response Time (seconds)')
        plt.xticks(rotation=45)
        plt.legend(title='Model Type')
        
        # Create subplot for response time distribution
        plt.subplot(1, 2, 2)
        sns.boxplot(data=df, x='provider', y='response_time')
        plt.title('Response Time Distribution by Provider')
        plt.ylabel('Response Time (seconds)')
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        if self.config.should_save_plots():
            plt.savefig(f"{self.config.get_plot_output_dir()}/response_times.png", dpi=300, bbox_inches='tight')
            plt.close()
    
    def _create_token_usage_chart(self, df: pd.DataFrame):
        """Create token usage comparison chart."""
        plt.figure(figsize=(15, 8))
        
        # Stacked bar chart for token usage
        plt.subplot(2, 2, 1)
        models = df['model_name'].tolist()
        prompt_tokens = df['prompt_tokens'].tolist()
        completion_tokens = df['completion_tokens'].tolist()
        
        x = np.arange(len(models))
        width = 0.6
        
        plt.bar(x, prompt_tokens, width, label='Prompt Tokens', alpha=0.8)
        plt.bar(x, completion_tokens, width, bottom=prompt_tokens, label='Completion Tokens', alpha=0.8)
        
        plt.xlabel('Models')
        plt.ylabel('Token Count')
        plt.title('Token Usage by Model')
        plt.xticks(x, models, rotation=45, ha='right')
        plt.legend()
        
        # Token efficiency (tokens per second)
        plt.subplot(2, 2, 2)
        df['tokens_per_second'] = df['total_tokens'] / df['response_time']
        sns.barplot(data=df, x='provider', y='tokens_per_second', hue='model_type')
        plt.title('Token Generation Efficiency')
        plt.ylabel('Tokens per Second')
        plt.xticks(rotation=45)
        plt.legend(title='Model Type')
        
        # Content length vs tokens
        plt.subplot(2, 2, 3)
        plt.scatter(df['content_length'], df['total_tokens'], 
                   c=df['provider'].astype('category').cat.codes, alpha=0.7)
        plt.xlabel('Content Length (characters)')
        plt.ylabel('Total Tokens')
        plt.title('Content Length vs Token Usage')
        
        # Add provider legend
        providers = df['provider'].unique()
        for i, provider in enumerate(providers):
            plt.scatter([], [], c=plt.cm.tab10(i), label=provider)
        plt.legend(title='Provider')
        
        # Token usage by model type
        plt.subplot(2, 2, 4)
        sns.boxplot(data=df, x='model_type', y='total_tokens')
        plt.title('Token Usage Distribution by Model Type')
        plt.ylabel('Total Tokens')
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        if self.config.should_save_plots():
            plt.savefig(f"{self.config.get_plot_output_dir()}/token_usage.png", dpi=300, bbox_inches='tight')
            plt.close()
    
    def _create_context_window_chart(self, df: pd.DataFrame):
        """Create context window comparison chart."""
        plt.figure(figsize=(10, 6))
        
        # Context window comparison
        plt.subplot(1, 2, 1)
        sns.barplot(data=df, x='provider', y='context_window', hue='model_type')
        plt.title('Context Window Size by Provider')
        plt.ylabel('Context Window (tokens)')
        plt.yscale('log')  # Log scale for better visualization
        plt.xticks(rotation=45)
        plt.legend(title='Model Type')
        
        # Context utilization (tokens used vs available)
        plt.subplot(1, 2, 2)
        df['context_utilization'] = (df['total_tokens'] / df['context_window']) * 100
        sns.barplot(data=df, x='provider', y='context_utilization', hue='model_type')
        plt.title('Context Window Utilization (%)')
        plt.ylabel('Utilization Percentage')
        plt.xticks(rotation=45)
        plt.legend(title='Model Type')
        
        plt.tight_layout()
        
        if self.config.should_save_plots():
            plt.savefig(f"{self.config.get_plot_output_dir()}/context_windows.png", dpi=300, bbox_inches='tight')
            plt.close()
    
    def _create_summary_table(self, responses: List[ModelResponse]):
        """Create a summary table of results."""
        table = Table(title="Model Comparison Summary")
        
        table.add_column("Provider", style="cyan")
        table.add_column("Model", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Response Time", style="blue")
        table.add_column("Tokens", style="magenta")
        table.add_column("Context Window", style="red")
        table.add_column("Status", style="white")
        
        for response in responses:
            status = "✓ Success" if 'error' not in response.metadata else "✗ Error"
            status_style = "green" if 'error' not in response.metadata else "red"
            
            table.add_row(
                response.provider.title(),
                response.model_name,
                response.model_type.title(),
                f"{response.response_time:.2f}s",
                str(response.token_usage['total_tokens']),
                f"{response.context_window:,}",
                f"[{status_style}]{status}[/{status_style}]"
            )
        
        self.console.print(table)
    
    def create_performance_comparison(self, responses: List[ModelResponse]):
        """Create a focused performance comparison."""
        if not responses:
            return
        
        df = self._responses_to_dataframe(responses)
        
        # Calculate performance metrics
        performance_metrics = []
        for _, row in df.iterrows():
            metrics = {
                'model': f"{row['provider']}/{row['model_name']}",
                'speed_score': 1 / row['response_time'],  # Higher is better
                'efficiency_score': row['total_tokens'] / row['response_time'],  # Tokens per second
                'context_efficiency': row['context_window'] / 1000,  # Normalized context window
                'overall_score': 0  # Will be calculated
            }
            
            # Calculate overall score (normalized)
            metrics['overall_score'] = (
                (metrics['speed_score'] * 0.4) +
                (metrics['efficiency_score'] * 0.4) +
                (metrics['context_efficiency'] * 0.2)
            )
            
            performance_metrics.append(metrics)
        
        # Create performance DataFrame
        perf_df = pd.DataFrame(performance_metrics)
        
        # Visualize performance comparison
        plt.figure(figsize=(12, 8))
        
        # Overall performance ranking
        plt.subplot(2, 2, 1)
        perf_df_sorted = perf_df.sort_values('overall_score', ascending=True)
        plt.barh(perf_df_sorted['model'], perf_df_sorted['overall_score'])
        plt.title('Overall Performance Ranking')
        plt.xlabel('Performance Score')
        
        # Speed vs Efficiency scatter
        plt.subplot(2, 2, 2)
        plt.scatter(perf_df['speed_score'], perf_df['efficiency_score'], alpha=0.7)
        for i, model in enumerate(perf_df['model']):
            plt.annotate(model.split('/')[-1], 
                        (perf_df.iloc[i]['speed_score'], perf_df.iloc[i]['efficiency_score']),
                        fontsize=8, alpha=0.7)
        plt.xlabel('Speed Score')
        plt.ylabel('Efficiency Score')
        plt.title('Speed vs Efficiency')
        
        plt.tight_layout()
        
        if self.config.should_save_plots():
            plt.savefig(f"{self.config.get_plot_output_dir()}/performance_comparison.png", dpi=300, bbox_inches='tight')
            plt.close()
        
        return perf_df
