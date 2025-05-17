"""
Git tools for the MCP server.

This module provides Git repository interaction capabilities through the MCP server,
allowing users to perform Git operations like checking status, viewing logs,
and making commits using the GitPython library.
"""

import os
import traceback
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import git

class GitTools:
    """Provides Git repository operations for the MCP server using GitPython."""
    
    def __init__(self, mcp_instance):
        """
        Initialize the Git tools.
        
        Args:
            mcp_instance: The MCP server instance
        """
        self.mcp = mcp_instance
        self.is_available = self._check_git_availability()
        self.tools_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_dir = os.path.dirname(self.tools_dir)
        self.default_repo_path = os.path.join(self.base_dir, 'mcp-git', 'servers')
        print(f"Git tools initialized with base directory: {self.base_dir}")
        print(f"Default Git repository path: {self.default_repo_path}")
    
    def _check_git_availability(self) -> bool:
        """Check if Git is available on the system."""
        try:
            git_version = git.Git().version()
            print(f"Git is available: {git_version}")
            return True
        except git.GitCommandError:
            print("WARNING: Git is not available on this system")
            return False
    
    def register_tools(self):
        """Register Git tools with the MCP server."""
        if not self.is_available:
            print("WARNING: Cannot register Git tools - Git is not available on this system")
            return False
        
        try:
            # Define a tool for Git status
            @self.mcp.tool()
            def git_status(repo_path: str = None) -> Dict[str, Any]:
                """
                Shows the working tree status of a Git repository.
                
                Args:
                    repo_path (str, optional): Path to the Git repository. 
                                          If None, uses default repository path.
                
                Returns:
                    dict: Information about the repository status
                """
                return self._git_status(repo_path)
            
            # Define a tool for Git log
            @self.mcp.tool()
            def git_log(repo_path: str = None, max_count: int = 10) -> Dict[str, Any]:
                """
                Shows the commit logs of a Git repository.
                
                Args:
                    repo_path (str, optional): Path to the Git repository.
                    max_count (int, optional): Maximum number of commits to show.
                
                Returns:
                    dict: Commit history information
                """
                return self._git_log(repo_path, max_count)
            
            # Define a tool for Git diff
            @self.mcp.tool()
            def git_diff(repo_path: str = None, staged: bool = False) -> Dict[str, Any]:
                """
                Shows changes in the working directory or staging area.
                
                Args:
                    repo_path (str, optional): Path to the Git repository.
                    staged (bool, optional): Show staged changes instead of unstaged.
                
                Returns:
                    dict: Diff information
                """
                return self._git_diff(repo_path, staged)
            
            # Define a tool for Git branch operations
            @self.mcp.tool()
            def git_branch_list(repo_path: str = None) -> Dict[str, Any]:
                """
                Lists branches in a Git repository.
                
                Args:
                    repo_path (str, optional): Path to the Git repository.
                
                Returns:
                    dict: List of branches
                """
                return self._git_branch_list(repo_path)
            
            # Define a tool for Git branch creation
            @self.mcp.tool()
            def git_branch_create(branch_name: str, repo_path: str = None, base_branch: str = None) -> Dict[str, Any]:
                """
                Creates a new branch in a Git repository.
                
                Args:
                    branch_name (str): Name of the branch to create.
                    repo_path (str, optional): Path to the Git repository.
                    base_branch (str, optional): Base branch to create from. Defaults to current branch.
                
                Returns:
                    dict: Result of the branch creation
                """
                return self._git_branch_create(branch_name, repo_path, base_branch)
            
            # Define a tool for Git checkout
            @self.mcp.tool()
            def git_branch_checkout(branch_name: str, repo_path: str = None) -> Dict[str, Any]:
                """
                Switches branches in a Git repository.
                
                Args:
                    branch_name (str): Name of the branch to checkout.
                    repo_path (str, optional): Path to the Git repository.
                
                Returns:
                    dict: Result of the branch checkout
                """
                return self._git_branch_checkout(branch_name, repo_path)
            
            # Define a tool for Git commit
            @self.mcp.tool()
            def git_commit(message: str, repo_path: str = None, add_all: bool = False) -> Dict[str, Any]:
                """
                Records changes to the repository.
                
                Args:
                    message (str): Commit message.
                    repo_path (str, optional): Path to the Git repository.
                    add_all (bool, optional): Add all changes before committing.
                
                Returns:
                    dict: Result of the commit operation
                """
                return self._git_commit(message, repo_path, add_all)
            
            # Define a tool for Git add
            @self.mcp.tool()
            def git_add(file_paths: List[str], repo_path: str = None) -> Dict[str, Any]:
                """
                Adds file contents to the staging area.
                
                Args:
                    file_paths (List[str]): Paths to files to add.
                    repo_path (str, optional): Path to the Git repository.
                
                Returns:
                    dict: Result of the add operation
                """
                return self._git_add(file_paths, repo_path)
            
            # Define a tool for Git init
            @self.mcp.tool()
            def git_init(repo_path: str) -> Dict[str, Any]:
                """
                Initializes a new Git repository.
                
                Args:
                    repo_path (str): Path where to create the repository.
                
                Returns:
                    dict: Result of the initialization
                """
                return self._git_init(repo_path)
            
            # Define a tool for Git show
            @self.mcp.tool()
            def git_show(revision: str, repo_path: str = None) -> Dict[str, Any]:
                """
                Shows the contents of a commit.
                
                Args:
                    revision (str): Commit hash or reference to show.
                    repo_path (str, optional): Path to the Git repository.
                
                Returns:
                    dict: Commit information and diff
                """
                return self._git_show(revision, repo_path)
            
            # Define a tool for Git reset
            @self.mcp.tool()
            def git_reset(repo_path: str = None) -> Dict[str, Any]:
                """
                Unstages all staged changes.
                
                Args:
                    repo_path (str, optional): Path to the Git repository.
                
                Returns:
                    dict: Result of the reset operation
                """
                return self._git_reset(repo_path)
            
            print("Git tools registered successfully")
            return True
        except Exception as e:
            print(f"ERROR: Failed to register Git tools: {e}")
            print(traceback.format_exc())
            return False
    
    def _get_repo(self, repo_path: str = None) -> git.Repo:
        """
        Get a Git repository instance.
        
        Args:
            repo_path (str, optional): Path to the Git repository.
            
        Returns:
            git.Repo: The Git repository instance
            
        Raises:
            git.InvalidGitRepositoryError: If the path is not a valid Git repository
            git.NoSuchPathError: If the path does not exist
        """
        if repo_path is None:
            # If no path is specified, use the default Git repository path
            repo_path = self.default_repo_path
            print(f"Using default repository path: {repo_path}")
        elif not os.path.isabs(repo_path):
            # If a relative path is provided, resolve it relative to base_dir
            repo_path = os.path.join(self.base_dir, repo_path)
            print(f"Resolved relative path to: {repo_path}")
        
        return git.Repo(repo_path)
    
    def _git_status(self, repo_path: str = None) -> Dict[str, Any]:
        """Get the Git repository status."""
        try:
            repo = self._get_repo(repo_path)
            
            # Get current branch
            try:
                current_branch = repo.active_branch.name
            except TypeError:
                # Handle detached HEAD state
                current_branch = "HEAD detached at " + repo.head.object.hexsha[:7]
            
            # Get status information
            changed_files = []
            for item in repo.index.diff(None):  # Unstaged changes
                changed_files.append({
                    "path": item.a_path,
                    "status": "unstaged: modified"
                })
            
            for item in repo.index.diff("HEAD"):  # Staged changes
                changed_files.append({
                    "path": item.a_path,
                    "status": "staged: modified"
                })
            
            for item in repo.untracked_files:  # Untracked files
                changed_files.append({
                    "path": item,
                    "status": "untracked"
                })
            
            # Get human-readable status
            status_message = repo.git.status()
            
            return {
                "success": True,
                "branch": current_branch,
                "changed_files": changed_files,
                "clean": len(changed_files) == 0,
                "status_message": status_message
            }
        except git.InvalidGitRepositoryError:
            return {
                "success": False,
                "error": f"Not a valid Git repository: {repo_path or os.getcwd()}"
            }
        except git.NoSuchPathError:
            return {
                "success": False,
                "error": f"Path does not exist: {repo_path}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting Git status: {str(e)}"
            }
    
    def _git_log(self, repo_path: str = None, max_count: int = 10) -> Dict[str, Any]:
        """Get Git commit history."""
        try:
            repo = self._get_repo(repo_path)
            
            # Get commit history
            commits = []
            for commit in list(repo.iter_commits(max_count=max_count)):
                commits.append({
                    "hash": commit.hexsha,
                    "author_name": commit.author.name,
                    "author_email": commit.author.email,
                    "date": str(datetime.fromtimestamp(commit.committed_date)),
                    "message": commit.message.strip()
                })
            
            return {
                "success": True,
                "commits": commits,
                "total_count": len(commits)
            }
        except git.InvalidGitRepositoryError:
            return {
                "success": False,
                "error": f"Not a valid Git repository: {repo_path or os.getcwd()}"
            }
        except git.NoSuchPathError:
            return {
                "success": False,
                "error": f"Path does not exist: {repo_path}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting Git log: {str(e)}"
            }
    
    def _git_diff(self, repo_path: str = None, staged: bool = False) -> Dict[str, Any]:
        """Get Git diff for modified files."""
        try:
            repo = self._get_repo(repo_path)
            
            # Get diff (staged or unstaged)
            if staged:
                diff_output = repo.git.diff("--cached")
            else:
                diff_output = repo.git.diff()
            
            return {
                "success": True,
                "diff": diff_output
            }
        except git.InvalidGitRepositoryError:
            return {
                "success": False,
                "error": f"Not a valid Git repository: {repo_path or os.getcwd()}"
            }
        except git.NoSuchPathError:
            return {
                "success": False,
                "error": f"Path does not exist: {repo_path}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting Git diff: {str(e)}"
            }
    
    def _git_branch_list(self, repo_path: str = None) -> Dict[str, Any]:
        """List Git branches."""
        try:
            repo = self._get_repo(repo_path)
            
            # Get all branches
            branches = [branch.name for branch in repo.branches]
            
            # Get current branch
            try:
                current_branch = repo.active_branch.name
            except TypeError:
                # Handle detached HEAD state
                current_branch = "HEAD detached at " + repo.head.object.hexsha[:7]
            
            return {
                "success": True,
                "branches": branches,
                "current_branch": current_branch
            }
        except git.InvalidGitRepositoryError:
            return {
                "success": False,
                "error": f"Not a valid Git repository: {repo_path or os.getcwd()}"
            }
        except git.NoSuchPathError:
            return {
                "success": False,
                "error": f"Path does not exist: {repo_path}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error listing Git branches: {str(e)}"
            }
    
    def _git_branch_create(self, branch_name: str, repo_path: str = None, base_branch: str = None) -> Dict[str, Any]:
        """Create a new Git branch."""
        try:
            repo = self._get_repo(repo_path)
            
            # Determine base reference (commit or branch)
            base_ref = None
            if base_branch:
                try:
                    base_ref = repo.refs[base_branch]
                except IndexError:
                    return {
                        "success": False,
                        "error": f"Base branch '{base_branch}' not found"
                    }
            else:
                base_ref = repo.head.commit
            
            # Create the branch
            new_branch = repo.create_head(branch_name, base_ref)
            
            return {
                "success": True,
                "message": f"Branch '{branch_name}' created successfully",
                "branch": branch_name,
                "base": base_branch or repo.head.reference.name
            }
        except git.InvalidGitRepositoryError:
            return {
                "success": False,
                "error": f"Not a valid Git repository: {repo_path or os.getcwd()}"
            }
        except git.NoSuchPathError:
            return {
                "success": False,
                "error": f"Path does not exist: {repo_path}"
            }
        except git.GitCommandError as e:
            return {
                "success": False,
                "error": f"Git error: {e.stderr.strip()}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error creating Git branch: {str(e)}"
            }
    
    def _git_branch_checkout(self, branch_name: str, repo_path: str = None) -> Dict[str, Any]:
        """Checkout a Git branch."""
        try:
            repo = self._get_repo(repo_path)
            
            # Check if branch exists
            if branch_name not in [b.name for b in repo.branches]:
                return {
                    "success": False,
                    "error": f"Branch '{branch_name}' not found"
                }
            
            # Get the branch reference
            branch = repo.branches[branch_name]
            
            # Checkout the branch
            branch.checkout()
            
            return {
                "success": True,
                "message": f"Switched to branch '{branch_name}'",
                "branch": branch_name
            }
        except git.InvalidGitRepositoryError:
            return {
                "success": False,
                "error": f"Not a valid Git repository: {repo_path or os.getcwd()}"
            }
        except git.NoSuchPathError:
            return {
                "success": False,
                "error": f"Path does not exist: {repo_path}"
            }
        except git.GitCommandError as e:
            return {
                "success": False,
                "error": f"Git error: {e.stderr.strip()}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error checking out Git branch: {str(e)}"
            }
    
    def _git_commit(self, message: str, repo_path: str = None, add_all: bool = False) -> Dict[str, Any]:
        """Commit changes to the Git repository."""
        try:
            repo = self._get_repo(repo_path)
            
            # Add all changes if requested
            if add_all:
                repo.git.add(A=True)
            
            # Check if there are staged changes
            if not repo.index.diff("HEAD"):
                return {
                    "success": False,
                    "error": "No changes staged for commit"
                }
            
            # Commit the changes
            commit = repo.index.commit(message)
            
            return {
                "success": True,
                "message": "Changes committed successfully",
                "commit_hash": commit.hexsha,
                "commit_message": message
            }
        except git.InvalidGitRepositoryError:
            return {
                "success": False,
                "error": f"Not a valid Git repository: {repo_path or os.getcwd()}"
            }
        except git.NoSuchPathError:
            return {
                "success": False,
                "error": f"Path does not exist: {repo_path}"
            }
        except git.GitCommandError as e:
            return {
                "success": False,
                "error": f"Git error: {e.stderr.strip()}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error committing changes: {str(e)}"
            }
    
    def _git_add(self, file_paths: List[str], repo_path: str = None) -> Dict[str, Any]:
        """Add files to the Git staging area."""
        try:
            repo = self._get_repo(repo_path)
            
            # Add specified files
            repo.index.add(file_paths)
            
            return {
                "success": True,
                "message": "Files added to staging area",
                "files": file_paths
            }
        except git.InvalidGitRepositoryError:
            return {
                "success": False,
                "error": f"Not a valid Git repository: {repo_path or os.getcwd()}"
            }
        except git.NoSuchPathError:
            return {
                "success": False,
                "error": f"Path does not exist: {repo_path}"
            }
        except git.GitCommandError as e:
            return {
                "success": False,
                "error": f"Git error: {e.stderr.strip()}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error adding files to Git: {str(e)}"
            }
    
    def _git_init(self, repo_path: str) -> Dict[str, Any]:
        """Initialize a new Git repository."""
        try:
            # Handle relative paths
            if not os.path.isabs(repo_path):
                repo_path = os.path.join(self.base_dir, repo_path)
                print(f"Resolved relative init path to: {repo_path}")
                
            # Create directory if it doesn't exist
            os.makedirs(repo_path, exist_ok=True)
            
            # Initialize the repository
            repo = git.Repo.init(repo_path)
            
            return {
                "success": True,
                "message": f"Initialized empty Git repository in {repo_path}",
                "repo_path": repo_path,
                "git_dir": repo.git_dir
            }
        except git.GitCommandError as e:
            return {
                "success": False,
                "error": f"Git error: {e.stderr.strip()}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error initializing Git repository: {str(e)}"
            }
    
    def _git_show(self, revision: str, repo_path: str = None) -> Dict[str, Any]:
        """Show the contents of a commit."""
        try:
            repo = self._get_repo(repo_path)
            
            # Get the commit
            try:
                commit = repo.commit(revision)
            except git.BadName:
                return {
                    "success": False,
                    "error": f"Invalid revision: {revision}"
                }
            
            # Get the diff
            if commit.parents:
                parent = commit.parents[0]
                diff = parent.diff(commit, create_patch=True)
            else:
                # For the first commit (no parent)
                diff = commit.diff(git.NULL_TREE, create_patch=True)
            
            # Format the diff output
            diff_output = []
            for d in diff:
                diff_output.append(f"\n--- a/{d.a_path}\n+++ b/{d.b_path}")
                diff_output.append(d.diff.decode('utf-8'))
            
            return {
                "success": True,
                "commit": {
                    "hash": commit.hexsha,
                    "author_name": commit.author.name,
                    "author_email": commit.author.email,
                    "date": str(datetime.fromtimestamp(commit.committed_date)),
                    "message": commit.message.strip()
                },
                "diff": "".join(diff_output)
            }
        except git.InvalidGitRepositoryError:
            return {
                "success": False,
                "error": f"Not a valid Git repository: {repo_path or os.getcwd()}"
            }
        except git.NoSuchPathError:
            return {
                "success": False,
                "error": f"Path does not exist: {repo_path}"
            }
        except git.GitCommandError as e:
            return {
                "success": False,
                "error": f"Git error: {e.stderr.strip()}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error showing Git commit: {str(e)}"
            }
    
    def _git_reset(self, repo_path: str = None) -> Dict[str, Any]:
        """Reset the staging area."""
        try:
            repo = self._get_repo(repo_path)
            
            # Reset the index
            repo.index.reset()
            
            return {
                "success": True,
                "message": "All staged changes reset"
            }
        except git.InvalidGitRepositoryError:
            return {
                "success": False,
                "error": f"Not a valid Git repository: {repo_path or os.getcwd()}"
            }
        except git.NoSuchPathError:
            return {
                "success": False,
                "error": f"Path does not exist: {repo_path}"
            }
        except git.GitCommandError as e:
            return {
                "success": False,
                "error": f"Git error: {e.stderr.strip()}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error resetting Git staging area: {str(e)}"
            }
