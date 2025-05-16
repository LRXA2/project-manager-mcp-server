import os
import json
import datetime
from typing import Dict, List, Optional, Any
from mcp.server.fastmcp import FastMCP

class ContextManager:
    """
    Context management with pure local storage.
    No external dependencies - uses simple JSON files and text processing.
    """
    
    def __init__(self, base_dir: str, mcp_instance: FastMCP):
        """
        Initialize the Context Manager
        
        Args:
            base_dir: The base directory of the MCP server project
            mcp_instance: The FastMCP instance to register tools with
        """
        self.base_dir = base_dir
        self.mcp = mcp_instance
        self.context_dir = os.path.join(base_dir, "context_storage")
        
        # Create context storage directory
        os.makedirs(self.context_dir, exist_ok=True)
        
        print("Context Manager initialized (local storage mode)")
        
        # Track significant events
        self.SIGNIFICANT_EVENTS = [
            "error_solved",
            "build_configuration_changed", 
            "new_feature_implemented",
            "deployment_completed",
            "preference_learned",
            "project_setup",
            "debugging_session",
            "optimization_applied"
        ]
    
    def is_available(self) -> bool:
        """Context management is always available with local storage"""
        return True
    
    def _get_context_file(self, context_type: str) -> str:
        """Get the file path for a specific context type"""
        return os.path.join(self.context_dir, f"{context_type}.json")
    
    def _load_context(self, context_type: str) -> List[Dict]:
        """Load context from file"""
        file_path = self._get_context_file(context_type)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return []
        return []
    
    def _save_context(self, context_type: str, data: List[Dict]):
        """Save context to file"""
        file_path = self._get_context_file(context_type)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except OSError as e:
            print(f"Error saving context: {e}")
    
    def _add_context_entry(self, context_type: str, entry: Dict):
        """Add a new context entry"""
        context = self._load_context(context_type)
        entry["timestamp"] = datetime.datetime.now().isoformat()
        context.append(entry)
        
        # Keep only last 50 entries per type to prevent unlimited growth
        if len(context) > 50:
            context = context[-50:]
        
        self._save_context(context_type, context)
    
    def _search_context(self, context_type: str, query: str = None, limit: int = 5) -> List[Dict]:
        """Search context with simple keyword matching"""
        context = self._load_context(context_type)
        
        if not query:
            # Return most recent entries
            return sorted(context, key=lambda x: x.get("timestamp", ""), reverse=True)[:limit]
        
        # Simple keyword search
        query_lower = query.lower()
        matches = []
        for entry in context:
            content = entry.get("content", "").lower()
            # Check if any word in the query appears in the content
            if any(word in content for word in query_lower.split()):
                # Calculate simple relevance score
                score = sum(1 for word in query_lower.split() if word in content)
                entry["_relevance_score"] = score
                matches.append(entry)
        
        # Sort by relevance score, then by timestamp
        matches.sort(key=lambda x: (x.get("_relevance_score", 0), x.get("timestamp", "")), reverse=True)
        return matches[:limit]
    
    def _truncate_text(self, text: str, max_words: int = 100) -> str:
        """Simple word-based text truncation"""
        words = text.split()
        if len(words) <= max_words:
            return text
        return " ".join(words[:max_words]) + "..."
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases using simple text analysis"""
        # Split into sentences
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        # Look for decision markers, problem statements, solution indicators
        key_phrases = []
        decision_markers = ['decided to', 'chose to', 'will use', 'going to', 'solution is', 'fixed by']
        problem_markers = ['error:', 'issue:', 'problem:', 'bug:', 'failed to']
        solution_markers = ['solved by', 'fixed by', 'resolved by', 'working now', 'solution:']
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            # Check for decision patterns
            if any(marker in sentence_lower for marker in decision_markers):
                key_phrases.append(f"DECISION: {sentence}")
            # Check for problem patterns  
            elif any(marker in sentence_lower for marker in problem_markers):
                key_phrases.append(f"PROBLEM: {sentence}")
            # Check for solution patterns
            elif any(marker in sentence_lower for marker in solution_markers):
                key_phrases.append(f"SOLUTION: {sentence}")
        
        return key_phrases
    
    def register_tools(self):
        """Register context management tools"""
        
        @self.mcp.tool()
        def end_session_summary(summary: str, tags: List[str] = None, max_words: int = 100) -> str:
            """
            Create a concise summary of current session.
            
            Args:
                summary (str): Summary of what was accomplished in the session
                tags (List[str]): Optional tags for categorization
                max_words (int): Maximum words for summary (default: 100)
            
            Returns:
                str: Confirmation message
            """
            # Truncate summary if needed
            truncated_summary = self._truncate_text(summary, max_words)
            
            # Extract key phrases for better searchability
            key_phrases = self._extract_key_phrases(summary)
            
            entry = {
                "content": truncated_summary,
                "full_content": summary,  # Keep original for reference
                "type": "session_summary",
                "tags": tags or [],
                "key_phrases": key_phrases,
                "word_count": len(truncated_summary.split())
            }
            
            self._add_context_entry("sessions", entry)
            return f"Session summary saved ({entry['word_count']} words, {len(key_phrases)} key phrases)"
        
        @self.mcp.tool()
        def record_significant_event(event_type: str, details: str, project: str = "project") -> str:
            """
            Record only significant development events.
            
            Args:
                event_type (str): Type of event (error_solved, build_configuration_changed, etc.)
                details (str): Description of what happened
                project (str): Project name
            
            Returns:
                str: Confirmation message
            """
            if event_type not in self.SIGNIFICANT_EVENTS:
                return f"Event type '{event_type}' not in significant events list. Available: {self.SIGNIFICANT_EVENTS}"
            
            entry = {
                "content": details,
                "type": "significant_event",
                "event_type": event_type,
                "project": project,
                "key_phrases": self._extract_key_phrases(details)
            }
            
            self._add_context_entry("events", entry)
            return f"Recorded {event_type} event for {project}"
        
        @self.mcp.tool()
        def save_context_levels(session_content: str) -> str:
            """
            Save context at multiple levels of detail.
            
            Args:
                session_content (str): Full content of the session to be processed
            
            Returns:
                str: Confirmation message
            """
            # Level 1: Session summary (brief)
            summary = self._truncate_text(session_content, max_words=50)
            self._add_context_entry("summaries", {
                "content": summary,
                "level": "summary",
                "type": "session"
            })
            
            # Level 2: Key decisions/problems/solutions
            key_phrases = self._extract_key_phrases(session_content)
            if key_phrases:
                self._add_context_entry("decisions", {
                    "content": "\n".join(key_phrases),
                    "level": "decisions",
                    "type": "session",
                    "phrase_count": len(key_phrases)
                })
            
            return f"Context saved at multiple levels (summary + {len(key_phrases)} key phrases)"
        
        @self.mcp.tool()
        def start_with_context(sessions_back: int = 3) -> str:
            """
            Get context from last N sessions to start with context.
            
            Args:
                sessions_back (int): Number of recent sessions to include
            
            Returns:
                str: Formatted context summary
            """
            sessions = self._search_context("sessions", limit=sessions_back)
            events = self._search_context("events", limit=5)
            
            context_parts = ["=== SESSION CONTEXT ===\n"]
            
            if sessions:
                context_parts.append("Recent Sessions:")
                for i, session in enumerate(sessions, 1):
                    content = session.get("content", "")
                    timestamp = session.get("timestamp", "Unknown")[:10]
                    tags = session.get("tags", [])
                    
                    context_parts.append(f"\n{i}. [{timestamp}] {content}")
                    if tags:
                        context_parts.append(f"   Tags: {', '.join(tags)}")
                    
                    # Include key phrases if available
                    key_phrases = session.get("key_phrases", [])
                    if key_phrases:
                        context_parts.append(f"   Key insights: {len(key_phrases)} items")
            
            if events:
                context_parts.append("\n\nRecent Events:")
                for event in events:
                    content = event.get("content", "")
                    timestamp = event.get("timestamp", "Unknown")[:10]
                    event_type = event.get("event_type", "unknown")
                    
                    context_parts.append(f"- [{timestamp}] {event_type}: {content}")
            
            context_parts.append("\n=== END CONTEXT ===")
            return "\n".join(context_parts)
        
        @self.mcp.tool()
        def get_relevant_context(current_task: str) -> str:
            """
            Get context specifically relevant to current task.
            
            Args:
                current_task (str): Description of current task/work
            
            Returns:
                str: Relevant context for the task
            """
            # Analyze task type using simple keyword matching
            task_lower = current_task.lower()
            
            context_type = "general"
            relevant_events = []
            relevant_sessions = []
            
            if any(word in task_lower for word in ["error", "bug", "debug", "fix", "problem"]):
                # Get debugging-related context
                relevant_events = self._search_context("events", "error_solved", limit=3)
                context_type = "debugging"
            elif any(word in task_lower for word in ["build", "compile", "deploy", "configuration"]):
                # Get build-related context
                relevant_events = self._search_context("events", "build_configuration", limit=3)
                context_type = "building"
            elif any(word in task_lower for word in ["feature", "implement", "add", "new"]):
                # Get feature development context
                relevant_events = self._search_context("events", "new_feature", limit=3)
                context_type = "feature_development"
            else:
                # Get general context
                relevant_sessions = self._search_context("sessions", current_task, limit=3)
                relevant_events = self._search_context("events", current_task, limit=2)
            
            result = [f"=== RELEVANT CONTEXT ({context_type.upper()}) ===\n"]
            
            if relevant_sessions:
                result.append("Related Sessions:")
                for session in relevant_sessions:
                    content = session.get("content", "")
                    timestamp = session.get("timestamp", "Unknown")[:10]
                    result.append(f"[{timestamp}] {content}")
            
            if relevant_events:
                result.append("Related Events:" if relevant_sessions else "Related Events:")
                for event in relevant_events:
                    content = event.get("content", "")
                    timestamp = event.get("timestamp", "Unknown")[:10]
                    event_type = event.get("event_type", "unknown")
                    result.append(f"[{timestamp}] {event_type}: {content}")
            
            return "\n".join(result) if len(result) > 1 else "No relevant context found"
        
        @self.mcp.tool()
        def get_context_stats() -> str:
            """
            Get statistics about stored context.
            
            Returns:
                str: Context storage statistics
            """
            sessions = self._load_context("sessions")
            events = self._load_context("events")
            summaries = self._load_context("summaries")
            decisions = self._load_context("decisions")
            
            total_words = 0
            total_key_phrases = 0
            
            for session in sessions:
                total_words += session.get("word_count", 0)
                total_key_phrases += len(session.get("key_phrases", []))
            
            stats = [
                "=== CONTEXT STATISTICS ===",
                f"Session summaries: {len(sessions)}",
                f"Total key phrases extracted: {total_key_phrases}",
                f"Significant events: {len(events)}",
                f"Hierarchical summaries: {len(summaries)}",
                f"Decision records: {len(decisions)}",
                f"Total words in summaries: {total_words}",
                f"Average words per summary: {total_words/len(sessions) if sessions else 0:.1f}",
                f"Storage location: {self.context_dir}",
                f"Storage method: Local JSON files (no external dependencies)"
            ]
            
            return "\n".join(stats)
        
        @self.mcp.tool()
        def search_context(query: str, context_type: str = "all", limit: int = 5) -> str:
            """
            Search through stored context for specific information.
            
            Args:
                query (str): Search query
                context_type (str): Type of context to search ("sessions", "events", "all")
                limit (int): Maximum number of results to return
            
            Returns:
                str: Formatted search results
            """
            results = []
            
            if context_type in ["sessions", "all"]:
                sessions = self._search_context("sessions", query, limit)
                results.extend([(s, "session") for s in sessions])
            
            if context_type in ["events", "all"]:
                events = self._search_context("events", query, limit)
                results.extend([(e, "event") for e in events])
            
            if not results:
                return f"No context found matching '{query}'"
            
            search_results = [f"=== SEARCH RESULTS for '{query}' ===\n"]
            
            for i, (result, result_type) in enumerate(results[:limit], 1):
                content = result.get("content", "")
                timestamp = result.get("timestamp", "Unknown")[:10]
                relevance = result.get("_relevance_score", 0)
                
                search_results.append(f"{i}. [{timestamp}] ({result_type}) [relevance: {relevance}]")
                search_results.append(f"   {content}")
                
                # Show key phrases if available
                key_phrases = result.get("key_phrases", [])
                if key_phrases:
                    search_results.append(f"   Key phrases: {len(key_phrases)} extracted")
                
                search_results.append("")
            
            return "\n".join(search_results)
        
        @self.mcp.tool()
        def clear_old_context(days_old: int = 30) -> str:
            """
            Clear context entries older than specified days.
            
            Args:
                days_old (int): Number of days - entries older than this will be removed
            
            Returns:
                str: Confirmation of cleanup
            """
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_old)
            cutoff_iso = cutoff_date.isoformat()
            
            removed_counts = {}
            for context_type in ["sessions", "events", "summaries", "decisions"]:
                context = self._load_context(context_type)
                original_count = len(context)
                
                # Filter out old entries
                context = [entry for entry in context 
                          if entry.get("timestamp", "") >= cutoff_iso]
                
                removed_counts[context_type] = original_count - len(context)
                
                if removed_counts[context_type] > 0:
                    self._save_context(context_type, context)
            
            total_removed = sum(removed_counts.values())
            result = f"Removed {total_removed} entries older than {days_old} days:\n"
            for context_type, count in removed_counts.items():
                if count > 0:
                    result += f"  - {context_type}: {count} entries\n"
            
            return result if total_removed > 0 else f"No entries older than {days_old} days found"
