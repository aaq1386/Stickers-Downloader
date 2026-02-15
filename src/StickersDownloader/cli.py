import argparse
import asyncio
import sys
from .core import StickersDownloader
from .utils import console


def main():
    parser = argparse.ArgumentParser(
        description="Telegram Sticker Pack Downloader",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s 123456:ABCdef https://t.me/addstickers/Example static
  %(prog)s 123456:ABCdef https://t.me/addstickers/Example animated --fps 50
  %(prog)s 123456:ABCdef https://t.me/addstickers/Example animated --indexes 0,2,5
        """
    )
    
    parser.add_argument(
        "token",
        help="Telegram Bot Token (from @BotFather)"
    )
    
    parser.add_argument(
        "link",
        help="Sticker pack link (e.g., https://t.me/addstickers/PackName)"
    )
    
    parser.add_argument(
        "type",
        choices=["static", "animated"],
        help="static (WEBP) or animated (TGS+GIF)"
    )
    
    parser.add_argument(
        "--fps",
        type=int,
        default=30,
        help="FPS for GIF conversion (default: 30, animated only)"
    )
    
    parser.add_argument(
        "--indexes",
        type=str,
        help="Comma-separated sticker indexes to download (e.g., 0,2,5)"
    )
    
    args = parser.parse_args()
    
    selected = None
    if args.indexes:
        try:
            selected = [int(i.strip()) for i in args.indexes.split(",") if i.strip().isdigit()]
            console.print(f"[cyan]Selected indexes: {selected}[/cyan]")
        except ValueError:
            console.print("[red]Invalid indexes format. Use comma-separated numbers.[/red]")
            sys.exit(1)
    
    try:
        downloader = StickersDownloader(
            token=args.token,
            pack_link=args.link,
            sticker_type=args.type,
            fps=args.fps
        )
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    
    try:
        asyncio.run(downloader.run(selected_indexes=selected))
    except KeyboardInterrupt:
        console.print("\n[yellow]Download cancelled by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()