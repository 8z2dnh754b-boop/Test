"""Télécharge des aperçus Pexels (sans clé) et fait une planche contact numérotée. Écarte les numéros déjà utilisés."""
import sys, os, subprocess
from PIL import Image, ImageDraw, ImageFont
used = set(open(os.path.join(os.path.dirname(__file__), "../data/pexels_photos_utilisees.txt")).read().split())
out = sys.argv[1]; ids = sys.argv[2:]
os.makedirs(out, exist_ok=True)
ok = []
for i in ids:
    if i in used:
        print("DÉJÀ UTILISÉE", i); continue
    f = os.path.join(out, f"{i}.jpg")
    if not os.path.exists(f):
        subprocess.run(["curl", "-sSf", "-o", f, f"https://images.pexels.com/photos/{i}/pexels-photo-{i}.jpeg?auto=compress&w=400"])
    if os.path.exists(f) and os.path.getsize(f) > 1000:
        ok.append(i)
    else:
        print("ÉCHEC", i)
cols = 6; tw, th = 300, 300
sheet = Image.new("RGB", (cols * tw, ((len(ok) + cols - 1) // cols) * th), "white")
font = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf", 26)
for k, i in enumerate(ok):
    im = Image.open(os.path.join(out, f"{i}.jpg")).convert("RGB"); im.thumbnail((tw - 6, th - 6))
    x, y = (k % cols) * tw, (k // cols) * th
    sheet.paste(im, (x + 3, y + 3))
    ImageDraw.Draw(sheet).text((x + 8, y + 6), i, font=font, fill="yellow", stroke_width=3, stroke_fill="black")
sheet.save(os.path.join(out, "planche.jpg"), quality=85)
print("ok:", len(ok))
