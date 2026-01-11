SEARCH_DESCRIPTION = "Search the internet for current events, locations, addresses, and public information. Use this for real-time data and information not in internal documents."

SEARCH_IN_FILE_DESCRIPTION = """Search semantic content within a specific file.
Auto-indexes the file if not already in knowledge base, then searches within it.
Use when user wants to find specific information INSIDE a file by meaning, not just read it.
Examples: "Find authentication logic in auth.py", "Where's the database config in settings.py?"
Returns relevant sections found in the file."""

READ_FILE_DESCRIPTION = """Read file contents and ALWAYS SUMMARIZE for voice interface.
NEVER read entire file verbatim - extract and present key information concisely.
For code: mention main components (classes, functions, purpose)
For config: highlight important settings
For text/docs: summarize main points
For data: describe structure and key fields
Only provide full content if explicitly requested."""

SEARCH_FILES_DESCRIPTION = """Find files by name/pattern and return concise list suitable for voice.
Summarize results clearly - mention count and key matches.
For many results: provide overview count rather than reading every filename."""

LIST_DIRECTORY_DESCRIPTION = """List directory contents and summarize for voice interface.
Provide clear overview - mention folder/file counts and notable items.
For large directories: give summary statistics rather than reading every item."""
