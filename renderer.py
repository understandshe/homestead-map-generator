# renderer.py - Lite Version (512MB RAM Friendly)
import io
import math
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

class PremiumHomesteadRenderer:
    def __init__(self, width_m: int, height_m: int, px_per_meter: int = 12):
        self.w_m, self.h_m = width_m, height_m
        self.ppm = px_per_meter
        self.img_w = min(int(width_m * px_per_meter), 2000)  # Max width cap
        self.img_h = min(int(height_m * px_per_meter), 1500)  # Max height cap
        
        self.base = Image.new("RGB", (self.img_w, self.img_h), color="#E8F4E8")
        self.draw = ImageDraw.Draw(self.base)
        
        # छोटे टेक्सचर टाइल्स (64×64) - मेमोरी सेफ
        self.tile_size = 64
        self.textures = {
            "field": self._make_tile("#8FBC8F", "#7A9F7A"),
            "house": self._make_tile("#C4A484", "#A68A64"),
            "pond": self._make_tile("#4A90E2", "#3A70B2"),
            "road": self._make_tile("#9E9E9E", "#7E7E7E"),
            "garden": self._make_tile("#7CB342", "#5A8A2A"),
            "barn": self._make_tile("#8D6E63", "#6D4E43"),
            "flower": self._make_tile("#7CB342", "#FFD54F", flower=True)
        }
        
        # फॉन्ट
        try:
            self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
            self.font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        except:
            self.font = ImageFont.load_default()
            self.font_small = self.font

    def _make_tile(self, base_color, dark_color, flower=False):
        """64×64 टेक्सचर टाइल बनाएं - मेमोरी एफिशिएंट"""
        tile = Image.new("RGB", (self.tile_size, self.tile_size), base_color)
        tdraw = ImageDraw.Draw(tile)
        
        # नॉइज डॉट्स
        for _ in range(30):
            x, y = random.randint(0, 63), random.randint(0, 63)
            tdraw.point((x, y), fill=dark_color)
        
        # फ्लावर स्पेशल
        if flower:
            for _ in range(8):
                x, y = random.randint(0, 63), random.randint(0, 63)
                color = "#FFD54F" if random.random() > 0.5 else "#FF6B9D"
                tdraw.ellipse([x-2, y-2, x+2, y+2], fill=color)
        
        return tile

    def _apply_texture(self, x1, y1, x2, y2, feature_type):
        """टाइल्ड टेक्सचर अप्लाई करें"""
        tile = self.textures.get(feature_type, self.textures["field"])
        for py in range(y1, y2, self.tile_size):
            for px in range(x1, x2, self.tile_size):
                self.base.paste(tile, (px, py))

    def _m_to_px(self, x, y):
        return int(x * self.ppm), int((self.h_m - y) * self.ppm)

    def add_feature(self, x, y, w, h, feature_type, shadow=True):
        left = int(x * self.ppm)
        right = min(int((x + w) * self.ppm), self.img_w)
        top_cart = y + h
        bottom_cart = y
        top_pil = max(int((self.h_m - top_cart) * self.ppm), 0)
        bottom_pil = min(int((self.h_m - bottom_cart) * self.ppm), self.img_h)
        
        # टेक्सचर अप्लाई
        self._apply_texture(left, top_pil, right, bottom_pil, feature_type)
        
        # शैडो (सिंपल)
        if shadow:
            shadow_layer = Image.new("RGBA", (right-left, bottom_pil-top_pil), (0,0,0,40))
            shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(4))
            self.base.paste(shadow_layer, (left+6, top_pil+6), shadow_layer)
        
        # बॉर्डर
        self.draw.rectangle([left, top_pil, right, bottom_pil], outline="#2C2C2C", width=2)
        # हाइलाइट
        self.draw.line([(left, top_pil), (right, top_pil)], fill="#FFFFFF80", width=1)
        self.draw.line([(left, top_pil), (left, bottom_pil)], fill="#FFFFFF80", width=1)

    def add_cartography(self):
        # ग्रिड
        grid_step = 10 * self.ppm
        for x in range(0, self.img_w, grid_step):
            self.draw.line([(x, 0), (x, self.img_h)], fill="#D0D0D080", width=1)
        for y in range(0, self.img_h, grid_step):
            self.draw.line([(0, y), (self.img_w, y)], fill="#D0D0D080", width=1)
        
        # स्केल बार
        sb_x, sb_y = 30, self.img_h - 45
        self.draw.rectangle([sb_x, sb_y, sb_x+120, sb_y+18], fill="#FFFFFF", outline="#333", width=1)
        self.draw.line([(sb_x, sb_y+18), (sb_x+120, sb_y+18)], fill="#333", width=2)
        self.draw.text((sb_x, sb_y-18), "0m", fill="#222", font=self.font_small)
        self.draw.text((sb_x+90, sb_y-18), "10m", fill="#222", font=self.font_small)
        
        # नॉर्थ एरो
        nx, ny = self.img_w - 50, 50
        self.draw.polygon([(nx, ny-25), (nx-12, ny+8), (nx+12, ny+8)], fill="#2C5F41", outline="#1A3D28")
        self.draw.text((nx-8, ny+12), "N", fill="#222", font=self.font_small)

    def render(self, features: list, legend: list) -> io.BytesIO:
        # बैकग्राउंड टेक्सचर
        self._apply_texture(0, 0, self.img_w, self.img_h, "field")
        
        # फीचर्स
        for f in features:
            self.add_feature(f["x"], f["y"], f["w"], f["h"], f["type"], f.get("shadow", True))
        
        # कार्टोग्राफी
        self.add_cartography()
        
        # लेजेंड
        leg_x, leg_y = 30, 30
        self.draw.rectangle([leg_x-8, leg_y-8, leg_x+150, leg_y + len(legend)*26 + 8], 
                            fill="#FFFFFFE0", outline="#888", width=1)
        for i, (label, color) in enumerate(legend):
            cy = leg_y + i * 26
            self.draw.rectangle([leg_x, cy, leg_x+18, cy+18], fill=color, outline="#333", width=1)
            self.draw.text((leg_x+24, cy+2), label, fill="#222", font=self.font_small)
        
        # एक्सपोर्ट
        buf = io.BytesIO()
        self.base.save(buf, format="PNG", dpi=(300, 300), optimize=True)
        buf.seek(0)
        return buf
