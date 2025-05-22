# Project Manager MCP Server - Complete Guide

## Table of Contents
1. [Safety Guidelines](#safety-guidelines)
2. [Context Manager](#context-manager)
3. [Project Customization](#project-customization)
4. [Shell Command Guidelines](#shell-command-guidelines)
5. [Documentation Guidelines](#documentation-guidelines)

---

# Safety Guidelines

## Important Safety Policies

### File Operations Restrictions

This MCP server implements safety policies for file system operations to prevent accidental data loss:

#### ALLOWED Operations (Executed Immediately)
- **Read files**: Full read access to project files
- **Create files**: Create new files and directories
- **Edit files**: Modify existing file contents (with staging for locked files)
- **Stage changes**: Preview changes before applying them
- **Move files**: Execute move operations with audit logging

#### LOGGED Operations (Require Manual Execution)
- **File renaming**: Creates logs for manual review and execution
- **File deletion**: Creates logs for manual review and execution

### Safety Mechanisms

#### 1. Move Operations (`move_*_path` tools)
```
EXECUTES IMMEDIATELY with logging
```
- Performs the move operation automatically
- Creates an audit log in `logs/{project}/move_completed/`
- Prevents overwriting existing files (returns error)
- Creates destination directories as needed
- Provides detailed audit trail

#### 2. Rename Operations (`rename_*_path` tools)
```
DOES NOT ACTUALLY RENAME FILES!
```
- Creates a detailed log file in `logs/{project}/rename/`
- Includes conflict detection (destination name exists)
- Provides manual commands for execution
- Only changes filename, not directory location
- Requires manual review and execution by the user

#### 3. Delete Operations (`delete_*_path` tools)
```
DOES NOT ACTUALLY DELETE FILES!
```
- Creates a detailed log file in `logs/{project}/deletion/`
- Includes size information and backup reminders
- Provides manual commands for execution
- Requires manual review and execution by the user

#### 4. Locked File Handling
When files are open in other applications:
- Changes are automatically staged in `.staging/{project}/`
- Manual review and application required
- No forced overwrites

### Why These Policies?

1. **Balance Safety with Productivity**: Move operations are common and generally safe when preventing overwrites
2. **Audit Trail**: All operations are logged for review and accountability
3. **Human Oversight**: Destructive operations (delete) and naming changes (rename) require confirmation
4. **Conflict Prevention**: Move operations prevent accidental overwrites
5. **Reversibility**: Rename and delete operations can be reviewed before execution

### Working with Operations

#### For Move Operations:
1. Use `move_*_path` - operation executes immediately
2. Review the generated audit log
3. Move will fail if destination exists (no overwrites)
4. Operation is logged for audit purposes

#### For Rename Operations:
1. Use `rename_*_path` to create a rename log
2. Review the generated log file
3. Check for naming conflicts
4. Execute the rename manually using provided commands
5. Delete the log file after successful completion

#### For Delete Operations:
1. Use `delete_*_path` to create a deletion log
2. Review the generated log file
3. Backup if necessary
4. Execute the deletion manually using provided commands
5. Delete the log file after successful completion

#### Viewing Operations:
- `list_*_moves`: See completed moves and any legacy staged operations
- `list_*_renames`: See all staged rename operations
- `list_*_deletions`: See all staged delete operations

### Best Practices

1. **Check destination paths** before moving files
2. **Review audit logs** periodically for move operations
3. **Always review logs** before executing renames/deletions
4. **Check for conflicts** on rename operations
5. **Backup important files** before deletion
6. **Use descriptive filenames** when renaming
7. **Clean up log files** after successful execution of manual operations

### Log File Locations

```
project_root/
├── logs/
│   ├── mcp/
│   │   ├── move_completed/  # Completed move audit logs
│   │   ├── rename/          # MCP project rename logs
│   │   └── deletion/        # MCP project deletion logs
│   └── target_project/
│       ├── move_completed/  # Completed move audit logs
│       ├── rename/          # Target project rename logs
│       └── deletion/        # Target project deletion logs
└── .staging/
    ├── mcp/            # Staged MCP file changes
    └── target_project/ # Staged target project file changes
```

### Operation Types Comparison

| Operation | Execution | Log Location | Purpose | Overwrites |
|-----------|-----------|-------------|----------|------------|
| **Move** | IMMEDIATE | `/logs/{project}/move_completed/` | Change location and/or filename | NO (error if exists) |
| **Rename** | MANUAL | `/logs/{project}/rename/` | Change filename only | NO (logged if conflict) |
| **Delete** | MANUAL | `/logs/{project}/deletion/` | Remove files/directories | N/A |

### Move Operation Safety Features

- **No Overwrites**: Move fails if destination exists
- **Directory Creation**: Creates destination directories as needed
- **Audit Logging**: Every move is logged with timestamp and details
- **Error Handling**: Clear error messages for invalid operations
- **Cross-Platform**: Works consistently on Windows and Unix systems

## Remember

**The MCP server balances safety with productivity:**
- Move operations execute immediately (common workflow need) but are logged
- Destructive operations (delete) require manual confirmation
- Naming changes (rename) require manual confirmation
- All operations maintain audit trails
- No accidental overwrites are possible

When you see operations marked as "completed" vs "staged", completed operations have already been executed and logged for audit purposes.

---

# Context Manager

## Overview

The Context Manager provides intelligent session tracking and context retrieval using **local JSON storage only**. No external APIs or services required - everything stays on your machine.

## Key Features

- **Local Storage**: All context stored in JSON files on your machine
- **Smart Text Analysis**: Automatically extracts key decisions, problems, and solutions
- **Event-Driven**: Only stores significant development events
- **Keyword Search**: Fast local search with relevance scoring
- **Zero Dependencies**: No API keys, no external services

## Quick Start

### Basic Usage

```python
# 1. End productive session
end_session_summary("Fixed database connection issues and optimized queries", 
                   tags=["debugging", "database"])

# 2. Start new session with context
start_with_context(3)  # Get context from last 3 sessions

# 3. Record significant events
record_significant_event("error_solved", "Fixed memory leak in data processing pipeline")
```

## Available Tools

### `end_session_summary(summary, tags=None, max_words=100)`
Save a concise summary of your session with automatic key phrase extraction.

**Parameters:**
- `summary` (str): What you accomplished in the session
- `tags` (list): Optional tags for categorization (e.g., ["debugging", "frontend"])
- `max_words` (int): Maximum words to store (default: 100)

**Example:**
```python
end_session_summary(
    "Implemented user authentication with JWT tokens. Fixed CORS issues on login endpoint. Added password validation rules.",
    tags=["authentication", "backend", "security"],
    max_words=50
)
```

### `record_significant_event(event_type, details, project="project")`
Record only important development milestones.

**Event Types:**
- `error_solved`
- `build_configuration_changed`
- `new_feature_implemented`
- `deployment_completed`
- `preference_learned`
- `project_setup`
- `debugging_session`
- `optimization_applied`

**Example:**
```python
record_significant_event("error_solved", 
                        "Database connection pool exhaustion fixed by increasing max connections from 10 to 50")
```

### `start_with_context(sessions_back=3)`
Begin a new session with context from recent work.

**Example:**
```python
start_with_context(5)  # Get context from last 5 sessions
```

### `get_relevant_context(current_task)`
Get context specifically relevant to your current task.

**Example:**
```python
# When debugging
get_relevant_context("Fixing database timeout errors")

# When building
get_relevant_context("Setting up production deployment")

# When implementing features
get_relevant_context("Adding user profile management")
```

### `search_context(query, context_type="all", limit=5)`
Search through stored context for specific information.

**Parameters:**
- `query` (str): What to search for
- `context_type` (str): "sessions", "events", or "all"
- `limit` (int): Maximum results to return

### `save_context_levels(session_content)`
Save context at multiple detail levels for better organization.

### `get_context_stats()`
View statistics about your stored context.

### `clear_old_context(days_old=30)`
Clean up context entries older than specified days.

## Automatic Key Phrase Extraction

The context manager automatically extracts key phrases from your sessions:

- **Decisions**: "decided to", "chose to", "will use", "going to"
- **Problems**: "error:", "issue:", "problem:", "bug:", "failed to"
- **Solutions**: "solved by", "fixed by", "resolved by", "working now"

These phrases are automatically tagged and become searchable.

## Context Organization

### Storage Structure
```
context_storage/
├── sessions.json     # Session summaries with key phrases
├── events.json       # Significant events only
├── summaries.json    # Compressed session summaries
└── decisions.json    # Extracted decisions and solutions
```

### Automatic Management
- **Size Limits**: Only keeps last 50 entries per type
- **Automatic Cleanup**: Old context can be removed
- **Smart Search**: Relevance scoring for better results

## Best Practices

### 1. End Each Session
Always save a session summary when you finish productive work:
```python
end_session_summary("Completed user registration flow with email verification", 
                   tags=["feature", "frontend", "email"])
```

### 2. Record Significant Events
Don't record everything - only significant developments:
```python
# Good ✅
record_significant_event("error_solved", "Fixed React hydration mismatch by updating useEffect dependencies")

# Too trivial ❌
record_significant_event("error_solved", "Fixed typo in component name")
```

### 3. Use Descriptive Tags
Tags help categorize and find context later:
```python
# Good tags ✅
tags=["database", "performance", "optimization"]

# Too generic ❌
tags=["work", "coding"]
```

### 4. Start With Context
Begin each session by reviewing recent context:
```python
start_with_context(3)  # Review last 3 sessions
```

### 5. Search Before Reinventing
Use search to find previous solutions:
```python
search_context("CORS error", context_type="events")
```

## Storage and Privacy

- **Local Only**: All data stored in JSON files on your machine
- **No Network**: Works completely offline
- **Easy Backup**: Copy the `context_storage/` directory
- **Human Readable**: JSON files can be viewed with any text editor
- **No Vendor Lock-in**: Standard JSON format, easily portable

---

# Project Customization

## Overview

This guide explains how to customize the Project Manager MCP Server for your specific project needs. The server is designed to be project-agnostic but can be extended with custom functionality.

## Basic Configuration

### 1. Set Your Target Project Path

In `main.py`, update the `TARGET_PROJECT_RELATIVE_PATH` to point to your project:

```python
# ========================================
# CONFIGURATION: Update this path to point to your project
# ========================================
TARGET_PROJECT_RELATIVE_PATH = "../your-project"

# Examples for different project types:
TARGET_PROJECT_RELATIVE_PATH = "../my-react-app"           # React/Node.js app
TARGET_PROJECT_RELATIVE_PATH = "../my-python-service"      # Python service
TARGET_PROJECT_RELATIVE_PATH = "../vscode-extension"       # VSCode extension
TARGET_PROJECT_RELATIVE_PATH = "../../company-project"     # Different directory level
```

### 2. Verify Configuration

After updating the path, restart the server. You should see:
```
Target project manager initialized for: /path/to/your/project
```

If the directory doesn't exist, you'll see:
```
WARNING: Target project directory not found: /path/to/your/project
   Please update TARGET_PROJECT_RELATIVE_PATH in main.py
```

## Custom File Filtering

### Modifying Skip Patterns

Edit `tools/skip_patterns.py` to customize which files and directories are excluded:

```python
# Add custom directories to skip
SKIP_DIRS.add('my_custom_build_dir')
SKIP_DIRS.add('generated_files')

# Add custom files to skip
SKIP_FILES.add('my_config.secret')
SKIP_FILES.add('*.backup')

# Add custom file extensions to skip
SKIP_EXTENSIONS.add('.temp')
SKIP_EXTENSIONS.add('.cache')
```

### Project-Specific Patterns

For different project types, you might want different skip patterns:

#### React/Node.js Projects
```python
SKIP_DIRS.update({
    'node_modules', '.next', 'dist', 'build',
    '.vercel', '.netlify'
})
SKIP_FILES.update({
    'package-lock.json', 'yarn.lock', '.env.local'
})
```

#### Python Projects
```python
SKIP_DIRS.update({
    '__pycache__', '.pytest_cache', '.mypy_cache',
    'venv', '.venv', 'env'
})
SKIP_FILES.update({
    '*.pyc', 'poetry.lock', 'Pipfile.lock'
})
```

#### Go Projects
```python
SKIP_DIRS.update({
    'vendor', '.go'
})
SKIP_FILES.update({
    'go.sum', '*.exe'
})
```

## Creating Custom Project Managers

### Basic Custom Manager

Create a custom project manager by extending `BaseProjectManager`:

```python
from tools.base_project_manager import BaseProjectManager

class ReactProjectManager(BaseProjectManager):
    """Custom manager for React projects"""
    
    def get_tool_prefix(self) -> str:
        return "react"
    
    def get_staging_subdir(self) -> str:
        return "react_project"
    
    def register_specific_tools(self):
        """Add React-specific tools"""
        
        @self.mcp.tool(name="react_build")
        def build_project() -> str:
            """Build the React project"""
            # Implementation here
            pass
        
        @self.mcp.tool(name="react_test")
        def run_tests() -> str:
            """Run React tests"""
            # Implementation here
            pass
```

### Using Custom Managers

Update `main.py` to use your custom manager:

```python
# Replace the TargetProjectManager class with your custom manager
class TargetProjectManager(ReactProjectManager):  # or YourCustomManager
    pass

# Or import from a separate file
from tools.react_project_manager import ReactProjectManager

class TargetProjectManager(ReactProjectManager):
    pass
```

## Best Practices

### 1. Keep It Simple
Start with basic configuration and gradually add custom features as needed.

### 2. Use Consistent Naming
Follow the existing naming conventions for tools and prefixes.

### 3. Document Custom Features
Add docstrings to custom tools and document their usage.

### 4. Handle Errors Gracefully
Always include proper error handling in custom tools.

### 5. Test Custom Managers
Test your custom managers with different project structures.

### 6. Version Your Configuration
Keep your custom managers and configurations in version control.

---

# Shell Command Guidelines

## Important: Use Standard Commands Only

The shell command execution feature is designed to work with **standard, vanilla commands** that are commonly available across different systems. This ensures reliability and prevents issues with custom scripts or advanced shell features.

## Recommended Commands

### File Operations
```bash
# List files and directories
ls -la                    # Unix/Linux/macOS
dir                       # Windows

# Copy files
cp file.txt backup.txt    # Unix/Linux/macOS
copy file.txt backup.txt  # Windows

# Move/rename files
mv old.txt new.txt        # Unix/Linux/macOS
move old.txt new.txt      # Windows

# Remove files
rm file.txt               # Unix/Linux/macOS
del file.txt              # Windows

# Create/remove directories
mkdir new_folder          # Both platforms
rmdir empty_folder        # Both platforms
```

### Navigation
```bash
# Change directory
cd /path/to/directory     # Unix/Linux/macOS
cd C:\path\to\directory   # Windows

# Print current directory
pwd                       # Unix/Linux/macOS
cd                        # Windows (shows current dir)
```

### Text Operations
```bash
# Display file contents
cat file.txt              # Unix/Linux/macOS
type file.txt             # Windows

# Print text
echo "Hello World"        # Both platforms

# Search in files
grep "pattern" file.txt   # Unix/Linux/macOS (if available)
findstr "pattern" file.txt # Windows
```

### Development Commands
```bash
# Node.js/npm
npm install
npm test
npm run build

# Python
pip install package
python script.py
pytest

# Git (when available)
git status
git add .
git commit -m "message"

# Build tools
make
cargo build
```

## Commands to Avoid

### Complex Shell Features
```bash
# Avoid complex pipes and redirections
command1 | command2 | command3 > file.txt

# Avoid shell scripting constructs
for file in *.txt; do echo $file; done

# Avoid advanced parameter expansion
${variable/pattern/replacement}
```

### Interactive Commands
```bash
# Avoid commands that require user input
sudo command          # Requires password
ssh user@server       # Interactive login
nano file.txt         # Text editor
```

### Non-Standard Utilities
```bash
# Avoid custom aliases or functions
ll                    # Custom alias for ls -la
myCustomScript        # User-defined function

# Avoid advanced tools that might not be installed
jq                    # JSON processor
htop                  # Interactive process viewer
```

## Best Practices

### 1. Keep Commands Simple
```bash
# Good: Simple, clear commands
ls -la
cd src
npm test

# Avoid: Complex one-liners
find . -name "*.js" -exec grep -l "pattern" {} \; | xargs -I {} mv {} backup/
```

### 2. Use Full Paths When Needed
```bash
# Good: Specify working directory
execute_command("npm test", working_directory="./my-project")

# Good: Use absolute paths when necessary
execute_command("ls /usr/local/bin")
```

### 3. Handle Cross-Platform Differences
```bash
# Check platform in your logic, then use appropriate commands
# Unix: ls -la
# Windows: dir

# Unix: cp file.txt backup.txt
# Windows: copy file.txt backup.txt
```

### 4. Use Appropriate Timeouts
```bash
# Set reasonable timeouts for different operations
execute_command("npm install", timeout_seconds=120)  # Package installation
execute_command("ls", timeout_seconds=5)             # Quick file listing
execute_command("npm test", timeout_seconds=300)     # Running tests
```

## Quick Reference

### Essential Cross-Platform Commands

| Operation | Unix/Linux/macOS | Windows |
|-----------|------------------|---------|
| List files | `ls -la` | `dir` |
| Copy file | `cp src dest` | `copy src dest` |
| Move file | `mv src dest` | `move src dest` |
| Delete file | `rm file` | `del file` |
| Make directory | `mkdir dir` | `mkdir dir` |
| Current directory | `pwd` | `cd` |
| File contents | `cat file` | `type file` |

### Remember
- **Stick to basics**: Use standard commands that work everywhere
- **Test first**: Verify commands work in your environment
- **Keep it simple**: Avoid complex shell scripting
- **Set timeouts**: Prevent commands from hanging
- **Use full paths**: Be explicit about file locations

The goal is reliability and cross-platform compatibility, not showcasing advanced shell features.

---

# Documentation Guidelines

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
