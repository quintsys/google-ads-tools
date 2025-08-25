# Contributing to Google Ads Management Tools

Thank you for your interest in contributing to this project! This toolkit helps manage Google Ads campaigns through a comprehensive set of Python and shell tools.

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Google Ads API access and developer token
- Git and GitHub account

### Setup Development Environment
```bash
# Clone the repository
git clone https://github.com/quintsys/google-ads-tools.git
cd google-ads-tools

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure Google Ads API (see auth/README.md for details)
```

## 📁 Project Structure

The project is organized into functional categories:
- `auth/` - Authentication and account discovery
- `audit/` - Campaign auditing and compliance
- `analysis/` - Data analysis and reporting
- `recovery/` - Asset recovery and migration
- `data-processing/` - Data transformation utilities

## 🤝 How to Contribute

### Reporting Issues
1. Check existing issues to avoid duplicates
2. Use the issue template when available
3. Provide detailed reproduction steps
4. Include error messages and environment details

### Suggesting Features
1. Open an issue describing the feature
2. Explain the use case and benefits
3. Consider backward compatibility
4. Be prepared to implement or help implement

### Contributing Code

#### Before You Start
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Follow the coding standards below

#### Coding Standards

**Python Code:**
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Include docstrings for functions and classes
- Handle errors gracefully with meaningful messages
- Support dry-run mode for operations that modify data

**Command Line Interface:**
- Use consistent argument naming across tools
- Provide helpful descriptions for all arguments
- Include usage examples in docstrings
- Support common patterns (--dry-run, --customer-id, etc.)

**Documentation:**
- Update relevant README files
- Include usage examples
- Document any new dependencies
- Add troubleshooting information

#### Tool Development Guidelines

**Safety First:**
- Always include dry-run capabilities for destructive operations
- Validate inputs before making API calls
- Provide clear error messages with suggested solutions
- Include appropriate warnings for potentially dangerous operations

**API Integration:**
- Use the established Google Ads client patterns
- Handle rate limiting appropriately
- Include proper error handling for API exceptions
- Test with both MCC and individual account scenarios

**User Experience:**
- Provide progress indicators for long operations
- Use consistent output formatting
- Include helpful statistics and summaries
- Support both console and CSV output where appropriate

#### Adding New Tools

When adding a new tool:

1. **Choose the Right Category:** Place it in the appropriate folder (auth, audit, analysis, recovery, data-processing)

2. **Follow Naming Conventions:** Use descriptive names that clearly indicate purpose

3. **Include Standard Features:**
   ```python
   import argparse
   from google.ads.googleads.client import GoogleAdsClient
   
   def main():
       parser = argparse.ArgumentParser(description="Tool description")
       parser.add_argument("--customer-id", required=True, help="Customer ID (without dashes)")
       parser.add_argument("--dry-run", action="store_true", help="Preview changes without executing")
       # ... other arguments
       args = parser.parse_args()
       
       try:
           client = GoogleAdsClient.load_from_storage()
           # ... implementation
       except Exception as e:
           print(f"Error: {e}", file=sys.stderr)
           sys.exit(1)
   ```

4. **Update Documentation:**
   - Add tool description to main README.md
   - Update the appropriate folder README.md
   - Include usage examples and common workflows

5. **Test Thoroughly:**
   - Test with both valid and invalid inputs
   - Test dry-run mode
   - Test error conditions
   - Test with different account types (MCC vs individual)

### Testing

**Manual Testing:**
- Test with non-production accounts when possible
- Verify dry-run mode works correctly
- Test error handling with invalid inputs
- Validate output formats are correct

**Integration Testing:**
- Test tool interactions and workflows
- Verify CSV input/output compatibility
- Test with different API versions

### Pull Request Process

1. **Before Submitting:**
   - Ensure all tests pass
   - Update documentation
   - Follow commit message conventions
   - Rebase on latest main branch

2. **Commit Messages:**
   Use descriptive commit messages:
   ```
   Add UTM parameter validation to ads audit tool
   
   - Support exact value and regex pattern matching
   - Add case enforcement options
   - Include auto-tagging bypass for gclid
   - Update documentation with examples
   ```

3. **Pull Request Description:**
   - Describe what changes were made and why
   - Include testing performed
   - Reference any related issues
   - Provide usage examples for new features

## 🔍 Code Review Guidelines

**For Reviewers:**
- Check for security issues (credential handling, input validation)
- Verify documentation is updated
- Test dry-run functionality
- Ensure error handling is appropriate
- Validate backward compatibility

**For Contributors:**
- Be responsive to feedback
- Test suggested changes
- Update documentation as requested
- Explain design decisions when asked

## 🎯 Areas for Contribution

**High Priority:**
- Additional audit checks and validations
- Enhanced error handling and user feedback
- Performance optimizations for large accounts
- Additional data export formats

**Medium Priority:**
- Additional geographic expansion options
- More sophisticated keyword analysis
- Integration with other Google Ads tools
- Automated testing framework

**Nice to Have:**
- Web interface for common operations
- Configuration file support
- Batch processing capabilities
- Integration with Google Ads scripts

## ❓ Questions and Support

- **Documentation Questions:** Check folder-specific README files
- **Usage Questions:** Open an issue with the "question" label  
- **Bug Reports:** Use the bug report template
- **Feature Requests:** Open an issue with detailed use case

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

---

Thank you for helping make this toolkit better for the Google Ads community! 🚀