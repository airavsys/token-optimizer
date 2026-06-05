#!/usr/bin/env python3
"""Documentation Analyzer Script - Analyze documentation structure and metrics."""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List
from collections import defaultdict
import re
from scripts.token_counter import TokenCounter
from scripts.utils import get_markdown_files, format_bytes
from tabulate import tabulate

class DocumentationAnalyzer:
    """Analyze documentation files and structure."""

    def __init__(self, model: str = 'gpt-3.5-turbo'):
        """Initialize analyzer."""
        self.token_counter = TokenCounter(model=model)
        self.model = model

    def extract_headers(self, content: str) -> List[tuple]:
        """Extract headers and their levels from markdown."""
        headers = []
        for line in content.split('\n'):
            match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if match:
                level = len(match.group(1))
                title = match.group(2)
                headers.append((level, title))
        return headers

    def extract_sections(self, content: str) -> Dict[str, Dict]:
        """Extract sections and analyze each."""
        headers = self.extract_headers(content)
        sections = defaultdict(lambda: {'tokens': 0, 'lines': 0, 'content': ''})
        
        current_section = 'intro'
        lines = content.split('\n')
        current_content = []
        
        for line in lines:
            if re.match(r'^#{1,6}\s+', line):
                if current_content:
                    section_text = '\n'.join(current_content)
                    sections[current_section]['tokens'] = self.token_counter.count_tokens(section_text)
                    sections[current_section]['content'] = section_text
                    sections[current_section]['lines'] = len(current_content)
                
                current_section = line.strip()
                current_content = [line]
            else:
                current_content.append(line)
        
        if current_content:
            section_text = '\n'.join(current_content)
            sections[current_section]['tokens'] = self.token_counter.count_tokens(section_text)
            sections[current_section]['content'] = section_text
            sections[current_section]['lines'] = len(current_content)
        
        return dict(sections)

    def analyze_file(self, filepath: str) -> Dict:
        """Analyze a single file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {'error': str(e), 'file': filepath}
        
        file_size = os.path.getsize(filepath)
        lines = content.split('\n')
        words = content.split()
        
        total_tokens = self.token_counter.count_tokens(content)
        headers = self.extract_headers(content)
        sections = self.extract_sections(content)
        
        code_blocks = len(re.findall(r'^```', content, re.MULTILINE))
        links = len(re.findall(r'\[.+?\]\(.+?\)', content))
        lists = len(re.findall(r'^[\-\*\+]\s+', content, re.MULTILINE))
        tables = len(re.findall(r'^\|.+?\|$', content, re.MULTILINE))
        
        return {
            'file': filepath,
            'file_size': file_size,
            'file_size_human': format_bytes(file_size),
            'total_tokens': total_tokens,
            'total_lines': len(lines),
            'total_words': len(words),
            'total_characters': len(content),
            'headers_count': len(headers),
            'sections_count': len(sections),
            'code_blocks': code_blocks,
            'links': links,
            'lists': lists,
            'tables': tables,
            'headers': headers,
            'sections': sections,
            'avg_tokens_per_section': total_tokens / len(sections) if sections else 0,
            'avg_words_per_line': len(words) / len(lines) if lines else 0,
        }

    def analyze_directory(self, directory: str, recursive: bool = True) -> List[Dict]:
        """Analyze all markdown files in directory."""
        markdown_files = get_markdown_files(directory, recursive)
        results = []
        
        for filepath in markdown_files:
            result = self.analyze_file(filepath)
            results.append(result)
        
        return results

    def generate_summary(self, results: List[Dict]) -> Dict:
        """Generate summary statistics."""
        valid_results = [r for r in results if 'error' not in r]
        
        if not valid_results:
            return {}
        
        return {
            'total_files': len(valid_results),
            'total_tokens': sum(r['total_tokens'] for r in valid_results),
            'total_words': sum(r['total_words'] for r in valid_results),
            'total_lines': sum(r['total_lines'] for r in valid_results),
            'total_size': sum(r['file_size'] for r in valid_results),
            'avg_tokens_per_file': sum(r['total_tokens'] for r in valid_results) / len(valid_results),
            'avg_tokens_per_section': sum(r['avg_tokens_per_section'] for r in valid_results) / len(valid_results),
            'largest_file': max(valid_results, key=lambda x: x['total_tokens'])['file'],
            'largest_file_tokens': max(r['total_tokens'] for r in valid_results),
        }

def format_report(results: List[Dict], summary: Dict, threshold: int = None) -> str:
    """Format analysis report."""
    valid_results = [r for r in results if 'error' not in r]
    
    output = "=" * 80 + "\n"
    output += "DOCUMENTATION ANALYSIS REPORT\n"
    output += "=" * 80 + "\n\n"
    
    if summary:
        output += "SUMMARY\n"
        output += "-" * 80 + "\n"
        output += f"Total Files: {summary['total_files']}\n"
        output += f"Total Tokens: {summary['total_tokens']:,}\n"
        output += f"Total Words: {summary['total_words']:,}\n"
        output += f"Total Lines: {summary['total_lines']:,}\n"
        output += f"Total Size: {format_bytes(summary['total_size'])}\n"
        output += f"Avg Tokens per File: {summary['avg_tokens_per_file']:.0f}\n"
        output += f"Avg Tokens per Section: {summary['avg_tokens_per_section']:.0f}\n"
        output += f"Largest File: {os.path.basename(summary['largest_file'])} ({summary['largest_file_tokens']:,} tokens)\n\n"
    
    output += "FILE BREAKDOWN\n"
    output += "-" * 80 + "\n"
    headers = ['File', 'Tokens', 'Sections', 'Words', 'Size']
    rows = []
    
    for r in sorted(valid_results, key=lambda x: x['total_tokens'], reverse=True):
        marker = " ⚠️" if threshold and r['total_tokens'] > threshold else ""
        rows.append([
            os.path.basename(r['file']) + marker,
            f"{r['total_tokens']:,}",
            f"{r['sections_count']}",
            f"{r['total_words']:,}",
            r['file_size_human']
        ])
    
    output += tabulate(rows, headers=headers, tablefmt='grid') + "\n\n"
    
    output += "DETAILED ANALYSIS\n"
    output += "-" * 80 + "\n"
    headers = ['File', 'Headers', 'Code', 'Links', 'Lists', 'Tables']
    rows = []
    
    for r in valid_results:
        rows.append([
            os.path.basename(r['file']),
            r['headers_count'],
            r['code_blocks'],
            r['links'],
            r['lists'],
            r['tables']
        ])
    
    output += tabulate(rows, headers=headers, tablefmt='grid') + "\n"
    
    return output

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Analyze documentation structure and metrics')
    
    parser.add_argument('path', help='Documentation directory')
    parser.add_argument('--threshold', type=int, help='Token threshold for warnings')
    parser.add_argument('--format', choices=['text', 'json'], default='text', help='Output format')
    parser.add_argument('--output', help='Output file path')
    parser.add_argument('--model', default='gpt-3.5-turbo', help='Tokenizer model')
    
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
        output = json.dumps({'summary': summary, 'files': results}, indent=2, default=str)
    else:
        output = format_report(results, summary, args.threshold)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Report written to {args.output}")
    else:
        print(output)

if __name__ == '__main__':
    main()
