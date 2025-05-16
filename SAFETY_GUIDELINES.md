# MCP Server Safety Guidelines

## Important Safety Policies

### File Operations Restrictions

This MCP server implements safety policies for file system operations to prevent accidental data loss:

#### ALLOWED Operations (Executed Immediately)
- **Read files**: Full read access to project files
- **Create files**: Create new files and directories
- **Edit files**: Modify existing file contents (with staging for locked files)
- **Stage changes**: Preview changes before applying them
- **Move files**: Execute move operations with audit logging

#### LOGGED Operations (Require Manual Execution)
- **File renaming**: Creates logs for manual review and execution
- **File deletion**: Creates logs for manual review and execution

### Safety Mechanisms

#### 1. Move Operations (`move_*_path` tools)
```
EXECUTES IMMEDIATELY with logging
```
- Performs the move operation automatically
- Creates an audit log in `logs/{project}/move_completed/`
- Prevents overwriting existing files (returns error)
- Creates destination directories as needed
- Provides detailed audit trail

#### 2. Rename Operations (`rename_*_path` tools)
```
DOES NOT ACTUALLY RENAME FILES!
```
- Creates a detailed log file in `logs/{project}/rename/`
- Includes conflict detection (destination name exists)
- Provides manual commands for execution
- Only changes filename, not directory location
- Requires manual review and execution by the user

#### 3. Delete Operations (`delete_*_path` tools)
```
DOES NOT ACTUALLY DELETE FILES!
```
- Creates a detailed log file in `logs/{project}/deletion/`
- Includes size information and backup reminders
- Provides manual commands for execution
- Requires manual review and execution by the user

#### 4. Locked File Handling
When files are open in other applications:
- Changes are automatically staged in `.staging/{project}/`
- Manual review and application required
- No forced overwrites

### Why These Policies?

1. **Balance Safety with Productivity**: Move operations are common and generally safe when preventing overwrites
2. **Audit Trail**: All operations are logged for review and accountability
3. **Human Oversight**: Destructive operations (delete) and naming changes (rename) require confirmation
4. **Conflict Prevention**: Move operations prevent accidental overwrites
5. **Reversibility**: Rename and delete operations can be reviewed before execution

### Working with Operations

#### For Move Operations:
1. Use `move_*_path` - operation executes immediately
2. Review the generated audit log
3. Move will fail if destination exists (no overwrites)
4. Operation is logged for audit purposes

#### For Rename Operations:
1. Use `rename_*_path` to create a rename log
2. Review the generated log file
3. Check for naming conflicts
4. Execute the rename manually using provided commands
5. Delete the log file after successful completion

#### For Delete Operations:
1. Use `delete_*_path` to create a deletion log
2. Review the generated log file
3. Backup if necessary
4. Execute the deletion manually using provided commands
5. Delete the log file after successful completion

#### Viewing Operations:
- `list_*_moves`: See completed moves and any legacy staged operations
- `list_*_renames`: See all staged rename operations
- `list_*_deletions`: See all staged delete operations

### Best Practices

1. **Check destination paths** before moving files
2. **Review audit logs** periodically for move operations
3. **Always review logs** before executing renames/deletions
4. **Check for conflicts** on rename operations
5. **Backup important files** before deletion
6. **Use descriptive filenames** when renaming
7. **Clean up log files** after successful execution of manual operations

### Log File Locations

```
project_root/
├── logs/
│   ├── mcp/
│   │   ├── move_completed/  # Completed move audit logs
│   │   ├── rename/          # MCP project rename logs
│   │   └── deletion/        # MCP project deletion logs
│   └── vscode_llm_chat/
│       ├── move_completed/  # Completed move audit logs
│       ├── rename/          # Extension project rename logs
│       └── deletion/        # Extension project deletion logs
└── .staging/
    ├── mcp/            # Staged MCP file changes
    └── vscode_llm_chat/ # Staged extension file changes
```

### Operation Types Comparison

| Operation | Execution | Log Location | Purpose | Overwrites |
|-----------|-----------|-------------|----------|------------|
| **Move** | IMMEDIATE | `/logs/{project}/move_completed/` | Change location and/or filename | NO (error if exists) |
| **Rename** | MANUAL | `/logs/{project}/rename/` | Change filename only | NO (logged if conflict) |
| **Delete** | MANUAL | `/logs/{project}/deletion/` | Remove files/directories | N/A |

### Move Operation Safety Features

- **No Overwrites**: Move fails if destination exists
- **Directory Creation**: Creates destination directories as needed
- **Audit Logging**: Every move is logged with timestamp and details
- **Error Handling**: Clear error messages for invalid operations
- **Cross-Platform**: Works consistently on Windows and Unix systems

## Remember

**The MCP server balances safety with productivity:**
- Move operations execute immediately (common workflow need) but are logged
- Destructive operations (delete) require manual confirmation
- Naming changes (rename) require manual confirmation
- All operations maintain audit trails
- No accidental overwrites are possible

When you see operations marked as "completed" vs "staged", completed operations have already been executed and logged for audit purposes.
