import json
import logging
import math
import os
import re
from copy import deepcopy
from pathlib import Path

from flask import Blueprint, session, redirect, render_template, request, jsonify, send_from_directory

from web.input._constants import DEBRIEFS_PATH
from web.input.config.config import WebConfigSingleton, InteractiveMapConfigSingleton
from web.input.services.MapCanvas import MapCanvas

from web.input.services.coords import Coords
from web.input.services.maps import Maps
from web.input.services.mission import Mission

dmpi_db_blueprint = Blueprint('dmpi_db_blueprint', __name__)
config = WebConfigSingleton.get_instance()
map_config = InteractiveMapConfigSingleton.get_instance()

app = dmpi_db_blueprint
logger = logging.getLogger(__name__)

_OVERRIDES_FILE = Path('overrides.txt')
_TARGET_PACKAGE_FILE = Path('target_package.json')
_dmpi_cache = {}
_draw_dmpi_cache = {}

def _reset_dmpi_cache():
    global _dmpi_cache
    global _draw_dmpi_cache
    _dmpi_cache = {}
    _draw_dmpi_cache = {}

def get_draw_dmpis():
    global _draw_dmpi_cache
    if _draw_dmpi_cache != {}:
        return _draw_dmpi_cache

    draw_dmpis = deepcopy(_get_dmpis())

    units = Mission.get_msn_units()

    for unit in units:
        dmpi = _create_dmpi_entry(True)
        dmpi['comment'] = unit['type']

        dmpi['coords']['x'] = unit['x']
        dmpi['coords']['y'] = unit['y']

        lat, lon = Coords.convert_xy_to_ddm(unit['y'], unit['x'])
        dmpi['aim_points']['01']['lat'] = lat
        dmpi['aim_points']['01']['lon'] = lon

        if unit['type'] == 'CVN_73':
            dmpi['heading'] = unit.get('heading',0)*180/math.pi

        name = unit['name']
        if unit['type'] in ['KC135MPRS']:
            match = re.search(r'^.*?\d\d', unit['name'])
            if match:
                name = match.group(0)

        draw_dmpis[name] = dmpi

    for dmpi_name in draw_dmpis:
        dmpi = draw_dmpis[dmpi_name]

        if not dmpi['in_msn']:
            continue
        if not dmpi['coords']['x'] or not dmpi['coords']['y']:
            continue

        i = Maps.get_current_id()
        mpp = map_config.map_scale_mpp[i]
        x = map_config.map_origin_x[i] + (dmpi['coords']['y'] / mpp)
        y = map_config.map_origin_y[i] - (dmpi['coords']['x'] / mpp)

        render_icon = False
        render_ring = False
        radius_meters = 0
        type_ = ''
        symbol = ''
        heading = dmpi.get('heading',0)

        for comment in map_config.comments:
            if comment not in dmpi['comment']:
                continue

            comment_info = map_config.comments[comment]

            render_icon = comment_info.get('render_icon', False)
            render_ring = comment_info.get('render_ring', False)
            radius_meters = comment_info.get('radius_meters', 0)
            symbol = comment_info.get('symbol', '')
            type_ = comment_info.get('type', 'SAD')
            break

        if radius_meters == 0 and symbol == '':
            for name in map_config.names:
                if not name in dmpi_name:
                    continue

                name_info = map_config.names[name]
                render_icon = name_info.get('render_icon', False)
                render_ring = name_info.get('render_ring', False)
                radius_meters = name_info.get('radius_meters', 0)
                symbol = name_info.get('symbol', '')

                type_ = name_info.get('type')
                if not type_:
                    type_ = name.replace('-','').strip()

        dmpi['draw'] = {
            "x": x,
            "y": y,
            "symbol": symbol,
            "render_icon": render_icon,
            "render_ring": render_ring,
            "radius_px": round(radius_meters / mpp, 3),
            "type": type_,
            "heading": heading
        }

    _draw_dmpi_cache = draw_dmpis
    return draw_dmpis

def _get_dmpis():
    dmpis = {}

    global _dmpi_cache
    if _dmpi_cache != {}:
        return _dmpi_cache

    logger.info('calculating dmpis')

    # Load DMPIs from mission file
    _load_dmpis_from_mission(dmpis)

    # Load DMPIs from debrief files
    _load_dmpis_from_debriefs(dmpis)

    # Apply overrides
    _apply_overrides(dmpis)

    packages = _load_target_packages()
    for dmpi_name, package_data in packages.items():
        if dmpi_name in dmpis:
            dmpis[dmpi_name]['package_url'] = package_data['url']

    _dmpi_cache = dmpis
    return dmpis

def draw_dynamic_map_threaded():
    _reset_dmpi_cache()
    MapCanvas.draw()

def _load_dmpis_from_mission(dmpis):
    deployment_msn_path = Mission.get_path()
    if not deployment_msn_path:
        return

    nav_points = Mission.get_miz_nav_points()

    for nav_point in nav_points:
        dmpi = nav_point['callsignStr'].upper().strip()
        dmpi_name, aim_point = _parse_dmpi_name(dmpi)

        if dmpi_name not in dmpis:
            dmpis[dmpi_name] = _create_dmpi_entry(in_msn=True)
            dmpis[dmpi_name]['coords']['x'] = nav_point['x']
            dmpis[dmpi_name]['coords']['y'] = nav_point['y']
            dmpis[dmpi_name]['comment'] = nav_point['comment']

        # Calculate lat/lon for this specific aim point
        lat, lon = Coords.convert_xy_to_ddm(nav_point['y'], nav_point['x'])

        dmpis[dmpi_name]["aim_points"][aim_point] = {
            "bda": None,
            "debrief_id": None,
            "lat": lat,
            "lon": lon
        }

def _load_dmpis_from_debriefs(dmpis):
    for debrief_dir in os.listdir(DEBRIEFS_PATH):
        submit_data_path = DEBRIEFS_PATH / debrief_dir / 'submit-data.json'

        if not os.path.exists(submit_data_path):
            continue

        debrief_data = _load_debrief_data(submit_data_path)
        _process_debrief_weapons(debrief_data, dmpis, debrief_dir)

def _load_debrief_data(file_path):
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
    try:
        overrides_content = load_overrides()
        if not overrides_content:
            return

        override_ids = [line.strip().upper() for line in overrides_content.split('\n') if line.strip()]

        for override_id in override_ids:
            dmpi_name, aim_point = _parse_dmpi_name(override_id)

            if dmpi_name not in dmpis:
                dmpis[dmpi_name] = _create_dmpi_entry()

            if aim_point not in dmpis[dmpi_name]['aim_points']:
                dmpis[dmpi_name]['aim_points'][aim_point] = {
                    "bda": None,
                    "debrief_id": None,
                    "lat": "",
                    "lon": ""
                }

            existing_lat = dmpis[dmpi_name]['aim_points'][aim_point].get('lat', '')
            existing_lon = dmpis[dmpi_name]['aim_points'][aim_point].get('lon', '')

            dmpis[dmpi_name]['aim_points'][aim_point]['bda'] = "1 - Direct Hit Visual"
            dmpis[dmpi_name]['aim_points'][aim_point]['debrief_id'] = None
            dmpis[dmpi_name]['aim_points'][aim_point]['lat'] = existing_lat
            dmpis[dmpi_name]['aim_points'][aim_point]['lon'] = existing_lon
            dmpis[dmpi_name]['collision'] = True

    except Exception as e:
        logger.error(f"Error applying overrides: {e}")

def load_overrides():
    try:
        if _OVERRIDES_FILE.exists():
            with open(_OVERRIDES_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                return content if content else ""
        else:
            return ""
    except Exception as e:
        logger.error(f"Error reading overrides file: {e}")
        return ""

def save_overrides(overrides_text):
    try:
        lines = [line.strip().replace(' ', '') for line in overrides_text.split('\n')]
        cleaned_text = '\n'.join(lines)

        with open(_OVERRIDES_FILE, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)
        return True
    except Exception as e:
        logger.error(f"Error saving overrides file: {e}")
        return False

def _load_target_packages():
    """Load target packages from JSON file, return empty dict if file doesn't exist"""
    if os.path.exists(_TARGET_PACKAGE_FILE):
        try:
            with open(_TARGET_PACKAGE_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading target packages: {e}")
            return {}
    return {}

def _save_target_packages(packages):
    """Save target packages to JSON file"""
    try:
        with open(_TARGET_PACKAGE_FILE, 'w') as f:
            json.dump(packages, f, indent=2)
        return True
    except IOError as e:
        logger.error(f"Error saving target packages: {e}")
        return False

@app.route('/target-package', methods=['POST'])
def target_package():
    if not (session.get('authed', False) or config.bypass_auth_debug):
        return redirect('/login')

    if not (session.get('discord_uid') in config.admin_uids) and (session.get('discord_uid') not in config.package_managers):
        return "400 Unauthorized"

    try:
        data = request.json

        if not data or 'dmpi_id' not in data or 'url' not in data:
            return "Missing dmpi_id or url in request", 400

        dmpi_id = data['dmpi_id']
        url = data['url']

        # Validate inputs
        if not dmpi_id.strip():
            return "DMPI ID cannot be empty", 400

        # Load existing target packages
        packages = _load_target_packages()

        # Update or add the new entry
        if url is None or not url.strip():
            del packages[dmpi_id]
        else:
            packages[dmpi_id] = {"url": url}

        res = _save_target_packages(packages)
        if res:
            draw_dynamic_map_threaded()
            return "Target package URL saved successfully", 200
        else:
            return "Failed to save target package", 500

    except Exception as e:
        logger.error(f"Error in target_package route: {e}")
        return "Internal server error", 500


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
            draw_dynamic_map_threaded()

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
        logger.error(f"Error processing DMPI override: {e}")
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
                           admin=session.get('discord_uid') in config.admin_uids,
                           package=session.get('discord_uid') in config.package_managers
                           )

@app.route('/planmsn')
def download_msn():
    if session.get('authed', False) or config.bypass_auth_debug:
        msn_path = Mission.get_path()
        return send_from_directory(msn_path.parent, msn_path.name, as_attachment=True)

    return redirect('/login')
