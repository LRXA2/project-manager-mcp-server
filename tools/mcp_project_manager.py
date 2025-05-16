import os
from tools.base_project_manager import BaseProjectManager
from mcp.server.fastmcp import FastMCP

class MCPProjectManager(BaseProjectManager):
    """Manages files within the MCP server project directory only"""
    
    def __init__(self, base_dir: str, mcp_instance: FastMCP):
        super().__init__(
            base_dir=base_dir,
            project_dir=base_dir,  # MCP project manages itself
            mcp_instance=mcp_instance,
            project_name="MCP"
        )
    
    def get_tool_prefix(self) -> str:
        """Return the prefix for tool names"""
        return "mcp"
    
    def get_staging_subdir(self) -> str:
        """Return the subdirectory name for staging"""
        return "mcp"
    
    def register_specific_tools(self):
        """Register MCP-specific tools"""
        
        @self.mcp.tool()
        def list_staged_files() -> list:
            """
            List all currently staged files.
            
            Returns:
                list: List of staged file paths
            """
            staging_dir = os.path.join(self.base_dir, ".staging")
            
            if not os.path.exists(staging_dir):
                return []
            
            staged_files = []
            for root, dirs, files in os.walk(staging_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, staging_dir)
                    staged_files.append(rel_path)
            
            return sorted(staged_files)
        
        @self.mcp.tool()
        def read_staged_file(relative_path: str) -> str:
            """
            Read the content of a staged file for review.
            
            Args:
                relative_path (str): The relative path to the staged file
            
            Returns:
                str: The content of the staged file
            """
            staging_dir = os.path.join(self.base_dir, ".staging")
            staged_file_path = os.path.join(staging_dir, relative_path)
            
            if not os.path.exists(staged_file_path):
                return f"Error: Staged file not found at .staging/{relative_path}"
            
            try:
                with open(staged_file_path, "r", encoding="utf-8") as f:
                    return f.read()
            except OSError as e:
                return f"Error reading staged file: {e}"
            except UnicodeDecodeError as e:
                return f"Error: Staged file contains binary data or unsupported encoding: {e}"
        
        @self.mcp.tool()
        def edit_staged_file(relative_path: str, find_str: str, replace_str: str) -> str:
            """
            Edit a function/content in the currently staged file.
            
            Args:
                relative_path (str): The staged file to edit
                find_str (str): Text to find
                replace_str (str): Text to replace with
            
            Returns:
                str: Confirmation message
            """
            # Read current staged content
            staged_content = read_staged_file(relative_path)
            if staged_content.startswith("Error:"):
                return f"No staged file found. Stage initial changes first."
            
            # Perform replacement
            if find_str not in staged_content:
                return f"String '{find_str}' not found in staged file"
            
            modified_content = staged_content.replace(find_str, replace_str)
            
            # Create a temporary staging function to re-stage the content
            def stage_modified_content():
                staging_subdir = self.get_staging_subdir()
                staging_dir = os.path.join(self.base_dir, ".staging", staging_subdir)
                staged_file_path = os.path.join(staging_dir, relative_path)
                staged_parent_dir = os.path.dirname(staged_file_path)
                
                os.makedirs(staged_parent_dir, exist_ok=True)
                
                with open(staged_file_path, "w", encoding="utf-8") as f:
                    f.write(modified_content)
                
                return f"Modified content re-staged at .staging/{staging_subdir}/{relative_path}"
            
            try:
                return stage_modified_content()
            except OSError as e:
                return f"Error re-staging modified content: {e}"
        
        @self.mcp.prompt()
        def analyze_mcp_structure() -> str:
            """
            Analyze and explain the overall structure of the MCP project.

            Returns:
                str: An LLM-generated analysis of the MCP project structure.
            """
            # Get directory structure without content for overview
            # Note: We need to use the tools directly since they're not registered yet
            is_valid, full_path = self._validate_path(self.project_dir, ".")
            if not is_valid:
                return "Error: Cannot analyze structure"
            
            # Build directory structure manually
            structure = {}
            for root, dirs, files in os.walk(full_path):
                dirs[:] = [d for d in dirs if not self._should_skip_dir(d)]
                rel_root = os.path.relpath(root, self.project_dir)
                structure[rel_root] = {}
                
                for file_name in files:
                    if not self._should_skip_file(file_name):
                        structure[rel_root][file_name] = "Content not loaded."
            
            # Get main files content for analysis
            main_files = []
            important_files = ["main.py", "pyproject.toml", "README.md", "tools/skip_patterns.py"]
            
            for file in important_files:
                file_is_valid, file_full_path = self._validate_path(self.project_dir, file)
                if file_is_valid and os.path.isfile(file_full_path):
                    try:
                        with open(file_full_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            main_files.append(f"\n\n### {file}:\n{content}")
                    except (OSError, UnicodeDecodeError):
                        main_files.append(f"\n\n### {file}:\nError reading file")
            
            combined_content = f"Directory structure:\n{structure}\n\nImportant files content:{''.join(main_files)}"
            
            return f"Analyze and explain the structure of this MCP server project. Focus on the purpose, organization, and key components:\n\n{combined_content}"
