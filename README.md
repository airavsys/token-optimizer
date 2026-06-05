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
# Clone repository
git clone https://github.com/airavsys/token-optimizer.git
cd token-optimizer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```bash
# Count tokens in files
python scripts/token_counter.py docs/ --detailed

# Analyze documentation
python scripts/doc_analyzer.py docs/ --threshold 2000

# Generate optimization report
python scripts/generate_report.py docs/ --format markdown --output report.md

# Optimize documentation
python scripts/doc_optimizer.py docs/ --output optimized_docs/

# Summarize documents
python scripts/summarizer.py docs/guide.md --ratio 0.5
```

## 📁 File Structure

```
token-optimizer/
├── scripts/
│   ├── token_counter.py
│   ├── doc_analyzer.py
│   ├── doc_optimizer.py
│   ├── summarizer.py
│   ├── generate_report.py
│   └── utils.py
├── config/
│   ├── .markdownlintrc
│   ├── .prettierrc
│   └── token_config.yaml
├── .github/workflows/
│   ├── token-check.yml
│   └── doc-optimization.yml
├── docs/examples/
├── requirements.txt
└── README.md
```

## 💻 Scripts Overview

| Script | Purpose |
|--------|---------|
| `token_counter.py` | Count tokens in markdown files |
| `doc_analyzer.py` | Analyze documentation structure |
| `doc_optimizer.py` | Optimize documentation |
| `summarizer.py` | Summarize content |
| `generate_report.py` | Generate reports |

## 🔧 Configuration

Edit `config/token_config.yaml` to customize token models, optimization targets, and linting rules.

## 💡 Best Practices

1. **Use lists instead of prose** - More efficient and readable
2. **Use tables for data** - 30-40% token reduction vs prose
3. **Remove redundancy** - Eliminate repeated sections
4. **Keep examples brief** - Only essential code
5. **Use active voice** - Shorter sentences, fewer tokens

## 🚀 GitHub Actions

- **token-check.yml** - Analyzes PRs for token changes
- **doc-optimization.yml** - Daily optimization with auto-PR

## 📖 Documentation

- [Getting Started Guide](docs/examples/getting-started.md)
- [API Reference](docs/examples/api-reference.md)
- [Best Practices](docs/examples/best-practices.md)

## 🔌 Supported Models

- GPT-3.5-turbo, GPT-4, GPT-4-turbo
- Claude 3
- Llama 2, Mistral

## ⚡ Performance Tips

1. **Caching** - Token counts are cached
2. **Incremental** - Only analyze changed files
3. **Batch Processing** - Process multiple files together
4. **Compression** - Export as compressed JSON

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Module not found | `pip install -r requirements.txt` |
| No files found | Verify `.md` extension and path |
| Permission denied | `chmod +x scripts/*.py` |

## 📄 License

MIT License - Feel free to use and modify!

## 💬 Support

- Open GitHub issues for bugs
- Discussions for questions
- Pull requests for contributions

---

**Start optimizing your documentation tokens today!** 🚀
