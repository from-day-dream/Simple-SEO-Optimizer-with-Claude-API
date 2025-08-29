# Simple SEO Content Optimizer with Claude

A simple desktop application that leverages Claude API and intelligent web research to automatically enhance content for search engine optimization. The tool systematically analyzes high-performing content to identify strategic keywords and seamlessly integrates them into your text.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![PySide6](https://img.shields.io/badge/PySide6-6.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Features

### Core Functionality

- **Intelligent Keyword Research** - Automatically extracts relevant search terms and performs comprehensive web searches
- **AI-Powered Content Enhancement** - Uses Claude's advanced language model to strategically integrate high-performing keywords
- **Data-Driven Optimization** - Analyzes search patterns from top-ranking pages to inform optimization decisions

### Dependencies

```bash
PySide6>=6.0.0
requests>=2.25.0
beautifulsoup4>=4.9.0
keyring>=23.0.0
aiohttp>=3.7.0
```

## Installation

### Method 1: From Source

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/seo-optimizer.git
   cd seo-optimizer
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up assets folder**

   ```
   seo-optimizer/
   ├── optimizer.py
   └── assets/
       ├── logo.svg
       └── Manrope-Regular.ttf
   ```

4. **Run the application**
   ```bash
   python seo_optimizer.py
   ```

### Method 2: Executable

Download the prebuilt executable from Releases and run (currently only for Windows. Mac & Linux coming soon).

## Configuration

### Claude API Setup

1. Create an account at [Anthropic Console](https://console.anthropic.com)
2. Generate an API key
3. Launch the application and enter your API key
4. Click "Save Key" to store it securely

## Usage

### Basic Workflow

1. **Launch Application** - Run the executable or Python script
2. **Configure AI Backend** - Enter Claude API key or configure local LLM
3. **Input Content** - Paste your text into the left panel
4. **Optimize** - Click "Optimize for SEO" and wait for processing
5. **Review Results** - Enhanced content appears in the right panel
6. **Refine** - Make additional edits as needed

### Best Practices

- **Content Length** - Works best with 10-1000 word articles
- **Quality Input** - Provide well-written base content for best results
- **Review Output** - Always review AI suggestions before publishing
- **Test Variations** - Try different optimization approaches for A/B testing

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`python -m pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

### Common Issues

- **Import Errors** - Ensure all dependencies are installed: `pip install -r requirements.txt`
- **Font Loading** - Verify `assets/Manrope-Regular.ttf` exists
- **API Errors** - Check your Claude API key and account credits

### Getting Help

- 📧 Email: support@day-dream.studio
- 🐛 Bug Reports: [GitHub Issues](https://github.com/yourusername/seo-optimizer/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/seo-optimizer/discussions)

## 🙏 Acknowledgments

- [Anthropic](https://anthropic.com) for Claude API
- [Qt Project](https://qt.io) for PySide6 framework
- [Manrope Font](https://github.com/sharanda/manrope) by Mikhail Sharanda
- Community contributors and testers

---

**Built with ❤️ by [day-dream](https://day-dream.studio)**
