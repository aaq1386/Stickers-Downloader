# StickersDownloader

A Python package for downloading and converting Telegram sticker packs, including animated stickers (TGS format) to GIF.

## Features

- Download static stickers (WEBP format) from Telegram sticker packs
- Download animated stickers (TGS format) with automatic conversion to GIF
- Select specific stickers by index or download entire packs
- Configurable FPS for GIF output
- Organized output structure: `downloads/static/` and `downloads/animated/`
- Async HTTP requests for optimal performance
- Rich console output with progress bars
- Automatic retry mechanism for failed requests

## Installation

```bash
pip install stickers-downloader
```

### Requirements

- Python 3.8 or higher
- System dependencies:
  - **Windows**: Visual C++ Build Tools
  - **Linux**: build-essential, cmake, liblz4-dev
  - **macOS**: Xcode Command Line Tools

## Usage

### Command Line Interface

Basic usage:

```bash
python -m stickers_downloader <BOT_TOKEN> <STICKER_PACK_LINK> <TYPE>
```

Parameters:
- `BOT_TOKEN`: Your Telegram bot token (from @BotFather)
- `STICKER_PACK_LINK`: Full URL of the sticker pack (e.g., https://t.me/addstickers/PackName)
- `TYPE`: `static` for WEBP stickers or `animated` for TGS+GIF

Options:
- `--fps`: FPS for GIF conversion (default: 30, animated type only)
- `--indexes`: Comma-separated list of sticker indexes to download

Examples:

```bash
# Download all static stickers
python -m stickers_downloader 123456:ABC-DEF1234 https://t.me/addstickers/ExamplePack static

# Download animated stickers with custom FPS
python -m stickers_downloader 123456:ABC-DEF1234 https://t.me/addstickers/ExamplePack animated --fps 50

# Download specific stickers by index
python -m stickers_downloader 123456:ABC-DEF1234 https://t.me/addstickers/ExamplePack animated --indexes 0,2,5
```

### Python API

```python
import asyncio
from stickers_downloader import StickersDownloader

async def main():
    # Initialize downloader
    downloader = StickersDownloader(
        token="YOUR_BOT_TOKEN",
        pack_link="https://t.me/addstickers/ExamplePack",
        sticker_type="animated",  # or "static"
        fps=30  # optional, default 30
    )
    
    # Download all stickers
    await downloader.run()
    
    # Download specific stickers
    await downloader.run(selected_indexes=[0, 2, 5])

asyncio.run(main())
```

## Output Structure

Downloads are organized in the following structure:

```
downloads/
├── static/
│   └── PackName/
│       ├── 😀_fileid1.webp
│       └── 😂_fileid2.webp
└── animated/
    └── PackName/
        ├── 😀_fileid1.tgs
        ├── 😀_fileid1.gif
        ├── 😂_fileid2.tgs
        └── 😂_fileid2.gif
```

## Dependencies

- `aiohttp>=3.9.0`: Async HTTP client
- `rlottie-python>=1.2.0`: Lottie animation renderer for TGS to GIF conversion
- `rich>=13.7.0`: Terminal formatting and progress bars

## Development

Install development dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Links

- [GitHub Repository](https://github.com/MrAAQPy/StickersDownloader)
- [Issue Tracker](https://github.com/MrAAQPy/StickersDownloader/issues)
- [PyPI Package](https://pypi.org/project/stickers-downloader/)

## Author

Ali Ayati Qaffari - [ayatiali910@gmail.com](mailto:ayatiali910@gmail.com)