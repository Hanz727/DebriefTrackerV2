import json
import os
import re
import threading
import zipfile
from datetime import datetime
from pathlib import Path

import numpy as np
import pyproj
from PIL import Image, ImageDraw, ImageFont
from PIL.Image import Resampling
from flask import Blueprint, session, redirect, render_template, request, jsonify
from pyproj import Transformer

from core.constants import BASE_DIR
from services.file_handler import FileHandler
from web.input._constants import DEBRIEFS_PATH
from web.input.config.config import WebConfigSingleton

from slpp import slpp as lua

dmpi_db_blueprint = Blueprint('dmpi_db_blueprint', __name__)
config = WebConfigSingleton.get_instance()
app = dmpi_db_blueprint

# Define the overrides file path
_OVERRIDES_FILE = Path('overrides.txt')
_dmpi_cache = {}

def get_deployment_msn_path() -> Path | None:
    deployment_miz_path = None
    for msn in FileHandler.sort_files_by_date_modified(config.missions_path):
        msn_sanitized = str(msn.name).strip().lower()
        if not msn_sanitized.endswith('.miz'):
            continue

        if not msn_sanitized.startswith(config.deployment_msn_prefix.strip().lower()):
            continue

        deployment_miz_path = msn
        break

    return deployment_miz_path

def _get_miz_nav_points(path: Path) -> list[dict]:
    try:
        with zipfile.ZipFile(path, 'r') as miz_archive:
            # Read the mission file
            mission_content = miz_archive.read('mission').decode('utf-8')

            # Extract the table part after "mission = "
            # Find the start of the table
            match = re.search(r'mission\s*=\s*(\{.*\})', mission_content, re.DOTALL)
            if not match:
                raise ValueError("Could not find mission table in file")

            table_content = match.group(1)

            # Parse the Lua table
            mission_table = lua.decode(table_content)

            dmpi_pattern = re.compile(r'^[^-]+-[^-]+-\d{5}-\d{2}$')
            filtered_nav_points = [x for x in mission_table['coalition']['red']['nav_points'].values()
                     if dmpi_pattern.match(x['callsignStr'])]

            return filtered_nav_points

    except Exception as e:
        print(f"Error parsing mission file: {e}")
        return []

def _reset_dmpi_cache():
    global _dmpi_cache
    _dmpi_cache = {}

def _get_dmpis():
    dmpis = {}

    global _dmpi_cache
    if _dmpi_cache != {}:
        return _dmpi_cache

    print('calculating dmpis')

    # Load DMPIs from mission file
    _load_dmpis_from_mission(dmpis)

    # Load DMPIs from debrief files
    _load_dmpis_from_debriefs(dmpis)

    # Apply overrides
    _apply_overrides(dmpis)

    _dmpi_cache = dmpis
    return dmpis


resampling = Resampling.BICUBIC
def _draw_sam_symbol_from_file(draw, x, y, scale_factor, image_path, symbol_size=12, active=True):
    try:
        # Load the symbol image
        symbol_img = Image.open(image_path)

        # Resize to desired size
        target_size = int(symbol_size * scale_factor * 2)  # *2 for good visibility
        symbol_img = symbol_img.resize((target_size, target_size), resampling)

        # Make very dark gray if not active
        if not active:
            # Preserve original alpha channel
            if symbol_img.mode != 'RGBA':
                symbol_img = symbol_img.convert('RGBA')
            original_alpha = symbol_img.split()[-1]

            # Convert to grayscale first to remove any color tints (like red)
            grayscale = symbol_img.convert('L')

            # Strengthen the black by darkening the grayscale values
            darkened = grayscale.point(lambda p: int(p * 1.2))  # Make very dark (20% of original)

            # Convert back to RGBA and restore alpha channel
            symbol_img = Image.merge('RGBA', (darkened, darkened, darkened, original_alpha))

        # Calculate position to center the symbol
        paste_x = int(x - target_size/2)
        paste_y = int(y - target_size/2)

        # Get the main image from the draw object (this is a bit hacky but works)
        main_img = draw._image

        # If symbol has transparency, use it
        if symbol_img.mode in ('RGBA', 'LA') or 'transparency' in symbol_img.info:
            main_img.paste(symbol_img, (paste_x, paste_y), symbol_img)
        else:
            main_img.paste(symbol_img, (paste_x, paste_y))

    except Exception as e:
        print(f"Could not load symbol from {image_path}: {e}")

def _get_map_id():
    current_map = config.current_map
    id_ = 0
    for i, map in enumerate(config.maps):
        if current_map in map:
            id_ = i
            break
    return id_

def draw_dynamic_map():
    _reset_dmpi_cache()
    dmpis = _get_dmpis()
    map_id = _get_map_id()
    print('drawing map')
    #threading.Thread(target=_draw_dynamic_map_from_dmpis, args=(dmpis, 0, 'SAD', 'interactive_map.png'), daemon=True).start()
    threading.Thread(target=_draw_dynamic_map_from_dmpis, args=(dmpis, map_id, 'SAD', 'interactive_map-air-defence.png'), daemon=True).start()
    threading.Thread(target=_draw_dynamic_map_from_dmpis, args=(dmpis, map_id+1, 'SAD', 'interactive_map-super-mez.png'), daemon=True).start()

    threading.Thread(target=_draw_dynamic_map_from_dmpis, args=(dmpis, map_id, 'SST', 'interactive_map-sact-all.png'), daemon=True).start()
    threading.Thread(target=_draw_dynamic_map_from_dmpis, args=(dmpis, map_id, 'SACT-C', 'interactive_map-sact-C.png'), daemon=True).start()
    threading.Thread(target=_draw_dynamic_map_from_dmpis, args=(dmpis, map_id, 'SACT-L', 'interactive_map-sact-L.png'), daemon=True).start()
    threading.Thread(target=_draw_dynamic_map_from_dmpis, args=(dmpis, map_id, 'SACT-CCC', 'interactive_map-sact-CCC.png'), daemon=True).start()
    threading.Thread(target=_draw_dynamic_map_from_dmpis, args=(dmpis, map_id, 'SACT-E', 'interactive_map-sact-E.png'), daemon=True).start()
    threading.Thread(target=_draw_dynamic_map_from_dmpis, args=(dmpis, map_id, 'SACT-O', 'interactive_map-sact-O.png'), daemon=True).start()
    threading.Thread(target=_draw_dynamic_map_from_dmpis, args=(dmpis, map_id, 'SACT-RR', 'interactive_map-sact-RR.png'), daemon=True).start()
    threading.Thread(target=_draw_dynamic_map_from_dmpis, args=(dmpis, map_id, 'SACT-A', 'interactive_map-sact-A.png'), daemon=True).start()
    threading.Thread(target=_draw_dynamic_map_from_dmpis, args=(dmpis, map_id, 'SACT-N', 'interactive_map-sact-N.png'), daemon=True).start()
    threading.Thread(target=_draw_dynamic_map_from_dmpis, args=(dmpis, map_id, 'SACT-MS', 'interactive_map-sact-MS.png'), daemon=True).start()
    threading.Thread(target=_draw_dynamic_map_from_dmpis, args=(dmpis, map_id, 'SACT-SC', 'interactive_map-sact-SC.png'), daemon=True).start()
    threading.Thread(target=_draw_dynamic_map_from_dmpis, args=(dmpis, map_id, 'SACT-RG', 'interactive_map-sact-RG.png'), daemon=True).start()

def _draw_dynamic_map_from_dmpis(dmpis, map_id, display_type,  output_name, bw_intensity=0.9, contrast=1.1, darken_shadows=1.5, symbol_size=12):
    try:
        deployment_msn_name = get_deployment_msn_path().name
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M')

        if os.path.exists(BASE_DIR / 'web' / 'static'):
            ref_dir = BASE_DIR / 'web' / 'static'
        else:
            ref_dir = BASE_DIR / 'web' / 'input' / 'static'

        os.makedirs(ref_dir / 'maps', exist_ok=True)
        img = Image.open(ref_dir / 'maps' / config.maps[map_id])

        if bw_intensity > 0:
            img_gray = img.convert('L').convert('RGB')
            img_array = np.array(img, dtype=np.float32)
            gray_array = np.array(img_gray, dtype=np.float32)
            blended_array = img_array * (1 - bw_intensity) + gray_array * bw_intensity
            img = Image.fromarray(blended_array.astype(np.uint8))

        if contrast != 1.0:
            img_array = np.array(img, dtype=np.float32)
            contrasted_array = (img_array - 128) * contrast + 128
            contrasted_array = np.clip(contrasted_array, 0, 255)
            img = Image.fromarray(contrasted_array.astype(np.uint8))

        if darken_shadows > 0:
            img_array = np.array(img, dtype=np.float32)
            normalized = img_array / 255.0
            shadow_factor = 1.0 - normalized
            shadow_factor = np.power(shadow_factor, 0.8)
            darken_amount = darken_shadows * 80
            darkened_array = img_array - darken_amount * shadow_factor
            darkened_array = np.clip(darkened_array, 0, 255)
            img = Image.fromarray(darkened_array.astype(np.uint8))

    except Exception as e:
        print(f"Error loading image: {e}")
        return

    # Create a copy for drawing at higher resolution for antialiasing
    scale_factor = 8
    img_width, img_height = img.size

    img_width_hires = img_width * scale_factor
    img_height_hires = img_height * scale_factor

    # Create high-res version
    img_hires = img.resize((img_width * scale_factor, img_height * scale_factor), resampling)
    draw = ImageDraw.Draw(img_hires)

    for dmpi_name in dmpis:
        if display_type == "SAD":
            if not("SAD" in dmpi_name or ("CCC" in dmpi_name and "EWR" in dmpis[dmpi_name]['comment'])):
                continue

        if display_type == "SST":
            if "SAD" in dmpi_name or ("CCC" in dmpi_name and "EWR" in dmpis[dmpi_name]['comment']):
                continue

        if display_type.startswith("SACT"):
            target_cat = "-" + display_type.split("-")[1].strip() + "-"
            if not target_cat in dmpi_name:
                continue

        dmpi = dmpis[dmpi_name]

        x = dmpi['coords']['y']
        y = -dmpi['coords']['x']

        if x == 0 or y == 0:
            continue

        mpp = config.map_scale_mpp[map_id]

        pixel_x = (config.map_origin_x[map_id] + x / mpp) * scale_factor
        pixel_y = (config.map_origin_y[map_id] + y / mpp) * scale_factor

        # Add some margin for the symbol size
        symbol_margin = symbol_size * scale_factor * 2  # 2x symbol size as margin
        if (pixel_x < -symbol_margin or pixel_x > img_width_hires + symbol_margin or
                pixel_y < -symbol_margin or pixel_y > img_height_hires + symbol_margin):
            continue

        radius_meters = 0
        ring_color = 'red'

        symbol_path = ''
        render_icon = False
        render_ring = False
        symbol_size_multiplier = 1.8

        if "SA-6" in dmpi['comment']:
            radius_meters = 35_560
            symbol_path = ref_dir / 'img' / 'nato-sam.png'
            render_ring = True
            render_icon = True
        if "SA-3" in dmpi['comment']:
            radius_meters = 25_000
            symbol_path = ref_dir / 'img' / 'nato-sam.png'
            render_ring = True
            render_icon = True
        if "SA-2" in dmpi['comment']:
            radius_meters = 51_860
            symbol_path = ref_dir / 'img' / 'nato-sam.png'
            render_ring = True
            render_icon = True
        if "SA-9" in dmpi['comment']:
            radius_meters = 4_640
            symbol_path = ref_dir / 'img' / 'nato-sam.png'
            render_ring = True
            render_icon = True
        if "HAAA" in dmpi['comment']:
            radius_meters = 3_000
            symbol_path = ref_dir / 'img' / 'nato-haaa.png'
            render_ring = True
            render_icon = True
        if "EWR" in dmpi['comment']:
            radius_meters = 463_000
            symbol_path = ref_dir / 'img' / 'nato-ewr.png'
            ring_color = 'yellow'
            render_ring = False
            render_icon = True
        if "HAWK" in dmpi['comment']:
            radius_meters = 47_410
            symbol_path = ref_dir / 'img' / 'nato-sam.png'
            render_ring = False
            render_icon = True

        if "-A-" in dmpi_name:
            symbol_path = ref_dir / 'img' / 'nato-airfield.png'
            render_ring = False
            render_icon = True
        if "-RG-" in dmpi_name:
            symbol_path = ref_dir / 'img' / 'nato-rg.png'
            render_ring = False
            render_icon = True
        if "-SC-" in dmpi_name:
            symbol_path = ref_dir / 'img' / 'nato-sc.png'
            render_ring = False
            render_icon = True
        if "-MS-" in dmpi_name:
            symbol_path = ref_dir / 'img' / 'nato-ms.png'
            render_ring = False
            render_icon = True
        if "-N-" in dmpi_name:
            symbol_path = ref_dir / 'img' / 'nato-n.png'
            render_ring = False
            render_icon = True
        if "-RR-" in dmpi_name:
            symbol_path = ref_dir / 'img' / 'nato-rr.png'
            render_ring = False
            render_icon = True
        if "-O-" in dmpi_name:
            symbol_path = ref_dir / 'img' / 'nato-o.png'
            render_ring = False
            render_icon = True
        if "-E-" in dmpi_name:
            symbol_path = ref_dir / 'img' / 'nato-e.png'
            render_ring = False
            render_icon = True
        if "-CCC-" in dmpi_name and radius_meters == 0:
            symbol_path = ref_dir / 'img' / 'nato-ccc.png'
            render_ring = False
            render_icon = True
        if "-L-" in dmpi_name:
            symbol_path = ref_dir / 'img' / 'nato-l.png'
            render_ring = False
            render_icon = True
        if "-C-" in dmpi_name:
            symbol_path = ref_dir / 'img' / 'nato-c.png'
            render_ring = False
            render_icon = True

        if ring_color == 'red':
            x = radius_meters
            redness = min(255, 1.647e-8*(x**2) - 0.00424*x + 305.808)
            redness = max(redness, 50)
            ring_color = (int(redness),0,0)

        radius_pixels = (radius_meters / mpp) * scale_factor

        circle_left = pixel_x - radius_pixels
        circle_top = pixel_y - radius_pixels
        circle_right = pixel_x + radius_pixels
        circle_bottom = pixel_y + radius_pixels

        if not dmpi['collision'] and render_ring:
            draw.ellipse([circle_left, circle_top, circle_right, circle_bottom],
                         fill=None, outline=ring_color, width=int(1.5 * scale_factor))

        if render_icon:
            _draw_sam_symbol_from_file(draw, pixel_x, pixel_y, scale_factor, symbol_path, symbol_size*symbol_size_multiplier, not dmpi['collision'])

    # Add watermark with deployment name and current date
    _draw_watermark(draw, img_width_hires, img_height_hires, deployment_msn_name, current_date, scale_factor)

    # Downsample back to original size for antialiasing effect
    img_with_symbols = img_hires.resize((img_width, img_height), resampling)

    img_with_symbols.save(ref_dir / 'maps' / output_name)

def _draw_watermark(draw, img_width, img_height, deployment_name, date_str, scale_factor):
    """Draw a transparent watermark in the bottom right corner with deployment name and date."""
    try:
        # Try to use a system font, fallback to default if not available
        try:
            font_size = int(30 * scale_factor)
            font = ImageFont.truetype("arial.ttf", font_size)
        except (ImportError, OSError):
            try:
                font = ImageFont.load_default()
            except:
                font = None

        # Prepare watermark text with title
        watermark_text = f"CVW-17 TARGET INTELLIGENCE CELL - AIR DEFENCE MAP\n{deployment_name}\n{date_str}"
        lines = watermark_text.split('\n')

        # Calculate text dimensions
        if font:
            line_widths = []
            line_heights = []
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                line_widths.append(bbox[2] - bbox[0])
                line_heights.append(bbox[3] - bbox[1])

            text_width = max(line_widths)
            line_spacing = int(4 * scale_factor)
            text_height = sum(line_heights) + (len(lines) - 1) * line_spacing
        else:
            # Rough estimation if no font available
            text_width = len(max(lines, key=len)) * int(10 * scale_factor)
            text_height = len(lines) * int(14 * scale_factor)

        # Position in bottom right corner with padding
        padding = int(20 * scale_factor)
        bg_padding = int(8 * scale_factor)
        x_pos = img_width - text_width - padding
        y_pos = img_height - text_height - padding

        # Get the base image from the draw object
        base_img = draw._image

        # Create a separate RGBA image for the watermark with transparency
        watermark_overlay = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        watermark_draw = ImageDraw.Draw(watermark_overlay)

        # Draw semi-transparent background rectangle
        bg_left = x_pos - bg_padding
        bg_top = y_pos - bg_padding
        bg_right = x_pos + text_width + bg_padding
        bg_bottom = y_pos + text_height + bg_padding

        # Semi-transparent dark background (RGBA: black with 60% opacity)
        bg_color = (0, 0, 0, 153)  # 153 = 60% of 255
        watermark_draw.rectangle([bg_left, bg_top, bg_right, bg_bottom], fill=bg_color)

        # Draw text with white color (fully opaque on the overlay)
        text_color = (255, 255, 255, 255)  # White, fully opaque

        if font:
            current_y = y_pos
            line_spacing = int(4 * scale_factor)
            for line in lines:
                watermark_draw.text((x_pos, current_y), line, fill=text_color, font=font)
                bbox = watermark_draw.textbbox((x_pos, current_y), line, font=font)
                current_y += (bbox[3] - bbox[1]) + line_spacing
        else:
            # Fallback without font
            current_y = y_pos
            for line in lines:
                watermark_draw.text((x_pos, current_y), line, fill=text_color)
                current_y += int(14 * scale_factor)

        # Convert base image to RGBA if it isn't already
        if base_img.mode != 'RGBA':
            base_img = base_img.convert('RGBA')

        # Composite the watermark overlay onto the base image
        base_img = Image.alpha_composite(base_img, watermark_overlay)

        # Convert back to RGB if needed (since you're saving as PNG, RGBA should be fine)
        # If you need RGB: base_img = base_img.convert('RGB')

        # Replace the original image data
        draw._image.paste(base_img, (0, 0))

    except Exception as e:
        print(f"Error drawing watermark: {e}")
        # Continue without watermark if there's an error

def load_overrides():
    """Load overrides from the overrides.txt file."""
    try:
        if _OVERRIDES_FILE.exists():
            with open(_OVERRIDES_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                return content if content else ""
        else:
            # Return default overrides if file doesn't exist
            return ""
    except Exception as e:
        print(f"Error reading overrides file: {e}")
        return ""

def save_overrides(overrides_text):
    """Save overrides to the overrides.txt file."""
    try:
        lines = [line.strip().replace(' ', '') for line in overrides_text.split('\n')]
        cleaned_text = '\n'.join(lines)

        with open(_OVERRIDES_FILE, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)
        return True
    except Exception as e:
        print(f"Error saving overrides file: {e}")
        return False


def _parse_dms(dms_string):
    """Parse DMS string to decimal degrees"""
    dms = dms_string.strip().upper()

    # Extract direction
    direction = None
    for char in ['N', 'S', 'E', 'W']:
        if char in dms:
            direction = char
            dms = dms.replace(char, '').strip()
            break

    if not direction:
        raise ValueError(f"Could not find direction in: {dms_string}")

    # Extract degrees, minutes, seconds
    pattern = r"(\d+)[°](\d+)[']([0-9.]+)[\"]*"
    match = re.search(pattern, dms)

    if not match:
        raise ValueError(f"Could not parse DMS format: {dms_string}")

    degrees = float(match.group(1))
    minutes = float(match.group(2))
    seconds = float(match.group(3))

    decimal = degrees + minutes/60.0 + seconds/3600.0

    if direction in ['S', 'W']:
        decimal = -decimal

    return decimal

def _decimal_to_ddm(decimal_degrees, coord_type='lat'):
    """Convert decimal degrees to DDM (Degrees Decimal Minutes) format"""
    if coord_type.lower() == 'lat':
        direction = 'N' if decimal_degrees >= 0 else 'S'
    else:
        direction = 'E' if decimal_degrees >= 0 else 'W'

    abs_degrees = abs(decimal_degrees)
    degrees = int(abs_degrees)
    minutes = (abs_degrees - degrees) * 60

    return f"{direction} {degrees}°{minutes:06.3f}'"

def _convert_xy_to_ddm(x, y, reference_dms):
    """
    Convert DCS x,y coordinates to DMS coordinates using UTM projection

    Args:
        x, y: DCS coordinates in meters
        reference_dms: Reference coordinates in DMS (e.g., "N 30°02'49\" E 31°14'41\"")

    Returns:
        tuple: (lat_dms, lon_dms) in DMS format
    """
    # Clean up encoding issues with degree symbol
    reference_dms = reference_dms.replace('Â°', '°')

    # Use regex to find lat and lon patterns
    # Pattern matches: direction + degrees°minutes'seconds"
    pattern = r'([NSEW])\s*(\d+)[°](\d+)\'([0-9.]+)"?'
    matches = re.findall(pattern, reference_dms)

    if len(matches) != 2:
        raise ValueError(f"Could not find 2 coordinates in: {reference_dms}")

    # Separate lat and lon
    lat_match = None
    lon_match = None

    for match in matches:
        direction, degrees, minutes, seconds = match
        if direction in ['N', 'S']:
            lat_match = match
        else:  # E, W
            lon_match = match

    if not lat_match or not lon_match:
        raise ValueError(f"Could not find both lat and lon in: {reference_dms}")

    # Convert to decimal
    def dms_match_to_decimal(match):
        direction, degrees, minutes, seconds = match
        decimal = float(degrees) + float(minutes)/60.0 + float(seconds)/3600.0
        if direction in ['S', 'W']:
            decimal = -decimal
        return decimal

    ref_lat = dms_match_to_decimal(lat_match)
    ref_lon = dms_match_to_decimal(lon_match)

    # Determine UTM zone
    utm_zone = int((ref_lon + 180) / 6) + 1
    utm_crs = pyproj.CRS.from_proj4(
        f"+proj=utm +zone={utm_zone} "
        f"+{'south' if ref_lat < 0 else 'north'} +datum=WGS84"
    )

    # Create transformers
    to_utm = Transformer.from_crs('EPSG:4326', utm_crs, always_xy=True)
    from_utm = Transformer.from_crs(utm_crs, 'EPSG:4326', always_xy=True)

    # Convert reference to UTM
    ref_x, ref_y = to_utm.transform(ref_lon, ref_lat)

    # Add DCS offset and convert back
    actual_x = ref_x + x
    actual_y = ref_y + y
    lon, lat = from_utm.transform(actual_x, actual_y)

    # Convert to DMS
    lat_dms = _decimal_to_ddm(lat, 'lat')
    lon_dms = _decimal_to_ddm(lon, 'lon')

    return lat_dms, lon_dms

def _load_dmpis_from_mission(dmpis):
    deployment_msn_path = get_deployment_msn_path()
    if not deployment_msn_path:
        return

    for nav_point in _get_miz_nav_points(deployment_msn_path):
        dmpi = nav_point['callsignStr'].upper().strip()
        dmpi_name, aim_point = _parse_dmpi_name(dmpi)

        if dmpi_name not in dmpis:
            dmpis[dmpi_name] = _create_dmpi_entry(in_msn=True)
            dmpis[dmpi_name]['coords']['x'] = nav_point['x']
            dmpis[dmpi_name]['coords']['y'] = nav_point['y']
            dmpis[dmpi_name]['comment'] = nav_point['comment']

        # Calculate lat/lon for this specific aim point
        lat, lon = _convert_xy_to_ddm(nav_point['y'], nav_point['x'], config.map_reference[_get_map_id()])

        dmpis[dmpi_name]["aim_points"][aim_point] = {
            "bda": None,
            "debrief_id": None,
            "lat": lat,
            "lon": lon
        }


def _load_dmpis_from_debriefs(dmpis):
    """Load DMPIs from debrief files."""
    for debrief_dir in os.listdir(DEBRIEFS_PATH):
        submit_data_path = DEBRIEFS_PATH / debrief_dir / 'submit-data.json'

        if not os.path.exists(submit_data_path):
            continue

        debrief_data = _load_debrief_data(submit_data_path)
        _process_debrief_weapons(debrief_data, dmpis, debrief_dir)

def _load_debrief_data(file_path):
    """Load and return debrief data from JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def _process_debrief_weapons(debrief_data, dmpis, debrief_id):
    """Process weapons data from a debrief file."""
    for weapon in debrief_data.get('ag_weapons', []):
        if weapon.get('target_type') != 'dmpi':
            continue

        target = weapon.get('target_value', '').strip().upper()
        if not target:
            continue

        dmpi_name, aim_point = _parse_dmpi_name(target)
        bda_result = weapon.get('bda_result', '').strip()

        date = debrief_data.get('mission_date')
        _update_dmpi_entry(dmpis, dmpi_name, aim_point, bda_result, debrief_id, date)

def _parse_dmpi_name(dmpi_full_name):
    """Parse DMPI name into base name and aim point."""
    parts = dmpi_full_name.rsplit('-', 1)
    dmpi_name = parts[0]
    aim_point = parts[1] if len(parts) > 1 else "01"
    return dmpi_name, aim_point

def _create_dmpi_entry(in_msn=False):
    """Create a new DMPI entry with default values."""
    return {
        "in_msn": in_msn,
        "collision": False,
        "comment": "",
        "coords": {"x": 0, "y": 0},  # Removed lat_dms and lon_dms from here
        "aim_points": {"01": {"bda": None, "debrief_id": None, "date": None, "lat": "", "lon": ""}}
    }

def _update_dmpi_entry(dmpis, dmpi_name, aim_point, bda_result, debrief_id, date):
    """Update or create a DMPI entry with new data."""
    if dmpi_name in dmpis:
        # Update existing DMPI
        if _should_update_bda(dmpis[dmpi_name], aim_point, bda_result):
            # Preserve existing lat/lon if they exist, otherwise set empty
            existing_lat = ""
            existing_lon = ""
            if aim_point in dmpis[dmpi_name]['aim_points']:
                existing_lat = dmpis[dmpi_name]['aim_points'][aim_point].get('lat', '')
                existing_lon = dmpis[dmpi_name]['aim_points'][aim_point].get('lon', '')

            dmpis[dmpi_name]['aim_points'][aim_point] = {
                "bda": bda_result,
                "debrief_id": debrief_id,
                "date": date,
                "lat": existing_lat,
                "lon": existing_lon
            }

        dmpis[dmpi_name]['collision'] = True
    else:
        # Create new DMPI
        dmpis[dmpi_name] = _create_dmpi_entry()
        dmpis[dmpi_name]['aim_points'][aim_point] = {
            "bda": bda_result,
            "debrief_id": debrief_id,
            "date": date,
            "lat": "",
            "lon": ""
        }

def _should_update_bda(dmpi_entry, aim_point, new_bda_result):
    """Determine if BDA result should be updated based on first digit comparison."""
    if not new_bda_result:
        return False

    current_aim_point = dmpi_entry['aim_points'].get(aim_point)
    if not current_aim_point:
        return True

    current_bda = current_aim_point.get('bda')
    if not current_bda:
        return True

    # Keep existing value if it has lower first digit
    return new_bda_result[0] < current_bda[0]

def _apply_overrides(dmpis):
    """Apply overrides to DMPIs, setting BDA to '1 - Direct Hit Visual'."""
    try:
        overrides_content = load_overrides()
        if not overrides_content:
            return

        # Parse override DMPI IDs
        override_ids = [line.strip().upper() for line in overrides_content.split('\n') if line.strip()]

        for override_id in override_ids:
            dmpi_name, aim_point = _parse_dmpi_name(override_id)

            # Create DMPI entry if it doesn't exist
            if dmpi_name not in dmpis:
                dmpis[dmpi_name] = _create_dmpi_entry()

            # Ensure the aim_points dictionary has the specific aim point
            if aim_point not in dmpis[dmpi_name]['aim_points']:
                dmpis[dmpi_name]['aim_points'][aim_point] = {
                    "bda": None,
                    "debrief_id": None,
                    "lat": "",
                    "lon": ""
                }

            # Set the BDA to "1 - Direct Hit Visual" for this aim point
            # Preserve existing lat/lon coordinates
            existing_lat = dmpis[dmpi_name]['aim_points'][aim_point].get('lat', '')
            existing_lon = dmpis[dmpi_name]['aim_points'][aim_point].get('lon', '')

            dmpis[dmpi_name]['aim_points'][aim_point]['bda'] = "1 - Direct Hit Visual"
            dmpis[dmpi_name]['aim_points'][aim_point]['debrief_id'] = None
            dmpis[dmpi_name]['aim_points'][aim_point]['lat'] = existing_lat
            dmpis[dmpi_name]['aim_points'][aim_point]['lon'] = existing_lon
            dmpis[dmpi_name]['collision'] = True

    except Exception as e:
        print(f"Error applying overrides: {e}")


@app.route('/dmpi_override', methods=['POST'])
def dmpi_override():
    if not (session.get('authed', False) or config.bypass_auth_debug):
        return redirect('/login')

    if not session.get('discord_uid') in config.admin_uids:
        return "400 Unauthorized"

    try:
        # Get JSON data from the request
        data = request.get_json()

        # Extract the overrides text
        overrides_text = data.get('overrides', '')

        # Save overrides to file
        if save_overrides(overrides_text):
            # Split by newlines to get individual DMPI IDs for counting
            dmpi_ids = [line.strip() for line in overrides_text.split('\n') if line.strip()]
            draw_dynamic_map()

            return jsonify({
                'success': True,
                'message': f'Successfully saved {len(dmpi_ids)} DMPI overrides to file'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to save overrides to file'
            }), 500

    except Exception as e:
        print(f"Error processing DMPI override: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to process override data'
        }), 500

@app.route('/dmpi_db')
def dmpi_db():
    if not (session.get('authed', False) or config.bypass_auth_debug):
        return redirect('/login')

    return render_template('dmpi_db.html',
                           overrides=load_overrides(),
                           dmpis=_get_dmpis(),
                           admin=session.get('discord_uid') in config.admin_uids
                           )