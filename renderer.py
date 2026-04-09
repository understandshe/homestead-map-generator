import io
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

class PremiumHomesteadRenderer:
    def __init__(self, width_m: int, height_m: int, px_per_meter: int = 15):
        self.w_m, self.h_m = width_m, height_m
        self.ppm = px_per_meter
        self.img_w, self.img_h = int(width_m * px_per_meter), int(height_m * px_per_meter)
        
        self.base = Image.new("RGBA", (self.img_w, self.img_h), (245, 240, 230, 255))
        self.draw = ImageDraw.Draw(self.base)
        
        self.textures = {
            "field": self._make_grass_texture(),
            "house": self._make_soil_texture(),
            "pond": self._make_water_texture(),
            "road": self._make_gravel_texture(),
            "garden": self._make_garden_texture(),
            "barn": self._make_wood_texture(),
            "flower": self._make_flower_texture()
        }
        
        try:
            self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
            self.font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except:
            self.font = ImageFont.load_default()
            self.font_small = self.font

    def _make_grass_texture(self):
        arr = np.random.normal(120, 15, (self.img_h, self.img_w, 3)).astype(np.uint8)
        arr[:, :, 0] = np.clip(arr[:, :, 0] + 30, 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] + 50, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] + 20, 0, 255)
        return Image.fromarray(arr, "RGB")

    def _make_water_texture(self):
        arr = np.random.normal(60, 10, (self.img_h, self.img_w, 3)).astype(np.uint8)
        arr[:, :, 0] = np.clip(arr[:, :, 0] + 40, 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] + 80, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] + 140, 0, 255)
        for i in range(0, self.img_h, 12):
            arr[i:i+2, :, 2] = np.clip(arr[i:i+2, :, 2] + 30, 0, 255)
        return Image.fromarray(arr, "RGB")

    def _make_soil_texture(self):
        arr = np.random.normal(140, 20, (self.img_h, self.img_w, 3)).astype(np.uint8)
        arr[:, :, 0] = np.clip(arr[:, :, 0] + 40, 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] + 20, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] - 10, 0, 255)
        return Image.fromarray(arr, "RGB")

    def _make_gravel_texture(self):
        arr = np.full((self.img_h, self.img_w, 3), 160, dtype=np.uint8)
        noise = np.random.randint(-20, 20, (self.img_h, self.img_w, 3), dtype=np.int16)
        arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
        return Image.fromarray(arr, "RGB")

    def _make_garden_texture(self):
        base = self._make_grass_texture()
        arr = np.array(base)
        arr[:, :, 1] = np.clip(arr[:, :, 1] + 30, 0, 255)
        return Image.fromarray(arr, "RGB")

    def _make_wood_texture(self):
        arr = np.random.normal(100, 15, (self.img_h, self.img_w, 3)).astype(np.uint8)
        arr[:, :, 0] = np.clip(arr[:, :, 0] + 50, 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] + 30, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] + 10, 0, 255)
        for i in range(0, self.img_w, 8):
            arr[:, i:i+1, 0] = np.clip(arr[:, i:i+1, 0] + 20, 0, 255)
        return Image.fromarray(arr, "RGB")

    def _make_flower_texture(self):
        base = self._make_garden_texture()
        arr = np.array(base)
        for _ in range(200):
            x, y = np.random.randint(0, self.img_w), np.random.randint(0, self.img_h)
            color = [255, 200, 50] if np.random.rand() > 0.5 else [255, 100, 150]
            arr[y-2:y+3, x-2:x+3] = color
        return Image.fromarray(arr, "RGB")

    def _m_to_px(self, x, y):
        return int(x * self.ppm), int((self.h_m - y) * self.ppm)

    def add_feature(self, x, y, w, h, feature_type, shadow=True):
        left = int(x * self.ppm)
        right = int((x + w) * self.ppm)
        top_cart = y + h
        bottom_cart = y
        top_pil = int((self.h_m - top_cart) * self.ppm)
        bottom_pil = int((self.h_m - bottom_cart) * self.ppm)
        
        width_px = right - left
        height_px = bottom_pil - top_pil
        
        tex = self.textures.get(feature_type, self.textures["field"]).copy()
        tex_crop = tex.crop((left, top_pil, right, bottom_pil))
        
        mask = Image.new("L", (width_px, height_px), 255)
        
        if shadow:
            shadow_offset = 8
            shadow_layer = Image.new("RGBA", (width_px + shadow_offset*2, height_px + shadow_offset*2), (0,0,0,0))
            shadow_base = Image.new("RGBA", (width_px, height_px), (0, 0, 0, 60))
            shadow_base = shadow_base.filter(ImageFilter.GaussianBlur(6))
            shadow_layer.paste(shadow_base, (shadow_offset, shadow_offset))
            self.base.paste(shadow_layer, (left - shadow_offset, top_pil - shadow_offset), shadow_layer)
        
        self.base.paste(tex_crop, (left, top_pil), mask)
        
        border_draw = ImageDraw.Draw(self.base)
        border_draw.rectangle([left, top_pil, right, bottom_pil], outline="#2C2C2C", width=2)
        border_draw.line([(left, top_pil), (right, top_pil)], fill="#FFFFFF", width=1)
        border_draw.line([(left, top_pil), (left, bottom_pil)], fill="#FFFFFF", width=1)

    def add_cartography(self):
        grid_step = 10 * self.ppm
        for x in range(0, self.img_w, grid_step):
            self.draw.line([(x, 0), (x, self.img_h)], fill="#D0D0D0", width=1)
        for y in range(0, self.img_h, grid_step):
            self.draw.line([(0, y), (self.img_w, y)], fill="#D0D0D0", width=1)
            
        sb_x, sb_y = 30, self.img_h - 50
        self.draw.rectangle([sb_x, sb_y, sb_x + 150, sb_y + 20], fill="#FFFFFF", outline="#333", width=2)
        self.draw.line([(sb_x, sb_y+20), (sb_x+150, sb_y+20)], fill="#333", width=3)
        self.draw.text((sb_x, sb_y - 20), "0m", fill="#222", font=self.font_small)
        self.draw.text((sb_x + 110, sb_y - 20), "10m", fill="#222", font=self.font_small)
        
        nx, ny = self.img_w - 60, 60
        self.draw.polygon([(nx, ny-30), (nx-15, ny+10), (nx+15, ny+10)], fill="#2C5F41", outline="#1A3D28")
        self.draw.text((nx-10, ny+15), "N", fill="#222", font=self.font_small)

    def render(self, features: list, legend: list) -> io.BytesIO:
        self.base.paste(self.textures["field"], (0, 0))
        
        for f in features:
            self.add_feature(f["x"], f["y"], f["w"], f["h"], f["type"], f.get("shadow", True))
            
        self.add_cartography()
        
        leg_x, leg_y = 30, 30
        self.draw.rectangle([leg_x-10, leg_y-10, leg_x+160, leg_y + len(legend)*28 + 10], 
                            fill="#FFFFFFCC", outline="#888", width=2)
        for i, (label, color) in enumerate(legend):
            cy = leg_y + i * 28
            self.draw.rectangle([leg_x, cy, leg_x+20, cy+20], fill=color, outline="#333", width=2)
            self.draw.text((leg_x + 28, cy + 2), label, fill="#222", font=self.font_small)
            
        buf = io.BytesIO()
        self.base.convert("RGB").save(buf, format="PNG", dpi=(300, 300), optimize=True)
        buf.seek(0)
        return buf
