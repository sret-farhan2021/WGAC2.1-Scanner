# 🔍 WCAG Accessibility Scanner

A comprehensive accessibility testing tool that scans HTML files for WCAG 2.1 compliance using Puppeteer and axe-core. Perfect for mobile apps, web applications, and ensuring your content meets international accessibility standards.

## ✨ Features

- **Comprehensive Testing**: Tests 100+ WCAG 2.1 accessibility rules
- **HTML File Scanning**: Automatically finds and scans `.html` files
- **Real Browser Testing**: Uses Puppeteer for accurate rendering and testing
- **Detailed Reports**: Generates interactive HTML and JSON reports
- **Mobile App Focused**: Optimized for mobile app HTML content
- **Automatic Setup**: Installs dependencies automatically if missing

## 🚀 Quick Start

### Prerequisites

- **Python 3.7+**
- **Node.js 18+** (for Puppeteer)
- **npm** (comes with Node.js)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd accessibility_scanner
   ```

2. **Create and activate Python virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

5. **Install axe-core globally (if not already installed):**
   ```bash
   npm install -g axe-core
   ```

6. **Verify installation:**
   ```bash
   python --version
   node --version
   npm --version
   axe --version  # Check if axe-core is available
   ```

### Manual Puppeteer Installation (if npm install fails)

If the automatic Puppeteer installation fails, try:

```bash
npm install puppeteer --unsafe-perm=true
```

Or install globally:

```bash
npm install -g puppeteer
```

### Configuration

Edit `scanner.py` and update the `Config` class:

```python
class Config:
    REPO_PATH = "/path/to/your/repository"  # Your repository path
    OUTPUT_DIR = "./reports"                 # Where to save reports
    EXCLUDE_DIRS = ["node_modules", "dist", "build"]  # Directories to skip
    FILE_LIMITS = {"html": 1000}            # Max HTML files to scan
    TIMEOUT_PER_FILE = 120                  # Timeout per file (seconds)
```

## 📱 Usage

### Basic Scan

Run the scanner from your project directory:

```bash
python scanner.py
```

The scanner will:
1. Find all `.html` files in your repository
2. Test each file for WCAG compliance using axe-core
3. Generate detailed reports
4. Optionally start a web server to view results

### What Gets Tested

The scanner automatically tests for:

- **Perceivable**: Alt text, color contrast, text alternatives
- **Operable**: Touch targets, keyboard navigation, focus management
- **Understandable**: Form labels, page structure, language attributes
- **Robust**: Semantic HTML, ARIA attributes, screen reader support

### Report Types

1. **HTML Report** (`report.html`): Interactive web interface with:
   - Summary of violations and passed tests
   - Detailed breakdown by file
   - Test coverage information
   - Pagination for large reports

2. **JSON Report** (`report.json`): Machine-readable data for:
   - CI/CD integration
   - Automated testing
   - Data analysis

## 📊 Understanding Results

### Test Categories

- **🔴 Violations**: Accessibility issues that need fixing
- **🟢 Passed**: Tests that meet WCAG standards
- **⚪ Inapplicable**: Tests that don't apply to your content

### Common Issues Found

- Missing image alt text
- Poor color contrast ratios
- Missing form labels
- Inadequate touch target sizes
- Missing page structure (headings, landmarks)
- Missing language attributes

### Priority Fixes

1. **Critical**: Missing alt text, form labels
2. **Serious**: Color contrast, touch target sizes
3. **Moderate**: Page structure, navigation
4. **Minor**: ARIA attributes, semantic HTML

## 🛠️ Customization

### Excluding Files/Directories

Update the `Config` class:

```python
EXCLUDE_DIRS = [
    "node_modules", "dist", "build", "www", ".git",
    "coverage", ".angular", "ios", "android"
]

EXCLUDE_FILE_PATTERNS = [
    "*.d.ts", "*.spec.ts", "*.test.ts", "*.mock.ts"
]
```

### Adjusting Timeouts

```python
TIMEOUT_PER_FILE = 120  # Increase for complex pages
```

### File Limits

```python
FILE_LIMITS = {"html": 1000}  # Adjust based on your needs
```

## 🌐 Web Interface

After scanning, the tool can start a local web server:

```bash
Start web server to view report? (y/n): y
```

This opens your browser to `http://localhost:8000/report.html` with:
- Interactive violation details
- Expandable file sections
- Pagination for large reports
- Search and filter capabilities

## 🔧 Troubleshooting

### Common Issues

1. **Puppeteer Installation Fails**
   - Ensure Node.js 18+ is installed
   - Check internet connection for downloads
   - Try running `npm install puppeteer` manually

2. **Timeout Errors**
   - Increase `TIMEOUT_PER_FILE` in config
   - Check for very large HTML files
   - Ensure stable internet connection

3. **Memory Issues**
   - Reduce `FILE_LIMITS` in config
   - Process files in smaller batches
   - Close other applications

### Debug Mode

The scanner provides detailed logging:
- File processing status
- Puppeteer installation progress
- Test execution details
- Error messages and stack traces

## 📋 Requirements

### Python Dependencies
- `rich`: Beautiful terminal output
- `requests`: HTTP operations
- `beautifulsoup4`: HTML parsing (fallback)

### Node.js Dependencies
- `puppeteer`: Browser automation
- `axe-core`: Accessibility testing engine

### OUTPUT EXAMPLE
<img width="1440" height="900" alt="Screenshot 2025-08-21 at 9 29 29 PM" src="https://github.com/user-attachments/assets/8a3efa0a-6234-4d09-8d47-28be93a32307" />

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **axe-core**: The accessibility testing engine
- **Puppeteer**: Browser automation framework
- **WCAG Guidelines**: Web Content Accessibility Guidelines

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the error logs
3. Open an issue on GitHub
4. Check axe-core documentation

---

**Happy accessibility testing! 🎉** 

