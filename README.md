# Project Manager MCP Server

A Model Context Protocol (MCP) server for managing any development project. Features safe file operations with audit logging, cross-platform shell command execution, intelligent context management with local storage, comprehensive project management tools, and Git integration.

## Purpose

This MCP server provides development tools for managing any software project, with built-in safety mechanisms and intelligent context management. Originally designed with VSCode extension development in mind, it's fully adaptable to any project type.

## Features

### Shell Command Execution
- **Timeout Protection**: Commands automatically timeout to prevent hanging
- **Cross-Platform**: Works on Windows (cmd/PowerShell) and Unix systems (bash/sh)
- **Process Management**: Automatic cleanup of active processes
- **Error Handling**: Comprehensive error reporting and handling

### Safe Project Management
- **Multiple Project Support**: Manage MCP server project and any target project
- **Safe File Operations**: Read, create, and edit files with staging for locked files
- **Intelligent Filtering**: Excludes build artifacts and unnecessary files
- **Path Validation**: Prevents access outside project boundaries

### Git Integration
- **Repository Management**: Check status, view logs, create branches
- **Code Tracking**: View diffs, commit changes, manage staging area
- **Cross-Platform**: Works with Git repositories on any OS
- **Safety-First**: Audit trails for all Git operations

### Configurable Project Integration
- **Dual Project Design**: Manages both MCP server files and your target project
- **Adaptable Structure**: Easy to configure for different project types
- **Modular Architecture**: Extend with project-specific tools as needed

### Local Context Management
- **Pure Local Storage**: No external dependencies - uses simple JSON files
- **Smart Text Analysis**: Automatic extraction of key decisions, problems, and solutions
- **Keyword Search**: Fast local search with relevance scoring
- **Hierarchical Context**: Multiple levels of detail (summaries, decisions, events)
- **Event-Driven Storage**: Only store significant development events
- **Context Cleanup**: Automatic management of storage size

### Safety-First Design
- **MOVE FILES WITH LOGGING**: Move operations execute with audit trail (no overwrites)
- **NO DIRECT FILE DELETION**: Delete operations create logs for manual review
- **LOGGED FILE RENAMING**: Rename operations create logs for manual execution
- **Staging System**: Locked files are staged for manual review
- **Audit Trail**: All operations are logged with detailed information
- **Human Oversight**: Destructive operations require manual confirmation

## Available Tools

### Shell Commands
- `execute_command`: Execute any shell command with timeout protection
- `get_platform_info`: Get current platform and shell information

### Git Tools
- `git_status`: Get repository status (branch, changed files)
- `git_log`: View commit history with author and message info
- `git_diff`: Show file changes (staged or unstaged)
- `git_branch_list`: List all repository branches
- `git_branch_create`: Create new branches
- `git_branch_checkout`: Switch between branches
- `git_commit`: Record changes to the repository
- `git_add`: Stage files for commit
- `git_init`: Initialize new Git repositories

### MCP Project Management
- File read/write operations in MCP project directory
- Directory listing and navigation
- File staging and editing
- **Move with logging**: Execute moves with audit trail (no overwrites)
- **Safe rename/delete**: Creates logs for manual execution (see [Safety Guidelines](SAFETY_GUIDELINES.md))

### Target Project Management
- File read/write operations in your project directory
- Directory listing and navigation
- File staging and editing
- **Move with logging**: Execute moves with audit trail (no overwrites)
- **Safe rename/delete**: Creates logs for manual execution

### Local Context Management
- `end_session_summary`: Save session insights with key phrase extraction
- `record_significant_event`: Track important development milestones
- `save_context_levels`: Store context at multiple detail levels
- `start_with_context`: Retrieve context from recent sessions
- `get_relevant_context`: Get task-specific context
- `search_context`: Search through stored context with relevance scoring
- `get_context_stats`: View statistics about stored context
- `clear_old_context`: Clean up old context entries

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -e .
   ```
   
   Or using uv:
   ```bash
   uv pip install -e .
   ```

3. Configure your target project path in `main.py`:
   ```python
   # Update this path to point to your project
   TARGET_PROJECT_RELATIVE_PATH = "../your-project"
   ```

## Usage

Start the MCP server:

```bash
python main.py
```

The server will initialize and provide access to all available tools through the MCP protocol.

### Quick Start Guide

1. **Configure Target Project** (Required for target project tools):
   ```python
   # In main.py, update this line to point to your project:
   TARGET_PROJECT_RELATIVE_PATH = "../my-react-app"
   ```

2. **Using Git Tools**:
   ```
   # Get repository status
   git_status(repo_path="/path/to/repository")
   
   # View commit history
   git_log(repo_path="/path/to/repository", max_count=10)
   
   # Create and checkout a new branch
   git_branch_create(branch_name="feature/new-feature", repo_path="/path/to/repository")
   git_branch_checkout(branch_name="feature/new-feature", repo_path="/path/to/repository")
   
   # Stage and commit changes
   git_add(file_paths=["file1.txt", "file2.py"], repo_path="/path/to/repository")
   git_commit(message="Add new files", repo_path="/path/to/repository")
   ```

3. **Basic Context Management**:
   ```
   # At end of productive session
   end_session_summary("Fixed database connection issues and optimized queries", ["debugging", "database"])
   
   # At start of new session
   start_with_context(3)
   
   # Record significant achievements
   record_significant_event("error_solved", "Fixed memory leak in data processing pipeline")
   ```

See [CONTEXT_MANAGER_GUIDE.md](CONTEXT_MANAGER_GUIDE.md) for detailed context management usage.

### Safety Guidelines

**IMPORTANT**: This server executes move operations immediately (with audit logging) but does not allow direct file deletion or renaming for safety. Delete and rename operations create logs for manual review and execution. See [SAFETY_GUIDELINES.md](SAFETY_GUIDELINES.md) for complete details.

## Architecture

```
project-manager-mcp-server/
├── main.py                                    # Server entry point
├── tools/
│   ├── shell_mcp_server.py                    # Shell command execution
│   ├── mcp_project_manager.py                 # MCP server project management
│   ├── base_project_manager.py                # Base project management class
│   ├── context_manager.py                     # Local context management
│   ├── git_tools.py                           # Git repository operations
│   └── skip_patterns.py                       # File filtering patterns
├── context_storage/                           # Local JSON context storage
├── logs/                                      # Operation logs (moves/deletes)
├── .staging/                                  # Staged file changes
├── README.md
├── CONTEXT_MANAGER_GUIDE.md                  # Detailed context management guide
├── SAFETY_GUIDELINES.md                      # File operation safety policies
└── TODO.md                                   # Development roadmap and future features
```

## Configuration

### Adding Your Project

1. Update `main.py` to point to your project:
```python
TARGET_PROJECT_RELATIVE_PATH = "../your-project-name"
```

2. Optionally create a custom project manager by extending `BaseProjectManager`:
```python
class YourProjectManager(BaseProjectManager):
    def register_specific_tools(self):
        # Add project-specific tools here
        pass
```

### Customizing File Filtering

Edit `tools/skip_patterns.py` to customize which files and directories are excluded:
```python
SKIP_DIRS.add('your_custom_dir')
SKIP_FILES.add('your_custom_file.ext')
```

## Roadmap & Future Features

See [TODO.md](TODO.md) for the complete development roadmap, including:
- **Graceful error handling** for startup component failures
- **Enhanced Git integration** with pull/push capabilities
- **Enhanced external tool support** in shell commands
- **Obsidian integration** for knowledge management
- **Improved architecture** and testing coverage

## Design Philosophy

### Safety First
- **No destructive operations**: Move/delete create logs instead of executing
- **Manual oversight**: Critical operations require human review
- **Audit trail**: All operations are logged with detailed instructions
- **Staged changes**: Locked files are staged for review

### Universal Design
- **Project-agnostic**: Works with any codebase or project type
- **Modular architecture**: Easy to extend for specific project needs
- **Configurable paths**: Simple setup for any project structure
- **Cross-platform**: Consistent behavior across operating systems

### Local-First Context Management
- **No external dependencies**: Uses simple JSON files for storage
- **Smart text analysis**: Extracts key decisions, problems, solutions automatically
- **Fast keyword search**: Local search with relevance scoring
- **Hierarchical storage**: Different detail levels for different needs
- **Zero cost**: No API fees or subscriptions required

### Local-First Data
- **All data stays on your machine**: Context stored in local JSON files
- **No network dependencies**: Works completely offline
- **Fast startup**: No API initialization delays
- **Easy backup**: Just copy the `context_storage` directory

## Example Project Integrations

This MCP server works well with:
- **Web Applications**: React, Vue, Angular projects
- **Backend Services**: Node.js, Python, Go, Rust projects
- **Mobile Apps**: React Native, Flutter projects
- **Desktop Applications**: Electron, Tauri projects
- **Documentation Sites**: Jekyll, Hugo, GitBook projects
- **VSCode Extensions**: TypeScript/JavaScript extension projects

## Credits

- Shell command execution implementation inspired by [mcp-server-shell](https://github.com/odysseus0/mcp-server-shell)
- Git tools implementation inspired by [modelcontextprotocol/servers/git](https://github.com/modelcontextprotocol/servers/tree/main/src/git)
- Thanks to the MCP community for robust subprocess handling patterns
- Built with the [FastMCP](https://docs.modl.ai/mcp/) framework

## Contributing

Contributions welcome! This project is designed to facilitate any software development workflow and can be adapted for various project types and development environments.

### Adding Project-Specific Features

1. Create a new project manager class extending `BaseProjectManager`
2. Add project-specific tools in the `register_specific_tools()` method
3. Update `main.py` to use your custom project manager
4. Submit a PR with your enhancements!

## Requirements

- Python 3.12+
- MCP framework
- GitPython (for Git tools)