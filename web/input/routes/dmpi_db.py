import json
import os
import re
import threading
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from flask import Blueprint, session, redirect, render_template, request, jsonify

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


def _draw_sam_symbol_from_file(draw, x, y, scale_factor, image_path, symbol_size=12, active=True):
    try:
        # Load the symbol image
        symbol_img = Image.open(image_path)

        # Resize to desired size
        target_size = int(symbol_size * scale_factor * 2)  # *2 for good visibility
        symbol_img = symbol_img.resize((target_size, target_size), Image.LANCZOS)

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



def draw_dynamic_map():
    _reset_dmpi_cache()
    dmpis = _get_dmpis()
    print('drawing map')
    threading.Thread(target=_draw_dynamic_map_from_dmpis, args=(dmpis, ), daemon=True).start()

def _draw_dynamic_map_from_dmpis(dmpis, bw_intensity=0.9, contrast=1.1, darken_shadows=1.5,symbol_size=12):
    try:
        if os.path.exists(BASE_DIR / 'web' / 'static'):
            os.makedirs(BASE_DIR / 'web' / 'static' / 'maps', exist_ok=True)
            img = Image.open(BASE_DIR / 'web' / 'static' / 'maps' / config.current_map_path)
        else:
            os.makedirs(BASE_DIR / 'web' / 'input' / 'static' / 'maps', exist_ok=True)
            img = Image.open(BASE_DIR / 'web' / 'input' / 'static' / 'maps' / config.current_map_path)

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
    scale_factor = 4
    img_width, img_height = img.size

    # Create high-res version
    img_hires = img.resize((img_width * scale_factor, img_height * scale_factor), Image.LANCZOS)
    draw = ImageDraw.Draw(img_hires)

    for dmpi_name in dmpis:
        if "SAD" not in dmpi_name:
            continue

        dmpi = dmpis[dmpi_name]

        x = dmpi['coords']['y']
        y = -dmpi['coords']['x']

        if x == 0 or y == 0:
            continue

        radius_meters = 35_560  # SA-6 (default)
        if "SA-3" in dmpi['comment']:
            radius_meters = 25_000
        if "SA-2" in dmpi['comment']:
             radius_meters = 51_860
        if "SA-9" in dmpi['comment']:
            radius_meters = 4_640
        if "HAAA" in dmpi['comment']:
            radius_meters = 3_000
        if "HAWK" in dmpi['comment']:
            radius_meters = 47_410

        mpp = config.map_scale_mpp
        radius_pixels = (radius_meters / mpp) * scale_factor

        pixel_x = (config.map_origin_x + x / mpp) * scale_factor
        pixel_y = (config.map_origin_y + y / mpp) * scale_factor

        img_width_hires = img_width * scale_factor
        img_height_hires = img_height * scale_factor

        # Add some margin for the symbol size
        symbol_margin = symbol_size * scale_factor * 2  # 2x symbol size as margin

        if (pixel_x < -symbol_margin or pixel_x > img_width_hires + symbol_margin or
                pixel_y < -symbol_margin or pixel_y > img_height_hires + symbol_margin):
            print(f"DMPI '{dmpi}': SKIPPED - outside image bounds")
            print(f"  World coords: ({x:.1f}, {y:.1f})")
            print(f"  Pixel coords: ({pixel_x / scale_factor:.1f}, {pixel_y / scale_factor:.1f})")
            print(f"  Image size: {img_width} x {img_height}")
            continue

        # Draw radius circle (same as before)
        circle_left = pixel_x - radius_pixels
        circle_top = pixel_y - radius_pixels
        circle_right = pixel_x + radius_pixels
        circle_bottom = pixel_y + radius_pixels

        if not dmpi['collision']:
            draw.ellipse([circle_left, circle_top, circle_right, circle_bottom],
                         fill=None, outline='red', width=1 * scale_factor)

        # Use external image file - you need to specify the path
        if os.path.exists(BASE_DIR / 'web' / 'static'):
            symbol_path = BASE_DIR / 'web' / 'static' / 'img' / 'nato.png'
        else:
            symbol_path = BASE_DIR / 'web' / 'input' / 'static' / 'img' / 'nato.png'

        _draw_sam_symbol_from_file(draw, pixel_x, pixel_y, scale_factor, symbol_path, symbol_size, not dmpi['collision'])

    # Downsample back to original size for antialiasing effect
    img_with_symbols = img_hires.resize((img_width, img_height), Image.LANCZOS)

    if os.path.exists(BASE_DIR / 'web' / 'static'):
        img_with_symbols.save(BASE_DIR / 'web' / 'static' / 'maps' / "interactive_map.png")
    else:
        img_with_symbols.save(BASE_DIR / 'web' / 'input' / 'static' / 'maps' / "interactive_map.png")

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
        with open(_OVERRIDES_FILE, 'w', encoding='utf-8') as f:
            f.write(overrides_text)
        return True
    except Exception as e:
        print(f"Error saving overrides file: {e}")
        return False

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

        dmpis[dmpi_name]["aim_points"][aim_point] = {"bda": None, "debrief_id": None}

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
        "coords": {"x": 0, "y": 0},
        "aim_points": {"01": {"bda": None, "debrief_id": None, "date": None}}
    }


def _update_dmpi_entry(dmpis, dmpi_name, aim_point, bda_result, debrief_id, date):
    """Update or create a DMPI entry with new data."""
    if dmpi_name in dmpis:
        # Update existing DMPI
        if _should_update_bda(dmpis[dmpi_name], aim_point, bda_result):
            dmpis[dmpi_name]['aim_points'][aim_point] = {
                "bda": bda_result,
                "debrief_id": debrief_id,
                "date": date
            }

        dmpis[dmpi_name]['collision'] = True
    else:
        # Create new DMPI
        dmpis[dmpi_name] = _create_dmpi_entry()
        dmpis[dmpi_name]['aim_points'][aim_point] = {
            "bda": bda_result,
            "debrief_id": debrief_id,
            "date": date
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
                dmpis[dmpi_name]['aim_points'][aim_point] = {"bda": None, "debrief_id": None}

            # Set the BDA to "1 - Direct Hit Visual" for this aim point
            dmpis[dmpi_name]['aim_points'][aim_point]['bda'] = "1 - Direct Hit Visual"
            dmpis[dmpi_name]['aim_points'][aim_point]['debrief_id'] = None
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