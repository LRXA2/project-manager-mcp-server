SKIP_DIRS = {
    # Build output directories
    'out', 'dist', 'build', 'target', '.output',
    
    # Node.js related
    'node_modules', '.npm', 'npm-debug.log*',
    
    # Python related
    '.venv', 'venv', '__pycache__', '.pyc',
    '.tox', '.pytest_cache', '.mypy_cache',
    
    # Version control
    '.git', '.github',
    
    # IDE directories
    '.vscode', '.idea', '.vs', '.vscode-test',
    
    # Coverage and testing
    'coverage', '.coverage', '.nyc_output', 'test-results',
    
    # Cache and temp directories
    '.cache', '.tmp', 'temp', 'templates',
    
    # OS specific
    '.DS_Store', 'Thumbs.db',
    
    # Logs
    # 'logs',
    
    # VSCode extension specific
    '.vscode-test-web',
}

# Files to skip
SKIP_FILES = {
    # Version control
    '.gitattributes',
    
    # Package managers
    'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
    '.npmrc', '.yarnrc',
    
    # Python
    '*.pyc', '*.pyo', '*.pyd', '__pycache__',
    'Pipfile.lock', 'poetry.lock',
    
    # Logs and temporary files
    '*.log', '*.tmp', '*.temp',
    
    # OS specific files
    '.DS_Store', 'Thumbs.db',
    
    # IDE/Editor files
    '.editorconfig', '*.swp', '*.swo',
    
    # Environment files (you might want to include these sometimes)
    '.env', '.env.local', '.env.dev',
    
    # VSCode extension specific
    '*.vsix',
}

# File extensions to skip
SKIP_EXTENSIONS = {
    '.pyc', '.pyo', '.pyd',
    '.log', '.tmp', '.temp',
    '.o', '.obj', '.exe', '.dll',
    '.so', '.dylib',
    '.vsix', '.map',  # VSCode extension package and source maps
}