#!/usr/bin/env python3
"""
Configuration file for WCAG Accessibility Scanner
"""

# Repository path to scan
REPO_PATH = "/dummy"

# Output directory for reports
OUTPUT_DIR = "./reports"

# Directories to exclude from scanning
EXCLUDE_DIRS = [
    "node_modules", "dist", "build", "www", ".git", 
    "coverage", ".angular", "ios", "android", "platforms",
    "Pods", "DerivedData", ".idea", ".vscode"
]

# File patterns to exclude from scanning
EXCLUDE_FILE_PATTERNS = ["*.d.ts", "*.spec.ts", "*.test.ts", "*.mock.ts", "*.data.ts"]

# File limits for different file types
FILE_LIMITS = {"html": 1000}

# Timeout per file in seconds (increased timeout for Puppeteer)
TIMEOUT_PER_FILE = 120