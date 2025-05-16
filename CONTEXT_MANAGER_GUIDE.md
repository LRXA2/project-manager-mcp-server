# Context Manager Guide

## Overview

The Context Manager provides intelligent session tracking and context retrieval using **local JSON storage only**. No external APIs or services required - everything stays on your machine.

## Key Features

- **Local Storage**: All context stored in JSON files on your machine
- **Smart Text Analysis**: Automatically extracts key decisions, problems, and solutions
- **Event-Driven**: Only stores significant development events
- **Keyword Search**: Fast local search with relevance scoring
- **Zero Dependencies**: No API keys, no external services

## Quick Start

### Basic Usage

```python
# 1. End productive session
end_session_summary("Fixed database connection issues and optimized queries", 
                   tags=["debugging", "database"])

# 2. Start new session with context
start_with_context(3)  # Get context from last 3 sessions

# 3. Record significant events
record_significant_event("error_solved", "Fixed memory leak in data processing pipeline")
```

## Available Tools

### `end_session_summary(summary, tags=None, max_words=100)`
Save a concise summary of your session with automatic key phrase extraction.

**Parameters:**
- `summary` (str): What you accomplished in the session
- `tags` (list): Optional tags for categorization (e.g., ["debugging", "frontend"])
- `max_words` (int): Maximum words to store (default: 100)

**Example:**
```python
end_session_summary(
    "Implemented user authentication with JWT tokens. Fixed CORS issues on login endpoint. Added password validation rules.",
    tags=["authentication", "backend", "security"],
    max_words=50
)
```

### `record_significant_event(event_type, details, project="project")`
Record only important development milestones.

**Event Types:**
- `error_solved`
- `build_configuration_changed`
- `new_feature_implemented`
- `deployment_completed`
- `preference_learned`
- `project_setup`
- `debugging_session`
- `optimization_applied`

**Example:**
```python
record_significant_event("error_solved", 
                        "Database connection pool exhaustion fixed by increasing max connections from 10 to 50")
```

### `start_with_context(sessions_back=3)`
Begin a new session with context from recent work.

**Example:**
```python
start_with_context(5)  # Get context from last 5 sessions
```

**Output:**
```
=== SESSION CONTEXT ===

Recent Sessions:
1. [2024-01-15] Fixed database connection issues and optimized queries
   Tags: debugging, database
   Key insights: 3 items

2. [2024-01-14] Implemented user authentication with JWT tokens
   Tags: authentication, backend, security
   Key insights: 2 items

Recent Events:
- [2024-01-15] error_solved: Database connection pool exhaustion fixed
- [2024-01-14] new_feature_implemented: JWT authentication system

=== END CONTEXT ===
```

### `get_relevant_context(current_task)`
Get context specifically relevant to your current task.

**Example:**
```python
# When debugging
get_relevant_context("Fixing database timeout errors")

# When building
get_relevant_context("Setting up production deployment")

# When implementing features
get_relevant_context("Adding user profile management")
```

### `search_context(query, context_type="all", limit=5)`
Search through stored context for specific information.

**Parameters:**
- `query` (str): What to search for
- `context_type` (str): "sessions", "events", or "all"
- `limit` (int): Maximum results to return

**Example:**
```python
search_context("database connection", context_type="all", limit=3)
```

### `save_context_levels(session_content)`
Save context at multiple detail levels for better organization.

**Example:**
```python
save_context_levels("""
Today I worked on fixing the database connection issues. The problem was that the connection pool was exhausting under load. 

DECISION: Increased max connections from 10 to 50
PROBLEM: Connection timeouts during peak usage
SOLUTION: Added connection pooling configuration

Also optimized the query performance by adding indexes on frequently accessed columns.
""")
```

### `get_context_stats()`
View statistics about your stored context.

**Example Output:**
```
=== CONTEXT STATISTICS ===
Session summaries: 15
Total key phrases extracted: 47
Significant events: 8
Hierarchical summaries: 12
Decision records: 5
Total words in summaries: 1,247
Average words per summary: 83.1
Storage location: /path/to/context_storage
Storage method: Local JSON files (no external dependencies)
```

### `clear_old_context(days_old=30)`
Clean up context entries older than specified days.

**Example:**
```python
clear_old_context(30)  # Remove entries older than 30 days
```

## Automatic Key Phrase Extraction

The context manager automatically extracts key phrases from your sessions:

- **Decisions**: "decided to", "chose to", "will use", "going to"
- **Problems**: "error:", "issue:", "problem:", "bug:", "failed to"
- **Solutions**: "solved by", "fixed by", "resolved by", "working now"

These phrases are automatically tagged and become searchable.

## Context Organization

### Storage Structure
```
context_storage/
├── sessions.json     # Session summaries with key phrases
├── events.json       # Significant events only
├── summaries.json    # Compressed session summaries
└── decisions.json    # Extracted decisions and solutions
```

### Automatic Management
- **Size Limits**: Only keeps last 50 entries per type
- **Automatic Cleanup**: Old context can be removed
- **Smart Search**: Relevance scoring for better results

## Best Practices

### 1. End Each Session
Always save a session summary when you finish productive work:
```python
end_session_summary("Completed user registration flow with email verification", 
                   tags=["feature", "frontend", "email"])
```

### 2. Record Significant Events
Don't record everything - only significant developments:
```python
# Good ✅
record_significant_event("error_solved", "Fixed React hydration mismatch by updating useEffect dependencies")

# Too trivial ❌
record_significant_event("error_solved", "Fixed typo in component name")
```

### 3. Use Descriptive Tags
Tags help categorize and find context later:
```python
# Good tags ✅
tags=["database", "performance", "optimization"]

# Too generic ❌
tags=["work", "coding"]
```

### 4. Start With Context
Begin each session by reviewing recent context:
```python
start_with_context(3)  # Review last 3 sessions
```

### 5. Search Before Reinventing
Use search to find previous solutions:
```python
search_context("CORS error", context_type="events")
```

## Advanced Usage

### Task-Specific Context
```python
# Get debugging-related context
get_relevant_context("Debugging authentication flow")

# Get build-related context
get_relevant_context("Setting up CI/CD pipeline")
```

### Multi-Level Context
```python
# Save detailed context with automatic extraction
save_context_levels("""
Extended debugging session for payment processing issues.

PROBLEM: Stripe webhooks failing intermittently
DECISION: Implemented retry mechanism with exponential backoff
SOLUTION: Added webhook signature verification and proper error handling

The issue was caused by network timeouts during peak load.
Success rate improved from 85% to 99.8%.
""")
```

## Storage and Privacy

- **Local Only**: All data stored in JSON files on your machine
- **No Network**: Works completely offline
- **Easy Backup**: Copy the `context_storage/` directory
- **Human Readable**: JSON files can be viewed with any text editor
- **No Vendor Lock-in**: Standard JSON format, easily portable

## Troubleshooting

### Context Not Found
If searches return no results, check:
1. Have you recorded any sessions?
2. Are you using correct keywords?
3. Try broader search terms

### Storage Issues
If context isn't saving:
1. Check file permissions on `context_storage/` directory
2. Ensure sufficient disk space
3. Verify the directory isn't read-only

### Performance
For better performance:
1. Regular cleanup with `clear_old_context()`
2. Use specific search terms instead of broad queries
3. Limit search results appropriately

## Integration with Development Workflow

### Daily Workflow
1. **Morning**: `start_with_context(3)` - Review recent work
2. **During Work**: Record significant events as they happen
3. **Evening**: `end_session_summary()` - Summarize the day

### Team Collaboration
- Export context to share with team members
- Use consistent tagging across team
- Document significant events for knowledge transfer

The context manager is designed to enhance your development workflow without adding overhead. Focus on recording meaningful information that will help you (and your team) understand project evolution over time.