#!/usr/bin/env python3
"""
WCAG Accessibility Scanner with Web Interface - Using Puppeteer for HTML
"""
import os
import json
import time
import subprocess
import sys
import tempfile
import fnmatch
from pathlib import Path
from typing import List, Dict, Any
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser
import threading
from config import REPO_PATH, OUTPUT_DIR, EXCLUDE_DIRS, EXCLUDE_FILE_PATTERNS, FILE_LIMITS, TIMEOUT_PER_FILE
from html_report_generator import HTMLReportGenerator

console = Console()

class AccessibilityScanner:
    def __init__(self):
        self.repo_path = Path(REPO_PATH)
        self.output_dir = Path(OUTPUT_DIR)
        self.output_dir.mkdir(exist_ok=True)
        self.html_generator = HTMLReportGenerator(self.output_dir, self.repo_path)
        
    def should_exclude_file(self, file_path: Path) -> bool:
        """Check if a file should be excluded based on patterns"""
        filename = file_path.name
        
        # Check against exclude patterns
        for pattern in EXCLUDE_FILE_PATTERNS:
            if fnmatch.fnmatch(filename, pattern):
                return True
        
        # Check if file is in excluded directories
        exclude_dirs = set(EXCLUDE_DIRS)
        for part in file_path.parts:
            if part in exclude_dirs:
                return True
        
        return False
        
    def find_files(self, pattern: str) -> List[Path]:
        """Find files matching pattern, excluding specified directories"""
        files = []
        exclude_dirs = set(EXCLUDE_DIRS)
        
        console.print(f"[bold blue]Searching for {pattern} files...[/]")
        
        for root, dirs, filenames in os.walk(self.repo_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs and not any(excl in root for excl in exclude_dirs)]
            
            for filename in filenames:
                if fnmatch.fnmatch(filename, f"*{pattern}"):
                    file_path = Path(root) / filename
                    
                    # Skip excluded files
                    if self.should_exclude_file(file_path):
                        continue
                    
                    files.append(file_path)
        
        console.print(f"[green]Found {len(files)} {pattern} files[/]")
        return files
    
    def scan_html_with_puppeteer_axe(self, html_file: Path) -> Dict[str, Any]:
        """Scan HTML file using Puppeteer and axe-core"""
        try:
            # Check if puppeteer and axe-core are available
            try:
                result = subprocess.run(['npm', 'list', 'puppeteer', 'axe-core'], 
                                      capture_output=True, text=True, timeout=10, cwd=str(self.repo_path), check=True)
                console.print(f"[dim]Puppeteer/axe-core check: {result.stdout[:200]}...[/]")
            except:
                console.print("[yellow]⚠️ Puppeteer/axe-core not found, installing...[/]")
                result = subprocess.run(['npm', 'install', 'puppeteer', 'axe-core'], 
                                      capture_output=True, text=True, timeout=120, cwd=str(self.repo_path))
                console.print(f"[dim]Puppeteer install result: {result.stderr[:200]}...[/]" if result.stderr else "[green]Install successful[/]")
            
            # Create a Node.js script to run axe with Puppeteer
            script_content = f"""
            const fs = require('fs');
            const puppeteer = require('puppeteer');
            
            async function runAxe() {{
                const browser = await puppeteer.launch({{ 
                    headless: 'new',
                    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-web-security']
                }});
                const page = await browser.newPage();
                
                try {{
                    await page.setDefaultNavigationTimeout(60000);
                    const htmlContent = fs.readFileSync('{html_file.absolute()}', 'utf8');
                    await page.setContent(htmlContent, {{
                        waitUntil: 'networkidle0',
                        timeout: 60000
                    }});
                    const axeCorePath = require.resolve('axe-core');
                    const axeScript = fs.readFileSync(axeCorePath, 'utf8');
                    await page.evaluate(axeScript);
                    const results = await page.evaluate(async () => {{
                        return await axe.run();
                    }});
                    console.log(JSON.stringify(results));
                    await browser.close();
                    process.exit(0);
                }} catch (error) {{
                    console.error(JSON.stringify({{ error: error.message, stack: error.stack }}));
                    await browser.close();
                    process.exit(1);
                }}
            }}
            
            runAxe().catch(error => {{
                console.error(JSON.stringify({{ error: error.message, stack: error.stack }}));
                process.exit(1);
            }});
            """
            
            # Write temporary script
            temp_dir = os.path.abspath(str(self.repo_path))
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False, dir=temp_dir) as script_file:
                script_file.write(script_content)
                script_path = script_file.name
            
            # Run the script
            result = subprocess.run([
                'node', script_path
            ], capture_output=True, text=True, timeout=TIMEOUT_PER_FILE, cwd=str(self.repo_path))
            
            # Clean up script
            os.unlink(script_path)
            
            console.print(f"[dim]Puppeteer exit code for {html_file.name}: {result.returncode}[/]")
            console.print(f"[dim]Puppeteer STDOUT: {result.stdout[:200]}...[/]" if result.stdout else "[dim]STDOUT: (empty)[/]")
            console.print(f"[dim]Puppeteer STDERR: {result.stderr[:200]}...[/]" if result.stderr else "[dim]STDERR: (empty)[/]")
            
            if result.returncode == 0 and result.stdout.strip():
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    return {"error": f"Invalid JSON output for {html_file.name}: {result.stdout}"}
            else:
                error_msg = result.stderr if result.stderr else result.stdout
                try:
                    error_data = json.loads(error_msg)
                    return {"error": error_data.get('error', error_msg)}
                except:
                    return {"error": f"Puppeteer error for {html_file.name}: {error_msg}"}
                
        except subprocess.TimeoutExpired:
            return {"error": f"Timeout after {TIMEOUT_PER_FILE} seconds for {html_file.name}"}
        except Exception as e:
            return {"error": f"Exception for {html_file.name}: {str(e)}"}
    
    def scan_html_with_alternative_method(self, html_file: Path) -> Dict[str, Any]:
        """Alternative method using direct HTML content analysis"""
        try:
            # Read HTML content
            content = html_file.read_text(encoding='utf-8', errors='ignore')
            
            # Simple accessibility checks (fallback method)
            violations = []
            
            # Check for missing alt text
            img_tags = content.split('<img')
            for i, img_tag in enumerate(img_tags[1:]):  # Skip first split part
                if ' alt=' not in img_tag and ' alt =' not in img_tag:
                    violations.append({
                        "id": "image-alt",
                        "impact": "critical",
                        "help": "Images must have alternate text",
                        "helpUrl": "https://dequeuniversity.com/rules/axe/4.7/image-alt",
                        "nodes": [{
                            "html": f"<img{img_tag.split('>')[0]}>",
                            "target": [f"img:nth-of-type({i+1})"]
                        }]
                    })
            
            # Check for missing form labels
            form_elements = ['<input', '<select', '<textarea']
            for element in form_elements:
                if element in content:
                    element_tags = content.split(element)
                    for i, tag in enumerate(element_tags[1:]):
                        if (' id=' not in tag or ' for=' not in content) and ' aria-label=' not in tag:
                            violations.append({
                                "id": "label",
                                "impact": "serious",
                                "help": "Form elements must have labels",
                                "helpUrl": "https://dequeuniversity.com/rules/axe/4.7/label",
                                "nodes": [{
                                    "html": f"{element}{tag.split('>')[0]}>",
                                    "target": [f"{element[1:]}:nth-of-type({i+1})"]
                                }]
                            })
            
            # Check for missing lang attribute
            if '<html' in content and ' lang=' not in content and ' lang =' not in content:
                violations.append({
                    "id": "html-has-lang",
                    "impact": "serious",
                    "help": "<html> element must have a lang attribute",
                    "helpUrl": "https://dequeuniversity.com/rules/axe/4.7/html-has-lang",
                    "nodes": [{
                        "html": "<html>",
                        "target": ["html"]
                    }]
                })
            
            # Check for missing document title
            if '<title>' not in content:
                violations.append({
                    "id": "document-title",
                    "impact": "serious",
                    "help": "Documents must have a title element",
                    "helpUrl": "https://dequeuniversity.com/rules/axe/4.7/document-title",
                    "nodes": [{
                        "html": "<head>",
                        "target": ["head"]
                    }]
                })
            
            return {
                "violations": violations,
                "passes": [],
                "incomplete": [],
                "inapplicable": [],
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "url": f"file://{html_file.absolute()}"
            }
            
        except Exception as e:
            return {"error": f"Exception for {html_file.name}: {str(e)}"}
    
    def scan_html_file(self, html_file: Path) -> Dict[str, Any]:
        """Main HTML scanning method using Puppeteer"""
        console.print(f"[dim]Scanning: {html_file.name}[/]")
        
        # Try Puppeteer method
        result = self.scan_html_with_puppeteer_axe(html_file)
        
        # If Puppeteer fails, use fallback
        if "error" in result:
            console.print(f"[yellow]⚠️ Puppeteer failed for {html_file.name}, using fallback method[/]")
            result = self.scan_html_with_alternative_method(html_file)
        
        return result
    
    def generate_json_report(self, results: Dict[str, Any]):
        """Generate JSON report"""
        report_path = self.output_dir / "report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        return report_path
    
    def start_web_server(self, port=8000):
        """Start a simple web server to view the report"""
        os.chdir(str(self.output_dir))
        
        class Handler(SimpleHTTPRequestHandler):
            def log_message(self, format, *args):
                console.print(f"[dim]Web server: {format % args}[/]")
        
        server = HTTPServer(('localhost', port), Handler)
        console.print(f"[green]🌐 Web server started at http://localhost:{port}[/]")
        console.print("[green]Press Ctrl+C to stop the server[/]")
        
        # Open browser automatically
        webbrowser.open(f'http://localhost:{port}/report.html')
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            console.print("[yellow]Web server stopped[/]")
    
    def run_scan(self):
        """Main scanning method"""
        console.print("[bold green]🚀 Starting WCAG Accessibility Scan[/]")
        console.print(f"[dim]Repository: {self.repo_path}[/]")
        
        # Find files
        html_files = self.find_files('.html')[:FILE_LIMITS["html"]]
        
        console.print(f"[bold]Found:[/] {len(html_files)} .html files")
        
        results = {}
        
        # Scan HTML files
        if html_files:
            console.print("[bold blue]📄 Scanning .html files with Puppeteer...[/]")
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TimeElapsedColumn(),
            ) as progress:
                task = progress.add_task(".html files", total=len(html_files))
                
                for html_file in html_files:
                    results[str(html_file.relative_to(self.repo_path))] = self.scan_html_file(html_file)
                    progress.update(task, advance=1)
        
        # Generate reports
        console.print("[bold blue]📊 Generating reports...[/]")
        json_report = self.generate_json_report(results)
        html_report = self.html_generator.generate_html_report(results)
        
        console.print(f"[green]✓ JSON report: {json_report}[/]")
        console.print(f"[green]✓ HTML report: {html_report}[/]")
        console.print("[bold green]✅ Scan completed![/]")
        
        return html_report

def main():
    """Main function"""
    try:
        scanner = AccessibilityScanner()
        html_report = scanner.run_scan()
        
        # Ask if user wants to start web server
        console.print("")
        response = input("Start web server to view report? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            scanner.start_web_server()
            
    except KeyboardInterrupt:
        console.print("[yellow]⏹️ Scan interrupted by user[/]")
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/]")
        sys.exit(1)

if __name__ == "__main__":
    main()