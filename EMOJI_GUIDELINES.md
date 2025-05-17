# Documentation Emoji Guidelines

## ✅ Safe to Use Emojis
- **Markdown files** (.md): README, TODO, CHANGELOG, guides
- **Documentation comments**: Docstrings in Python files
- **Log files**: Generated logs (already created as markdown)
- **User notes**: Context summaries, session notes

## ❌ Avoid Emojis
- **Print statements**: Any `print()` calls in Python code
- **Console output**: Error messages, status updates
- **Return strings**: Tool function return values
- **Exception messages**: Error handling text

## Examples

### ✅ Good - In Markdown Documentation
```markdown
# Project Features

## 🚀 Quick Start
1. **Install dependencies** 📦
2. **Configure project** ⚙️
3. **Run server** 🏃‍♂️

### 🛡️ Safety Features
- ✅ Safe file operations
- ⚠️ Manual delete confirmation
```

### ✅ Good - In Docstrings
```python
def create_project(name: str) -> str:
    """
    Create a new project 🎉
    
    Features:
    - 📁 Auto-generated structure
    - 🔧 Configurable templates
    - 🚀 Ready to run
    """
    return f"Project {name} created successfully"  # No emoji here
```

### ❌ Bad - In Print Statements
```python
# DON'T DO THIS - Will cause encoding errors
print("✅ Project created successfully")
print("⚠️ Warning: Configuration not found")

# DO THIS INSTEAD
print("SUCCESS: Project created successfully")
print("WARNING: Configuration not found")
```

## Implementation Strategy

1. **Keep all existing code emoji-free** (already done)
2. **Use emojis freely in documentation**
3. **Consider adding emoji support for user-facing content**

## Optional: Emoji-Safe Output Function

If you want emojis in output but safe fallbacks:

```python
def safe_print(message: str, fallback: str = None):
    """Print with emoji fallback for encoding issues"""
    try:
        print(message)
    except UnicodeEncodeError:
        print(fallback or message.encode('ascii', 'ignore').decode())

# Usage:
safe_print("✅ Success!", "SUCCESS: Success!")
```
