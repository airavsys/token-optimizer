# Token Optimizer Toolkit

A comprehensive Python toolkit for optimizing documentation and analyzing token usage for AI/LLM applications.

## 🎯 Features

- ✅ **Token Counting** - Analyze token usage across markdown files
- ✅ **Documentation Analysis** - Generate reports on documentation metrics
- ✅ **Automatic Summarization** - Compress documentation while preserving meaning
- ✅ **Markdown Linting** - Enforce documentation best practices
- ✅ **Batch Processing** - Process entire documentation directories
- ✅ **CI/CD Integration** - GitHub Actions workflows included
- ✅ **Token Tracking** - Monitor token usage over time
- ✅ **Optimization Recommendations** - Get suggestions for token reduction

## 📋 Quick Start

### Installation

```bash
git clone https://github.com/airavsys/token-optimizer.git
cd token-optimizer
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

#Basic Usage
python scripts/token_counter.py docs/ --detailed
python scripts/doc_analyzer.py docs/
python scripts/generate_report.py docs/ --format markdown
python scripts/doc_optimizer.py docs/ --output optimized_docs/
