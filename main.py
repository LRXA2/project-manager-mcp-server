from mcp.server.fastmcp import FastMCP
from tools.mcp_project_manager import MCPProjectManager
from tools.shell_mcp_server import ShellMCPServer
from tools.context_manager import ContextManager
from tools.git.git_tools import GitTools
import os
import atexit
import traceback
import sys
import requests
    
# Record component initialization status
component_status = {
    "mcp_server": {"initialized": False, "error": None},
    "mcp_project_manager": {"initialized": False, "error": None},
    "target_project_manager": {"initialized": False, "error": None},
    "shell_server": {"initialized": False, "error": None},
    "context_manager": {"initialized": False, "error": None},
    "git_tools": {"initialized": False, "error": None}
}

try:
    # Base MCP server instance
    mcp = FastMCP("Project Manager MCP Server")
    component_status["mcp_server"]["initialized"] = True
except Exception as e:
    component_status["mcp_server"]["error"] = str(e)
    print(f"CRITICAL ERROR: MCP Server failed to initialize: {e}")
    print(traceback.format_exc())
    sys.exit(1)

# Directory paths
BASE_DIR = os.path.dirname(__file__)

# ========================================
# CONFIGURATION: Update this path to point to your project
# ========================================
TARGET_PROJECT_RELATIVE_PATH = "../your-project"
# Examples:
# TARGET_PROJECT_RELATIVE_PATH = "../my-react-app"
# TARGET_PROJECT_RELATIVE_PATH = "../my-python-service"
# TARGET_PROJECT_RELATIVE_PATH = "../vscode-extension"
# ========================================

# Initialize and register the MCP Project Manager (manages this MCP server's files)
mcp_manager = None
try:
    mcp_manager = MCPProjectManager(BASE_DIR, mcp)
    mcp_manager.register_tools()
    component_status["mcp_project_manager"]["initialized"] = True
except Exception as e:
    component_status["mcp_project_manager"]["error"] = str(e)
    print(f"ERROR: MCP Project Manager failed to initialize: {e}")

# Initialize and register the Target Project Manager (manages your actual project)
target_project_dir = None
target_project_manager = None

try:
    # Import the base project manager as default target project manager
    from tools.base_project_manager import BaseProjectManager
    
    # Create a simple project manager for your target project
    class TargetProjectManager(BaseProjectManager):
        """Manages your target project files"""
        
        def get_tool_prefix(self) -> str:
            return "target"
        
        def get_staging_subdir(self) -> str:
            return "target_project"
        
        def register_specific_tools(self):
            """Override this method to add project-specific tools"""
            pass
    
    target_project_dir = os.path.abspath(os.path.join(BASE_DIR, TARGET_PROJECT_RELATIVE_PATH))
    
    # Check if directory exists before initializing
    if os.path.exists(target_project_dir):
        target_project_manager = TargetProjectManager(
            base_dir=BASE_DIR,
            project_dir=target_project_dir,
            mcp_instance=mcp,
            project_name="Target Project"
        )
        target_project_manager.register_tools()
        component_status["target_project_manager"]["initialized"] = True
    else:
        component_status["target_project_manager"]["error"] = f"Directory not found: {target_project_dir}"
        print(f"WARNING: Target project directory not found: {target_project_dir}")
        print(f"   Please update TARGET_PROJECT_RELATIVE_PATH in main.py")
        target_project_manager = None
        
except Exception as e:
    component_status["target_project_manager"]["error"] = str(e)
    print(f"ERROR: Target Project Manager initialization failed: {e}")
    target_project_manager = None

# Initialize and register Shell MCP Server
shell_server = None
try:
    shell_server = ShellMCPServer(mcp)
    shell_server.register_tools()
    component_status["shell_server"]["initialized"] = True
except Exception as e:
    component_status["shell_server"]["error"] = str(e)
    print(f"ERROR: Shell MCP Server failed to initialize: {e}")

# Initialize and register Context Manager
context_manager = None
try:
    context_manager = ContextManager(BASE_DIR, mcp)
    context_manager.register_tools()
    component_status["context_manager"]["initialized"] = True
except Exception as e:
    component_status["context_manager"]["error"] = str(e)
    print(f"ERROR: Context Manager failed to initialize: {e}")

# Initialize and register Git Tools
git_tools = None
try:
    git_tools = GitTools(mcp)
    if git_tools.is_available:
        git_tools.register_tools()
        component_status["git_tools"]["initialized"] = True
    else:
        component_status["git_tools"]["error"] = "Git not available on this system"
        print("WARNING: Git tools not available - Git not found on system")
except Exception as e:
    component_status["git_tools"]["error"] = str(e)
    print(f"ERROR: Git tools failed to initialize: {e}")

# Register cleanup handler for shell server if initialized
if shell_server:
    try:
        atexit.register(shell_server.cleanup)
    except Exception as e:
        print(f"WARNING: Failed to register shell server cleanup handler: {e}")

# Calculate the system health percentage
def get_system_health():
    total_components = len(component_status)
    initialized_components = sum(1 for component in component_status.values() if component["initialized"])
    return (initialized_components / total_components) * 100

if __name__ == "__main__":
    system_health = get_system_health()
    
    print("\n" + "="*50)
    print(f"Project Manager MCP Server Started! (System Health: {system_health:.1f}%)")
    print("="*50)
    
    # Print component status
    print("\nComponent Status:")
    for component_name, status in component_status.items():
        status_text = "✓ RUNNING" if status["initialized"] else "✗ FAILED"
        print(f"- {component_name.replace('_', ' ').title()}: {status_text}")
        if not status["initialized"] and status["error"]:
            print(f"  Error: {status['error']}")
    
    print("\nConfiguration:")
    print(f"   Target project path: {TARGET_PROJECT_RELATIVE_PATH}")
    
    if system_health < 100:
        print("\nWARNING: Some components failed to initialize.")
        print("See component status above for details.")
    
    # Only run if MCP server is initialized (should always be true as we exit earlier if not)
    if component_status["mcp_server"]["initialized"]:
        try:
            mcp.run()
        except Exception as e:
            print(f"CRITICAL ERROR: MCP Server run failed: {e}")
            print(traceback.format_exc())
            sys.exit(1)
    else:
        print("CRITICAL ERROR: Cannot run without base MCP server.")
        sys.exit(1)