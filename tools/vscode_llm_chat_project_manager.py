import os
import json
import subprocess
from tools.base_project_manager import BaseProjectManager
from mcp.server.fastmcp import FastMCP

class VscodeLlmChatProjectManager(BaseProjectManager):
    """Manages the VSCode LLM Chat Extension project directory with comprehensive development tools"""
    
    def __init__(self, mcp_base_dir: str, vscode_llm_chat_relative_path: str, mcp_instance: FastMCP):
        """
        Initialize the VSCode LLM Chat Project Manager
        
        Args:
            mcp_base_dir: The base directory of the MCP server project
            vscode_llm_chat_relative_path: The relative path from MCP base dir to the VSCode LLM Chat extension project
            mcp_instance: The FastMCP instance to register tools with
        """
        self.vscode_llm_chat_relative_path = vscode_llm_chat_relative_path
        vscode_llm_chat_dir = os.path.abspath(os.path.join(mcp_base_dir, vscode_llm_chat_relative_path))
        
        super().__init__(
            base_dir=mcp_base_dir,
            project_dir=vscode_llm_chat_dir,
            mcp_instance=mcp_instance,
            project_name="VSCode LLM Chat Extension"
        )
    
    def get_tool_prefix(self) -> str:
        """Return the prefix for tool names"""
        return "vscode_llm_chat"
    
    def get_staging_subdir(self) -> str:
        """Return the subdirectory name for staging"""
        return "vscode_llm_chat"
    
    def register_specific_tools(self):
        """Register VSCode LLM Chat extension-specific tools including npm management"""
        
        @self.mcp.tool()
        def run_npm_command(command: str, args: str = "") -> dict:
            """
            Run npm commands in the VSCode LLM Chat extension project directory.
            
            Args:
                command (str): The npm command to run (e.g., 'install', 'run', 'update')
                args (str): Additional arguments for the command
            
            Returns:
                dict: Command output with success status, stdout, and stderr
            """
            # Construct the full npm command
            full_command = f"npm {command}"
            if args:
                full_command += f" {args}"
            
            try:
                # Run the command in the VSCode LLM Chat extension directory
                result = subprocess.run(
                    full_command,
                    shell=True,
                    cwd=self.project_dir,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                return {
                    "success": result.returncode == 0,
                    "command": full_command,
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "cwd": self.project_dir
                }
                
            except subprocess.TimeoutExpired:
                return {
                    "success": False,
                    "command": full_command,
                    "error": "Command timed out after 5 minutes",
                    "cwd": self.project_dir
                }
            except Exception as e:
                return {
                    "success": False,
                    "command": full_command,
                    "error": str(e),
                    "cwd": self.project_dir
                }
        
        @self.mcp.tool()
        def check_vscode_llm_chat_status(self) -> dict:
            """
            Check the current state of the VSCode LLM Chat extension project.
            
            Returns:
                dict: Project status including installed packages, scripts, and build state
            """
            status = {
                "project_path": self.project_dir,
                "project_name": "VSCode LLM Chat Extension",
                "package_json_exists": False,
                "node_modules_exists": False,
                "dependencies": {},
                "dev_dependencies": {},
                "scripts": {},
                "main_file": None,
                "build_output": {}
            }
            
            # Check package.json
            package_json_path = os.path.join(self.project_dir, "package.json")
            if os.path.exists(package_json_path):
                status["package_json_exists"] = True
                try:
                    with open(package_json_path, 'r', encoding='utf-8') as f:
                        package_data = json.load(f)
                        status["dependencies"] = package_data.get("dependencies", {})
                        status["dev_dependencies"] = package_data.get("devDependencies", {})
                        status["scripts"] = package_data.get("scripts", {})
                        status["main_file"] = package_data.get("main", None)
                        status["display_name"] = package_data.get("displayName", "")
                        status["version"] = package_data.get("version", "")
                except Exception as e:
                    status["package_json_error"] = str(e)
            
            # Check node_modules
            node_modules_path = os.path.join(self.project_dir, "node_modules")
            status["node_modules_exists"] = os.path.exists(node_modules_path)
            
            # Check for built files
            out_dir = os.path.join(self.project_dir, "out")
            if os.path.exists(out_dir):
                try:
                    out_files = [f for f in os.listdir(out_dir) if f.endswith('.js')]
                    status["build_output"]["out_files"] = out_files
                    status["build_output"]["out_dir_exists"] = True
                except:
                    status["build_output"]["error"] = "Cannot read out directory"
            else:
                status["build_output"]["out_dir_exists"] = False
            
            return status
        
        @self.mcp.tool()
        def install_vscode_llm_chat_package(package_name: str, dev: bool = False, version: str = "") -> dict:
            """
            Install a specific npm package for the VSCode LLM Chat extension.
            
            Args:
                package_name (str): The package name to install
                dev (bool): Install as dev dependency
                version (str): Specific version to install (optional)
            
            Returns:
                dict: Installation result
            """
            # Construct the command
            command = "install"
            
            # Add package specification
            if version:
                args = f"{package_name}@{version}"
            else:
                args = package_name
            
            # Add dev flag if needed
            if dev:
                args += " --save-dev"
            else:
                args += " --save"
            
            return run_npm_command(command, args)
        
        @self.mcp.tool()
        def build_vscode_llm_chat_extension(self) -> dict:
            """
            Build the VSCode LLM Chat extension using npm compile script.
            
            Returns:
                dict: Build result with output
            """
            return run_npm_command("run", "compile")
        
        @self.mcp.tool()
        def watch_vscode_llm_chat_extension(self) -> dict:
            """
            Start watch mode for the VSCode LLM Chat extension (useful for development).
            
            Returns:
                dict: Command result (this will start a background process)
            """
            return run_npm_command("run", "watch")
        
        @self.mcp.tool()
        def package_vscode_llm_chat_extension(self) -> dict:
            """
            Package the VSCode LLM Chat extension into a .vsix file using vsce.
            Installs vsce if not available.
            
            Returns:
                dict: Packaging result
            """
            # First check if vsce is available
            vsce_check = run_npm_command("list", "vsce --depth=0")
            
            if not vsce_check["success"] or "vsce" not in vsce_check["stdout"]:
                # Install vsce globally
                install_result = run_npm_command("install", "-g vsce")
                if not install_result["success"]:
                    return {
                        "success": False,
                        "error": "Failed to install vsce",
                        "details": install_result
                    }
            
            # Run vsce package
            try:
                result = subprocess.run(
                    "vsce package",
                    shell=True,
                    cwd=self.project_dir,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                return {
                    "success": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }
        
        @self.mcp.tool()
        def search_vscode_llm_chat_files(search_term: str, file_pattern: str = "*.ts,*.js,*.json,*.md") -> dict:
            """
            Search for a term within files in the VSCode LLM Chat extension project.

            Args:
                search_term (str): The term to search for.
                file_pattern (str): Comma-separated file patterns to search in (e.g., "*.ts,*.js").

            Returns:
                dict: Dictionary with file paths as keys and matching lines as values.
            """
            results = {}
            patterns = [p.strip() for p in file_pattern.split(',')]
            
            for root, dirs, files in os.walk(self.project_dir):
                # Skip common build/dependency directories
                dirs[:] = [d for d in dirs if not self._should_skip_dir(d)]
                
                for file in files:
                    if self._should_skip_file(file):
                        continue
                    
                    # Check if file matches any pattern
                    if not any(file.endswith(p.replace('*', '')) for p in patterns if p.startswith('*')):
                        continue
                    
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.project_dir)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            for line_num, line in enumerate(f, 1):
                                if search_term.lower() in line.lower():
                                    if rel_path not in results:
                                        results[rel_path] = []
                                    results[rel_path].append({
                                        'line_number': line_num,
                                        'line': line.strip()
                                    })
                    except (OSError, UnicodeDecodeError):
                        continue
            
            return results
        
        @self.mcp.tool()
        def analyze_vscode_llm_chat_dependencies(dependency_type: str = "all") -> dict:
            """
            Analyze dependencies in the VSCode LLM Chat extension project.

            Args:
                dependency_type (str): Type of dependencies to analyze: "npm", "extension", or "all".

            Returns:
                dict: Analysis of dependencies found in the project.
            """
            analysis = {}
            
            if dependency_type in ["npm", "all"]:
                # Analyze package.json
                package_json_path = os.path.join(self.project_dir, "package.json")
                if os.path.exists(package_json_path):
                    try:
                        with open(package_json_path, 'r', encoding='utf-8') as f:
                            package_data = json.load(f)
                            
                            analysis["npm_dependencies"] = {
                                "dependencies": package_data.get("dependencies", {}),
                                "devDependencies": package_data.get("devDependencies", {}),
                                "extensionDependencies": package_data.get("extensionDependencies", []),
                                "extensionPack": package_data.get("extensionPack", [])
                            }
                    except (OSError, json.JSONDecodeError) as e:
                        analysis["npm_dependencies"] = {"error": str(e)}
            
            if dependency_type in ["extension", "all"]:
                # Search for import/require statements
                import_patterns = []
                for root, dirs, files in os.walk(self.project_dir):
                    dirs[:] = [d for d in dirs if not self._should_skip_dir(d)]
                    
                    for file in files:
                        if file.endswith(('.ts', '.js')):
                            file_path = os.path.join(root, file)
                            rel_path = os.path.relpath(file_path, self.project_dir)
                            
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    for line_num, line in enumerate(f, 1):
                                        stripped = line.strip()
                                        if stripped.startswith(('import ', 'require(')) or ' import ' in stripped:
                                            import_patterns.append({
                                                'file': rel_path,
                                                'line': line_num,
                                                'statement': stripped
                                            })
                            except (OSError, UnicodeDecodeError):
                                continue
                
                analysis["import_statements"] = import_patterns
            
            return analysis
        
        @self.mcp.prompt()
        def analyze_vscode_llm_chat_structure() -> str:
            """
            Analyze and explain the structure of the VSCode LLM Chat extension project.

            Returns:
                str: An LLM-generated analysis of the VSCode LLM Chat extension project structure.
            """
            # Get directory structure without content for overview
            # Build directory structure manually since tools aren't registered yet
            is_valid, full_path = self._validate_path(self.project_dir, ".")
            if not is_valid:
                return "Error: Cannot analyze VSCode LLM Chat extension structure"
            
            structure = {}
            for root, dirs, files in os.walk(full_path):
                dirs[:] = [d for d in dirs if not self._should_skip_dir(d)]
                rel_root = os.path.relpath(root, self.project_dir)
                structure[rel_root] = {}
                
                for file_name in files:
                    if not self._should_skip_file(file_name):
                        structure[rel_root][file_name] = "Content not loaded."
            
            # Get key files content for analysis
            key_files = []
            important_files = ["package.json", "README.md", "CHANGELOG.md", "src/extension.ts", "src/extension.js"]
            
            for file in important_files:
                file_is_valid, file_full_path = self._validate_path(self.project_dir, file)
                if file_is_valid and os.path.isfile(file_full_path):
                    try:
                        with open(file_full_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            preview = content[:1000] + ('...' if len(content) > 1000 else '')
                            key_files.append(f"\n\n### {file}:\n{preview}")
                    except (OSError, UnicodeDecodeError):
                        key_files.append(f"\n\n### {file}:\nError reading file")
            
            # Get dependency analysis
            deps = analyze_vscode_llm_chat_dependencies("all")
            
            combined_content = f"""Directory structure:
{structure}

Key files content:{''.join(key_files)}

Dependency analysis:
{deps}"""
            
            return f"Analyze and explain the structure of this VSCode LLM Chat extension project. Focus on the purpose, architecture, key files, and dependencies:\n\n{combined_content}"
