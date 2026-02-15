import os  # این خط را اضافه کنید
import gzip
import json
from rich.console import Console

console = Console()

RLOTTIE_AVAILABLE = False
LottieAnimation = None

try:
    from rlottie_python import LottieAnimation
    RLOTTIE_AVAILABLE = True
    console.print("[green]✓ rlottie-python loaded successfully[/green]")
except ImportError:
    try:
        from rlottie import LottieAnimation
        RLOTTIE_AVAILABLE = True
        console.print("[green]✓ rlottie loaded successfully[/green]")
    except ImportError:
        RLOTTIE_AVAILABLE = False
        console.print("[yellow]⚠️ rlottie-python not installed. TGS to GIF conversion will be disabled.[/yellow]")
        LottieAnimation = None


def _get_available_methods():
    if not RLOTTIE_AVAILABLE or LottieAnimation is None:
        return []
    
    methods = []
    
    all_methods = dir(LottieAnimation)
    
    constructor_methods = [
        'from_tgs', 'from_data', 'from_string', 'from_json', 
        'from_file', 'from_dict', 'lottie_animation_from_data',
        'lottie_animation_from_file', 'load', 'load_from_data',
        'from_buffer', 'from_bytes'
    ]
    
    for method_name in constructor_methods:
        if method_name in all_methods:
            methods.append(method_name)
    
    return methods


def load_lottie_auto(path: str):
    if not RLOTTIE_AVAILABLE or LottieAnimation is None:
        raise ImportError("rlottie-python is not installed")
    
    with open(path, "rb") as f:
        data = f.read()
    
    is_gzipped = data[:2] == b"\x1f\x8b"
    
    available_methods = _get_available_methods()
    
    if is_gzipped and 'from_tgs' in available_methods:
        try:
            console.print(f"[dim]Trying from_tgs for {os.path.basename(path)}[/dim]")
            return LottieAnimation.from_tgs(path)
        except Exception as e:
            console.print(f"[dim]from_tgs failed: {e}[/dim]")
    
    if 'from_file' in available_methods:
        try:
            console.print(f"[dim]Trying from_file for {os.path.basename(path)}[/dim]")
            return LottieAnimation.from_file(path)
        except Exception as e:
            console.print(f"[dim]from_file failed: {e}[/dim]")
    
    if 'lottie_animation_from_file' in available_methods:
        try:
            console.print(f"[dim]Trying lottie_animation_from_file for {os.path.basename(path)}[/dim]")
            return LottieAnimation.lottie_animation_from_file(path)
        except Exception as e:
            console.print(f"[dim]lottie_animation_from_file failed: {e}[/dim]")
    
    if is_gzipped:
        try:
            data = gzip.decompress(data)
            console.print(f"[dim]Decompressed gzip file[/dim]")
        except Exception as e:
            console.print(f"[dim]Decompression failed: {e}[/dim]")
    
    try:
        json_str = data.decode('utf-8')
        
        for method_name in ['from_data', 'from_string', 'from_json', 'lottie_animation_from_data', 'load_from_data', 'from_bytes']:
            if method_name in available_methods:
                try:
                    console.print(f"[dim]Trying {method_name} for {os.path.basename(path)}[/dim]")
                    method = getattr(LottieAnimation, method_name)
                    
                    if method_name == 'lottie_animation_from_data':
                        return method(json_str)
                    elif method_name == 'from_bytes':
                        return method(json_str.encode('utf-8'))
                    else:
                        return method(json_str)
                except Exception as e:
                    console.print(f"[dim]{method_name} failed: {e}[/dim]")
                    continue
        
        try:
            json_obj = json.loads(json_str)
            if 'from_dict' in available_methods:
                try:
                    console.print(f"[dim]Trying from_dict for {os.path.basename(path)}[/dim]")
                    return LottieAnimation.from_dict(json_obj)
                except Exception as e:
                    console.print(f"[dim]from_dict failed: {e}[/dim]")
        except:
            pass
            
    except UnicodeDecodeError:
        pass
    
    try:
        idx = data.find(b"{")
        if idx != -1:
            json_str = data[idx:].decode("utf-8", errors="ignore")
            end_idx = json_str.rfind("}")
            if end_idx != -1:
                json_str = json_str[:end_idx + 1]
                console.print(f"[dim]Trying brute-force method for {os.path.basename(path)}[/dim]")
                
                for method_name in ['from_data', 'from_string', 'from_json', 'lottie_animation_from_data']:
                    if method_name in available_methods:
                        try:
                            method = getattr(LottieAnimation, method_name)
                            if method_name == 'lottie_animation_from_data':
                                return method(json_str)
                            else:
                                return method(json_str)
                        except:
                            continue
    except Exception as e:
        console.print(f"[dim]Brute-force method failed: {e}[/dim]")
    
    raise Exception(f"Could not load animation with any method: {path}")


def is_rlottie_available():
    return RLOTTIE_AVAILABLE


def get_available_methods():
    return _get_available_methods()