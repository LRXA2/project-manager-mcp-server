# Git Credentials Configuration

This file provides documentation for setting up Git credentials for use with the MCP server's Git tools.

## Configuration

1. Copy one of the template/example files to create your credentials file:
   ```bash
   # From template (blank values)
   cp git.json.template git.json

   # Or from example (with example values to modify)
   cp git.json.example git.json
   ```

2. Edit the git.json file with your Git provider credentials:
   ```json
   {
     "github.com": {
       "username": "your-github-username",
       "token": "your-github-personal-access-token"
     },
     "gitlab.com": {
       "username": "your-gitlab-username",
       "token": "your-gitlab-personal-access-token"
     }
   }
   ```

## Obtaining Credentials

### GitHub
1. Go to your GitHub account settings
2. Select "Developer settings" > "Personal access tokens" > "Tokens (classic)"
3. Click "Generate new token"
4. Give it a name, select the appropriate scopes (at minimum: `repo`)
5. Copy the generated token and store it securely

### GitLab
1. Go to your GitLab account preferences
2. Select "Access Tokens"
3. Create a new personal access token with appropriate scopes (at minimum: `read_repository`, `write_repository`)
4. Copy the generated token and store it securely

### Bitbucket
1. Go to your Bitbucket account settings
2. Select "App passwords" under "Access Management"
3. Create a new app password with appropriate permissions
4. Copy the generated password and store it securely

### Azure DevOps
1. Go to your Azure DevOps account
2. Select "Personal Access Tokens"
3. Click "New Token"
4. Give it a name and select the appropriate scopes (at minimum: "Code (read and write)")
5. Copy the generated token and store it securely

## Security Considerations

- Store credentials securely and do not commit them to source control
- Use the minimum required permissions for tokens
- Consider using different tokens for different contexts
- Rotate tokens regularly according to your organization's security policies
