# Contributing to Xalora AI Interview System

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## 🤝 How to Contribute

### Reporting Bugs
1. Check if the bug has already been reported in Issues
2. Create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable
   - Environment details (OS, Python version, etc.)

### Suggesting Features
1. Check if the feature has been suggested
2. Create a new issue with:
   - Clear description of the feature
   - Use cases and benefits
   - Possible implementation approach

### Pull Requests
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes
4. Test thoroughly
5. Commit with clear messages (`git commit -m 'Add some AmazingFeature'`)
6. Push to your branch (`git push origin feature/AmazingFeature`)
7. Open a Pull Request

## 📝 Development Guidelines

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and small
- Comment complex logic

### Testing
- Test your changes locally
- Ensure all existing tests pass
- Add tests for new features
- Test with different scenarios

### Commit Messages
- Use present tense ("Add feature" not "Added feature")
- Be descriptive but concise
- Reference issues when applicable

## 🏗️ Project Structure

```
xalora-ai-interview/
├── app.py                  # Main application
├── voice_service.py        # Voice features
├── agents/                 # AI interview agents
├── static/                 # Frontend files
├── database/               # Session storage
└── cache/                  # Response cache
```

## 🧪 Testing

Run tests before submitting:
```bash
python test_system.py
```

## 📚 Documentation

- Update README.md for user-facing changes
- Add inline comments for complex code
- Update docstrings when modifying functions

## ✅ Checklist Before Submitting PR

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] No unnecessary files included
- [ ] .env not committed

## 🎯 Areas for Contribution

### High Priority
- Multi-language support
- Mobile responsiveness
- Performance optimization
- Additional voice providers

### Medium Priority
- Video interview capability
- Real-time feedback
- Analytics dashboard
- Custom question banks

### Low Priority
- UI/UX improvements
- Additional themes
- Export formats
- Integration with other tools

## 💬 Questions?

Feel free to:
- Open an issue for discussion
- Ask in pull request comments
- Contact maintainers

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🎉
