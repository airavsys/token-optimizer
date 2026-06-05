#!/usr/bin/env python3
"""Report Generation Script - Generate comprehensive token optimization reports."""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from scripts.doc_analyzer import DocumentationAnalyzer
from scripts.utils import format_bytes, estimate_cost

def generate_json_report(analyzer, results, summary) -> str:
    """Generate JSON report."""
    report = {
        'timestamp': datetime.now().isoformat(),
        'summary': summary,
        'files': results,
    }
    return json.dumps(report, indent=2, default=str)

def generate_markdown_report(analyzer, results, summary, include_recommendations=True) -> str:
    """Generate Markdown report."""
    valid_results = [r for r in results if 'error' not in r]
    
    output = "# Token Optimization Report\n\n"
    output += f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
    
    output += "## Executive Summary\n\n"
    if summary:
        output += f"- **Total Files**: {summary['total_files']}\n"
        output += f"- **Total Tokens**: {summary['total_tokens']:,}\n"
        output += f"- **Total Words**: {summary['total_words']:,}\n"
        output += f"- **Total Size**: {format_bytes(summary['total_size'])}\n"
        output += f"- **Avg Tokens/File**: {summary['avg_tokens_per_file']:.0f}\n"
        output += f"- **Avg Tokens/Section**: {summary['avg_tokens_per_section']:.0f}\n\n"
    
    total_tokens = summary.get('total_tokens', 0) if summary else 0
    output += "## Cost Analysis\n\n"
    output += "| Model | Estimated Cost | Reduction (30%) |\n"
    output += "|-------|---|---|\n"
    for model in ['gpt-3.5-turbo', 'gpt-4', 'claude']:
        cost = estimate_cost(total_tokens, model)
        cost_reduced = estimate_cost(int(total_tokens * 0.7), model)
        output += f"| {model} | ${cost:.4f} | ${cost_reduced:.4f} |\n"
    output += "\n"
    
    output += "## File Analysis\n\n"
    output += "| File | Tokens | Words | Sections | Size |\n"
    output += "|------|--------|-------|----------|------|\n"
    
    for r in sorted(valid_results, key=lambda x: x['total_tokens'], reverse=True):
        output += f"| {os.path.basename(r['file'])} | {r['total_tokens']:,} | {r['total_words']:,} | {r['sections_count']} | {r['file_size_human']} |\n"
    output += "\n"
    
    if include_recommendations:
        output += "## Optimization Recommendations\n\n"
        output += "### High Priority (>2000 tokens)\n\n"
        
        large_files = [r for r in valid_results if r['total_tokens'] > 2000]
        if large_files:
            for r in sorted(large_files, key=lambda x: x['total_tokens'], reverse=True):
                potential_savings = int(r['total_tokens'] * 0.25)
                output += f"- **{os.path.basename(r['file'])}**: {r['total_tokens']:,} tokens → Potential savings: ~{potential_savings:,} tokens\n"
        else:
            output += "- No files exceed 2000 tokens\n"
        
        output += "\n### Optimization Strategies\n\n"
        output += "1. **Consolidate Related Content**: Reduce duplication by merging similar sections\n"
        output += "2. **Use Tables**: Convert prose lists to table format for 15-30% token reduction\n"
        output += "3. **Add Cross-References**: Link to sections instead of repeating content\n"
        output += "4. **Shorten Examples**: Keep examples focused and concise\n"
        output += "5. **Remove Redundancy**: Identify and consolidate repeated explanations\n\n"
    
    return output

def generate_html_report(analyzer, results, summary) -> str:
    """Generate HTML report."""
    valid_results = [r for r in results if 'error' not in r]
    
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Token Optimization Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
        h1 { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
        h2 { color: #555; margin-top: 30px; }
        table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #007bff; color: white; }
        tr:hover { background-color: #f9f9f9; }
        .metric { display: inline-block; margin: 10px 20px 10px 0; }
        .metric-value { font-size: 24px; font-weight: bold; color: #007bff; }
        .metric-label { font-size: 14px; color: #666; }
        .summary { background: #e8f4f8; padding: 15px; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Token Optimization Report</h1>
        <p><em>Generated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</em></p>
        
        <div class="summary">
            <h2>Executive Summary</h2>
    """
    
    if summary:
        html += f"""<div class="metric">
            <div class="metric-label">Total Files</div>
            <div class="metric-value">{summary['total_files']}</div>
        </div>
        <div class="metric">
            <div class="metric-label">Total Tokens</div>
            <div class="metric-value">{summary['total_tokens']:,}</div>
        </div>
        <div class="metric">
            <div class="metric-label">Total Words</div>
            <div class="metric-value">{summary['total_words']:,}</div>
        </div>
        """
    
    html += """</div>
        
        <h2>File Analysis</h2>
        <table>
            <tr>
                <th>File</th>
                <th>Tokens</th>
                <th>Words</th>
                <th>Sections</th>
                <th>Size</th>
            </tr>
    """
    
    for r in sorted(valid_results, key=lambda x: x['total_tokens'], reverse=True):
        html += f"""<tr>
                <td>{os.path.basename(r['file'])}</td>
                <td>{r['total_tokens']:,}</td>
                <td>{r['total_words']:,}</td>
                <td>{r['sections_count']}</td>
                <td>{r['file_size_human']}</td>
            </tr>
        """
    
    html += """</table>
    </div>
</body>
</html>
    """
    
    return html

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Generate token optimization reports')
    
    parser.add_argument('path', help='Documentation directory')
    parser.add_argument('--format', choices=['json', 'markdown', 'html'], default='markdown', help='Report format')
    parser.add_argument('--output', help='Output file path')
    parser.add_argument('--model', default='gpt-3.5-turbo', help='Tokenizer model')
    parser.add_argument('--include-recommendations', action='store_true', help='Include optimization recommendations')
    
    args = parser.parse_args()
    
    analyzer = DocumentationAnalyzer(model=args.model)
    
    path = Path(args.path)
    if not path.exists():
        print(f"Error: Path not found: {args.path}", file=sys.stderr)
        sys.exit(1)
    
    if path.is_file():
        results = [analyzer.analyze_file(str(path))]
    else:
        results = analyzer.analyze_directory(str(path))
    
    summary = analyzer.generate_summary(results)
    
    if args.format == 'json':
        output = generate_json_report(analyzer, results, summary)
    elif args.format == 'html':
        output = generate_html_report(analyzer, results, summary)
    else:
        output = generate_markdown_report(analyzer, results, summary, args.include_recommendations)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Report written to {args.output}")
    else:
        print(output)

if __name__ == '__main__':
    main()
