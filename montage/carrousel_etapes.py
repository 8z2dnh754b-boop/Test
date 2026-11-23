"""Page « étapes » pour carrousel Instagram (1080 x 1350), style élégant : fond crème, titres bordeaux,
6 vraies photos Pexels avec leur texte. Usage : python3 carrousel_etapes.py sortie.png"""
import os, sys, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1350
CREME, BORDEAUX, OR, TEXTE = (246, 239, 227), (110, 22, 32), (176, 141, 72), (55, 40, 35)
F = "/usr/share/fonts/truetype/liberation/LiberationSerif-"
PHOTOS = os.path.abspath(os.path.join(os.path.dirname(__file__), "../videos/carrousels/photos"))

TITRE = "Bûche chocolat pas chère"
SOUS_TITRE = "LES SIX ÉTAPES"
ETAPES = [  # (titre, texte, id Pexels, focale x, focale y)
    ("1. Fouetter", "4 œufs et 100 g de sucre, 5 min, jusqu'à ce que ça blanchisse.", 4099123, .5, .45),
    ("2. Tamiser", "70 g de farine et 30 g de cacao, puis mélanger doucement.", 8176584, .5, .55),
    ("3. Cuire", "Étaler sur une plaque avec papier cuisson. 10 min à 180 °C.", 7965956, .5, .5),
    ("4. La crème", "150 g de chocolat fondu dans 20 cl de crème chaude. Laisser refroidir.", 691168, .5, .5),
    ("5. Rouler", "Étaler la crème sur le biscuit tiède et rouler serré. 2 h au frais.", 19898618, .5, .5),
    ("6. Décorer", "Un voile de cacao et quelques rosaces de crème fouettée.", 30372662, .45, .5),
]
ASTUCE = ("Le bon geste", "Roule le biscuit encore tiède : froid, il casse.")
SIGNATURE = "On mange quoi ce soir ?"


def font(style, size):
    return ImageFont.truetype(F + style + ".ttf", size)


def fetch(pid):
    f = os.path.join(PHOTOS, f"{pid}.jpg")
    if not os.path.exists(f):
        os.makedirs(PHOTOS, exist_ok=True)
        subprocess.run(["curl", "-sSf", "-o", f,
                        f"https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg?auto=compress&cs=tinysrgb&w=1200"], check=True)
    return Image.open(f).convert("RGB")


def cover(img, w, h, fx, fy):
    s = max(w / img.width, h / img.height)
    im = img.resize((int(img.width * s + 1), int(img.height * s + 1)), Image.LANCZOS)
    x = int(max(0, min(im.width - w, fx * im.width - w / 2)))
    y = int(max(0, min(im.height - h, fy * im.height - h / 2)))
    return im.crop((x, y, x + w, y + h))


def wrap(d, text, f, maxw):
    lines, cur = [], ""
    for w in text.split(" "):
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw:
            cur = t
        else:
            lines.append(cur); cur = w
    return lines + [cur]


def centre(d, y, text, f, fill, x0=0, x1=W):
    d.text(((x0 + x1 - d.textlength(text, font=f)) / 2, y), text, font=f, fill=fill)


def filet(d, y, text_w, cx=W // 2, marge=40, long=230):
    d.line((cx - text_w / 2 - marge - long, y, cx - text_w / 2 - marge, y), fill=OR, width=2)
    d.line((cx + text_w / 2 + marge, y, cx + text_w / 2 + marge + long, y), fill=OR, width=2)


def main(out):
    img = Image.new("RGB", (W, H), CREME)
    # léger grain papier
    noise = Image.effect_noise((W, H), 10).convert("L").filter(ImageFilter.GaussianBlur(0.6))
    img = Image.composite(img, Image.new("RGB", (W, H), (236, 226, 208)), noise.point(lambda v: 255 if v > 120 else 225))
    d = ImageDraw.Draw(img)

    ft = font("Bold", 74)
    centre(d, 34, TITRE, ft, BORDEAUX)
    fs = font("Regular", 30)
    sw = d.textlength(" ".join(SOUS_TITRE), font=fs)
    centre(d, 128, " ".join(SOUS_TITRE), fs, BORDEAUX)
    filet(d, 146, sw)

    cols, mx, gap = 2, 44, 28
    cw = (W - 2 * mx - gap) // cols
    ph, top, rowh = 200, 188, 334
    fe, fx = font("BoldItalic", 34), font("Regular", 23)
    for k, (t, txt, pid, fxx, fyy) in enumerate(ETAPES):
        c, r = k % cols, k // cols
        x, y = mx + c * (cw + gap), top + r * rowh
        photo = cover(fetch(pid), cw, ph, fxx, fyy)
        mask = Image.new("L", (cw, ph), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, cw - 1, ph - 1), 14, fill=255)
        img.paste(photo, (x, y), mask)
        d.text((x + 4, y + ph + 8), t, font=fe, fill=BORDEAUX)
        for i, line in enumerate(wrap(d, txt, fx, cw - 8)[:2]):
            d.text((x + 4, y + ph + 50 + i * 27), line, font=fx, fill=TEXTE)
    # séparateurs fins
    for r in range(1, 3):
        yy = top + r * rowh - 13
        d.line((mx, yy, W - mx, yy), fill=OR + (0,), width=1)
    

    # encadré astuce
    by = top + 3 * rowh + 2
    d.rounded_rectangle((90, by, W - 90, by + 92), 14, outline=OR, width=2)
    centre(d, by + 8, ASTUCE[0], font("BoldItalic", 36), BORDEAUX)
    centre(d, by + 52, ASTUCE[1], font("Italic", 27), TEXTE)

    fsig = font("Italic", 32)
    sgw = d.textlength(SIGNATURE, font=fsig)
    centre(d, H - 58, SIGNATURE, fsig, BORDEAUX)
    filet(d, H - 38, sgw, long=200)
    img.save(out, quality=95)
    print(out)


if __name__ == "__main__":
    main(sys.argv[1])
