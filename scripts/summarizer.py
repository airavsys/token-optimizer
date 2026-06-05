#!/usr/bin/env python3
"""Documentation Summarizer Script - Summarize documentation to reduce token usage."""

import os
import sys
import argparse
from pathlib import Path
from typing import List
import re
from scripts.token_counter import TokenCounter

class DocumentationSummarizer:
    """Summarize documentation content."""

    def __init__(self, model: str = 'gpt-3.5-turbo'):
        """Initialize summarizer."""
        self.token_counter = TokenCounter(model=model)

    def extract_sentences(self, text: str) -> List[str]:
        """Extract sentences from text."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def summarize_by_ratio(self, text: str, ratio: float = 0.5) -> str:
        """Summarize by keeping a ratio of sentences."""
        sentences = self.extract_sentences(text)
        num_sentences = max(1, int(len(sentences) * ratio))
        
        if len(sentences) <= 3:
            return text
        
        selected = []
        selected.append(sentences[0])
        
        step = len(sentences) // (num_sentences - 2) if num_sentences > 2 else 1
        for i in range(step, len(sentences) - 1, step):
            if len(selected) < num_sentences - 1:
                selected.append(sentences[i])
        
        selected.append(sentences[-1])
        
        return ' '.join(selected[:num_sentences])

    def summarize_by_sentences(self, text: str, num_sentences: int = 5) -> str:
        """Summarize to specific number of sentences."""
        sentences = self.extract_sentences(text)
        return ' '.join(sentences[:num_sentences])

    def summarize_file(self, filepath: str, ratio: float = 0.5, output_path: str = None) -> dict:
        """Summarize a file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {'error': str(e), 'file': filepath}
        
        original_tokens = self.token_counter.count_tokens(content)
        summarized = self.summarize_by_ratio(content, ratio)
        summarized_tokens = self.token_counter.count_tokens(summarized)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(summarized)
        
        return {
            'file': filepath,
            'original_tokens': original_tokens,
            'summarized_tokens': summarized_tokens,
            'tokens_saved': original_tokens - summarized_tokens,
            'reduction_percent': ((original_tokens - summarized_tokens) / original_tokens * 100) if original_tokens > 0 else 0,
            'original_sentences': len(self.extract_sentences(content)),
            'summarized_sentences': len(self.extract_sentences(summarized)),
        }

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Summarize markdown documentation')
    
    parser.add_argument('file', help='Markdown file to summarize')
    parser.add_argument('--ratio', type=float, default=0.5, help='Compression ratio (0-1)')
    parser.add_argument('--sentences', type=int, help='Number of sentences in summary')
    parser.add_argument('--output', help='Output file path')
    parser.add_argument('--model', default='gpt-3.5-turbo', help='Tokenizer model')
    
    args = parser.parse_args()
    
    summarizer = DocumentationSummarizer(model=args.model)
    
    if not os.path.exists(args.file):
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)
    
    result = summarizer.summarize_file(args.file, args.ratio, args.output)
    
    if 'error' in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    
    print(f"\n📄 Summary Results:\n")
    print(f"Original Tokens: {result['original_tokens']:,}")
    print(f"Summarized Tokens: {result['summarized_tokens']:,}")
    print(f"Tokens Saved: {result['tokens_saved']:,} ({result['reduction_percent']:.1f}%)")
    print(f"\nOriginal Sentences: {result['original_sentences']}")
    print(f"Summarized Sentences: {result['summarized_sentences']}")
    
    if args.output:
        print(f"\n✅ Summarized content written to: {args.output}")

if __name__ == '__main__':
    main()
