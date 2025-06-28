# Contributing to TestBase Research

We welcome contributions to TestBase Research! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Issues

1. Check if the issue already exists
2. Create a new issue with:
   - Clear title and description
   - Steps to reproduce (if applicable)
   - Expected vs actual behavior
   - System information (Python version, OS)

### Suggesting Enhancements

1. Open an issue with the "enhancement" label
2. Describe the feature and its benefits
3. Provide use cases and examples

### Code Contributions

1. **Fork the repository**
2. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes:**
   - Follow the existing code style
   - Add docstrings to functions
   - Include type hints where appropriate
   - Update documentation if needed

4. **Test your changes:**
   ```bash
   python -m pytest tests/  # if tests exist
   ```

5. **Commit with clear messages:**
   ```bash
   git commit -m "Add: feature description"
   ```

6. **Push and create a Pull Request**

## Code Style Guidelines

- Follow PEP 8
- Use meaningful variable names
- Add comments for complex logic
- Keep functions focused and small

## Documentation

- Update README.md for new features
- Add docstrings using Google style:
  ```python
  def function(param1: str, param2: int) -> dict:
      """Brief description.
      
      Args:
          param1: Description of param1
          param2: Description of param2
          
      Returns:
          Description of return value
      """
  ```

## Testing

- Add tests for new features
- Ensure existing tests pass
- Test with different Python versions (3.7+)

## Pull Request Process

1. Update documentation
2. Add your changes to CHANGELOG.md (if exists)
3. Ensure all tests pass
4. Request review from maintainers

## Questions?

Feel free to open an issue for any questions about contributing!

Thank you for contributing to TestBase Research! 🎉