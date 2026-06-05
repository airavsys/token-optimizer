#!/usr/bin/env python3
"""Documentation Optimizer Script - Optimize documentation for token efficiency."""

import os
import sys
import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple
from scripts.token_counter import TokenCounter
from scripts.utils import get_markdown_files

class DocumentationOptimizer:
    """Optimize markdown documentation for token efficiency."""

    def __init__(self, model: str = 'gpt-3.5-turbo', aggressive: bool = False):
        """Initialize optimizer."""
        self.token_counter = TokenCounter(model=model)
        self.aggressive = aggressive
        self.optimization_log = []

    def optimize_text(self, text: str) -> Tuple[str, Dict]:
        """Optimize text content."""
        original_tokens = self.token_counter.count_tokens(text)
        optimized = text
        stats = {
            'original_tokens': original_tokens,
            'changes': []
        }

        # Remove excessive whitespace
        optimized = re.sub(r'\n\n\n+', '\n\n', optimized)
        stats['changes'].append('Removed excessive blank lines')

        # Simplify language (if aggressive)
        if self.aggressive:
            replacements = {
                r'In order to': 'To',
                r'as a matter of fact': '',
                r'it is important to note that': '',
                r'it is worth noting that': '',
                r'the fact that': '',
                r'that said': '',
            }
            
            for pattern, replacement in replacements.items():
                if re.search(pattern, optimized, re.IGNORECASE):
                    optimized = re.sub(pattern, replacement, optimized, flags=re.IGNORECASE)
                    stats['changes'].append(f'Replaced "{pattern}"')

        # Remove redundant headers
        lines = optimized.split('\n')
        processed_lines = []
        last_header = None
        
        for line in lines:
            if re.match(r'^#{1,6}\s+', line):
                if line != last_header:
                    processed_lines.append(line)
                    last_header = line
            else:
                processed_lines.append(line)
                if not re.match(r'^#{1,6}\s+', line):
                    last_header = None
        
        optimized = '\n'.join(processed_lines)

        # Remove extra punctuation in titles
        optimized = re.sub(r'^(#{1,6}\s+.+?)\s*[:.!?]+\s*$', r'\1', optimized, flags=re.MULTILINE)
        stats['changes'].append('Normalized header punctuation')

        optimized_tokens = self.token_counter.count_tokens(optimized)
        stats['optimized_tokens'] = optimized_tokens
        stats['tokens_saved'] = original_tokens - optimized_tokens
        stats['reduction_percent'] = (stats['tokens_saved'] / original_tokens * 100) if original_tokens > 0 else 0

        return optimized, stats

    def optimize_file(self, filepath: str, output_path: str = None) -> Dict:
        """Optimize a single file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {'error': str(e), 'file': filepath}
        
        optimized_content, stats = self.optimize_text(content)
        
        if output_path is None:
            output_path = filepath
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(optimized_content)
        except Exception as e:
            return {'error': f'Write error: {str(e)}', 'file': filepath}
        
        return {
            'file': filepath,
            'output_file': output_path,
            **stats
        }

    def optimize_directory(self, input_dir: str, output_dir: str = None, recursive: bool = True) -> List[Dict]:
        """Optimize all markdown files in directory."""
        if output_dir is None:
            output_dir = input_dir
        
        markdown_files = get_markdown_files(input_dir, recursive)
        results = []
        
        for filepath in markdown_files:
            rel_path = os.path.relpath(filepath, input_dir)
            output_path = os.path.join(output_dir, rel_path)
            result = self.optimize_file(filepath, output_path)
            results.append(result)
        
        return results

def print_results(results: List[Dict]) -> str:
    """Format and print optimization results."""
    valid_results = [r for r in results if 'error' not in r]
    
    if not valid_results:
        return "No files optimized."
    
    output = "\n" + "=" * 80 + "\n"
    output += "DOCUMENTATION OPTIMIZATION RESULTS\n"
    output += "=" * 80 + "\n\n"
    
    total_original = sum(r['original_tokens'] for r in valid_results)
    total_optimized = sum(r['optimized_tokens'] for r in valid_results)
    total_saved = total_original - total_optimized
    total_percent = (total_saved / total_original * 100) if total_original > 0 else 0
    
    output += f"Total Files Optimized: {len(valid_results)}\n"
    output += f"Total Original Tokens: {total_original:,}\n"
    output += f"Total Optimized Tokens: {total_optimized:,}\n"
    output += f"Total Tokens Saved: {total_saved:,}\n"
    output += f"Overall Reduction: {total_percent:.1f}%\n\n"
    
    output += "FILE-BY-FILE BREAKDOWN:\n"
    output += "-" * 80 + "\n"
    
    for r in sorted(valid_results, key=lambda x: x['tokens_saved'], reverse=True):
        output += f"\n📄 {os.path.basename(r['file'])}\n"
        output += f"   Original: {r['original_tokens']:,} tokens\n"
        output += f"   Optimized: {r['optimized_tokens']:,} tokens\n"
        output += f"   Saved: {r['tokens_saved']:,} tokens ({r['reduction_percent']:.1f}%)\n"
        
        if r['changes']:
            output += f"   Changes:\n"
            for change in r['changes'][:3]:
                output += f"      - {change}\n"
    
    return output

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Optimize markdown documentation for token efficiency')
    
    parser.add_argument('input', help='Input file or directory')
    parser.add_argument('--output', help='Output directory (default: overwrite input)')
    parser.add_argument('--aggressive', action='store_true', help='Apply aggressive optimizations')
    parser.add_argument('--model', default='gpt-3.5-turbo', help='Tokenizer model')
    
    args = parser.parse_args()
    
    optimizer = DocumentationOptimizer(model=args.model, aggressive=args.aggressive)
    
    path = Path(args.input)
    if not path.exists():
        print(f"Error: Path not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    
    if path.is_file():
        result = optimizer.optimize_file(str(path), args.output)
        results = [result]
    else:
        results = optimizer.optimize_directory(str(path), args.output)
    
    output = print_results(results)
    print(output)

if __name__ == '__main__':
    main()
