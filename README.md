# 🚁 PilotCmd

Your AI-powered terminal copilot that converts natural language into system commands.

## ✨ Features

- 🧠 **Natural Language Processing**: Describe what you want in plain English
- 🔒 **Safety First**: Commands are validated before execution with confirmation prompts
- 🖥️ **Cross-Platform**: Works on Windows, Linux, and macOS
- 🤖 **Multiple AI Models**: Support for OpenAI GPT and local Ollama models
- 📚 **Command History**: Remembers and learns from your previous commands
- 🎨 **Rich Output**: Beautiful, colored terminal interface
- 🧩 **Thinking Mode**: Break down complex tasks into ordered, numbered commands (uses more tokens)

## 🚀 Quick Start

### System Requirements

- Python 3.8 or higher
- pip (Python package installer)
- Terminal/Command Prompt access

### Installation

#### Option 1: Install from Source (Current)
```bash
# Clone the repository
git clone https://github.com/mascenaa/pilotcmd.git
cd pilotcmd

# Install in development mode
pip install -e .
```

#### Option 2: Direct Installation from GitHub
```bash
pip install git+https://github.com/mascenaa/pilotcmd.git
```

#### Option 3: PyPI (Coming Soon)
```bash
# This will be available once the package is published to PyPI
pip install pilotcmd
```

#### Linux
```bash
# Ubuntu/Debian - Install Python and pip if needed
sudo apt update
sudo apt install python3-pip git

# Install PilotCmd
pip3 install git+https://github.com/mascenaa/pilotcmd.git

# CentOS/RHEL/Fedora
sudo yum install python3-pip git  # or dnf install python3-pip git
pip3 install git+https://github.com/mascenaa/pilotcmd.git

# Arch Linux
sudo pacman -S python-pip git
pip install git+https://github.com/mascenaa/pilotcmd.git
```

#### macOS
```bash
# Using Homebrew (recommended)
brew install python3 git
pip3 install git+https://github.com/mascenaa/pilotcmd.git

# Using MacPorts
sudo port install py311-pip git
pip3 install git+https://github.com/mascenaa/pilotcmd.git

# Direct installation (if Python and git are already installed)
pip3 install git+https://github.com/mascenaa/pilotcmd.git
```

#### Windows
```bash
# Ensure you have Python and git installed, then:
pip install git+https://github.com/mascenaa/pilotcmd.git

# Or if you have multiple Python versions
py -m pip install git+https://github.com/mascenaa/pilotcmd.git
```

#### Virtual Environment (Recommended for all platforms)
```bash
# Linux/macOS
python3 -m venv pilotcmd-env
source pilotcmd-env/bin/activate
pip install git+https://github.com/mascenaa/pilotcmd.git

# Windows
python -m venv pilotcmd-env
pilotcmd-env\Scripts\activate
pip install git+https://github.com/mascenaa/pilotcmd.git
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
# Complex tasks with planning
pilotcmd "set up a new Python project" --thinking
```

Thinking mode returns commands labeled with step numbers so you can execute complex workflows like server setup one step at a time.

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
  --thinking           Enable multi-step planning (uses more tokens)
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

## 🧭 OS Command Mapping Matrix

PilotCmd automatically adapts commands for Linux, macOS and Windows. The table below highlights common tasks and their platform-specific equivalents along with notes on quirks:

| Task | Linux | macOS | Windows | Notes |
| --- | --- | --- | --- | --- |
| List network interfaces | `ip addr show` | `ifconfig` | `ipconfig /all` | |
| Manage firewall status | `sudo ufw status` / `sudo nft list ruleset` | `sudo pfctl -s all` | `netsh advfirewall show allprofiles` | Linux picks `ufw`, `nft`, or `iptables` if available |
| Enable firewall | `sudo ufw enable` / `sudo systemctl start nftables` | `sudo pfctl -E` | `netsh advfirewall set allprofiles state on` | |
| Start service | `systemctl start <svc>` | `launchctl start <svc>` | `sc start <svc>` | `systemctl` vs `sc` |
| Install package | `sudo apt install` / `sudo dnf install` / `sudo pacman -S` | `brew install` | `winget install` / `choco install` | Package manager auto-detected with fallbacks |

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

PilotCmd generates and executes system commands based on your input. While we implement safety measures, always review commands before execution, especially with `--dry-run`. Use responsibly and at your own risk. 

