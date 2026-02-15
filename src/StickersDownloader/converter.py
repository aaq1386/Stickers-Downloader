import os
from .utils import load_lottie_auto, is_rlottie_available, console, get_available_methods
import asyncio
import traceback
from typing import List


class TgsToGifConverter:
    def __init__(self, fps: int = 30):
        self.fps = fps
        self.available = is_rlottie_available()
        
        if not self.available:
            console.print("[yellow]⚠️ TGS to GIF conversion disabled (rlottie-python not installed)[/yellow]")
        else:
            methods = get_available_methods()
            if methods:
                console.print(f"[dim]Available rlottie methods: {', '.join(methods)}[/dim]")

    async def convert(self, tgs_path: str, gif_path: str):
        if not self.available:
            console.print(f"[yellow]⚠️ Skipping conversion (rlottie not available): {os.path.basename(tgs_path)}[/yellow]")
            return False
        
        try:
            console.print(f"[cyan]🔄 Converting: {os.path.basename(tgs_path)} -> {os.path.basename(gif_path)}[/cyan]")
            anim = load_lottie_auto(tgs_path)
            
            converted = False
            
            if hasattr(anim, 'save_gif'):
                anim.save_gif(gif_path, self.fps)
                converted = True
                console.print(f"[green]✓ Saved with save_gif method[/green]")
            elif hasattr(anim, 'save_animation'):
                try:
                    anim.save_animation(gif_path, self.fps)
                    converted = True
                    console.print(f"[green]✓ Saved with save_animation (with FPS)[/green]")
                except Exception as e:
                    console.print(f"[dim]save_animation with FPS failed: {e}[/dim]")
                    try:
                        anim.save_animation(gif_path)
                        converted = True
                        console.print(f"[green]✓ Saved with save_animation (without FPS)[/green]")
                    except Exception as e2:
                        console.print(f"[dim]save_animation without FPS failed: {e2}[/dim]")
            
            if not converted:
                converted = self._render_gif_frame_by_frame(anim, gif_path)

            if not converted:
                save_methods = [m for m in dir(anim) if 'save' in m.lower() and ('gif' in m.lower() or 'animation' in m.lower())]
                
                for method_name in save_methods:
                    try:
                        method = getattr(anim, method_name)
                        try:
                            method(gif_path, self.fps)
                            converted = True
                            console.print(f"[green]✓ Saved with {method_name} (with FPS)[/green]")
                            break
                        except:
                            try:
                                method(gif_path)
                                converted = True
                                console.print(f"[green]✓ Saved with {method_name} (without FPS)[/green]")
                                break
                            except:
                                continue
                    except:
                        continue
            
            if converted:
                console.print(f"[bold green]✅ Converted: {os.path.basename(tgs_path)} -> {os.path.basename(gif_path)}[/bold green]")
                return True
            else:
                raise Exception("No suitable save method found")
            
        except Exception as e:
            console.print(f"[red]❌ Convert failed {os.path.basename(tgs_path)}: {e}[/red]")
            traceback.print_exc()  
            return False

    def _render_gif_frame_by_frame(self, anim, gif_path: str) -> bool:
        """Fallback GIF renderer for rlottie builds where `save_animation` fails."""
        if not hasattr(anim, 'render_pillow_frame'):
            return False

        try:
            total_frames = self._resolve_total_frames(anim)
            if total_frames <= 0:
                console.print("[dim]Frame-by-frame fallback skipped: total frame count is zero[/dim]")
                return False

            frame_duration_ms = self._resolve_frame_duration_ms(anim)
            frames: List = []

            for frame_no in range(total_frames):
                frame = anim.render_pillow_frame(frame_no)
                if frame.mode != 'RGBA':
                    frame = frame.convert('RGBA')
                frames.append(frame)

            if not frames:
                return False

            frames[0].save(
                gif_path,
                format='GIF',
                save_all=True,
                append_images=frames[1:],
                duration=frame_duration_ms,
                loop=0,
                disposal=2,
            )
            console.print(f"[green]✓ Saved with render_pillow_frame fallback ({total_frames} frames)[/green]")
            return True
        except Exception as e:
            console.print(f"[dim]render_pillow_frame fallback failed: {e}[/dim]")
            return False

    def _resolve_total_frames(self, anim) -> int:
        frame_getters = [
            'lottie_animation_get_totalframe',
            'get_totalframe',
            'total_frame',
            'totalframe',
        ]

        for getter_name in frame_getters:
            if hasattr(anim, getter_name):
                try:
                    value = int(getattr(anim, getter_name)())
                    if value > 0:
                        return value
                except Exception:
                    continue

        return 0

    def _resolve_frame_duration_ms(self, anim) -> int:
        fps = self.fps if self.fps and self.fps > 0 else None

        if fps is None and hasattr(anim, 'lottie_animation_get_framerate'):
            try:
                anim_fps = int(anim.lottie_animation_get_framerate())
                fps = anim_fps if anim_fps > 0 else None
            except Exception:
                fps = None

        if fps is None:
            fps = 30

        return max(1, int(1000 / fps))
