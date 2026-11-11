"""Moteur motion design (style After Effects) : sprites dessinés en Python, animations, rendu ffmpeg."""
import math, random, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
SS = 3  # sur-échantillonnage pour des bords lisses
OUT = (62, 42, 32, 255)  # contour "cartoon"
FONT = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
FONT_B = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"


# ---------- outils de dessin ----------
class Pen:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.img = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)

    def _b(self, box):
        return [v * SS for v in box]

    def ell(self, box, fill, ow=5, out=OUT):
        self.d.ellipse(self._b(box), fill=fill, outline=out if ow else None, width=ow * SS)

    def rect(self, box, fill, r=0, ow=5, out=OUT):
        self.d.rounded_rectangle(self._b(box), radius=r * SS, fill=fill, outline=out if ow else None, width=ow * SS)

    def poly(self, pts, fill, ow=5, out=OUT):
        p = [(x * SS, y * SS) for x, y in pts]
        self.d.polygon(p, fill=fill)
        if ow:
            self.d.line(p + [p[0]], fill=out, width=ow * SS, joint="curve")

    def line(self, pts, fill=OUT, w=5):
        self.d.line([(x * SS, y * SS) for x, y in pts], fill=fill, width=w * SS, joint="curve")

    def arc(self, box, a0, a1, fill=OUT, w=5):
        self.d.arc(self._b(box), a0, a1, fill=fill, width=w * SS)

    def text(self, xy, s, size, fill, font=FONT, anchor="mm"):
        f = ImageFont.truetype(font, size * SS)
        self.d.text((xy[0] * SS, xy[1] * SS), s, font=f, fill=fill, anchor=anchor)

    def done(self):
        return self.img.resize((self.w, self.h), Image.LANCZOS)


def blob_pts(cx, cy, rx, ry, seed, amp=0.08, n=40, egg=0.0):
    rnd = random.Random(seed)
    ph = [rnd.random() * 6.28 for _ in range(3)]
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        r = 1 + amp * (math.sin(2 * t + ph[0]) * 0.6 + math.sin(3 * t + ph[1]) * 0.4)
        x = cx + rx * r * math.cos(t) * (1 + egg * math.sin(t))
        y = cy + ry * r * math.sin(t)
        pts.append((x, y))
    return pts


# ---------- ingrédients ----------
def egg():
    p = Pen(170, 210)
    p.poly(blob_pts(85, 108, 68, 92, 1, amp=0, egg=0.13), (255, 250, 238, 255))
    p.ell((48, 45, 72, 85), (255, 255, 255, 255), ow=0)
    return p.done()


def potato():
    p = Pen(250, 190)
    p.poly(blob_pts(125, 95, 110, 78, 7, amp=0.07), (214, 168, 98, 255))
    for x, y in [(80, 70), (150, 60), (170, 120), (100, 125), (128, 95)]:
        p.ell((x - 7, y - 5, x + 7, y + 5), (170, 125, 65, 255), ow=0)
    return p.done()


def onion():
    p = Pen(220, 250)
    body = blob_pts(110, 150, 92, 88, 3, amp=0.02)
    body = [(x, y - max(0, (150 - y)) * 0.35 if y < 150 else y) for x, y in body]
    p.poly(body, (232, 176, 112, 255))
    p.poly([(98, 60), (110, 18), (122, 60)], (232, 176, 112, 255))
    for dx in (-45, 0, 45):
        p.arc((110 - 60 + dx * 0.5 - abs(dx) * 0.4, 70, 110 + 60 + dx * 0.5 + abs(dx) * 0.4, 232),
              200 if dx < 0 else 250, 300 if dx <= 0 else 340, (190, 130, 70, 255), 4)
    for dx in (-14, 0, 14):
        p.line([(110, 236), (110 + dx, 248)], (150, 110, 70, 255), 4)
    return p.done()


def peas_pod():
    p = Pen(300, 140)
    p.poly([(20, 70), (70, 25), (230, 25), (285, 60), (230, 115), (70, 115)], (110, 180, 60, 255))
    p.poly([(45, 70), (85, 45), (220, 45), (260, 66), (220, 95), (85, 95)], (170, 220, 110, 255), ow=3)
    for i in range(5):
        x = 85 + i * 32
        p.ell((x - 17, 53, x + 17, 87), (90, 170, 50, 255), ow=3)
        p.ell((x - 9, 59, x - 1, 67), (200, 240, 160, 255), ow=0)
    return p.done()


def rice_bowl():
    p = Pen(330, 270)
    p.d.pieslice(p._b((40, 20, 290, 230)), 180, 360, fill=(255, 255, 250, 255), outline=OUT, width=5 * SS)
    rnd = random.Random(4)
    for _ in range(45):
        a = rnd.uniform(math.pi, 2 * math.pi)
        r = rnd.uniform(0, 1)
        x = 165 + math.cos(a) * 110 * r
        y = 125 + math.sin(a) * 95 * r
        p.ell((x - 8, y - 4, x + 8, y + 4), (238, 232, 215, 255), ow=0)
    p.d.pieslice(p._b((15, 40, 315, 250)), 0, 180, fill=(80, 160, 205, 255), outline=OUT, width=5 * SS)
    p.rect((15, 136, 315, 150), (80, 160, 205, 255), r=7)
    p.line([(70, 190), (260, 190)], (255, 255, 255, 200), 6)
    return p.done()


def penne(color=(246, 206, 110, 255)):
    p = Pen(130, 60)
    p.poly([(12, 50), (30, 10), (120, 10), (102, 50)], color, ow=4)
    for x in (45, 62, 79, 96):
        p.line([(x, 14), (x - 12, 46)], (215, 165, 70, 255), 3)
    p.ell((97, 9, 125, 51), (225, 175, 80, 255), ow=4)
    return p.done()


def penne_pile():
    img = Image.new("RGBA", (300, 230), (0, 0, 0, 0))
    rnd = random.Random(9)
    pn = penne()
    for _ in range(11):
        s = pn.rotate(rnd.uniform(-70, 70), Image.BICUBIC, expand=True)
        x = int(rnd.uniform(20, 300 - s.width - 10))
        y = int(rnd.uniform(40, 230 - s.height - 5))
        img.alpha_composite(s, (x, y))
    return img


def tuna_can():
    p = Pen(260, 220)
    p.rect((25, 60, 235, 180), (70, 135, 205, 255), r=0, ow=0)
    p.ell((25, 145, 235, 205), (70, 135, 205, 255))
    p.rect((25, 60, 235, 175), (70, 135, 205, 255), r=0, ow=0)
    p.line([(25, 60), (25, 175)]); p.line([(235, 60), (235, 175)])
    p.ell((25, 25, 235, 95), (205, 210, 220, 255))
    p.ell((50, 35, 210, 85), (180, 186, 198, 255), ow=3)
    p.ell((90, 110, 160, 150), (255, 255, 255, 255), ow=0)
    p.poly([(155, 130), (185, 110), (185, 150)], (255, 255, 255, 255), ow=0)
    p.ell((100, 120, 110, 130), (70, 135, 205, 255), ow=0)
    return p.done()


def tomato(size=120):
    p = Pen(size, size)
    s = size / 120
    p.ell((8 * s, 18 * s, 112 * s, 114 * s), (226, 52, 40, 255), ow=int(4 * s) or 1)
    star = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        r = (30 if i % 2 == 0 else 12) * s
        star.append((60 * s + r * math.cos(a), 30 * s + r * math.sin(a)))
    p.poly(star, (80, 160, 60, 255), ow=int(3 * s) or 1)
    p.ell((25 * s, 45 * s, 42 * s, 62 * s), (255, 140, 120, 255), ow=0)
    return p.done()


def coulis_jar():
    p = Pen(200, 290)
    p.rect((25, 60, 175, 280), (205, 45, 38, 255), r=34)
    p.rect((45, 22, 155, 66), (235, 190, 70, 255), r=10)
    p.rect((42, 120, 158, 230), (255, 248, 236, 255), r=14, ow=4)
    p.rect((40, 80, 54, 250), (255, 120, 110, 200), r=7, ow=0)
    jar = p.done()
    jar.alpha_composite(tomato(80), (60, 135))
    return jar


def carrot():
    p = Pen(320, 150)
    p.poly([(20, 80), (225, 45), (250, 60), (252, 100), (225, 115)], (245, 130, 40, 255))
    for x in (80, 130, 180):
        p.line([(x, 70 + (x - 80) * -0.12), (x + 14, 76 + (x - 80) * -0.12)], (200, 95, 20, 255), 4)
    for a in (-35, 0, 35):
        r = math.radians(a)
        p.poly([(250, 80), (250 + 70 * math.cos(r) - 12 * math.sin(r), 80 + 70 * math.sin(r) - 12),
                (250 + 70 * math.cos(r) + 12 * math.sin(r), 80 + 70 * math.sin(r) + 12)], (90, 175, 60, 255), ow=4)
    return p.done()


def bread_slice():
    p = Pen(260, 270)
    shape = lambda m: [(30 + m, 255 - m), (30 + m, 110)] + \
        [(130 + (100 - m) * math.cos(math.radians(a)), 105 + (80 - m * 0.8) * math.sin(math.radians(a))) for a in range(180, 361, 10)] + \
        [(230 - m, 110), (230 - m, 255 - m)]
    p.poly(shape(0), (196, 132, 62, 255))
    p.poly(shape(16), (252, 224, 168, 255), ow=0)
    for x, y in [(90, 140), (150, 180), (120, 220), (175, 120)]:
        p.ell((x - 5, y - 3, x + 5, y + 3), (225, 190, 130, 255), ow=0)
    return p.done()


def ham():
    p = Pen(260, 230)
    p.poly(blob_pts(130, 115, 115, 98, 11, amp=0.04), (255, 205, 210, 255))
    p.poly(blob_pts(130, 115, 95, 80, 11, amp=0.04), (238, 140, 155, 255), ow=0)
    for x, y in [(100, 90), (160, 130), (120, 150)]:
        p.ell((x - 12, y - 6, x + 12, y + 6), (250, 175, 185, 255), ow=0)
    return p.done()


def cheese():
    p = Pen(290, 210)
    p.poly([(20, 175), (270, 175), (270, 95), (40, 60)], (255, 208, 70, 255))
    p.poly([(20, 175), (40, 60), (270, 95), (270, 110), (36, 82)], (255, 226, 120, 255), ow=0)
    p.line([(20, 175), (40, 60), (270, 95)])
    for x, y, r in [(90, 130, 18), (170, 145, 12), (220, 125, 15), (140, 110, 9)]:
        p.ell((x - r, y - r * 0.8, x + r, y + r * 0.8), (225, 170, 40, 255), ow=0)
    return p.done()


# ---------- plats ----------
def pan(inner_fn, seed=0):
    p = Pen(720, 520)
    p.rect((470, 225, 715, 285), (60, 55, 60, 255), r=28)
    p.ell((10, 10, 510, 510), (70, 74, 84, 255))
    p.ell((40, 40, 480, 480), (105, 110, 122, 255), ow=3)
    inner_fn(p, 260, 260, 205, seed)
    return p.done()


def omelette_inner(p, cx, cy, r, seed):
    p.poly(blob_pts(cx, cy, r, r, 21, amp=0.03), (252, 206, 72, 255), ow=4, out=(220, 160, 40, 255))
    p.poly(blob_pts(cx - 20, cy - 25, r * 0.6, r * 0.5, 22, amp=0.1), (255, 222, 110, 255), ow=0)
    rnd = random.Random(5)
    for _ in range(9):
        a, rr = rnd.uniform(0, 6.28), rnd.uniform(0, r * 0.75)
        x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr
        p.rect((x - 17, y - 15, x + 17, y + 15), (244, 222, 160, 255), r=7, ow=3, out=(200, 160, 90, 255))
    for _ in range(14):
        a, rr = rnd.uniform(0, 6.28), rnd.uniform(0, r * 0.85)
        x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr
        p.ell((x - 5, y - 5, x + 5, y + 5), (80, 160, 60, 255), ow=0)


def fried_rice_inner(p, cx, cy, r, seed):
    p.ell((cx - r, cy - r, cx + r, cy + r), (240, 226, 190, 255), ow=0)
    rnd = random.Random(8)
    for _ in range(260):
        a, rr = rnd.uniform(0, 6.28), r * math.sqrt(rnd.random()) * 0.95
        x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr
        ang = rnd.uniform(0, 3.14)
        dx, dy = 9 * math.cos(ang), 9 * math.sin(ang)
        p.line([(x - dx, y - dy), (x + dx, y + dy)], (255, 252, 240, 255), 8)
    for _ in range(14):
        a, rr = rnd.uniform(0, 6.28), r * math.sqrt(rnd.random()) * 0.85
        x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr
        p.poly(blob_pts(x, y, 22, 15, rnd.randint(0, 99), amp=0.2, n=12), (255, 205, 60, 255), ow=3, out=(220, 160, 40, 255))
    for _ in range(26):
        a, rr = rnd.uniform(0, 6.28), r * math.sqrt(rnd.random()) * 0.9
        x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr
        p.ell((x - 11, y - 11, x + 11, y + 11), (95, 175, 55, 255), ow=3, out=(50, 110, 30, 255))


def pot(content, w=440, h=360, color=(176, 186, 200, 255)):
    """Casserole vue de côté ; content(p, cx, cy, rx, ry) dessine la surface."""
    p = Pen(w, h)
    top = 90
    p.rect((5, top + 20, 50, top + 50), (90, 95, 105, 255), r=14)
    p.rect((w - 50, top + 20, w - 5, top + 50), (90, 95, 105, 255), r=14)
    p.rect((35, top, w - 35, h - 15), color, r=40)
    p.rect((35, top, w - 35, top + 60), color, r=0, ow=0)
    p.line([(35, top + 30), (35, h - 60)]); p.line([(w - 35, top + 30), (w - 35, h - 60)])
    p.ell((35, top - 40, w - 35, top + 40), (120, 128, 142, 255))
    content(p, w / 2, top, (w - 90) / 2, 30)
    p.line([(70, top + 70), (70, h - 60)], (230, 235, 242, 255), 10)
    return p.done()


def water_pasta(p, cx, cy, rx, ry):
    p.ell((cx - rx, cy - ry, cx + rx, cy + ry), (170, 215, 240, 255), ow=3)
    rnd = random.Random(2)
    for _ in range(7):
        x = cx + rnd.uniform(-rx * 0.7, rx * 0.7); y = cy + rnd.uniform(-ry * 0.5, ry * 0.5)
        a = rnd.uniform(-0.6, 0.6)
        p.line([(x - 22 * math.cos(a), y - 8 * math.sin(a)), (x + 22 * math.cos(a), y + 8 * math.sin(a))], (246, 206, 110, 255), 13)
    for _ in range(6):
        x = cx + rnd.uniform(-rx * 0.8, rx * 0.8); y = cy + rnd.uniform(-ry * 0.6, ry * 0.6)
        p.ell((x - 7, y - 5, x + 7, y + 5), (230, 245, 255, 255), ow=2, out=(130, 180, 210, 255))


def red_sauce(p, cx, cy, rx, ry):
    p.ell((cx - rx, cy - ry, cx + rx, cy + ry), (205, 48, 38, 255), ow=3)
    p.ell((cx - rx * 0.5, cy - ry * 0.5, cx - rx * 0.1, cy), (240, 100, 80, 255), ow=0)
    p.ell((cx + rx * 0.2, cy - ry * 0.2, cx + rx * 0.45, cy + ry * 0.3), (240, 100, 80, 255), ow=0)


def orange_soup(p, cx, cy, rx, ry):
    p.ell((cx - rx, cy - ry, cx + rx, cy + ry), (250, 150, 50, 255), ow=3)
    p.ell((cx - rx * 0.5, cy - ry * 0.5, cx - rx * 0.05, cy + ry * 0.1), (255, 190, 100, 255), ow=0)


def soup_bowl():
    p = Pen(300, 230)
    p.d.pieslice(p._b((20, 0, 280, 220)), 0, 180, fill=(255, 255, 255, 255), outline=OUT, width=5 * SS)
    p.ell((20, 80, 280, 140), (250, 150, 50, 255))
    p.ell((70, 92, 140, 115), (255, 190, 100, 255), ow=0)
    return p.done()


def hand_blender():
    p = Pen(140, 420)
    p.rect((30, 10, 110, 190), (245, 245, 248, 255), r=34)
    p.rect((52, 60, 88, 100), (90, 160, 220, 255), r=10, ow=3)
    p.rect((58, 185, 82, 340), (200, 205, 215, 255), r=6)
    p.d.pieslice(p._b((22, 300, 118, 410)), 180, 360, fill=(200, 205, 215, 255), outline=OUT, width=5 * SS)
    p.line([(22, 355), (118, 355)])
    return p.done()


def croque():
    p = Pen(300, 230)
    p.rect((20, 70, 280, 215), (200, 135, 60, 255), r=22)
    p.rect((20, 40, 280, 180), (236, 176, 92, 255), r=22)
    p.poly([(28, 70), (272, 70), (272, 105), (240, 135), (215, 105), (170, 150), (135, 105), (95, 140), (60, 105), (28, 120)],
           (255, 205, 60, 255), ow=4, out=(215, 150, 30, 255))
    for x in (90, 150, 210):
        p.line([(x - 25, 160), (x + 25, 160)], (170, 105, 40, 255), 6)
    return p.done()


def oven(glow=1.0):
    p = Pen(560, 520)
    p.rect((10, 10, 550, 510), (236, 240, 245, 255), r=30)
    p.rect((10, 10, 550, 110), (200, 208, 218, 255), r=30)
    p.rect((10, 70, 550, 110), (200, 208, 218, 255), r=0, ow=0)
    p.line([(10, 110), (550, 110)])
    for x in (80, 160, 400, 480):
        p.ell((x - 24, 36, x + 24, 84), (90, 95, 105, 255), ow=4)
        p.line([(x, 42), (x, 58)], (255, 255, 255, 255), 5)
    p.rect((250, 42, 310, 78), (40, 45, 55, 255), r=8, ow=3)
    p.rect((60, 145, 500, 175), (150, 158, 170, 255), r=14)
    g = int(150 + 70 * glow)
    p.rect((60, 200, 500, 470), (255, g, 90, 255), r=24)
    p.rect((90, 225, 470, 445), (255, min(255, g + 40), 140, 255), r=16, ow=0)
    img = p.done()
    c = croque().resize((240, 184), Image.LANCZOS)
    img.alpha_composite(c, (160, 255))
    shine = Pen(560, 520)
    shine.line([(110, 240), (180, 240)], (255, 255, 255, 170), 9)
    img.alpha_composite(shine.done())
    return img


def plate():
    p = Pen(560, 420)
    p.rect((20, 120, 50, 400), (200, 205, 215, 255), r=12)
    for x in (16, 30, 44):
        p.rect((x - 4, 40, x + 6, 140), (200, 205, 215, 255), r=4, ow=3)
    p.rect((510, 120, 540, 400), (200, 205, 215, 255), r=12)
    p.poly([(510, 230), (510, 40), (545, 80), (540, 230)], (220, 225, 232, 255))
    p.ell((70, 30, 490, 410), (255, 255, 255, 255))
    p.ell((120, 80, 440, 360), (245, 246, 250, 255), ow=3, out=(215, 218, 225, 255))
    p.poly(blob_pts(280, 220, 120, 85, 31, amp=0.08), (252, 200, 80, 255), ow=4)
    p.poly(blob_pts(250, 200, 55, 35, 32, amp=0.15), (255, 225, 130, 255), ow=0)
    for x, y in [(230, 230), (310, 190), (330, 250), (270, 175)]:
        p.ell((x - 12, y - 12, x + 12, y + 12), (90, 170, 60, 255), ow=3)
    for x, y in [(200, 200), (350, 215)]:
        p.ell((x - 16, y - 16, x + 16, y + 16), (220, 60, 50, 255), ow=3)
    return p.done()


def timer(label, progress, accent):
    p = Pen(260, 300)
    p.rect((112, 4, 148, 34), (90, 95, 105, 255), r=8)
    p.ell((20, 40, 240, 260), (255, 255, 255, 255), ow=7)
    a1 = -90 + 360 * max(0.001, min(1, progress))
    p.d.arc(p._b((40, 60, 220, 240)), -90, a1, fill=accent, width=16 * SS)
    p.text((130, 140), label.split()[0], 64, (40, 40, 40, 255))
    p.text((130, 192), label.split()[1], 30, (90, 90, 90, 255), font=FONT_B)
    return p.done()


def cupboard(open_f):
    """Placard 640x720 ; open_f 0 = fermé, 1 = ouvert (portes repliées)."""
    p = Pen(640, 720)
    p.rect((10, 10, 630, 710), (186, 126, 76, 255), r=20)
    p.rect((40, 40, 600, 680), (243, 222, 190, 255), r=8, ow=4)
    p.rect((40, 330, 600, 352), (186, 126, 76, 255), r=0, ow=4)
    return p.done()


def cupboard_doors(open_f):
    p = Pen(640, 720)
    w = 280 * (1 - open_f) + 20 * open_f
    c = (200, 140, 88, 255)
    p.rect((40, 40, 40 + w, 680), c, r=8, ow=4)
    p.rect((600 - w, 40, 600, 680), c, r=8, ow=4)
    if open_f < 0.85:
        p.rect((40 + w - 40, 330, 40 + w - 22, 410), (240, 200, 90, 255), r=8, ow=3)
        p.rect((600 - w + 22, 330, 600 - w + 40, 410), (240, 200, 90, 255), r=8, ow=3)
    return p.done()


def egg_carton():
    p = Pen(320, 150)
    for i in range(4):
        x = 55 + i * 70
        p.poly(blob_pts(x, 60, 30, 42, 1, amp=0, egg=0.13), (255, 248, 236, 255), ow=4)
    p.rect((10, 70, 310, 140), (205, 190, 170, 255), r=10)
    for i in range(3):
        x = 90 + i * 70
        p.line([(x, 78), (x, 132)], (170, 155, 135, 255), 4)
    return p.done()


def rice_bag():
    p = Pen(190, 230)
    p.poly([(30, 30), (160, 30), (175, 215), (15, 215)], (250, 248, 240, 255))
    p.line([(30, 30), (60, 12), (130, 12), (160, 30)], OUT, 5)
    p.rect((35, 85, 155, 160), (90, 170, 120, 255), r=12, ow=4)
    p.text((95, 123), "RIZ", 40, (255, 255, 255, 255))
    return p.done()


def pasta_jar():
    p = Pen(180, 240)
    p.rect((40, 10, 140, 45), (240, 190, 70, 255), r=10)
    p.rect((20, 40, 160, 230), (225, 240, 248, 255), r=26)
    img = p.done()
    rnd = random.Random(3)
    pn = penne().resize((70, 32), Image.LANCZOS)
    for row in range(5):
        for col in range(2):
            s = pn.rotate(rnd.uniform(-30, 30), Image.BICUBIC, expand=True)
            img.alpha_composite(s, (35 + col * 55 + rnd.randint(-5, 5), 70 + row * 30))
    gl = Pen(180, 240)
    gl.line([(38, 70), (38, 200)], (255, 255, 255, 200), 8)
    img.alpha_composite(gl.done())
    return img


def can(color):
    p = Pen(130, 170)
    p.rect((12, 20, 118, 160), color, r=10)
    p.rect((12, 60, 118, 120), (255, 255, 255, 255), r=0, ow=4)
    p.ell((12, 8, 118, 34), (205, 210, 220, 255), ow=4)
    p.ell((40, 74, 90, 106), color, ow=0)
    return p.done()


def speech_bubble():
    p = Pen(460, 380)
    p.poly([(120, 290), (90, 370), (200, 290)], (255, 255, 255, 255), ow=0)
    p.rect((10, 10, 450, 300), (255, 255, 255, 255), r=60, ow=7)
    p.line([(120, 296), (90, 370), (200, 300)], OUT, 7)
    p.rect((112, 280, 205, 300), (255, 255, 255, 255), r=0, ow=0)
    return p.done()


def subscribe_btn():
    p = Pen(620, 170)
    p.rect((10, 10, 610, 160), (255, 60, 100, 255), r=75, ow=6)
    # cloche
    p.poly([(90, 55), (120, 45), (150, 55), (160, 115), (80, 115)], (255, 255, 255, 255), ow=0)
    p.ell((105, 112, 135, 135), (255, 255, 255, 255), ow=0)
    p.text((380, 87), "S'abonner", 64, (255, 255, 255, 255))
    return p.done()


def soft_dot(r, color=(255, 255, 255), a=255):
    mask = Image.new("L", (r * 4, r * 4), 0)
    ImageDraw.Draw(mask).ellipse((r, r, r * 3, r * 3), fill=a)
    img = Image.new("RGBA", mask.size, color + (0,))
    img.putalpha(mask.filter(ImageFilter.GaussianBlur(r * 0.45)))
    return img


# ---------- texte ----------
def wrap(text, font, maxw):
    d = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    lines, cur = [], ""
    for w in text.split(" "):
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= maxw:
            cur = t
        else:
            lines.append(cur); cur = w
    lines.append(cur)
    return lines


def bubble(text, size, fg, bg, maxw=900, pad=(38, 22), radius=40, shadow=True, one_line=False):
    for p in "!?:;":
        text = text.replace(" " + p, "\u00a0" + p)
    f = ImageFont.truetype(FONT, size)
    if one_line:
        dd0 = ImageDraw.Draw(Image.new("RGB", (1, 1)))
        while size > 40 and dd0.textlength(text, font=f) > maxw - 2 * pad[0]:
            size -= 2; f = ImageFont.truetype(FONT, size)
    lines = wrap(text, f, maxw - 2 * pad[0])
    d = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    tw = max(d.textlength(l, font=f) for l in lines)
    lh = int(size * 1.22)
    bw, bh = int(tw + 2 * pad[0]), lh * len(lines) + 2 * pad[1]
    sh = 24
    img = Image.new("RGBA", (bw + 2 * sh, bh + 2 * sh), (0, 0, 0, 0))
    if shadow:
        s = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(s).rounded_rectangle((sh, sh + 8, sh + bw, sh + bh + 8), radius, fill=(0, 0, 0, 55))
        img.alpha_composite(s.filter(ImageFilter.GaussianBlur(9)))
    dd = ImageDraw.Draw(img)
    dd.rounded_rectangle((sh, sh, sh + bw, sh + bh), radius, fill=bg)
    for i, l in enumerate(lines):
        x = sh + (bw - dd.textlength(l, font=f)) / 2
        dd.text((x, sh + pad[1] + i * lh + (lh - size) * 0.3), l, font=f, fill=fg)
    return img


# ---------- animation ----------
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_back(x, c1=1.70158):
    c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def ease_out(x):
    return 1 - (1 - x) ** 3


def ease_in(x):
    return x ** 3


def put(cv, spr, cx, cy, s=1.0, rot=0.0, a=1.0):
    if s <= 0.02 or a <= 0.02:
        return
    if abs(s - 1) > 0.003:
        spr = spr.resize((max(1, int(spr.width * s)), max(1, int(spr.height * s))), Image.BILINEAR)
    if abs(rot) > 0.2:
        spr = spr.rotate(rot, Image.BILINEAR, expand=True)
    al = spr.getchannel("A")
    if a < 0.999:
        al = al.point(lambda v: int(v * a))
    cv.paste(spr, (int(cx - spr.width / 2), int(cy - spr.height / 2)), al)


def pop(cv, spr, x, y, t, tin, tout=None, scale=1.0, phase=0.0, float_amp=10, spin=-12):
    """Apparition avec rebond, flottement léger, sortie en fondu."""
    if t < tin:
        return
    p = clamp((t - tin) / 0.55)
    s = ease_back(p) * scale
    a = clamp(p * 3)
    rot = spin * (1 - ease_out(p)) + 2.5 * math.sin(t * 1.7 + phase)
    dy = float_amp * math.sin(t * 2.1 + phase)
    if tout is not None and t > tout:
        q = ease_in(clamp((t - tout) / 0.35))
        s *= 1 - 0.5 * q; a *= 1 - q; dy -= 120 * q
    put(cv, spr, x, y + dy, s, rot, a)


def gradient(c1, c2):
    y = np.linspace(0, 1, H)[:, None, None]
    arr = (np.array(c1)[None, None, :] * (1 - y) + np.array(c2)[None, None, :] * y)
    arr = np.repeat(arr, W, axis=1).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


class Background:
    def __init__(self, c1, c2, seed):
        self.base = gradient(c1, c2)
        rnd = random.Random(seed)
        self.big = soft_dot(170, a=60)
        self.small = soft_dot(14, a=150)
        self.blobs = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(0.6, 1.3), rnd.uniform(0, 6.28)) for _ in range(6)]
        self.dots = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(0.5, 1.4), rnd.uniform(20, 70)) for _ in range(22)]

    def frame(self, t):
        cv = self.base.copy()
        for x, y, s, ph in self.blobs:
            put(cv, self.big, x + 60 * math.sin(t * 0.4 + ph), y + 50 * math.cos(t * 0.35 + ph), s)
        for x, y, s, sp in self.dots:
            put(cv, self.small, x, (y - t * sp) % (H + 80) - 40, s, a=0.8)
        return cv


STEAM = None


def steam(cv, cx, cy, t, width=200, n=6):
    global STEAM
    if STEAM is None:
        STEAM = soft_dot(34, a=200)
    for i in range(n):
        ph = (t * 0.55 + i / n) % 1.0
        x = cx + (i - n / 2 + 0.5) * width / n + 18 * math.sin(t * 2 + i)
        put(cv, STEAM, x, cy - ph * 260, 0.6 + ph * 0.9, a=math.sin(ph * math.pi) * 0.85)


def circle_wipe(cv, t_local, dur, color, mode):
    """mode 'in' : le disque grandit (fin de carte) ; 'out' : il se rétracte (début de carte)."""
    R = 2300
    d = ImageDraw.Draw(cv)
    if mode == "in":
        r = R * ease_in(clamp(t_local / dur))
        cx, cy = W * 0.15, H * 0.9
    else:
        r = R * (1 - ease_out(clamp(t_local / dur)))
        cx, cy = W * 0.85, H * 0.1
    if r > 2:
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color)


def render_segment(path, dur, frame_fn):
    n = int(round(dur * FPS))
    pr = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                           "-crf", "18", "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    for i in range(n):
        pr.stdin.write(frame_fn(i / FPS).tobytes())
    pr.stdin.close(); pr.wait()


def concat(parts, final, dur=60):
    lst = final + ".txt"
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
                    "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-t", str(dur), "-movflags", "+faststart", final], check=True)


def cover_fill(img, w, h):
    s = max(w / img.width, h / img.height)
    im = img.resize((int(img.width * s + 1), int(img.height * s + 1)), Image.BILINEAR)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))
