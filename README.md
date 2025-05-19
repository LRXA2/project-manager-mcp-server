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
- **Remote Operations**: Clone, pull, push to remote repositories
- **Branch Management**: Create, list, and checkout branches
- **Cross-Platform**: Works with Git repositories on any OS
- **Safety-First**: Audit trails for all Git operations
- **Secure Credentials**: Template-based credential management with .gitignore protection

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