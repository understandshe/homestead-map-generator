# renderer.py
import io
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math

class HomesteadRenderer:
    def __init__(self, width_m: int, height_m: int, px_per_meter: int = 12):
        self.w_m, self.h_m = width_m, height_m
        self.ppm = px_per_meter
        self.img_w, self.img_h = int(width_m * px_per_meter), int(height_m * px_per_meter)
        self.base = Image.new("RGB", (self.img_w, self.img_h), color="#F4EFE6")
        self.draw = ImageDraw.Draw(self.base)

    def _m_to_px(self, x, y):
        # कार्टोग्राफी: (0,0) = बॉटम-लेफ्ट, Y ऊपर बढ़ता है
        # PIL: (0,0) = टॉप-लेफ्ट, Y नीचे बढ़ता है
        return int(x * self.ppm), int((self.h_m - y) * self.ppm)

    def add_rect(self, x, y, w, h, fill, outline="#333", width=2):
        # x, y = बॉटम-लेफ्ट कॉर्नर (मीटर में, कार्टोग्राफी कोऑर्ड्स)
        left = int(x * self.ppm)
        right = int((x + w) * self.ppm)
        
        # कार्टोग्राफी में Y ऊपर बढ़ता है, PIL में नीचे
        # इसलिए: कार्टोग्राफी का "टॉप" = PIL का "टॉप" (छोटा Y), और वाइस वर्सा
        top_cart = y + h          # ऊपर वाला एज (कार्टोग्राफी)
        bottom_cart = y           # नीचे वाला एज (कार्टोग्राफी)
        
        top_pil = int((self.h_m - top_cart) * self.ppm)      # PIL में टॉप (छोटा मान)
        bottom_pil = int((self.h_m - bottom_cart) * self.ppm) # PIL में बॉटम (बड़ा मान)
        
        # अब rectangle को सही ऑर्डर में पास करें: [left, top, right, bottom]
        self.draw.rectangle([left, top_pil, right, bottom_pil], fill=fill, outline=outline, width=width)

    def add_shadow(self, x, y, w, h, angle=135, length=18, blur=5):
        # शैडो के लिए भी सही कोऑर्डिनेट कैलकुलेशन
        left = int(x * self.ppm)
        right = int((x + w) * self.ppm)
        top_cart = y + h
        bottom_cart = y
        top_pil = int((self.h_m - top_cart) * self.ppm)
        bottom_pil = int((self.h_m - bottom_cart) * self.ppm)
        
        dx = int(length * math.cos(math.radians(angle)))
        dy = int(length * math.sin(math.radians(angle)))  # ध्यान दें: +dy क्योंकि शैडो नीचे-दाईं ओर
        
        shadow = Image.new("RGBA", (right - left, bottom_pil - top_pil), (0, 0, 0, 90))
        shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
        self.base.paste(shadow, (left + dx, top_pil + dy), shadow)

    def add_legend(self, items, x=20, y=20):
        font = ImageFont.load_default()
        for i, (label, color) in enumerate(items):
            cy = y + i * 24
            self.draw.rectangle([x, cy, x+16, cy+16], fill=color, outline="#333")
            self.draw.text((x + 22, cy + 2), label, fill="#222", font=font)

    def add_scale_bar(self, meters_per_segment=10, x=20, y=None):
        if y is None: y = self.img_h - 40
        seg_px = meters_per_segment * self.ppm
        self.draw.line([(x, y), (x + seg_px, y)], fill="#333", width=3)
        self.draw.text((x, y + 6), f"{meters_per_segment}m", fill="#222", font=ImageFont.load_default())
        self.draw.text((x + seg_px - 20, y + 6), "0", fill="#222", font=ImageFont.load_default())

    def render(self, features: list, legend: list) -> io.BytesIO:
        # बेस लेयर (खेत/जमीन)
        for f in features:
            self.add_rect(f["x"], f["y"], f["w"], f["h"], fill=f["color"])
            if f.get("shadow", False):
                self.add_shadow(f["x"], f["y"], f["w"], f["h"])

        # कार्टोग्राफी एलिमेंट्स
        self.add_legend(legend)
        self.add_scale_bar(meters_per_segment=10)

        # PNG बाइट्स में रिटर्न
        buf = io.BytesIO()
        self.base.save(buf, format="PNG", dpi=(300, 300))
        buf.seek(0)
        return buf
