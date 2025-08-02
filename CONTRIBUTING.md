# Contributing to PilotCmd

Thank you for your interest in contributing to PilotCmd! 🚁

## Development Setup

### Windows
```cmd
git clone https://github.com/mascenaa/pilotcmd.git
cd pilotcmd
setup.bat
```

### Linux/macOS
```bash
git clone https://github.com/mascenaa/pilotcmd.git
cd pilotcmd
python setup_dev.py
source venv/bin/activate
```

## Development Workflow

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Run tests**: `pytest tests/`
5. **Format code**: `black src/ tests/` and `isort src/ tests/`
6. **Commit changes**: `git commit -m 'Add amazing feature'`
7. **Push to branch**: `git push origin feature/amazing-feature`
8. **Open a Pull Request**

## Code Style

- Use **Black** for code formatting
- Use **isort** for import sorting
- Follow **PEP 8** guidelines
- Add type hints where possible
- Write docstrings for functions and classes

## Testing

- Write tests for new features
- Ensure all tests pass: `pytest tests/`
- Aim for good test coverage
- Test on multiple platforms when possible

## Areas for Contribution

- 🤖 **New AI Model Support**: Add support for new LLM providers
- 🔒 **Safety Improvements**: Enhance command validation and safety checks
- 🌐 **OS Support**: Improve cross-platform compatibility
- 📚 **Documentation**: Improve docs, examples, and tutorials
- 🧪 **Testing**: Add more comprehensive tests
- 🎨 **UI/UX**: Enhance the CLI interface and user experience
- 🔧 **Features**: Add new functionality based on user needs

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions or ideas
- Check existing issues before creating new ones

We appreciate all contributions, big and small! 🙏
