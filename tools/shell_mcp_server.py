# Shell command execution with timeout protection for Project Manager MCP Server
# Implementation inspired by MCP community projects, particularly:
# - https://github.com/odysseus0/mcp-server-shell
# - Thanks to the MCP community for robust subprocess handling patterns

import subprocess
import sys
import os
import time
import threading
from typing import Dict, Union, Optional, Any
from mcp.server.fastmcp import FastMCP


class ShellExecutor:
    """Simple and robust shell command executor with timeout protection."""
    
    def __init__(self):
        self.active_processes = {}
        self.process_lock = threading.Lock()
    
    def execute_command(
        self,
        command: str,
        working_directory: Optional[str] = None,
        timeout_seconds: int = 30,
        shell: str = "default"
    ) -> Dict[str, Any]:
        """Execute a shell command with timeout protection."""
        start_time = time.time()
        
        # Validate working directory
        if working_directory and not os.path.exists(working_directory):
            return {
                "success": False,
                "error": f"Working directory does not exist: {working_directory}",
                "command": command,
                "output": "",
                "stdout": "",
                "stderr": "",
                "return_code": -1,
                "execution_time": 0
            }
        
        # Set up shell command based on platform
        if shell == "default":
            if sys.platform == "win32":
                shell_cmd = ["cmd", "/c", command]
            else:
                shell_cmd = ["/bin/bash", "-c", command]
        else:
            shell_cmd = [shell, "-c", command] if sys.platform != "win32" else ["cmd", "/c", command]
        
        try:
            # Create process with timeout
            process = subprocess.Popen(
                shell_cmd,
                cwd=working_directory,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # Line buffered
                universal_newlines=True
            )
            
            # Track the process
            with self.process_lock:
                self.active_processes[process.pid] = process
            
            try:
                # Wait for completion with timeout
                stdout, stderr = process.communicate(timeout=timeout_seconds)
                
                # Calculate execution time
                execution_time = time.time() - start_time
                
                # Clean up
                with self.process_lock:
                    if process.pid in self.active_processes:
                        del self.active_processes[process.pid]
                
                # Combine output for backward compatibility
                combined_output = stdout
                if stderr:
                    combined_output += f"\n--- STDERR ---\n{stderr}"
                
                return {
                    "success": process.returncode == 0,
                    "command": command,
                    "output": combined_output,
                    "stdout": stdout,
                    "stderr": stderr,
                    "return_code": process.returncode,
                    "execution_time": round(execution_time, 2),
                    "working_directory": working_directory or os.getcwd(),
                    "shell": shell
                }
                
            except subprocess.TimeoutExpired:
                # Handle timeout
                execution_time = time.time() - start_time
                
                # Try to terminate gracefully
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if terminate doesn't work
                    process.kill()
                    process.wait()
                
                # Clean up
                with self.process_lock:
                    if process.pid in self.active_processes:
                        del self.active_processes[process.pid]
                
                return {
                    "success": False,
                    "error": f"Command timed out after {timeout_seconds} seconds",
                    "command": command,
                    "output": f"Command timed out after {timeout_seconds} seconds",
                    "stdout": "",
                    "stderr": "",
                    "return_code": -1,
                    "execution_time": round(execution_time, 2),
                    "working_directory": working_directory or os.getcwd(),
                    "shell": shell,
                    "timeout": True
                }
                
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "command": command,
                "output": f"Error: {str(e)}",
                "stdout": "",
                "stderr": "",
                "return_code": -1,
                "execution_time": round(execution_time, 2),
                "working_directory": working_directory or os.getcwd(),
                "shell": shell,
                "exception": True
            }
    
    def cleanup(self):
        """Clean up any remaining active processes."""
        with self.process_lock:
            for pid, process in list(self.active_processes.items()):
                try:
                    process.terminate()
                    process.wait(timeout=2)
                except:
                    try:
                        process.kill()
                        process.wait()
                    except:
                        pass
            self.active_processes.clear()


class ShellMCPServer:
    """MCP server for standard shell command execution in project development."""
    
    def __init__(self, mcp_instance: FastMCP):
        self.mcp = mcp_instance
        self.executor = ShellExecutor()
    
    def register_tools(self):
        """Register only the standard shell execution tools."""
        
        @self.mcp.tool()
        def execute_command(
            command: str,
            working_directory: Optional[str] = None,
            timeout_seconds: int = 30,
            shell: str = "default"
        ) -> Dict[str, Any]:
            """
            Execute a standard shell command and return its output.
            
            IMPORTANT: Use only standard/vanilla commands that are commonly available.
            Avoid complex commands, advanced shell features, or non-standard utilities.
            
            RECOMMENDED COMMANDS:
            - File operations: ls, dir, cp, copy, mv, move, rm, del, mkdir, rmdir
            - Navigation: cd, pwd
            - Text operations: cat, type, echo, grep, find, sort
            - Process/system: ps, kill, top, df, du
            - Network: ping, curl (if available)
            - Build tools: make, npm, pip, cargo (when in project context)
            
            AVOID:
            - Complex pipes and redirections
            - Advanced shell scripting
            - Non-standard utilities or aliases
            - Interactive commands
            - Commands that require user input
            
            Args:
                command (str): Standard shell command to execute
                working_directory (str, optional): Directory to run the command in
                timeout_seconds (int): Maximum execution time in seconds (default: 30)
                shell (str): Shell to use for execution (default: auto-detect)
            
            Returns:
                dict: Command result containing:
                    - success: Whether the command succeeded
                    - command: The executed command
                    - output: Combined stdout and stderr output
                    - stdout: Standard output only
                    - stderr: Standard error only  
                    - return_code: Command execution return code
                    - execution_time: Time taken to execute
                    - working_directory: Directory where command was run
                    - shell: Shell used for execution
            
            Examples:
                execute_command("ls -la")                    # List files (Unix)
                execute_command("dir", working_directory="C:\\Windows")  # List files (Windows)
                execute_command("echo 'Hello World'")        # Print text
                execute_command("cd src && npm test")        # Change directory and run tests
            """
            return self.executor.execute_command(
                command=command,
                working_directory=working_directory,
                timeout_seconds=timeout_seconds,
                shell=shell
            )
        
        @self.mcp.tool()
        def get_platform_info() -> Dict[str, Any]:
            """
            Get information about the current platform and shell.
            
            Returns:
                dict: Platform information including OS, Python version, and available shells
            """
            try:
                # Get basic platform info
                info = {
                    "platform": sys.platform,
                    "os_name": os.name,
                    "python_version": sys.version,
                    "current_directory": os.getcwd()
                }
                
                # Check available shells
                shells = []
                
                if sys.platform == "win32":
                    shells.append("cmd")
                    # Check for PowerShell
                    try:
                        subprocess.run(["powershell", "-Command", "echo test"], 
                                     capture_output=True, timeout=5)
                        shells.append("powershell")
                    except:
                        pass
                else:
                    # Check for common Unix shells
                    for shell in ["/bin/bash", "/bin/sh", "/bin/zsh", "/bin/fish"]:
                        if os.path.exists(shell):
                            shells.append(shell)
                
                info["available_shells"] = shells
                
                return {
                    "success": True,
                    "platform_info": info
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "platform_info": {
                        "platform": sys.platform,
                        "error": "Failed to get complete platform info"
                    }
                }
    
    def cleanup(self):
        """Clean up resources."""
        self.executor.cleanup()
