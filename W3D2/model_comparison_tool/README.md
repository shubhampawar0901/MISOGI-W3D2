# Model Comparison Tool

A comprehensive command-line tool for comparing Base, Instruct, and Fine-tuned AI models from popular providers (OpenAI, Anthropic, and Hugging Face).

## Features

- 🔄 **Multi-Provider Support**: Compare models from OpenAI, Anthropic, and Hugging Face
- 🎯 **Model Type Comparison**: Base, Instruct, and Fine-tuned models
- 📊 **Detailed Analytics**: Token usage, response time, and context window analysis
- 📈 **Visualization**: Interactive charts and performance comparisons
- 🖥️ **Interactive CLI**: User-friendly command-line interface
- ⚡ **Concurrent Processing**: Parallel API calls for faster comparisons
- 📝 **Comprehensive Logging**: Detailed comparison reports

## Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd model_comparison_tool
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env file with your API keys
   ```

## Configuration

### API Keys

Add your API keys to the `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
```

### Model Configuration

Customize available models and settings in `config.yaml`:

```yaml
providers:
  openai:
    instruct_models:
      - name: "gpt-4"
        description: "GPT-4 with instruction following capabilities"
        context_window: 8192
        available: true
```

## Usage

### Interactive Mode

Run the tool in interactive mode for guided usage:

```bash
python main.py --interactive
```

### Single Query Mode

Compare models with a specific query:

```bash
python main.py --query "Explain quantum computing" --model-type instruct --provider openai
```

### Command-Line Options

```bash
python main.py [OPTIONS]

Options:
  -q, --query TEXT          Query to send to the models
  -t, --model-type CHOICE   Model type: base, instruct, fine-tuned, all
  -p, --provider CHOICE     Provider: openai, anthropic, huggingface, all
  -i, --interactive         Run in interactive mode
  -v, --visualize          Show token usage and context window visualization
  --config PATH            Path to configuration file (default: config.yaml)
```

### Examples

1. **Compare all available models**:
   ```bash
   python main.py --query "Write a short poem about AI" --model-type all --provider all
   ```

2. **Compare only instruction-tuned models from OpenAI**:
   ```bash
   python main.py --query "Explain machine learning" --model-type instruct --provider openai
   ```

3. **Interactive mode with visualization**:
   ```bash
   python main.py --interactive --visualize
   ```

## Model Types Explained

### Base Models
- **Description**: Pre-trained models without instruction tuning
- **Characteristics**: Raw language modeling capabilities
- **Use Cases**: Text completion, creative writing, research
- **Availability**: Limited public access

### Instruct Models
- **Description**: Models fine-tuned to follow instructions
- **Characteristics**: Better at following user commands and structured responses
- **Use Cases**: Q&A, task completion, conversational AI
- **Availability**: Widely available through APIs

### Fine-tuned Models
- **Description**: Models customized for specific tasks or domains
- **Characteristics**: Specialized performance for particular use cases
- **Use Cases**: Domain-specific applications, custom workflows
- **Availability**: User-specific or specialized models

## Output Format

The tool provides detailed output including:

- **Model Response**: The actual generated text
- **Performance Metrics**: Response time, token usage
- **Model Information**: Context window, model type, provider
- **Comparison Summary**: Aggregate statistics and rankings

### Sample Output

```
┌─ OpenAI - gpt-4 (instruct) ─────────────────────────────────────┐
│ Quantum computing is a revolutionary approach to computation... │
│                                                                 │
│ Response Time: 2.34s                                           │
│ Tokens: 156 (prompt: 12, completion: 144)                     │
│ Context Window: 8,192                                          │
└─────────────────────────────────────────────────────────────────┘
```

## Visualization Features

When using the `--visualize` flag, the tool generates:

1. **Response Time Charts**: Compare speed across models
2. **Token Usage Analysis**: Prompt vs completion tokens
3. **Context Window Utilization**: Efficiency metrics
4. **Performance Rankings**: Overall model comparison

## Project Structure

```
model_comparison_tool/
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── config.yaml            # Configuration
├── .env.example           # Environment template
├── src/
│   ├── __init__.py
│   ├── cli.py             # Command-line interface
│   ├── config.py          # Configuration management
│   ├── model_manager.py   # Model coordination
│   ├── visualization.py   # Charts and graphs
│   └── providers/
│       ├── __init__.py
│       ├── base.py        # Provider interface
│       ├── openai_provider.py
│       ├── anthropic_provider.py
│       └── huggingface_provider.py
├── comparisons.md         # Sample comparisons
└── README.md             # This file
```

## Troubleshooting

### Common Issues

1. **API Key Errors**:
   - Verify API keys in `.env` file
   - Check API key permissions and quotas

2. **Model Availability**:
   - Some base models may not be publicly available
   - Fine-tuned models require specific access

3. **Rate Limiting**:
   - Reduce concurrent requests in config
   - Add delays between API calls

4. **Memory Issues**:
   - Use API mode instead of local models for Hugging Face
   - Reduce batch sizes for large comparisons

### Getting Help

- Check the `comparisons.md` file for example outputs
- Review configuration in `config.yaml`
- Enable debug logging for detailed error information

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Requirements

- Python 3.8+
- API keys for desired providers
- Internet connection for API calls
- Optional: CUDA for local Hugging Face models

## Performance Notes

- API calls are made concurrently for faster comparisons
- Local model loading may require significant memory
- Response times vary by provider and model size
- Token usage affects API costs

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for GPT models and API
- Anthropic for Claude models and API
- Hugging Face for open-source models and transformers library
- Rich library for beautiful terminal output
