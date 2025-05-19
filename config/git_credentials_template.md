# Git Credentials Configuration

This file describes the structure of the git_credentials.json file that should be created
in this directory. The file itself is gitignored for security.

Expected structure:
```json
{
  "github": {
    "username": "your-github-username",
    "token": "your-github-personal-access-token"
  },
  "gitlab": {
    "username": "your-gitlab-username",
    "token": "your-gitlab-access-token"
  },
  "bitbucket": {
    "username": "your-bitbucket-username",
    "token": "your-bitbucket-app-password"
  }
}
```

To add credentials, create the git_credentials.json file with the above structure 
and replace the placeholder values with your actual credentials.

The credentials in this file will be used for Git operations that require authentication,
such as cloning private repositories or pushing to remote repositories.
