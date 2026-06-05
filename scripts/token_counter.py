#!/usr/bin/env python3
"""
Token Counter Script - Count tokens in markdown files
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List
import tiktoken
from tabulate import tabulate

def get_markdown_files(directory: str, recursive: bool = True) -> List[str]:
    """Get all markdown files in a directory."""
    md_files = []
    if recursive:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.md'):
                    md_files.append(os.path.join(root, file))
    else:
        for file in os.listdir(directory):
            if file.endswith('.md'):
                filepath = os.path.join(directory, file)
                if os.path.isfile(filepath):
                    md_files.append(filepath)
    return sorted(md_files)

def format_bytes(bytes_size: int) -> str:
    """Format bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"

class TokenCounter:
    """Count tokens in text using various tokenizer models."""

    MODELS = {
        'gpt-3.5-turbo': 'cl100k_base',
        'gpt-4': 'cl100k_base',
        'gpt-4-turbo': 'cl100k_base',
        'claude': 'cl100k_base',
    }

    def __init__(self, model: str = 'gpt-3.5-turbo'):
        """Initialize token counter with specified model."""
        if model not in self.MODELS:
            raise ValueError(f"Model {model} not supported. Choose from: {list(self.MODELS.keys())}")
        
        self.model = model
        self.encoding_name = self.MODELS[model]
        self.encoding = tiktoken.get_encoding(self.encoding_name)
        self.cache = {}

    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        if not text:
            return 0
        text_hash = hash(text)
        if text_hash in self.cache:
            return self.cache[text_hash]
        tokens = len(self.encoding.encode(text))
        self.cache[text_hash] = tokens
        return tokens

    def count_tokens_detailed(self, text: str) -> Dict:
        """Get detailed token breakdown."""
        lines = text.split('\n')
        analysis = {
            'total_tokens': self.count_tokens(text),
            'total_characters': len(text),
            'total_words': len(text.split()),
            'total_lines': len(lines),
            'avg_tokens_per_line': 0,
            'avg_tokens_per_word': 0,
        }
        
        if analysis['total_lines'] > 0:
            analysis['avg_tokens_per_line'] = analysis['total_tokens'] / analysis['total_lines']
        if analysis['total_words'] > 0:
            analysis['avg_tokens_per_word'] = analysis['total_tokens'] / analysis['total_words']
        
        return analysis

    def analyze_file(self, filepath: str) -> Dict:
        """Analyze a single markdown file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {'error': str(e), 'file': filepath}
        
        file_size = os.path.getsize(filepath)
        detailed = self.count_tokens_detailed(content)
        
        return {
            'file': filepath,
            'file_size': file_size,
            'file_size_human': format_bytes(file_size),
            **detailed
        }

    def analyze_directory(self, directory: str, recursive: bool = True) -> List[Dict]:
        """Analyze all markdown files in directory."""
        markdown_files = get_markdown_files(directory, recursive)
        results = []
        for filepath in markdown_files:
            result = self.analyze_file(filepath)
            results.append(result)
        return results

def print_results(results: List[Dict], detailed: bool = False, csv: bool = False) -> str:
    """Format and print results."""
    if not results:
        return "No files analyzed."
    
    valid_results = [r for r in results if 'error' not in r]
    
    if csv:
        headers = ['File', 'Tokens', 'Words', 'Characters', 'Size']
        rows = []
        for r in valid_results:
            rows.append([
                r['file'],
                r['total_tokens'],
                r['total_words'],
                r['total_characters'],
                r['file_size_human']
            ])
        return '\n'.join([','.join(headers)] + [','.join(str(x) for x in row) for row in rows])
    
    if detailed:
        headers = ['File', 'Tokens', 'Words', 'Lines', 'Tokens/Line', 'Size']
        rows = []
        for r in valid_results:
            rows.append([
                os.path.basename(r['file']),
                r['total_tokens'],
                r['total_words'],
                r['total_lines'],
                f"{r['avg_tokens_per_line']:.1f}",
                r['file_size_human']
            ])
        
        output = tabulate(rows, headers=headers, tablefmt='grid')
        total_tokens = sum(r['total_tokens'] for r in valid_results)
        total_words = sum(r['total_words'] for r in valid_results)
        total_size = sum(r['file_size'] for r in valid_results)
        
        output += f"\n\nSummary:\n"
        output += f"Total Files: {len(valid_results)}\n"
        output += f"Total Tokens: {total_tokens:,}\n"
        output += f"Total Words: {total_words:,}\n"
        output += f"Total Size: {format_bytes(total_size)}\n"
        output += f"Average Tokens/File: {total_tokens / len(valid_results):.0f}\n"
        
        return output
    else:
        headers = ['File', 'Tokens', 'Words', 'Size']
        rows = []
        for r in valid_results:
            rows.append([
                os.path.basename(r['file']),
                r['total_tokens'],
                r['total_words'],
                r['file_size_human']
            ])
        return tabulate(rows, headers=headers, tablefmt='grid')

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Count tokens in markdown documentation'
    )
    
    parser.add_argument('path', help='File or directory to analyze')
    parser.add_argument('--model', default='gpt-3.5-turbo', help='Tokenizer model')
    parser.add_argument('--detailed', action='store_true', help='Show detailed analysis')
    parser.add_argument('--csv', action='store_true', help='Output as CSV')
    parser.add_argument('--output', help='Output file path')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    try:
        counter = TokenCounter(model=args.model)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    path = Path(args.path)
    if not path.exists():
        print(f"Error: Path not found: {args.path}", file=sys.stderr)
        sys.exit(1)
    
    if path.is_file():
        results = [counter.analyze_file(str(path))]
    else:
        results = counter.analyze_directory(str(path))
    
    if args.json:
        output = json.dumps(results, indent=2)
    else:
        output = print_results(results, detailed=args.detailed, csv=args.csv)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Results written to {args.output}")
    else:
        print(output)

if __name__ == '__main__':
    main()
