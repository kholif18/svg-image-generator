# core/generate.py
import pandas as pd
from lxml import etree
import os
import base64
import time
import traceback
import re
from typing import Dict, Any, Optional
import shutil

from core.paths import resolve_path

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class FlexibleGenerator:
    """Generator fleksibel untuk template SVG dengan Field Mapping dan Color Mapping"""
    
    def __init__(self, config: Dict[str, Any]):
        # Resolve all paths in config
        self.config = config.copy()
        path_keys = ['template_file', 'data_file', 'foto_base_dir', 'output_svg_dir', 'output_image_dir']
        for key in path_keys:
            if key in self.config:
                self.config[key] = resolve_path(self.config[key])
        
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'errors': [],
            'time': 0
        }
        
    def safe_filename(self, name: str) -> str:
        """Buat filename yang aman"""
        forbidden = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', ' ']
        result = str(name).lower().strip()
        for char in forbidden:
            result = result.replace(char, '-')
        while '--' in result:
            result = result.replace('--', '-')
        return result.strip('-')
    
    def get_image_path(self, row: pd.Series, foto_config: Dict) -> Optional[str]:
        """Dapatkan path gambar berdasarkan konfigurasi"""
        if not isinstance(foto_config, dict):
            return None
            
        foto_field = foto_config.get('column') or foto_config.get('field')
        if not foto_field or foto_field not in row:
            return None
            
        foto_file = str(row[foto_field]).strip()
        if not foto_file or foto_file == 'nan':
            return None
            
        foto_base_dir = self.config.get('foto_base_dir', 'photos')
        if self.config.get('foto_subfolder_kelas') and 'kelas' in row:
            kelas = str(row['kelas']).strip()
            foto_path = os.path.join(foto_base_dir, kelas, foto_file)
        else:
            foto_path = os.path.join(foto_base_dir, foto_file)
            
        if os.path.exists(foto_path):
            return foto_path
            
        alt_path = os.path.join(foto_base_dir, foto_file)
        if os.path.exists(alt_path):
            return alt_path
            
        return None
    
    def apply_color_mappings(self, root: etree.Element, row: pd.Series, color_mappings: Dict[str, str]) -> None:
        """Ganti warna di SVG berdasarkan mapping ke kolom Excel"""
        if not color_mappings:
            return

        # Prepare replacement map: {original_color_upper: new_color_from_excel}
        replacements = {}
        for orig_color, col_name in color_mappings.items():
            if col_name in row:
                new_color = str(row[col_name]).strip()
                if new_color.startswith('#'):
                    replacements[orig_color.upper()] = new_color.upper()

        if not replacements:
            return

        for elem in root.iter():
            # 1. Check direct attributes: fill, stroke, stop-color
            for attr in ['fill', 'stroke', 'stop-color']:
                val = elem.get(attr)
                if val:
                    val_upper = val.upper()
                    if val_upper in replacements:
                        elem.set(attr, replacements[val_upper])

            # 2. Check style attribute (e.g., style="fill:#xxxxxx;stroke:#yyyyyy")
            style = elem.get('style')
            if style:
                new_style = style
                for orig_color, new_color in replacements.items():
                    # Case insensitive replacement for HEX in style string
                    pattern = re.compile(re.escape(orig_color), re.IGNORECASE)
                    new_style = pattern.sub(new_color, new_style)
                
                if new_style != style:
                    elem.set('style', new_style)

    def replace_placeholders(self, root: etree.Element, row: pd.Series, field_mappings: Dict) -> None:
        """Ganti semua placeholder dan warna di SVG"""

        # 1. Apply Color Mappings
        color_mappings = self.config.get('color_mappings', {})
        self.apply_color_mappings(root, row, color_mappings)

        # 2. Data Field Mapping (NAMA, JABATAN, etc)
        for field_name, field_config in field_mappings.items():
            if not isinstance(field_config, dict):
                continue

            field_type = field_config.get('type', 'text')

            if field_type == 'text':
                placeholder = field_config.get('placeholder', f'{{{{{field_name}}}}}')
                value = str(row.get(field_name, ''))

                for elem in root.iter():
                    if elem.text and placeholder in elem.text:
                        elem.text = elem.text.replace(placeholder, value)
                    if elem.tail and placeholder in elem.tail:
                        elem.tail = elem.tail.replace(placeholder, value)

            elif field_type == 'image':
                placeholder_id = field_config.get('image_id', field_name)
                image_path = self.get_image_path(row, field_config)

                if image_path and os.path.exists(image_path):
                    image_elem = root.xpath(f".//*[@id='{placeholder_id}']")
                    if image_elem:
                        image_elem = image_elem[0]
                        with open(image_path, "rb") as f:
                            encoded = base64.b64encode(f.read()).decode()
                        ext = os.path.splitext(image_path)[1].lower().replace(".", "")
                        href = f"data:image/{ext};base64,{encoded}"
                        image_elem.set("{http://www.w3.org/1999/xlink}href", href)
    
    def convert_to_image(self, svg_path: str, output_path: str, format: str, dpi: int = 300, quality: int = 95) -> bool:
        """Convert SVG ke format gambar menggunakan Inkscape"""
        try:
            inkscape_exe = shutil.which(self.config.get("inkscape_path", "inkscape"))
            if not inkscape_exe:
                return False
            
            format_lower = format.lower()
            quiet = " > nul 2>&1" if os.name == 'nt' else " > /dev/null 2>&1"
            
            if format_lower == 'png':
                cmd = f'"{inkscape_exe}" "{svg_path}" --export-type=png --export-filename="{output_path}" --export-dpi={dpi}{quiet}'
                result = os.system(cmd)
                return result == 0
                
            elif format_lower in ['jpg', 'jpeg']:
                temp_png = output_path.replace('.jpg', '.png').replace('.jpeg', '.png')
                cmd_png = f'"{inkscape_exe}" "{svg_path}" --export-type=png --export-filename="{temp_png}" --export-dpi={dpi}{quiet}'
                
                result = os.system(cmd_png)
                
                if result == 0 and os.path.exists(temp_png):
                    success = False
                    if PIL_AVAILABLE:
                        try:
                            img = Image.open(temp_png)
                            if img.mode in ('RGBA', 'LA', 'P'):
                                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                                if img.mode == 'RGBA' and len(img.split()) > 3:
                                    rgb_img.paste(img, mask=img.split()[-1])
                                else:
                                    rgb_img.paste(img)
                                rgb_img.save(output_path, 'JPEG', quality=quality)
                            else:
                                img.save(output_path, 'JPEG', quality=quality)
                            success = True
                        except Exception:
                            pass
                    
                    if not success:
                        magick_cmd = f'convert "{temp_png}" -quality {quality} "{output_path}"'
                        os.system(magick_cmd)
                        success = os.path.exists(output_path)
                    
                    try:
                        os.remove(temp_png)
                    except:
                        pass
                    
                    return success
                return False
                
            elif format_lower == 'pdf':
                cmd = f'"{inkscape_exe}" "{svg_path}" --export-type=pdf --export-filename="{output_path}"{quiet}'
                result = os.system(cmd)
                return result == 0
                
            return False
        except Exception:
            return False
    
    def generate_single(self, row: pd.Series, index: int, output_folder: str, is_image_output: bool = False) -> Dict:
        """Generate untuk satu record"""
        result = {'success': False, 'svg_path': None, 'image_paths': [], 'error': None}
        
        try:
            template_file = self.config.get('template_file')
            if not template_file or not os.path.exists(template_file):
                result['error'] = f"Template not found: {template_file}"
                return result
                
            tree = etree.parse(template_file)
            root = tree.getroot()
            
            field_mappings = self.config.get('field_mappings', {})
            
            self.replace_placeholders(root, row, field_mappings)
            
            # Cari nama dan kelas dari row secara case-insensitive
            nama = f"record_{index}"
            kelas = "umum"
            
            for col in row.index:
                if str(col).lower() == 'nama':
                    nama = str(row[col]).strip()
                elif str(col).lower() == 'kelas':
                    kelas = str(row[col]).strip()
            
            safe_name = self.safe_filename(nama)
            safe_kelas = self.safe_filename(kelas)
            
            kelas_output_dir = os.path.join(output_folder, safe_kelas)
            os.makedirs(kelas_output_dir, exist_ok=True)
            
            include_svg = self.config.get('include_svg', True)
            output_formats = self.config.get('output_formats', [])
            
            if not is_image_output and include_svg:
                svg_filename = os.path.join(kelas_output_dir, f"{safe_name}.svg")
                tree.write(svg_filename, encoding='utf-8', xml_declaration=True)
                result['svg_path'] = svg_filename
            
            if is_image_output and output_formats:
                temp_svg = os.path.join(kelas_output_dir, f"temp_{safe_name}.svg")
                tree.write(temp_svg, encoding='utf-8', xml_declaration=True)
                
                for fmt in output_formats:
                    img_filename = os.path.join(kelas_output_dir, f"{safe_name}.{fmt.lower()}")
                    if self.convert_to_image(temp_svg, img_filename, fmt, 
                                           self.config.get('image_dpi', 300),
                                           self.config.get('image_quality', 95)):
                        result['image_paths'].append(img_filename)
                
                if os.path.exists(temp_svg):
                    os.remove(temp_svg)
            elif not is_image_output and output_formats and result['svg_path']:
                for fmt in output_formats:
                    img_filename = os.path.join(kelas_output_dir, f"{safe_name}.{fmt.lower()}")
                    self.convert_to_image(result['svg_path'], img_filename, fmt,
                                         self.config.get('image_dpi', 300),
                                         self.config.get('image_quality', 95))
            
            result['success'] = True
        except Exception as e:
            result['error'] = str(e)
            
        return result
    
    def generate_all(self, progress_callback=None) -> Dict:
        """Generate semua data dengan callback progress"""
        start_time = time.time()
        
        try:
            data_file = self.config.get('data_file')
            if not data_file or not os.path.exists(data_file):
                self.stats['errors'].append(f"Data file not found: {data_file}")
                self.stats['time'] = round(time.time() - start_time, 2)
                return self.stats
                
            df = pd.read_excel(data_file)
            # Use columns as is for mapping, but normalize for internal usage
            original_columns = df.columns.tolist()
            # We don't lowercase all columns here because mapping needs exact match
            
            self.stats['total'] = len(df)
            
            output_svg_dir = self.config.get('output_svg_dir', 'output/svg')
            output_image_dir = self.config.get('output_image_dir', 'output/images')
            include_svg = self.config.get('include_svg', True)
            output_formats = self.config.get('output_formats', [])
            
            if include_svg:
                os.makedirs(output_svg_dir, exist_ok=True)
            if output_formats:
                os.makedirs(output_image_dir, exist_ok=True)
            
            for index, row in df.iterrows():
                nomor = index + 1
                
                if progress_callback:
                    # Try to find a 'nama' column case-insensitively for the status message
                    display_name = "Unknown"
                    for col in original_columns:
                        if col.lower() == 'nama':
                            display_name = row[col]
                            break
                    progress_callback(nomor, self.stats['total'], f"Memproses: {display_name}")
                
                result_svg = None
                result_images = None
                has_svg_success = False
                has_image_success = False
                
                if include_svg:
                    result_svg = self.generate_single(row, index, output_svg_dir, is_image_output=False)
                    if result_svg and isinstance(result_svg, dict):
                        has_svg_success = result_svg.get('success', False)
                
                if output_formats:
                    result_images = self.generate_single(row, index, output_image_dir, is_image_output=True)
                    if result_images and isinstance(result_images, dict):
                        has_image_success = result_images.get('success', False)
                
                if has_svg_success or has_image_success:
                    self.stats['success'] += 1
                else:
                    self.stats['failed'] += 1
                    error_msg = "Unknown error"
                    if result_svg and isinstance(result_svg, dict) and result_svg.get('error'):
                        error_msg = result_svg['error']
                    elif result_images and isinstance(result_images, dict) and result_images.get('error'):
                        error_msg = result_images['error']
                    self.stats['errors'].append(f"Row {nomor}: {error_msg}")
            
            self.stats['time'] = round(time.time() - start_time, 2)
        except Exception as e:
            error_detail = traceback.format_exc()
            self.stats['errors'].append(f"System error:\n{error_detail}")
            self.stats['time'] = round(time.time() - start_time, 2)
            
        return self.stats
