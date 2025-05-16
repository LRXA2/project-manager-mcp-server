# Project Customization Guide

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

### Advanced Custom Manager

Here's a more comprehensive example for a VSCode extension project:

```python
class VSCodeExtensionManager(BaseProjectManager):
    """Specialized manager for VSCode extension development"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extension_manifest = None
        self._load_extension_manifest()
    
    def _load_extension_manifest(self):
        """Load package.json to understand extension structure"""
        manifest_path = os.path.join(self.project_dir, "package.json")
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, 'r') as f:
                    self.extension_manifest = json.load(f)
            except (json.JSONDecodeError, OSError):
                pass
    
    def get_tool_prefix(self) -> str:
        return "vscode"
    
    def get_staging_subdir(self) -> str:
        return "vscode_extension"
    
    def register_specific_tools(self):
        """Register VSCode extension specific tools"""
        
        @self.mcp.tool(name="vscode_package")
        def package_extension() -> str:
            """Package the VSCode extension"""
            # Use vsce to package the extension
            # Implementation here
            pass
        
        @self.mcp.tool(name="vscode_publish")
        def publish_extension() -> str:
            """Publish the extension to marketplace"""
            # Implementation here
            pass
        
        @self.mcp.tool(name="vscode_get_commands")
        def get_extension_commands() -> str:
            """Get all commands defined in the extension"""
            if not self.extension_manifest:
                return "No package.json found"
            
            commands = self.extension_manifest.get("contributes", {}).get("commands", [])
            return json.dumps(commands, indent=2)
        
        @self.mcp.tool(name="vscode_update_version")
        def update_version(version: str) -> str:
            """Update the extension version"""
            # Implementation here
            pass
```

### Using Custom Managers

Update `main.py` to use your custom manager:

```python
# Replace the TargetProjectManager class with your custom manager
class TargetProjectManager(ReactProjectManager):  # or VSCodeExtensionManager
    pass

# Or import from a separate file
from tools.react_project_manager import ReactProjectManager

class TargetProjectManager(ReactProjectManager):
    pass
```

## Project-Specific Configuration

### Environment-Specific Settings

Create environment-specific configurations:

```python
class ProjectConfig:
    def __init__(self, project_dir: str):
        self.project_dir = project_dir
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """Load project-specific configuration"""
        config_file = os.path.join(self.project_dir, ".mcp-config.json")
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return json.load(f)
        return {}
    
    def get_build_command(self) -> str:
        return self.config.get("build_command", "npm run build")
    
    def get_test_command(self) -> str:
        return self.config.get("test_command", "npm test")
```

### Project Configuration File

Create a `.mcp-config.json` in your project root:

```json
{
  "build_command": "npm run build:prod",
  "test_command": "npm run test:coverage",
  "deploy_command": "npm run deploy",
  "custom_skip_patterns": {
    "dirs": ["custom_temp", "local_cache"],
    "files": ["*.local", "*.dev"]
  },
  "project_type": "react",
  "tools_enabled": ["build", "test", "deploy", "lint"]
}
```

## Adding Project-Specific Context

### Custom Event Types

Extend the context manager with project-specific events:

```python
# In your custom manager
def register_specific_tools(self):
    # Extend significant events for your project
    context_manager = self.mcp_instance._context_manager
    context_manager.SIGNIFICANT_EVENTS.extend([
        "extension_published",
        "marketplace_update",
        "user_feedback_received"
    ])
    
    @self.mcp.tool(name="record_extension_event")
    def record_extension_event(event_type: str, details: str) -> str:
        """Record VSCode extension specific events"""
        # Use the existing context manager
        return context_manager.record_significant_event(event_type, details, "vscode-extension")
```

### Project Tags

Automatically tag context with project-specific information:

```python
def end_session_with_project_context(self, summary: str, additional_tags: List[str] = None) -> str:
    """End session with automatic project tags"""
    project_tags = ["vscode-extension"]
    
    # Add automatic tags based on files changed
    if self._contains_typescript_changes():
        project_tags.append("typescript")
    if self._contains_test_changes():
        project_tags.append("testing")
    
    all_tags = project_tags + (additional_tags or [])
    return self.context_manager.end_session_summary(summary, tags=all_tags)
```

## Multi-Project Management

### Managing Multiple Projects

You can extend the server to manage multiple projects simultaneously:

```python
# In main.py
projects = [
    {
        "name": "Frontend",
        "path": "../frontend-app",
        "manager_class": ReactProjectManager,
        "prefix": "frontend"
    },
    {
        "name": "Backend",
        "path": "../backend-service",
        "manager_class": PythonProjectManager,
        "prefix": "backend"
    }
]

project_managers = []
for project_config in projects:
    project_dir = os.path.abspath(os.path.join(BASE_DIR, project_config["path"]))
    if os.path.exists(project_dir):
        manager = project_config["manager_class"](
            base_dir=BASE_DIR,
            project_dir=project_dir,
            mcp_instance=mcp,
            project_name=project_config["name"]
        )
        manager.register_tools()
        project_managers.append(manager)
```

## Integration Examples

### Git Integration

Add Git-aware tools to your custom manager:

```python
@self.mcp.tool(name="git_status")
def get_git_status() -> str:
    """Get current Git status"""
    # Implementation using subprocess
    pass

@self.mcp.tool(name="git_diff_summary")
def get_diff_summary() -> str:
    """Get summary of current changes"""
    # Implementation here
    pass
```

### Build System Integration

Integrate with your build system:

```python
@self.mcp.tool(name="run_build")
def run_build(mode: str = "development") -> str:
    """Run project build"""
    config = ProjectConfig(self.project_dir)
    
    if mode == "production":
        command = config.get_build_command_prod()
    else:
        command = config.get_build_command_dev()
    
    # Execute using shell server
    return self.shell_server.execute_command(command, self.project_dir)
```

### Testing Integration

Add testing-specific tools:

```python
@self.mcp.tool(name="run_tests")
def run_tests(pattern: str = None) -> str:
    """Run project tests with optional pattern"""
    config = ProjectConfig(self.project_dir)
    command = config.get_test_command()
    
    if pattern:
        command += f" --grep {pattern}"
    
    return self.shell_server.execute_command(command, self.project_dir)
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

## Troubleshooting

### Common Issues

1. **Target project not found**: Verify the relative path is correct
2. **Tools not appearing**: Check that your custom manager is properly registered
3. **Permission errors**: Ensure the MCP server has read/write access to your project
4. **Build failures**: Verify build commands in your project-specific configuration

### Debugging Custom Managers

Add logging to your custom managers:

```python
import logging

class MyCustomManager(BaseProjectManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(f"custom_manager_{self.project_name}")
    
    def register_specific_tools(self):
        self.logger.info(f"Registering tools for {self.project_name}")
        # Tool registration here
```

This guide should help you customize the MCP server for your specific project needs. Start with basic configuration and gradually add more sophisticated features as your requirements grow.