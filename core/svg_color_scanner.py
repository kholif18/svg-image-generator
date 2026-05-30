# core/svg_color_scanner.py
import re
import os
from lxml import etree
from typing import List, Set

class SVGColorScanner:
    """Scan SVG for all unique colors in fill, stroke, and style attributes"""
    
    # Regex for HEX colors #RRGGBB or #RGB
    COLOR_REGEX = r'#(?:[0-9a-fA-F]{3}){1,2}\b'
    
    @staticmethod
    def normalize_color(color: str) -> str:
        """Normalize color to #RRGGBB uppercase"""
        color = color.upper()
        if len(color) == 4: # #RGB -> #RRGGBB
            return f"#{color[1]*2}{color[2]*2}{color[3]*2}"
        return color

    @staticmethod
    def scan(file_path: str) -> List[str]:
        if not os.path.exists(file_path):
            return []
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Use regex for a broad sweep first (handles fill, stroke, and style strings)
            matches = re.findall(SVGColorScanner.COLOR_REGEX, content)
            
            unique_colors = set()
            for color in matches:
                unique_colors.add(SVGColorScanner.normalize_color(color))
                
            # Also specifically check attributes via etree to be sure
            # stop-color in gradients is sometimes not caught by simple regex if it has namespaces
            try:
                tree = etree.parse(file_path)
                root = tree.getroot()
                for elem in root.iter():
                    # Check direct attributes
                    for attr in ['fill', 'stroke', 'stop-color']:
                        val = elem.get(attr)
                        if val and val.startswith('#'):
                            color_match = re.search(SVGColorScanner.COLOR_REGEX, val)
                            if color_match:
                                unique_colors.add(SVGColorScanner.normalize_color(color_match.group()))
                    
                    # Check style attribute
                    style = elem.get('style')
                    if style:
                        style_matches = re.findall(SVGColorScanner.COLOR_REGEX, style)
                        for color in style_matches:
                            unique_colors.add(SVGColorScanner.normalize_color(color))
            except:
                pass # Fallback to regex results only if XML parsing fails
                
            return sorted(list(unique_colors))
        except Exception as e:
            print(f"Error scanning SVG colors: {e}")
            return []
