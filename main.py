from mcp.server.fastmcp import FastMCP
from tools.mcp_project_manager import MCPProjectManager
from tools.shell_mcp_server import ShellMCPServer
from tools.context_manager import ContextManager
import os
import atexit

# Base MCP server instance
mcp = FastMCP("Project Manager MCP Server")

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
mcp_manager = MCPProjectManager(BASE_DIR, mcp)
mcp_manager.register_tools()

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
        print(f"Target project manager initialized for: {target_project_dir}")
    else:
        print(f"WARNING: Target project directory not found: {target_project_dir}")
        print(f"   Please update TARGET_PROJECT_RELATIVE_PATH in main.py")
        print(f"   Current setting: {TARGET_PROJECT_RELATIVE_PATH}")
        target_project_manager = None
        
except Exception as e:
    print(f"Error during Target Project Manager initialization: {e}")
    target_project_manager = None

# Initialize and register Shell MCP Server
shell_server = ShellMCPServer(mcp)
shell_server.register_tools()
print("Shell MCP server registered successfully")

# Initialize and register Context Manager
context_manager = ContextManager(BASE_DIR, mcp)
context_manager.register_tools()
print("Context Manager initialized (local storage mode)")

# Register cleanup handler
atexit.register(shell_server.cleanup)

if __name__ == "__main__":
    print("\n" + "="*50)
    print("Project Manager MCP Server Started!")
    print("="*50)
    print("\nAvailable tools:")
    print("- execute_command: Execute any shell command")
    print("- get_platform_info: Get platform and shell information")
    print("- MCP project management tools (mcp_*)")
    
    if target_project_manager:
        print("- Target project management tools (target_*)")
        print(f"  Managing: {target_project_dir}")
    else:
        print("- Target project tools: NOT CONFIGURED")
        print(f"   Set TARGET_PROJECT_RELATIVE_PATH in main.py to enable")
    
    print("- Local context management tools (no external dependencies)")
    print("  - end_session_summary: Save session insights")
    print("  - record_significant_event: Track important events")
    print("  - start_with_context: Resume with recent context")
    print("  - search_context: Find relevant past information")
    
    print(f"\nConfiguration:")
    print(f"   Target project path: {TARGET_PROJECT_RELATIVE_PATH}")
    print(f"   Context storage: Local JSON files only")
    print("\n" + "="*50)
    mcp.run()
