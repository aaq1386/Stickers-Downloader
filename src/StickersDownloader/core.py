import os
import aiohttp
import asyncio
from urllib.parse import urlparse
from typing import List, Optional
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn

from .utils import console
from .converter import TgsToGifConverter


class StickersDownloader:
    BASE_URL = "https://api.telegram.org/bot{token}/"

    def __init__(self, token: str, pack_link: str, sticker_type: str, fps: int = 30):
        if sticker_type not in ["animated", "static"]:
            raise ValueError("sticker_type must be 'animated' or 'static'")

        self.token = token
        self.sticker_type = sticker_type
        self.pack_name = self._extract_pack_name(pack_link)
        self.fps = fps
        self.converter = TgsToGifConverter(fps) if sticker_type == "animated" else None

        self.output_dir = os.path.join("downloads", sticker_type, self.pack_name)
        os.makedirs(self.output_dir, exist_ok=True)

    @staticmethod
    def _extract_pack_name(link: str) -> str:
        return urlparse(link).path.split('/')[-1]

    async def _request(self, session: aiohttp.ClientSession, method: str, params: dict):
        url = f"{self.BASE_URL.format(token=self.token)}{method}"
        async with session.get(url, params=params, timeout=10) as resp:
            data = await resp.json()
            if not data.get("ok"):
                raise Exception(f"API error: {data}")
            return data["result"]

    async def fetch_stickers(self, session: aiohttp.ClientSession) -> List[dict]:
        return await self._request(session, "getStickerSet", {"name": self.pack_name})

    async def download_file(self, session: aiohttp.ClientSession, file_id: str, save_path: str):
        file_info = await self._request(session, "getFile", {"file_id": file_id})
        file_url = f"https://api.telegram.org/file/bot{self.token}/{file_info['file_path']}"

        async with session.get(file_url) as resp:
            with open(save_path, "wb") as f:
                f.write(await resp.read())

    async def process_sticker(self, session: aiohttp.ClientSession, sticker: dict, progress, task):
        emoji = sticker["emoji"]
        uid = sticker["file_unique_id"]
        ext = "tgs" if self.sticker_type == "animated" else "webp"
        filename = f"{emoji}_{uid}.{ext}"
        filepath = os.path.join(self.output_dir, filename)

        try:
            if not os.path.exists(filepath):
                await self.download_file(session, sticker["file_id"], filepath)
                console.print(f"[green]✓ Downloaded: {filename}[/green]")
            else:
                console.print(f"[dim]⏭️ Skipped (already exists): {filename}[/dim]")

            if self.sticker_type == "animated" and self.converter and self.converter.available:
                gif_path = filepath.replace(".tgs", ".gif")
                if not os.path.exists(gif_path):
                    await self.converter.convert(filepath, gif_path)
                else:
                    console.print(f"[dim]⏭️ GIF already exists: {os.path.basename(gif_path)}[/dim]")
            
            progress.update(task, advance=1)
            
        except Exception as e:
            console.print(f"[red]❌ Failed to process {filename}: {e}[/red]")
            progress.update(task, advance=1)

    async def run(self, selected_indexes: Optional[List[int]] = None):
        async with aiohttp.ClientSession() as session:
            try:
                result = await self.fetch_stickers(session)
                stickers = result["stickers"]
            except Exception as e:
                console.print(f"[red]Failed to fetch: {e}[/red]")
                return

            if selected_indexes:
                stickers = [stickers[i] for i in selected_indexes]

            console.print(f"[bold blue]📦 Pack:[/bold blue] {self.pack_name}")
            console.print(f"[bold green]🎨 Type:[/bold green] {self.sticker_type}")
            console.print(f"[bold yellow]🔢 Count:[/bold yellow] {len(stickers)}")

            with Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                "[progress.percentage]{task.percentage:>3.0f}%",
                TimeRemainingColumn(),
                console=console
            ) as progress:
                task = progress.add_task("[cyan]Downloading...[/cyan]", total=len(stickers))
                await asyncio.gather(*[
                    self.process_sticker(session, s, progress, task) for s in stickers
                ])
                
            console.print(f"[bold green]✅ All done! Files saved in: {self.output_dir}[/bold green]")