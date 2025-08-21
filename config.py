import os

# Configuration
CONFIG = {
    "repo_path": "/Users/mohammedfarhank/Desktop/fyle-workspace/fyle-mobile-app",
    "exclude_dirs": [
        "node_modules", "dist", "build", "www", ".git", 
        "coverage", ".angular", "ios", "android", "platforms"
    ],
    "exclude_files": ["*.d.ts", "*.spec.ts", "*.test.ts", "*.mock.ts", "*.data.ts", "*.service.ts", "*.model.ts"],
    "file_limits": {
        "html": 1000,  # Max HTML files to process
        "typescript": 500,  # Max TS files to process
        "components": 300   # Max component files to process
    },
    "timeout_per_file": 30,  # seconds
    "max_workers": 4,  # Parallel processing
    "output_dir": "./reports"
}