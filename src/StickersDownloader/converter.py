import os
from .utils import load_lottie_auto, is_rlottie_available, console, get_available_methods
import asyncio
import traceback


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