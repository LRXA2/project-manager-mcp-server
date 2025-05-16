import os
import json
import datetime
import shutil
from abc import ABC, abstractmethod
from typing import Dict, Tuple, Any
from mcp.server.fastmcp import FastMCP
from tools.skip_patterns import SKIP_DIRS, SKIP_FILES, SKIP_EXTENSIONS

class BaseProjectManager(ABC):
    """Base class for managing files within a specific project directory"""
    
    def __init__(self, base_dir: str, project_dir: str, mcp_instance: FastMCP, project_name: str):
        """
        Initialize the BaseProjectManager
        
        Args:
            base_dir: The base directory of the MCP server project
            project_dir: The absolute path to the project directory to manage
            mcp_instance: The FastMCP instance to register tools with
            project_name: Name of the project (for tool names and error messages)
        """
        self.base_dir = base_dir
        self.project_dir = project_dir
        self.mcp = mcp_instance
        self.project_name = project_name
        
        # Validate that the project directory exists
        if not os.path.exists(self.project_dir):
            raise ValueError(f"{self.project_name} directory not found: {self.project_dir}")
    
    @staticmethod
    def _validate_path(project_dir: str, relative_path: str) -> Tuple[bool, str]:
        """
        Validate that a path is within the project directory.
        
        Args:
            project_dir: The base directory of the project
            relative_path: The relative path to validate
        
        Returns:
            tuple: (is_valid, full_path)
        """
        try:
            full_path = os.path.abspath(os.path.join(project_dir, relative_path))
            if not full_path.startswith(project_dir):
                return False, ""
            return True, full_path
        except:
            return False, ""
    
    def _should_skip_dir(self, dir_name: str) -> bool:
        """Check if a directory should be skipped."""
        return dir_name in SKIP_DIRS or dir_name.startswith('.')
    
    def _should_skip_file(self, file_name: str) -> bool:
        """Check if a file should be skipped."""
        # Check exact matches
        if file_name in SKIP_FILES:
            return True
            
        # Check file extensions
        _, ext = os.path.splitext(file_name)
        if ext in SKIP_EXTENSIONS:
            return True
            
        # Check patterns (simple glob-like matching)
        for pattern in SKIP_FILES:
            if pattern.startswith('*') and file_name.endswith(pattern[1:]):
                return True
        return False
    
    @staticmethod
    def _is_file_editable(file_path: str) -> bool:
        """
        Check if a file is currently editable (not locked/open in another process).
        
        Args:
            file_path: The full path to the file
            
        Returns:
            bool: True if the file can be edited, False otherwise
        """
        if not os.path.exists(file_path):
            return True  # New files can always be created
        
        try:
            # Try to open the file in append mode (least invasive)
            # This will fail if the file is locked/open in exclusive mode
            with open(file_path, 'a') as f:
                pass
            return True
        except (PermissionError, OSError):
            return False
    
    def _stage_file_with_content(self, relative_path: str, new_content: str) -> str:
        """
        Helper method to stage a file with given content.
        
        Args:
            relative_path: The relative path to the file
            new_content: The content to stage
            
        Returns:
            str: Confirmation message
        """
        # Validate path
        is_valid, _ = self._validate_path(self.project_dir, relative_path)
        if not is_valid:
            return f"Error: Invalid path or access denied for '{relative_path}'"
        
        try:
            # Create staging directory structure
            staging_subdir = self.get_staging_subdir()
            staging_dir = os.path.join(self.base_dir, ".staging", staging_subdir)
            staged_file_path = os.path.join(staging_dir, relative_path)
            staged_parent_dir = os.path.dirname(staged_file_path)
            
            # Create necessary directories
            os.makedirs(staged_parent_dir, exist_ok=True)
            
            # Write the new content to staged file
            with open(staged_file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            
            return f"{self.project_name} file staged successfully at .staging/{staging_subdir}/{relative_path}\nFile was open/locked, so changes were staged for manual review."
        
        except OSError as e:
            return f"Error staging {self.project_name} file: {e}"
    
    def _mark_for_deletion(self, relative_path: str, is_directory: bool = False) -> str:
        """
        Mark a file or directory for deletion by creating a deletion log.
        
        Args:
            relative_path: The relative path to mark for deletion
            is_directory: Whether the path is a directory
            
        Returns:
            str: Confirmation message
        """
        # Validate path
        is_valid, full_path = self._validate_path(self.project_dir, relative_path)
        if not is_valid:
            return f"Error: Invalid path or access denied for '{relative_path}'"
        
        # Check if path exists
        if not os.path.exists(full_path):
            return f"Error: Path not found: {relative_path}"
        
        # Verify the type matches
        if is_directory and not os.path.isdir(full_path):
            return f"Error: Path is not a directory: {relative_path}"
        elif not is_directory and not os.path.isfile(full_path):
            return f"Error: Path is not a file: {relative_path}"
        
        try:
            # Create deletion log directory in logs/{project}/deletion/
            staging_subdir = self.get_staging_subdir()
            deletion_log_dir = os.path.join(self.base_dir, "logs", staging_subdir, "deletion")
            os.makedirs(deletion_log_dir, exist_ok=True)
            
            # Create deletion log entry
            timestamp = datetime.datetime.now().isoformat()
            deletion_entry = {
                "timestamp": timestamp,
                "path": relative_path,
                "full_path": full_path,
                "type": "directory" if is_directory else "file",
                "size": self._get_size_info(full_path, is_directory),
                "confirmed": False
            }
            
            # Generate log file name
            safe_path = relative_path.replace('/', '_').replace('\\', '_')
            log_file = f"deletion_{timestamp.split('T')[0]}_{safe_path}.md"
            log_path = os.path.join(deletion_log_dir, log_file)
            
            # Create markdown content
            markdown_content = f"""# Deletion Log: {relative_path}

## Summary
- **Path**: `{relative_path}`
- **Type**: {deletion_entry['type']}
- **Marked for deletion**: {timestamp}
- **Status**: Pending manual confirmation

## Details
```json
{json.dumps(deletion_entry, indent=2)}
```

## Manual Steps Required
1. **Review this log** to confirm deletion is intended
2. **Backup if needed** - ensure any important data is saved
3. **Execute deletion**:
   ```bash
   # For files:
   rm "{relative_path}"
   
   # For directories:
   rm -rf "{relative_path}"
   ```
4. **Remove this log file** after successful deletion:
   ```bash
   rm "{log_path}"
   ```

## Size Information
{self._format_size_info(deletion_entry['size'])}

---
*Deletion log created by MCP VSCode LLM Chat Editor*
"""
            
            # Write deletion log
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            return f"{self.project_name} {'directory' if is_directory else 'file'} '{relative_path}' marked for deletion.\nDeletion log: logs/{staging_subdir}/deletion/{log_file}\nPlease review and manually delete when ready."
        
        except OSError as e:
            return f"Error marking {self.project_name} path for deletion: {e}"
    
    def _stage_rename_operation(self, old_path: str, new_name: str) -> str:
        """
        Stage a rename operation by creating a rename log.
        
        Args:
            old_path: Current path relative to project directory
            new_name: New filename (without directory path)
            
        Returns:
            str: Confirmation message
        """
        # Validate old path
        old_valid, old_full = self._validate_path(self.project_dir, old_path)
        if not old_valid:
            return f"Error: Invalid path or access denied for '{old_path}'"
        
        # Check if source exists
        if not os.path.exists(old_full):
            return f"Error: File not found: {old_path}"
        
        # Construct new path (same directory, new filename)
        old_dir = os.path.dirname(old_path)
        new_path = os.path.join(old_dir, new_name) if old_dir else new_name
        new_valid, new_full = self._validate_path(self.project_dir, new_path)
        
        if not new_valid:
            return f"Error: Invalid destination path for '{new_path}'"
        
        try:
            # Create rename log directory
            staging_subdir = self.get_staging_subdir()
            rename_log_dir = os.path.join(self.base_dir, "logs", staging_subdir, "rename")
            os.makedirs(rename_log_dir, exist_ok=True)
            
            # Create rename log entry
            timestamp = datetime.datetime.now().isoformat()
            is_directory = os.path.isdir(old_full)
            
            rename_entry = {
                "timestamp": timestamp,
                "old_path": old_path,
                "old_full_path": old_full,
                "new_path": new_path,
                "new_full_path": new_full,
                "new_name": new_name,
                "type": "directory" if is_directory else "file",
                "size": self._get_size_info(old_full, is_directory),
                "dest_exists": os.path.exists(new_full),
                "confirmed": False,
                "conflict": os.path.exists(new_full)
            }
            
            # Generate log file name
            safe_old = old_path.replace('/', '_').replace('\\', '_').replace('.', '_')
            safe_new = new_name.replace('/', '_').replace('\\', '_').replace('.', '_')
            log_file = f"rename_{timestamp.split('T')[0]}_{safe_old}_to_{safe_new}.md"
            log_path = os.path.join(rename_log_dir, log_file)
            
            # Create markdown content
            markdown_content = f"""# Rename Operation Log: {old_path} → {new_name}

## Summary
- **Current name**: `{os.path.basename(old_path)}`
- **New name**: `{new_name}`
- **Full path**: `{old_path}` → `{new_path}`
- **Type**: {rename_entry['type']}
- **Staged**: {timestamp}
- **Status**: Pending manual execution
- **Conflict**: {'WARNING - YES - Destination exists!' if rename_entry['conflict'] else 'No conflicts'}

## Details
```json
{json.dumps(rename_entry, indent=2)}
```

## Manual Steps Required

### 1. Review Rename Operation
- **Current**: `{old_path}`
- **New**: `{new_path}`
- **Conflict**: {'WARNING - YES (will overwrite existing)' if rename_entry['conflict'] else 'NO (safe to rename)'}

### 2. Handle Conflicts (if any)
{f'''WARNING: Destination `{new_path}` already exists!
- **Backup existing file** if needed:
  ```bash
  cp "{new_path}" "{new_path}.backup"
  ```
- **Or choose a different name** and update this log
''' if rename_entry['conflict'] else 'No conflicts detected - safe to proceed'}

### 3. Execute Rename
```bash
# Standard rename/move command:
mv "{old_path}" "{new_path}"

# Git-aware rename (if this is a git repository):
# git mv "{old_path}" "{new_path}"
```

### 4. Remove This Log
After successful rename:
```bash
rm "{log_path}"
```

## Size Information
{self._format_size_info(rename_entry['size'])}

## Notes
- This operation renames the file/directory while keeping it in the same location
- Only the filename changes, not the directory path
- Be careful with file extensions when renaming files

---
*Rename log created by MCP VSCode LLM Chat Editor*
"""
            
            # Write rename log
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            result = f"{self.project_name} {'directory' if is_directory else 'file'} '{old_path}' staged for rename to '{new_name}'.\n"
            result += f"Rename log: logs/{staging_subdir}/rename/{log_file}\n"
            
            if rename_entry["conflict"]:
                result += f"WARNING: Destination already exists!\n"
            
            result += "Please review and manually perform the rename when ready."
            
            return result
        
        except OSError as e:
            return f"Error staging rename operation: {e}"
    
    def _move_with_logging(self, source_relative: str, dest_relative: str) -> str:
        """
        Perform a move operation and log it for audit trail.
        
        Args:
            source_relative: Source path relative to project directory
            dest_relative: Destination path relative to project directory
            
        Returns:
            str: Confirmation message
        """
        # Validate paths
        source_valid, source_full = self._validate_path(self.project_dir, source_relative)
        dest_valid, dest_full = self._validate_path(self.project_dir, dest_relative)
        
        if not source_valid:
            return f"Error: Invalid source path or access denied for '{source_relative}'"
        if not dest_valid:
            return f"Error: Invalid destination path or access denied for '{dest_relative}'"
        
        # Check if source exists
        if not os.path.exists(source_full):
            return f"Error: Source not found: {source_relative}"
        
        # Check for destination conflict
        if os.path.exists(dest_full):
            return f"Error: Destination already exists: {dest_relative}. Cannot overwrite existing files."
        
        try:
            # Create the destination directory if it doesn't exist
            dest_parent = os.path.dirname(dest_full)
            if dest_parent:
                os.makedirs(dest_parent, exist_ok=True)
            
            # Record information before move
            timestamp = datetime.datetime.now().isoformat()
            is_directory = os.path.isdir(source_full)
            size_info = self._get_size_info(source_full, is_directory)
            
            # Perform the actual move
            shutil.move(source_full, dest_full)
            
            # Create audit log after successful move
            staging_subdir = self.get_staging_subdir()
            move_log_dir = os.path.join(self.base_dir, "logs", staging_subdir, "move_completed")
            os.makedirs(move_log_dir, exist_ok=True)
            
            # Create move log entry
            move_entry = {
                "timestamp": timestamp,
                "source_path": source_relative,
                "dest_path": dest_relative,
                "type": "directory" if is_directory else "file",
                "size": size_info,
                "status": "completed",
                "operation": "move"
            }
            
            # Generate log file name
            safe_source = source_relative.replace('/', '_').replace('\\', '_')
            safe_dest = dest_relative.replace('/', '_').replace('\\', '_')
            log_file = f"move_{timestamp.split('T')[0]}_{safe_source}_to_{safe_dest}.md"
            log_path = os.path.join(move_log_dir, log_file)
            
            # Create markdown content
            markdown_content = f"""# Move Operation Completed: {source_relative} → {dest_relative}

## Summary
- **Source**: `{source_relative}`
- **Destination**: `{dest_relative}`
- **Type**: {move_entry['type']}
- **Completed**: {timestamp}
- **Status**: Successfully moved

## Details
```json
{json.dumps(move_entry, indent=2)}
```

## Operation Results
- **Move completed successfully**
- **Source location**: {source_relative} (no longer exists)
- **New location**: {dest_relative}

## Size Information
{self._format_size_info(size_info)}

## Notes
- This operation was completed automatically and logged for audit purposes
- The file/directory has been successfully moved to the new location
- This log serves as an audit trail of the operation

---
*Move operation log created by MCP VSCode LLM Chat Editor*
"""
            
            # Write move log
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            result = f"SUCCESS: {self.project_name} {'directory' if is_directory else 'file'} successfully moved:\n"
            result += f"   From: {source_relative}\n"
            result += f"   To: {dest_relative}\n"
            result += f"   Audit log: logs/{staging_subdir}/move_completed/{log_file}"
            
            return result
        
        except OSError as e:
            return f"Error moving {self.project_name} path: {e}"
        except Exception as e:
            return f"Unexpected error during move operation: {e}"
    
    def _format_size_info(self, size_info: Dict[str, Any]) -> str:
        """Format size information for display in markdown logs."""
        if 'error' in size_info:
            return f"- **Size**: Unable to determine ({size_info['error']})"
        
        if size_info['type'] == 'directory':
            total_mb = size_info.get('total_size_bytes', 0) / (1024 * 1024)
            return f"""- **Total size**: {total_mb:.2f} MB ({size_info.get('total_size_bytes', 0):,} bytes)
- **File count**: {size_info.get('file_count', 0)} files"""
        else:
            size_mb = size_info.get('size_bytes', 0) / (1024 * 1024)
            return f"- **Size**: {size_mb:.2f} MB ({size_info.get('size_bytes', 0):,} bytes)"
    
    def _get_size_info(self, full_path: str, is_directory: bool) -> Dict[str, Any]:
        """Get size information for a file or directory."""
        try:
            if is_directory:
                total_size = 0
                file_count = 0
                for root, dirs, files in os.walk(full_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            total_size += os.path.getsize(file_path)
                            file_count += 1
                        except OSError:
                            pass
                return {
                    "total_size_bytes": total_size,
                    "file_count": file_count,
                    "type": "directory"
                }
            else:
                size = os.path.getsize(full_path)
                return {
                    "size_bytes": size,
                    "type": "file"
                }
        except OSError:
            return {"error": "Unable to get size information"}
    
    @abstractmethod
    def get_tool_prefix(self) -> str:
        """Return the prefix for tool names (e.g., 'mcp', 'extension')"""
        pass
    
    @abstractmethod
    def get_staging_subdir(self) -> str:
        """Return the subdirectory name for staging (e.g., 'mcp', 'extension')"""
        pass
    
    def _register_read_file_tool(self):
        """Register the read file tool"""
        tool_name = f"read_{self.get_tool_prefix()}_file"
        
        @self.mcp.tool(name=tool_name)
        def read_file(relative_path: str) -> str:
            f"""
            Read any file in the {self.project_name} project directory.
            
            Args:
                relative_path (str): The relative path from the {self.project_name} project directory root.
            
            Returns:
                str: The content of the file or an error message.
            """
            is_valid, full_path = self._validate_path(self.project_dir, relative_path)
            if not is_valid:
                return f"Error: Invalid path or access denied for '{relative_path}'"
            
            try:
                # Check if file exists
                if not os.path.isfile(full_path):
                    return f"Error: File not found at path: {relative_path}"
                
                # Read the file
                with open(full_path, "r", encoding="utf-8") as f:
                    return f.read()
                    
            except OSError as e:
                return f"Error reading file at '{relative_path}': {e}"
            except UnicodeDecodeError as e:
                return f"Error: Cannot read file '{relative_path}' as text. It might be a binary file: {e}"
        
        return read_file
    
    def _register_edit_file_tool(self):
        """Register the edit file tool with automatic staging for locked files"""
        tool_name = f"edit_{self.get_tool_prefix()}_file"
        
        @self.mcp.tool(name=tool_name)
        def edit_file(relative_path: str, new_content: str, mode: str = "replace") -> str:
            f"""
            Edit any file in the {self.project_name} project directory.
            If the file is open/locked in another application, changes will be automatically staged for manual review.

            Args:
                relative_path (str): The relative path from the {self.project_name} project directory root.
                new_content (str): The content to write or append.
                mode (str): 'replace' to overwrite the file, 'append' to add to the end. Defaults to 'replace'.

            Returns:
                str: Confirmation message or staging notification.
            """
            if mode not in ["replace", "append"]:
                return "Invalid mode. Use 'replace' or 'append'."
            
            is_valid, full_path = self._validate_path(self.project_dir, relative_path)
            if not is_valid:
                return f"Error: Invalid path or access denied for '{relative_path}'"

            # Check if file is editable
            if not self._is_file_editable(full_path):
                # File is locked/open, stage the changes instead
                if mode == "append" and os.path.exists(full_path):
                    # For append mode, we need to read existing content first
                    try:
                        with open(full_path, "r", encoding="utf-8") as f:
                            existing_content = f.read()
                        combined_content = existing_content + "\n" + new_content
                        return self._stage_file_with_content(relative_path, combined_content)
                    except (OSError, UnicodeDecodeError):
                        return f"Error: Cannot read existing content for append mode. File is locked/open in another application."
                else:
                    return self._stage_file_with_content(relative_path, new_content)

            try:
                # Create parent directories if they don't exist
                parent_dir = os.path.dirname(full_path)
                os.makedirs(parent_dir, exist_ok=True)
                
                file_mode = "w" if mode == "replace" else "a"
                
                with open(full_path, file_mode, encoding="utf-8") as f:
                    f.write(new_content)
                    if mode == "append":
                        f.write("\n")  # Ensure clean line endings when appending
                
                return f"{self.project_name} file '{relative_path}' successfully updated with mode '{mode}'."
            except OSError as e:
                # If we get an error here, the file might have become locked between checks
                # Fall back to staging
                if "being used by another process" in str(e) or "Permission denied" in str(e):
                    return self._stage_file_with_content(relative_path, new_content)
                else:
                    return f"Error editing {self.project_name} file '{relative_path}': {e}"
        
        return edit_file
    
    def _register_create_path_tool(self):
        """Register the create path tool"""
        tool_name = f"create_{self.get_tool_prefix()}_path"
        
        @self.mcp.tool(name=tool_name)
        def create_path(relative_path: str, is_folder: bool = False, content: str = "") -> str:
            f"""
            Create a new folder or file in the {self.project_name} project directory.

            Args:
                relative_path (str): The relative path from the {self.project_name} project directory root.
                is_folder (bool): If True, create a folder. If False, create a file. Defaults to False.
                content (str): Initial content to write if creating a file. Ignored if creating a folder.

            Returns:
                str: Confirmation message or error.
            """
            is_valid, full_path = self._validate_path(self.project_dir, relative_path)
            if not is_valid:
                return f"Error: Invalid path or access denied for '{relative_path}'"

            try:
                if is_folder:
                    os.makedirs(full_path, exist_ok=True)
                    return f"{self.project_name} folder created at: {relative_path}"
                else:
                    parent_dir = os.path.dirname(full_path)
                    os.makedirs(parent_dir, exist_ok=True)
                    with open(full_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    return f"{self.project_name} file created at: {relative_path}"
            except OSError as e:
                return f"Error creating {self.project_name} path: {e}"
        
        return create_path
    
    def _register_rename_path_tool(self):
        """Register the safe rename tool that stages rename operations"""
        tool_name = f"rename_{self.get_tool_prefix()}_path"
        
        @self.mcp.tool(name=tool_name)
        def rename_path(old_path: str, new_name: str) -> str:
            f"""
            IMPORTANT: This does NOT actually rename files/directories!
            
            Stage a rename operation for a file or directory in the {self.project_name} project.
            Creates a detailed log for manual review and execution by the user.
            
            SAFETY POLICY: Direct file system renames are logged for safety reasons.
            All rename operations must be manually reviewed and executed by the user.

            Args:
                old_path (str): Current relative path from the {self.project_name} project directory root.
                new_name (str): New filename (just the name, not the full path).

            Returns:
                str: Confirmation that the rename operation was staged with log location.
                
            Example: rename_path("old_file.txt", "new_file.txt") creates a log for manual review.
            Note: This only changes the filename, not the directory location.
            """
            return self._stage_rename_operation(old_path, new_name)
        
        return rename_path
    
    def _register_list_renames_tool(self):
        """Register tool to list all staged rename operations"""
        tool_name = f"list_{self.get_tool_prefix()}_renames"
        
        @self.mcp.tool(name=tool_name)
        def list_renames() -> str:
            f"""
            List all files and directories staged for renaming in the {self.project_name} project.

            Returns:
                str: A formatted list of items staged for renaming.
            """
            staging_subdir = self.get_staging_subdir()
            rename_log_dir = os.path.join(self.base_dir, "logs", staging_subdir, "rename")
            
            if not os.path.exists(rename_log_dir):
                return f"No items staged for renaming in {self.project_name} project."
            
            rename_files = [f for f in os.listdir(rename_log_dir) if f.startswith('rename_') and f.endswith('.md')]
            
            if not rename_files:
                return f"No items staged for renaming in {self.project_name} project."
            
            result = f"Items staged for renaming in {self.project_name} project:\n\n"
            
            for rename_file in sorted(rename_files):
                try:
                    with open(os.path.join(rename_log_dir, rename_file), 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract information from markdown content
                    lines = content.split('\n')
                    old_name = new_name = file_type = timestamp = ""
                    conflict = False
                    
                    for line in lines:
                        if line.startswith('- **Current name**:'):
                            old_name = line.split('`')[1]
                        elif line.startswith('- **New name**:'):
                            new_name = line.split('`')[1]
                        elif line.startswith('- **Type**:'):
                            file_type = line.split(': ')[1]
                        elif line.startswith('- **Staged**:'):
                            timestamp = line.split(': ')[1]
                        elif 'WARNING - YES - Destination exists!' in line:
                            conflict = True
                    
                    result += f"FILE: {old_name} → {new_name} ({file_type})\n"
                    result += f"   Staged: {timestamp}\n"
                    
                    if conflict:
                        result += f"   WARNING: Destination exists!\n"
                    
                    result += f"   Log: logs/{staging_subdir}/rename/{rename_file}\n\n"
                except (OSError, IndexError) as e:
                    result += f"ERROR reading {rename_file}: {e}\n\n"
            
            result += f"Review these renames in the log directory:\n"
            result += f"logs/{staging_subdir}/rename/\n\n"
            result += "NOTE: After manual verification, perform the renames and remove their .md log files."
            
            return result
        
        return list_renames
    
    def _register_move_path_tool(self):
        """Register the move tool that executes moves with logging"""
        tool_name = f"move_{self.get_tool_prefix()}_path"
        
        @self.mcp.tool(name=tool_name)
        def move_path(source_path: str, dest_path: str) -> str:
            f"""
            Move a file or directory in the {self.project_name} project with audit logging.
            
            This operation executes immediately but creates an audit log for tracking.
            Will not overwrite existing files - returns error if destination exists.

            Args:
                source_path (str): The current relative path from the {self.project_name} project directory root.
                dest_path (str): The destination relative path from the {self.project_name} project directory root.

            Returns:
                str: Confirmation of successful move with audit log location.
                
            Example: move_path("old_dir/file.txt", "new_dir/file.txt") moves the file and logs the operation.
            """
            return self._move_with_logging(source_path, dest_path)
        
        return move_path
    
    def _register_list_moves_tool(self):
        """Register tool to list all move operations (completed and any staged)"""
        tool_name = f"list_{self.get_tool_prefix()}_moves"
        
        @self.mcp.tool(name=tool_name)
        def list_moves() -> str:
            f"""
            List all move operations (completed and any remaining staged) in the {self.project_name} project.

            Returns:
                str: A formatted list of move operations.
            """
            staging_subdir = self.get_staging_subdir()
            move_log_dir = os.path.join(self.base_dir, "logs", staging_subdir, "move")
            completed_log_dir = os.path.join(self.base_dir, "logs", staging_subdir, "move_completed")
            
            result_parts = []
            
            # Check for completed moves
            if os.path.exists(completed_log_dir):
                completed_files = [f for f in os.listdir(completed_log_dir) if f.startswith('move_') and f.endswith('.md')]
                if completed_files:
                    result_parts.append(f"Recently completed moves in {self.project_name} project:\n")
                    for move_file in sorted(completed_files)[-5:]:  # Show last 5
                        try:
                            with open(os.path.join(completed_log_dir, move_file), 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            # Extract information from markdown
                            lines = content.split('\n')
                            source = dest = move_type = timestamp = ""
                            
                            for line in lines:
                                if line.startswith('- **Source**:'):
                                    source = line.split('`')[1]
                                elif line.startswith('- **Destination**:'):
                                    dest = line.split('`')[1]
                                elif line.startswith('- **Type**:'):
                                    move_type = line.split(': ')[1]
                                elif line.startswith('- **Completed**:'):
                                    timestamp = line.split(': ')[1]
                            
                            result_parts.append(f"SUCCESS: {source} → {dest} ({move_type})")
                            result_parts.append(f"   Completed: {timestamp[:16]}")
                            result_parts.append(f"   Log: logs/{staging_subdir}/move_completed/{move_file}\n")
                        except (OSError, IndexError) as e:
                            result_parts.append(f"ERROR reading {move_file}: {e}\n")
            
            # Check for any remaining staged moves (old system)
            if os.path.exists(move_log_dir):
                staged_files = [f for f in os.listdir(move_log_dir) if f.startswith('move_') and f.endswith('.md')]
                if staged_files:
                    result_parts.append(f"\nWARNING: Legacy staged moves (require manual execution):\n")
                    for move_file in sorted(staged_files):
                        try:
                            with open(os.path.join(move_log_dir, move_file), 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            # Extract information from markdown
                            lines = content.split('\n')
                            source = dest = move_type = timestamp = ""
                            conflict = False
                            
                            for line in lines:
                                if line.startswith('- **Source**:'):
                                    source = line.split('`')[1]
                                elif line.startswith('- **Destination**:'):
                                    dest = line.split('`')[1]
                                elif line.startswith('- **Type**:'):
                                    move_type = line.split(': ')[1]
                                elif line.startswith('- **Staged**:'):
                                    timestamp = line.split(': ')[1]
                                elif 'WARNING - YES - Destination exists!' in line:
                                    conflict = True
                            
                            result_parts.append(f"FILE: {source} → {dest} ({move_type})")
                            result_parts.append(f"   Staged: {timestamp[:16]}")
                            
                            if conflict:
                                result_parts.append(f"   WARNING: Destination exists!")
                            
                            result_parts.append(f"   Log: logs/{staging_subdir}/move/{move_file}\n")
                        except (OSError, IndexError) as e:
                            result_parts.append(f"ERROR reading {move_file}: {e}\n")
            
            if not result_parts:
                return f"No move operations found in {self.project_name} project."
            
            return "\n".join(result_parts)
        
        return list_moves
    
    def _register_delete_path_tool(self):
        """Register the safe delete tool that marks items for deletion"""
        tool_name = f"delete_{self.get_tool_prefix()}_path"
        
        @self.mcp.tool(name=tool_name)
        def delete_path(relative_path: str) -> str:
            f"""
            IMPORTANT: This does NOT actually delete files/directories!
            
            Mark a file or directory for deletion in the {self.project_name} project.
            Creates a detailed log for manual review and execution by the user.
            
            SAFETY POLICY: Direct file system deletions are not allowed for safety reasons.
            All delete operations must be manually reviewed and executed by the user.

            Args:
                relative_path (str): The relative path from the {self.project_name} project directory root.

            Returns:
                str: Confirmation that the item was marked for deletion with log location.
                
            Example: delete_path("temp_file.txt") creates a log for manual review and deletion.
            """
            is_valid, full_path = self._validate_path(self.project_dir, relative_path)
            if not is_valid:
                return f"Error: Invalid path or access denied for '{relative_path}'"
            
            if not os.path.exists(full_path):
                return f"Error: Path not found: {relative_path}"
            
            # Determine if it's a directory or file
            is_directory = os.path.isdir(full_path)
            
            return self._mark_for_deletion(relative_path, is_directory)
        
        return delete_path
    
    def _register_list_deletions_tool(self):
        """Register tool to list all items marked for deletion"""
        tool_name = f"list_{self.get_tool_prefix()}_deletions"
        
        @self.mcp.tool(name=tool_name)
        def list_deletions() -> str:
            f"""
            List all files and directories marked for deletion in the {self.project_name} project.

            Returns:
                str: A formatted list of items marked for deletion.
            """
            staging_subdir = self.get_staging_subdir()
            deletion_log_dir = os.path.join(self.base_dir, "logs", staging_subdir, "deletion")
            
            if not os.path.exists(deletion_log_dir):
                return f"No items marked for deletion in {self.project_name} project."
            
            deletion_files = [f for f in os.listdir(deletion_log_dir) if f.startswith('deletion_') and f.endswith('.md')]
            
            if not deletion_files:
                return f"No items marked for deletion in {self.project_name} project."
            
            result = f"Items marked for deletion in {self.project_name} project:\n\n"
            
            for deletion_file in sorted(deletion_files):
                try:
                    with open(os.path.join(deletion_log_dir, deletion_file), 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract information from markdown content
                    lines = content.split('\n')
                    path = file_type = timestamp = ""
                    
                    for line in lines:
                        if line.startswith('- **Path**:'):
                            path = line.split('`')[1]
                        elif line.startswith('- **Type**:'):
                            file_type = line.split(': ')[1]
                        elif line.startswith('- **Marked for deletion**:'):
                            timestamp = line.split(': ')[1]
                    
                    result += f"FILE: {path} ({file_type})\n"
                    result += f"   Marked: {timestamp}\n"
                    result += f"   Log: logs/{staging_subdir}/deletion/{deletion_file}\n\n"
                except (OSError, IndexError) as e:
                    result += f"ERROR reading {deletion_file}: {e}\n\n"
            
            result += f"Review these items in the log directory:\n"
            result += f"logs/{staging_subdir}/deletion/\n\n"
            result += "NOTE: After manual verification, delete the items and remove their .md log files."
            
            return result
        
        return list_deletions
    
    def _register_read_directory_tool(self):
        """Register the read directory tool"""
        tool_name = f"read_{self.get_tool_prefix()}_directory"
        
        @self.mcp.tool(name=tool_name)
        def read_directory(relative_dir: str = ".", include_content: bool = False) -> Dict[str, Any]:
            f"""
            Recursively read all files and subfolders from the {self.project_name} project directory.
            Excludes common build artifacts and unnecessary directories.

            Args:
                relative_dir (str): The relative directory path from the {self.project_name} project root.
                include_content (bool): If True, read and include file contents.

            Returns:
                dict: A nested dictionary representing the directory structure and optionally file contents.
            """
            is_valid, full_path = self._validate_path(self.project_dir, relative_dir)
            if not is_valid:
                return {"error": f"Invalid path or access denied for '{relative_dir}'"}

            result = {}

            for root, dirs, files in os.walk(full_path):
                # Filter out directories to skip
                dirs[:] = [d for d in dirs if not self._should_skip_dir(d)]
                
                # Make paths relative to project_dir for cleaner output
                rel_root = os.path.relpath(root, self.project_dir)
                result[rel_root] = {}

                # Filter out files to skip
                for file_name in files:
                    if self._should_skip_file(file_name):
                        continue
                        
                    file_path = os.path.join(root, file_name)
                    if include_content:
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                result[rel_root][file_name] = f.read()
                        except OSError as e:
                            result[rel_root][file_name] = f"Error reading file: {e}"
                        except UnicodeDecodeError:
                            result[rel_root][file_name] = "Binary file - content not shown"
                    else:
                        result[rel_root][file_name] = "Content not loaded."

            return result
        
        return read_directory
    
    def _register_stage_file_tool(self):
        """Register the stage file edit tool"""
        tool_name = f"stage_{self.get_tool_prefix()}_file_edit"
        
        @self.mcp.tool(name=tool_name)
        def stage_file_edit(relative_path: str, new_content: str) -> str:
            f"""
            Create a staged version of a {self.project_name} file with new content for manual review.
            
            Args:
                relative_path (str): The relative path to the {self.project_name} file
                new_content (str): The new content to stage
            
            Returns:
                str: Confirmation message with staged file path
            """
            return self._stage_file_with_content(relative_path, new_content)
        
        return stage_file_edit
    
    def register_common_tools(self):
        """Register all common tools that every project manager should have"""
        self._register_read_file_tool()
        self._register_edit_file_tool()
        self._register_create_path_tool()
        self._register_rename_path_tool()
        self._register_list_renames_tool()
        self._register_move_path_tool()
        self._register_list_moves_tool()
        self._register_delete_path_tool()
        self._register_list_deletions_tool()
        self._register_read_directory_tool()
        self._register_stage_file_tool()
    
    @abstractmethod
    def register_specific_tools(self):
        """Register project-specific tools that each implementation should define"""
        pass
    
    def register_tools(self):
        """Register all tools for this project manager"""
        self.register_common_tools()
        self.register_specific_tools()
