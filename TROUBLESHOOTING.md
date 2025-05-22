# Troubleshooting Guide

## Common Installation Issues

### Requests Library Configuration Error

**Problem:** When using the MCP server with Claude, you might encounter this error:
```
error: Failed to spawn: `requests` Caused by: program not found
```

**Cause:** The system is trying to execute `requests` as a command-line program rather than importing it as a Python library.

**Solution:**

1. Install the requests library in your environment:
   ```bash
   uv add requests
   ```

2. Make sure to use proper Python imports in your code:
   ```python
   try:
       import requests
       REQUESTS_AVAILABLE = True
   except ImportError:
       REQUESTS_AVAILABLE = False
       print("WARNING: Requests library not available")
   ```

3. When using Claude with this MCP server, adjust Claude's configuration to include the `requests` library. Add this to your VSCode settings:

   ```json
   "VSCode LLM Chat Editor": {
     "command": "C:\\Users\\Aarron\\.local\\bin\\uv.EXE",
     "args": [
       "run",
       "--with",
       "mcp[cli]",
       "--with",
       "requests>=2.31.0",
       "mcp",
       "run",
       "D:\\Aarron\\personal\\projects\\MCP vscode-llm-chat editor\\main.py"
     ]
   }
   ```

   The key addition is the `"--with", "requests>=2.31.0"` arguments.

## Shell Command Issues

### Claude Shell Command Timeouts

**Problem:** Shell commands timeout after 30 seconds when using Claude's execute_command tool.

**Symptoms:**
- First `python` command execution works fine (`python --version`)
- All subsequent shell commands time out after 30 seconds
- Error message: "Command timed out after 30 seconds"

**Analysis:** This appears to be a Claude-specific issue, not related to the MCP server code itself. The MCP server's `execute_command` tool has proper timeout handling and process cleanup.

**Workaround:** Use the MCP server's built-in `execute_command` tool through the MCP protocol instead of Claude's shell execution.

## Configuration Issues

### Target Project Not Found

**Problem:** Warning message on startup:
```
WARNING: Target project directory not found: /path/to/your/project
   Please update TARGET_PROJECT_RELATIVE_PATH in main.py
```

**Solution:** Update the target project path in `main.py`:
```python
TARGET_PROJECT_RELATIVE_PATH = "../your-actual-project"
```

### Component Initialization Failures

**Problem:** Some components show as "FAILED" in the startup status.

**Common Causes:**
1. **Git not available**: Git tools will fail if Git is not installed
2. **Directory permissions**: Check read/write access to project directories
3. **Python dependencies**: Ensure all required packages are installed

**Solution:** Check the specific error message in the component status and address the underlying issue.

## File Operation Issues

### Files Not Editable (Staging Behavior)

**Problem:** File edits are being staged instead of applied directly.

**Cause:** File is open/locked in another application (VS Code, text editor, etc.).

**Solution:** 
1. Close the file in other applications
2. Or review and apply the staged changes manually from `.staging/` directory

### Move Operations Failing

**Problem:** Move operations return errors about existing destinations.

**Cause:** The safety policy prevents overwriting existing files.

**Solutions:**
1. Check if destination already exists
2. Choose a different destination name
3. Manually remove the destination file if overwrite is intended

### Delete/Rename Logs Not Being Executed

**Problem:** Delete and rename operations create logs but nothing happens.

**Expected Behavior:** This is intentional! Delete and rename operations require manual review and execution for safety.

**Solution:** 
1. Review the log files in `logs/{project}/deletion/` or `logs/{project}/rename/`
2. Execute the operations manually using the commands provided in the logs
3. Delete the log files after successful execution

## Context Management Issues

### Context Not Saving

**Problem:** Context sessions or events are not being recorded.

**Possible Causes:**
1. Permissions issue with `context_storage/` directory
2. Disk space insufficient
3. JSON file corruption

**Solutions:**
1. Check directory permissions: `ls -la context_storage/`
2. Verify disk space: `df -h`
3. Check JSON file integrity by trying to open `context_storage/*.json`

### Search Returns No Results

**Problem:** Context search returns "No context found" even when data exists.

**Solutions:**
1. Try broader search terms
2. Check if you've recorded any sessions: `get_context_stats()`
3. Verify JSON files contain data: `cat context_storage/sessions.json`

## Git Integration Issues

### Git Authentication Failures

**Problem:** Git push/pull operations fail with authentication errors.

**Solutions:**
1. Set up Git credentials in `config/credentials.json`
2. Use personal access tokens instead of passwords
3. Ensure Git is properly configured: `git config --list`

### Git Operations Not Available

**Problem:** Git tools show as not available.

**Cause:** Git is not installed or not in system PATH.

**Solution:** Install Git and ensure it's accessible from command line: `git --version`

## Performance Issues

### Slow File Operations

**Problem:** File reading/writing is slow in large projects.

**Solutions:**
1. Check if antivirus is scanning files
2. Exclude project directories from real-time scanning
3. Review skip patterns in `tools/skip_patterns.py` to exclude more directories

### Context Storage Growing Too Large

**Problem:** Context files becoming very large.

**Solution:** Use the cleanup tool: `clear_old_context(30)` to remove entries older than 30 days.

## Platform-Specific Issues

### Windows Path Issues

**Problem:** Path-related errors on Windows systems.

**Common Issues:**
- Backslash vs forward slash in paths
- Long path names exceeding Windows limits
- Special characters in path names

**Solutions:**
1. Use forward slashes in configuration: `../project` instead of `..\\project`
2. Ensure paths are not too long (< 260 characters)
3. Avoid special characters in directory names

### Unix Permission Issues

**Problem:** Permission denied errors on Unix/Linux systems.

**Solutions:**
1. Check file permissions: `ls -la`
2. Ensure MCP server has proper permissions: `chmod +x main.py`
3. Check directory ownership: `ls -la ..`

## Debugging Tips

### Enable Verbose Logging

Add logging to troubleshoot issues:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Component Status

The startup message shows which components initialized successfully:
```
Component Status:
- MCP Server: ✓ RUNNING
- Git Tools: ✗ FAILED
  Error: Git not found on system
```

### Verify MCP Server Health

Check the system health percentage in the startup message. Less than 100% indicates some components failed to initialize.

### Test Individual Tools

Test tools individually through the MCP interface to isolate issues.

## Getting Help

### Check Log Files

1. **Operation logs**: `logs/{project}/` directories
2. **Context storage**: `context_storage/*.json` files
3. **Staging area**: `.staging/{project}/` directories

### Verify Environment

1. **Python version**: Should be 3.12+
2. **Dependencies**: Run `uv pip list` to see installed packages
3. **Platform compatibility**: Ensure commands work in your shell

### Reset to Clean State

If all else fails:
1. Stop the MCP server
2. Remove `.staging/` directory
3. Clear `context_storage/` (backup first if needed)
4. Remove `logs/` directory (backup first if needed)
5. Restart the server

This should reset the system to a clean state while preserving your project files.
