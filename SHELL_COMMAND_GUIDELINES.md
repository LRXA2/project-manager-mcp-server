# Shell Command Guidelines

## Important: Use Standard Commands Only

The shell command execution feature is designed to work with **standard, vanilla commands** that are commonly available across different systems. This ensures reliability and prevents issues with custom scripts or advanced shell features.

## Recommended Commands

### File Operations
```bash
# List files and directories
ls -la                    # Unix/Linux/macOS
dir                       # Windows

# Copy files
cp file.txt backup.txt    # Unix/Linux/macOS
copy file.txt backup.txt  # Windows

# Move/rename files
mv old.txt new.txt        # Unix/Linux/macOS
move old.txt new.txt      # Windows

# Remove files
rm file.txt               # Unix/Linux/macOS
del file.txt              # Windows

# Create/remove directories
mkdir new_folder          # Both platforms
rmdir empty_folder        # Both platforms
```

### Navigation
```bash
# Change directory
cd /path/to/directory     # Unix/Linux/macOS
cd C:\path\to\directory   # Windows

# Print current directory
pwd                       # Unix/Linux/macOS
cd                        # Windows (shows current dir)
```

### Text Operations
```bash
# Display file contents
cat file.txt              # Unix/Linux/macOS
type file.txt             # Windows

# Print text
echo "Hello World"        # Both platforms

# Search in files
grep "pattern" file.txt   # Unix/Linux/macOS (if available)
findstr "pattern" file.txt # Windows
```

### Process and System
```bash
# List processes
ps aux                    # Unix/Linux/macOS
tasklist                  # Windows

# Check disk usage
df -h                     # Unix/Linux/macOS
dir                       # Windows (basic info)

# System information
uname -a                  # Unix/Linux/macOS
systeminfo                # Windows
```

### Development Commands
```bash
# Node.js/npm
npm install
npm test
npm run build

# Python
pip install package
python script.py
pytest

# Git (when available)
git status
git add .
git commit -m "message"

# Build tools
make
cargo build
```

## Commands to Avoid

### Complex Shell Features
```bash
# Avoid complex pipes and redirections
command1 | command2 | command3 > file.txt

# Avoid shell scripting constructs
for file in *.txt; do echo $file; done

# Avoid advanced parameter expansion
${variable/pattern/replacement}
```

### Interactive Commands
```bash
# Avoid commands that require user input
sudo command          # Requires password
ssh user@server       # Interactive login
nano file.txt         # Text editor
```

### Non-Standard Utilities
```bash
# Avoid custom aliases or functions
ll                    # Custom alias for ls -la
myCustomScript        # User-defined function

# Avoid advanced tools that might not be installed
jq                    # JSON processor
htop                  # Interactive process viewer
```

### Platform-Specific Advanced Features
```bash
# Avoid PowerShell-specific syntax (use basic commands)
Get-ChildItem | Where-Object { $_.Length -gt 1000 }

# Avoid bash-specific features
command <(another_command)
```

## Best Practices

### 1. Keep Commands Simple
```bash
# Good: Simple, clear commands
ls -la
cd src
npm test

# Avoid: Complex one-liners
find . -name "*.js" -exec grep -l "pattern" {} \; | xargs -I {} mv {} backup/
```

### 2. Use Full Paths When Needed
```bash
# Good: Specify working directory
execute_command("npm test", working_directory="./my-project")

# Good: Use absolute paths when necessary
execute_command("ls /usr/local/bin")
```

### 3. Handle Cross-Platform Differences
```bash
# Check platform in your logic, then use appropriate commands
# Unix: ls -la
# Windows: dir

# Unix: cp file.txt backup.txt
# Windows: copy file.txt backup.txt
```

### 4. Use Appropriate Timeouts
```bash
# Set reasonable timeouts for different operations
execute_command("npm install", timeout_seconds=120)  # Package installation
execute_command("ls", timeout_seconds=5)             # Quick file listing
execute_command("npm test", timeout_seconds=300)     # Running tests
```

### 5. Verify Commands Work
```bash
# Test commands before using them in scripts
# Make sure they work on your target platform
# Consider what happens if the command fails
```

## Common Use Cases

### Project Development
```bash
# Check project status
ls -la
git status

# Install dependencies
npm install
pip install -r requirements.txt

# Run tests
npm test
pytest
cargo test

# Build project
npm run build
python setup.py build
make
```

### File Management
```bash
# Backup important files
cp config.json config.json.backup

# Clean build artifacts
rm -rf node_modules
rm -rf __pycache__

# Create project structure
mkdir -p src/components
mkdir -p tests
```

### Debugging
```bash
# Check what's running
ps aux | grep node
tasklist | findstr "node"

# Check disk space
df -h
dir C:\

# View recent logs
tail -f logfile.txt         # Unix/Linux/macOS
type logfile.txt            # Windows (shows all)
```

## Quick Reference

### Essential Cross-Platform Commands

| Operation | Unix/Linux/macOS | Windows |
|-----------|------------------|---------|
| List files | `ls -la` | `dir` |
| Copy file | `cp src dest` | `copy src dest` |
| Move file | `mv src dest` | `move src dest` |
| Delete file | `rm file` | `del file` |
| Make directory | `mkdir dir` | `mkdir dir` |
| Current directory | `pwd` | `cd` |
| File contents | `cat file` | `type file` |

### Remember
- **Stick to basics**: Use standard commands that work everywhere
- **Test first**: Verify commands work in your environment
- **Keep it simple**: Avoid complex shell scripting
- **Set timeouts**: Prevent commands from hanging
- **Use full paths**: Be explicit about file locations

The goal is reliability and cross-platform compatibility, not showcasing advanced shell features.
