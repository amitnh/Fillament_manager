import zipfile
import re
import io
from typing import List

def parse_material_usage(file_content: bytes, filename: str) -> List[float]:
    """
    Parses .gcode or .3mf files to extract filament usage.
    Returns a list of weights (in grams) for each filament slot/index.
    """
    filename = filename.lower()
    if filename.endswith(".gcode"):
        return parse_gcode(file_content)
    elif filename.endswith(".3mf"):
        return parse_3mf(file_content)
    return []

def parse_gcode(content: bytes) -> List[float]:
    text = content.decode("utf-8", errors="ignore")
    
    # Pattern 1: Standard Bambu/Prusa comment
    # ; filament used [g] = 23.4, 10.1, 0
    match = re.search(r";\s*filament used\s*\[g\]\s*=\s*(.*)", text)
    if match:
        try:
            weights_str = match.group(1).strip()
            weights = [float(w.strip()) for w in weights_str.split(",") if w.strip()]
            # If at least one weight is > 0, return it
            if any(w > 0 for w in weights):
                return weights
        except ValueError:
            pass

    # Pattern 2: Some newer Bambu Studio versions use separate lines or differ slightly
    # ; total filament used [g] = 23.4
    match_total = re.search(r";\s*total filament used\s*\[g\]\s*=\s*([\d\.]+)", text)
    if match_total:
        try:
            return [float(match_total.group(1))]
        except ValueError:
            pass

    # Pattern 3: Bambu Studio "total filament weight [g] :"
    # ; total filament weight [g] : 2.58,0.97
    match_weight = re.search(r";\s*total filament weight\s*\[g\]\s*[:=]\s*(.*)", text)
    if match_weight:
        try:
            weights_str = match_weight.group(1).strip()
            weights = [float(w.strip()) for w in weights_str.split(",") if w.strip()]
            if any(w > 0 for w in weights):
                return weights
        except ValueError:
            pass
            
    # Pattern 4: Look for "filament_used_g" config value often found in 3mf slice_info
    # filament_used_g = 12.4
    match_config = re.findall(r"filament_used_g\s*=\s*([\d\.]+)", text)
    if match_config:
        try:
            # This might match multiple times for multiple plates/objects, 
            # but usually in slice_info it appears as a list or sequence
            # Let's try to find the list version first
            pass 
        except:
            pass

    return []

def parse_3mf(content: bytes) -> List[float]:
    """
    Attempts to find slice info in 3MF metadata.
    Bambu Studio 3MFs usually contain a 'Metadata/slice_info.config' 
    or sometimes 'Metadata/project_settings.config'
    """
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as z:
            # 1. Try slice_info.config (most common for sliced files)
            for name in z.namelist():
                if name.endswith("slice_info.config"):
                    with z.open(name) as f:
                        return parse_gcode(f.read())
            
            # 2. Try G-code files directly if they exist in the 3mf (less common for project files)
            for name in z.namelist():
                if name.endswith(".gcode"):
                    with z.open(name) as f:
                        return parse_gcode(f.read())

    except Exception:
        pass
    return []


