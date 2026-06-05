#!/usr/bin/env python3
"""Utility functions for token optimization toolkit."""

import os
from pathlib import Path
from typing import List

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

def estimate_cost(tokens: int, model: str = 'gpt-3.5-turbo') -> float:
    """Estimate API cost for tokens."""
    pricing = {
        'gpt-3.5-turbo': {'input': 0.0005, 'output': 0.0015},
        'gpt-4': {'input': 0.03, 'output': 0.06},
        'gpt-4-turbo': {'input': 0.01, 'output': 0.03},
        'claude': {'input': 0.003, 'output': 0.015},
    }
    
    if model not in pricing:
        model = 'gpt-3.5-turbo'
    
    input_cost = (tokens * 0.5) * pricing[model]['input'] / 1000
    output_cost = (tokens * 0.5) * pricing[model]['output'] / 1000
    
    return input_cost + output_cost

def calculate_tokens_per_word(tokens: int, words: int) -> float:
    """Calculate average tokens per word."""
    if words == 0:
        return 0
    return tokens / words

def calculate_compression_ratio(original_tokens: int, compressed_tokens: int) -> float:
    """Calculate compression ratio."""
    if original_tokens == 0:
        return 0
    return (original_tokens - compressed_tokens) / original_tokens
