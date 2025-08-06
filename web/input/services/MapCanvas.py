import math
import os
import threading

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from PIL.Image import Resampling

from core.constants import BASE_DIR
from web.input.config.config import InteractiveMapConfigSingleton
from web.input.services.maps import Maps
from web.input.services.mission import Mission

map_config = InteractiveMapConfigSingleton.get_instance()

class MapCanvas:
    @classmethod
    def draw(cls):
        map_id = Maps.get_current_id()
        threading.Thread(target=cls.__draw_dynamic_map, args=(map_id, 'BLUE', 'interactive_map_z1.jpg'), daemon=True).start()

    @classmethod
    def __draw_dynamic_map(cls, map_id, display_type, output_name, scale_factor=4):
        if os.path.exists(BASE_DIR / 'web' / 'static'):
            ref_dir = BASE_DIR / 'web' / 'static'
        else:
            ref_dir = BASE_DIR / 'web' / 'input' / 'static'

        try:
            os.makedirs(ref_dir / 'maps', exist_ok=True)
            img = Image.open(ref_dir / 'maps' / map_config.maps[map_id])
            img = img.convert('RGB')
        except Exception as e:
            print(e)
            return

        img = cls.__apply_filters(img)
        img_width, img_height = img.size

        if display_type == 'EMPTY':
            img.save(ref_dir / 'maps' / output_name, format='JPEG')
            return

        img_hires = img.resize((img_width * scale_factor, img_height * scale_factor), Resampling.LANCZOS)
        draw = ImageDraw.Draw(img_hires)

        if display_type == 'BLUE':
            cls.__draw_tanker_tracks(draw, scale_factor, map_id)
            cls.__draw_course_line(draw, scale_factor, map_id)
            img_hires = img_hires.resize((img_width, img_height), Resampling.LANCZOS)
            img_hires.save(ref_dir / 'maps' / output_name, format='JPEG')
            return

    @staticmethod
    def __apply_filters(img, bw_intensity=0.9, contrast=1.1, darken_shadows=1.5):
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

        return img

    @staticmethod
    def __draw_tanker_tracks(draw, scale_factor, map_id):
        mpp = map_config.map_scale_mpp[map_id]

        color = (128, 224, 255)

        for tanker_name, coords in Mission.get_miz_tanker_data().items():
            name = tanker_name.split('-')[-1]
            x1 = (map_config.map_origin_x[map_id] + (coords["y1"] / mpp)) * scale_factor
            y1 = (map_config.map_origin_y[map_id] - (coords["x1"] / mpp)) * scale_factor

            x2 = (map_config.map_origin_x[map_id] + (coords["y2"] / mpp)) * scale_factor
            y2 = (map_config.map_origin_y[map_id] - (coords["x2"] / mpp)) * scale_factor

            line_length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            if line_length > 0:
                ux = (x2 - x1) / line_length
                uy = (y2 - y1) / line_length
                px = -uy
                py = ux

                rect_width = line_length / 2

                corner1 = (x1, y1)
                corner2 = (x2, y2)  # Use the actual end point
                corner3 = (x2 + rect_width * px, y2 + rect_width * py)
                corner4 = (x1 + rect_width * px, y1 + rect_width * py)

                # Draw the rotated rectangle
                rect_points = [corner1, corner2, corner3, corner4, corner1]
                draw.polygon(rect_points, outline=color, fill=None, width=3 * scale_factor)

                # Add blue text next to the rectangle with larger, more readable font
                text_x = x2 + rect_width * px + 15 * scale_factor
                text_y = y2 + rect_width * py - 15 * scale_factor

                try:
                    font = ImageFont.truetype("arial.ttf", 24 * scale_factor)
                except:
                    try:
                        font = ImageFont.load_default(size=24 * scale_factor)
                    except:
                        font = ImageFont.load_default()

                draw.text((text_x, text_y), name, fill=color, font=font)

    @staticmethod
    def __draw_course_line(draw, scale_factor, map_id):
        mpp = map_config.map_scale_mpp[map_id]  # meters per pixel (for scale_factor == 1)

        cvn73 = Mission.get_msn_unit('CVN_73')[0]
        heading = cvn73['heading']  # radians

        color_line = (128, 224, 255)
        color_dot = (0, 0, 150)

        # Current carrier position on map
        x = (map_config.map_origin_x[map_id] + (cvn73["y"] / mpp)) * scale_factor
        y = (map_config.map_origin_y[map_id] - (cvn73["x"] / mpp)) * scale_factor

        # Speed and time constants
        speed_kts = 20  # knots
        speed_mps = speed_kts * 0.514444  # convert knots to meters per second

        # Time intervals
        start_time_minutes = 30  # start 30 minutes ahead
        end_time_minutes = 135  # extend to 2 hours ahead (adjust as needed)
        interval_minutes = 15  # 15-minute intervals

        # Calculate heading components (note: heading is typically from north, clockwise)
        dx_per_meter = math.sin(heading) / mpp * scale_factor  # x component per meter
        dy_per_meter = -math.cos(
            heading) / mpp * scale_factor  # y component per meter (negative for screen coordinates)

        # Store courseline points and marker data
        courseline_points = []
        marker_data = []

        # Calculate all courseline points and marker data
        for t_minutes in range(start_time_minutes, end_time_minutes + 1, interval_minutes):
            t_seconds = t_minutes * 60
            distance_meters = speed_mps * t_seconds

            # Calculate position at this time
            pos_x = x + dx_per_meter * distance_meters
            pos_y = y + dy_per_meter * distance_meters

            courseline_points.append((pos_x, pos_y))

            # Store marker data for later drawing
            marker_data.append({
                'pos': (pos_x, pos_y),
                'time_minutes': t_minutes
            })

        # Draw the main courseline FIRST
        if len(courseline_points) > 1:
            draw.line(courseline_points, fill=color_line, width=max(1, int(2 * scale_factor)))