# 🚁 PilotCmd

Your AI-powered terminal copilot that converts natural language into system commands.

## ✨ Features

- 🧠 **Natural Language Processing**: Describe what you want in plain English
- 🔒 **Safety First**: Commands are validated before execution with confirmation prompts
- 🖥️ **Cross-Platform**: Works on Windows, Linux, and macOS
- 🤖 **Multiple AI Models**: Support for OpenAI GPT and local Ollama models
- 📚 **Command History**: Remembers and learns from your previous commands
- 🎨 **Rich Output**: Beautiful, colored terminal interface

## 🚀 Quick Start

### Installation

```bash
pip install pilotcmd
```

### Basic Usage

```bash
# Simple file operations
pilotcmd "list all Python files in current directory"
pilotcmd "create a new directory called 'projects'"
pilotcmd "copy all .txt files to backup folder"

# Network operations
pilotcmd "ping google.com 5 times"
pilotcmd "show my IP address"

# System information
pilotcmd "show disk usage"
pilotcmd "list running processes"

# Preview commands without executing (dry run)
pilotcmd "delete all .tmp files" --dry-run

# Use a specific AI model
pilotcmd "install docker" --model ollama
```

### Configuration

Set your OpenAI API key:
```bash
pilotcmd config --api-key YOUR_API_KEY_HERE
```

View current configuration:
```bash
pilotcmd config --show
```

### Command History

View your recent commands:
```bash
pilotcmd history

# Search in history
pilotcmd history --search "docker"

# Show more entries
pilotcmd history --limit 20
```

## 🛠️ Setup

### 1. OpenAI Setup (Recommended)

Get an API key from [OpenAI](https://platform.openai.com/api-keys) and set it:

```bash
export OPENAI_API_KEY="your-api-key-here"
# or
pilotcmd config --api-key your-api-key-here
```

### 2. Ollama Setup (Local Alternative)

1. Install [Ollama](https://ollama.ai/)
2. Pull a model: `ollama pull llama2`
3. Use with PilotCmd: `pilotcmd "your prompt" --model ollama`

## 🔧 Advanced Options

```bash
pilotcmd "your prompt" [OPTIONS]

Options:
  -m, --model TEXT     AI model to use (openai, ollama) [default: openai]
  -d, --dry-run        Show commands without executing
  -r, --run            Execute without confirmation prompts
  -v, --verbose        Enable verbose output
  --help               Show help message
```

## 🛡️ Safety Features

- **Confirmation Required**: Dangerous commands require explicit confirmation
- **Dry Run Mode**: Preview commands before execution with `--dry-run`
- **Safety Classifications**: Commands are classified as safe, caution, or dangerous
- **Command Validation**: Built-in protection against destructive operations
- **History Tracking**: All commands and results are logged locally

## 📁 Examples

### File Management
```bash
pilotcmd "find all files larger than 100MB"
pilotcmd "create a backup of my Documents folder"
pilotcmd "organize photos by date in separate folders"
```

### Development Tasks
```bash
pilotcmd "start a simple HTTP server on port 8000"
pilotcmd "find all TODO comments in Python files"
pilotcmd "check git status and show recent commits"
```

### System Administration
```bash
pilotcmd "show top 10 processes by memory usage"
pilotcmd "check available disk space on all drives"
pilotcmd "restart the nginx service"
```

### Network Operations
```bash
pilotcmd "test connection to github.com"
pilotcmd "show all open network connections"
pilotcmd "find my external IP address"
```

## 🏗️ Architecture

PilotCmd is built with a modular architecture:

- **CLI Interface**: Simple, intuitive command-line interface
- **AI Models**: Pluggable support for different LLM backends
- **NLP Parser**: Converts natural language to system commands
- **Command Executor**: Safely executes validated commands
- **Context DB**: SQLite database for history and learning
- **OS Utils**: Cross-platform command adaptation

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

PilotCmd generates and executes system commands based on your input. While we implement safety measures, always review commands before execution, especially with `--dry-run`. Use responsibly and at your own risk. 

