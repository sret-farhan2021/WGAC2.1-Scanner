#!/usr/bin/env python3
"""
HTML Report Generator for WCAG Accessibility Scanner
"""
import os
import json
import time
import html
from pathlib import Path
from typing import Dict, Any
from rich.console import Console

console = Console()

class HTMLReportGenerator:
    def __init__(self, output_dir: Path, repo_path: Path):
        self.output_dir = output_dir
        self.repo_path = repo_path
    
    def generate_html_report(self, results: Dict[str, Any]):
        """Generate interactive HTML report with pagination, violations, and incomplete results"""
        console.print("[bold blue]🔍 Generating HTML report...[/]")
        console.print(f"[dim]Results keys: {list(results.keys())}[/]")  # Debug: Print file paths
        console.print(f"[dim]Total results: {len(results)}[/]")  # Debug: Print total files
        
        html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>WCAG Accessibility Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .header { background: #2c3e50; color: white; padding: 20px; border-radius: 5px; margin-bottom: 30px; }
                .summary-card { background: #ecf0f1; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
                .violation { background: #ffe6e6; border-left: 4px solid #e74c3c; padding: 15px; margin: 10px 0; border-radius: 3px; }
                .incomplete { background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 10px 0; border-radius: 3px; }
                .success { background: #d4edda; border-left: 4px solid #28a745; padding: 15px; margin: 10px 0; border-radius: 3px; }
                .file-section { margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 5px; }
                .toggle { cursor: pointer; color: #3498db; }
                .hidden { display: none; }
                .impact-critical { border-left-color: #e74c3c !important; }
                .impact-serious { border-left-color: #e67e22 !important; }
                .impact-moderate { border-left-color: #f39c12 !important; }
                .impact-minor { border-left-color: #f1c40f !important; }
                .error { background: #f8d7da; border-left: 4px solid #dc3545; padding: 15px; margin: 10px 0; border-radius: 3px; }
                .code-snippet { background: #f1f1f1; padding: 10px; border-radius: 3px; font-family: monospace; overflow-x: auto; white-space: pre-wrap; }
                .pagination { margin: 20px 0; text-align: center; }
                .pagination button { padding: 10px 20px; margin: 0 5px; cursor: pointer; }
                .pagination button:disabled { cursor: not-allowed; opacity: 0.5; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔍 WCAG Accessibility Report</h1>
                    <p>Generated on {{timestamp}}</p>
                </div>
                
                <div class="summary-card">
                    <h2>📊 Summary</h2>
                    <p><strong>Total files scanned:</strong> {{total_files}}</p>
                    <p><strong>Total violations found:</strong> {{total_violations}}</p>
                    <p><strong>Total incomplete results:</strong> {{total_incomplete}}</p>
                    <p><strong>Files with errors:</strong> {{error_files}}</p>
                    <p><strong>Repository:</strong> {{repo_path}}</p>
                </div>
                
                <div class="summary-card">
                    <h2 class="toggle" onclick="toggleSection('tests-executed')">
                        🧪 Tests Executed <small>(Click to expand)</small>
                    </h2>
                    <div id="tests-executed" class="hidden">
                        <h3>Actual Tests Run by axe-core:</h3>
                        {{tests_executed_section}}
                        <p><em>Note: These are the actual axe-core test IDs that were run during the scan. Each ID represents a specific WCAG accessibility rule.</em></p>
                    </div>
                </div>
                
                <div class="pagination">
                    <button onclick="prevPage()" id="prevBtn">Previous</button>
                    <span id="pageInfo"></span>
                    <button onclick="nextPage()" id="nextBtn">Next</button>
                </div>
                
                <h2>📋 Detailed Results</h2>
                <div id="results">{{results}}</div>
            </div>
            
            <script>
                try {
                    const resultsDiv = document.getElementById('results');
                    const fileSections = Array.from(resultsDiv.getElementsByClassName('file-section'));
                    const filesPerPage = 10;
                    let currentPage = 0;
                    
                    function showPage(page) {
                        fileSections.forEach((section, index) => {
                            section.style.display = (index >= page * filesPerPage && index < (page + 1) * filesPerPage) ? 'block' : 'none';
                        });
                        document.getElementById('pageInfo').textContent = `Page ${page + 1} of ${Math.ceil(fileSections.length / filesPerPage)}`;
                        document.getElementById('prevBtn').disabled = page === 0;
                        document.getElementById('nextBtn').disabled = page === Math.ceil(fileSections.length / filesPerPage) - 1;
                    }
                    
                    function prevPage() {
                        if (currentPage > 0) {
                            currentPage--;
                            showPage(currentPage);
                        }
                    }
                    
                    function nextPage() {
                        if (currentPage < Math.ceil(fileSections.length / filesPerPage) - 1) {
                            currentPage++;
                            showPage(currentPage);
                        }
                    }
                    
                    function toggleSection(id) {
                        const element = document.getElementById(id);
                        element.classList.toggle('hidden');
                    }
                    
                    showPage(0); // Initialize first page
                } catch (e) {
                    alert('Error rendering report: ' + e.message);
                    console.error(e);
                }
            </script>
        </body>
        </html>
        """
        
        total_violations = 0
        total_incomplete = 0
        total_files = len(results)
        error_files = 0
        results_html = []
        
        # Collect actual tests that were run
        tests_executed = set()
        tests_passed = set()
        tests_inapplicable = set()
        
        # Process each file in results
        for file_path, file_results in sorted(results.items()):  # Sort for consistent order
            console.print(f"[dim]Processing file: {file_path}[/]")  # Debug: Log each file
            file_id = file_path.replace('/', '_').replace('.', '_').replace(' ', '_')
            
            if isinstance(file_results, dict) and 'error' in file_results:
                error_files += 1
                results_html.append(f'''
                <div class="file-section">
                    <h3 class="toggle" onclick="toggleSection('{file_id}')">
                        ❌ {html.escape(file_path)} <small>(Error during scan)</small>
                    </h3>
                    <div id="{file_id}" class="hidden">
                        <div class="error">
                            <p><strong>Error:</strong> {html.escape(str(file_results.get('error', 'Unknown error')))}</p>
                            {f'<p><strong>Details:</strong> {html.escape(str(file_results.get("stderr", "")))}</p>' if file_results.get("stderr") else ''}
                        </div>
                    </div>
                </div>
                ''')
            else:
                # Handle Puppeteer output (.html)
                violations = []
                incomplete = []
                passes = []
                inapplicable = []
                
                if isinstance(file_results, dict) and 'violations' in file_results:
                    # Puppeteer output
                    violations = file_results.get('violations', [])
                    incomplete = file_results.get('incomplete', [])
                    passes = file_results.get('passes', [])
                    inapplicable = file_results.get('inapplicable', [])
                    
                    # Collect test IDs from all result types
                    for violation in violations:
                        tests_executed.add(violation.get('id', 'unknown'))
                    for inc in incomplete:
                        tests_executed.add(inc.get('id', 'unknown'))
                    for pass_test in passes:
                        tests_passed.add(pass_test.get('id', 'unknown'))
                    for inapp in inapplicable:
                        tests_inapplicable.add(inapp.get('id', 'unknown'))
                
                total_violations += len(violations)
                total_incomplete += len(incomplete)
                
                console.print(f"[dim]Violations for {file_path}: {len(violations)}[/]")  # Debug: Log violations
                console.print(f"[dim]Incomplete results for {file_path}: {len(incomplete)}[/]")  # Debug: Log incomplete
                
                if violations or incomplete:
                    results_html.append(f'''
                    <div class="file-section">
                        <h3 class="toggle" onclick="toggleSection('{file_id}')">
                            📄 {html.escape(file_path)} <small>({len(violations)} violations, {len(incomplete)} incomplete)</small>
                        </h3>
                        <div id="{file_id}" class="hidden">
                    ''')
                    
                    # Render violations
                    for i, violation in enumerate(violations):
                        impact = violation.get('impact', 'unknown')
                        help_text = violation.get('help', 'No description')
                        help_url = violation.get('helpUrl', '#')
                        html_snippet = violation.get('nodes', [{}])[0].get('html', '')
                        failure_summary = violation.get('nodes', [{}])[0].get('failureSummary', '')
                        
                        # Replace problematic tags in html_snippet
                        html_snippet = html_snippet.replace('<title>', '&lt;title&gt;').replace('</title>', '&lt;/title&gt;')
                        failure_summary = html.escape(failure_summary.replace('<title>', '&lt;title&gt;').replace('</title>', '&lt;/title&gt;'))
                        
                        results_html.append(f'''
                            <div class="violation impact-{html.escape(impact)}">
                                <h4>Violation #{i+1}: {html.escape(violation.get('id', 'Unknown'))} <small>(Impact: {html.escape(impact)})</small></h4>
                                <p><strong>Description:</strong> {html.escape(help_text)}</p>
                                <p><strong>Help:</strong> <a href="{html.escape(help_url)}" target="_blank">{html.escape(help_url)}</a></p>
                                {f'<div class="code-snippet"><strong>Code:</strong> {html.escape(html_snippet)}</div>' if html_snippet else ''}
                                {f'<p><strong>Failure Summary:</strong> {failure_summary}</p>' if failure_summary else ''}
                            </div>
                        ''')
                    
                    # Render incomplete results
                    for i, inc in enumerate(incomplete):
                        impact = inc.get('impact', 'unknown')
                        help_text = inc.get('help', 'No description')
                        help_url = inc.get('helpUrl', '#')
                        html_snippet = inc.get('nodes', [{}])[0].get('html', '')
                        
                        html_snippet = html_snippet.replace('<title>', '&lt;title&gt;').replace('</title>', '&lt;/title&gt;')
                        
                        results_html.append(f'''
                            <div class="incomplete impact-{html.escape(impact)}">
                                <h4>Incomplete #{i+1}: {html.escape(inc.get('id', 'Unknown'))} <small>(Impact: {html.escape(impact)})</small></h4>
                                <p><strong>Description:</strong> {html.escape(help_text)}</p>
                                <p><strong>Help:</strong> <a href="{html.escape(help_url)}" target="_blank">{html.escape(help_url)}</a></p>
                                {f'<div class="code-snippet"><strong>Code:</strong> {html.escape(html_snippet)}</div>' if html_snippet else ''}
                            </div>
                        ''')
                    
                    results_html.append('</div></div>')
                else:
                    results_html.append(f'''
                    <div class="file-section">
                        <h3 class="toggle" onclick="toggleSection('{file_id}')">
                            ✅ {html.escape(file_path)} <small>(No violations or incomplete results)</small>
                        </h3>
                        <div id="{file_id}" class="hidden success">
                            <p>No accessibility issues found in this file.</p>
                        </div>
                    </div>
                    ''')
        
        # Generate tests executed section content
        if tests_executed or tests_passed or tests_inapplicable:
            tests_executed_section = f"""
                <div style="margin-bottom: 20px;">
                    <h4>🔴 Tests with Issues Found:</h4>
                    {f'<p><strong>Total violations/incomplete:</strong> {len(tests_executed)}</p><ul>{chr(10).join([f"<li><strong>{test_id}</strong></li>" for test_id in sorted(tests_executed)])}</ul>' if tests_executed else '<p><em>No violations or incomplete results found! 🎉</em></p>'}
                </div>
                
                <div style="margin-bottom: 20px;">
                    <h4>🟢 Tests That Passed:</h4>
                    {f'<p><strong>Total passed tests:</strong> {len(tests_passed)}</p><ul>{chr(10).join([f"<li><strong>{test_id}</strong></li>" for test_id in sorted(tests_passed)])}</ul>' if tests_passed else '<p><em>No tests passed (possibly due to errors or limited content)</em></p>'}
                </div>
                
                <div style="margin-bottom: 20px;">
                    <h4>⚪ Tests Not Applicable:</h4>
                    {f'<p><strong>Total inapplicable tests:</strong> {len(tests_inapplicable)}</p><ul>{chr(10).join([f"<li><strong>{test_id}</strong></li>" for test_id in sorted(tests_inapplicable)])}</ul>' if tests_inapplicable else '<p><em>All tests were applicable to your content</em></p>'}
                </div>
                
                <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 20px;">
                    <p><strong>📊 Total Testing Coverage:</strong></p>
                    <ul>
                        <li><strong>Total unique tests run:</strong> {len(tests_executed | tests_passed | tests_inapplicable)}</li>
                        <li><strong>Tests with issues:</strong> {len(tests_executed)}</li>
                        <li><strong>Tests passed:</strong> {len(tests_passed)}</li>
                        <li><strong>Tests not applicable:</strong> {len(tests_inapplicable)}</li>
                    </ul>
                </div>
            """
        else:
            tests_executed_section = '<p><em>No tests were executed (possibly due to errors or empty results)</em></p>'
        
        # Replace placeholders
        html_content = html_template \
            .replace('{{timestamp}}', time.strftime('%Y-%m-%d %H:%M:%S')) \
            .replace('{{total_files}}', str(total_files)) \
            .replace('{{total_violations}}', str(total_violations)) \
            .replace('{{total_incomplete}}', str(total_incomplete)) \
            .replace('{{error_files}}', str(error_files)) \
            .replace('{{repo_path}}', str(self.repo_path)) \
            .replace('{{tests_executed_section}}', tests_executed_section) \
            .replace('{{results}}', '\n'.join(results_html) if results_html else '<div class="success">🎉 No accessibility issues found!</div>')
        
        # Validate HTML size
        html_lines = len(html_content.splitlines())
        console.print(f"[dim]Generated HTML lines: {html_lines}[/]")
        if html_lines < 100 or total_files != len(results_html):
            console.print(f"[red]⚠️ Warning: HTML may be truncated. Expected {total_files} file sections, found {len(results_html)}[/]")
        
        # Save HTML report
        html_report_path = self.output_dir / "report.html"
        with open(html_report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        console.print(f"[green]✓ HTML report generated: {html_report_path} (approx. {html_lines} lines)[/]")
        return html_report_path 