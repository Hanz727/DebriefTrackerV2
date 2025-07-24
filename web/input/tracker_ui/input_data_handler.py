import os

from clients.databases.contracts import CVW17DatabaseRow
from services import Logger
from web.input._constants import BDA_IMAGE_PATH

class InputDataHandler:
    @staticmethod
    def validate_row(row: CVW17DatabaseRow):
        if None in [row.date, row.pilot_name, row.fl_name, row.msn_name, row.msn_nr, row.event, row.tail_number, row.hit,
                    row.destroyed, row.weapon_type, row.squadron, row.debrief_id]:
            return False

        if row.weapon_type not in ['A/A', 'A/G', 'N/A']:
            return False

        if 3 > len(row.event) > 4:
            return False

        return True

    @staticmethod
    def safe_int(x: str) -> int | None:
        if x.isdigit():
            return int(x)
        return None

    @staticmethod
    def validate_data_json(data) -> bool:
        return all(data.get(key) for key in ['mission_name',
                                             'mission_number',
                                             'mission_event',
                                             'mission_date',
                                             'callsign',
                                             'aircrew',
                                             'form_metadata'])

    @staticmethod
    def find_latest_numbered_folder(directory_path="."):
        items = os.listdir(directory_path)

        numeric_dirs = []
        for item in items:
            full_path = os.path.join(directory_path, item)
            if os.path.isdir(full_path) and item.isdigit():
                numeric_dirs.append(int(item))

        if numeric_dirs:
            latest = max(numeric_dirs)
            next_number = latest + 1
            Logger.info(f"Latest numbered folder: {latest}")
        else:
            next_number = 1
            Logger.info("No numbered folders found. Starting with 1.")

        new_folder_path = os.path.join(directory_path, str(next_number))

        try:
            os.makedirs(new_folder_path)
            return next_number
        except FileExistsError:
            Logger.warning(f"Folder {next_number} already exists!")
            return next_number + 1
        except Exception as e:
            Logger.error(f"Error creating folder: {e}")
            return None

    @staticmethod
    def save_bda_image(base64_data, debrief_id, filename):
        """
        Save base64 image data to file with proper extension
        Returns: filepath or None if error
        """
        import base64
        import os
        from pathlib import Path

        try:
            # Extract MIME type and extension from base64 data
            if not base64_data.startswith('data:image/'):
                print("Invalid base64 image data - missing data:image/ prefix")
                return None

            # Parse the data URL: data:image/jpeg;base64,/9j/4AAQ...
            header, encoded_data = base64_data.split(',', 1)
            mime_type = header.split(';')[0].split(':')[1]  # Extract "image/jpeg"

            # Map MIME types to file extensions
            mime_to_ext = {
                'image/jpeg': 'jpg',
                'image/jpg': 'jpg',
                'image/png': 'png',
                'image/gif': 'gif',
                'image/webp': 'webp',
                'image/bmp': 'bmp',
                'image/tiff': 'tiff'
            }

            file_extension = mime_to_ext.get(mime_type)
            if not file_extension:
                print(f"Unsupported image type: {mime_type}")
                return None

            # Add proper extension to filename if not already present
            filename_with_ext = filename
            if not filename.lower().endswith(f'.{file_extension}'):
                filename_with_ext = f"{filename}.{file_extension}"

            image_data = base64.b64decode(encoded_data)

            os.makedirs(BDA_IMAGE_PATH / str(debrief_id), exist_ok=True)

            filepath = BDA_IMAGE_PATH / Path(str(debrief_id)) / Path(filename_with_ext)
            with open(filepath, 'wb') as f:
                f.write(image_data)

            print(f"BDA image saved: {filepath} (type: {mime_type})")
            return filepath

        except Exception as e:
            print(f"Error saving BDA image: {str(e)}")
            return None
