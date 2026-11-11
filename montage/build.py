"""Montage 60 s, 1080x1920 : 8 cartes de texte, une vidéo de fond par carte.
Usage : python3 build.py <dossier_video>   (le dossier contient spec.json et bg/carteN.mp4)
"""
import json, subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
TIMES = [0, 4.5, 12, 19.5, 27, 34.5, 42.5, 51, 60]
FONTS = {
    "inter": ("/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf", True),
    "times": ("/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf", False),
}

def find_font(path):
    if os.path.exists(path):
        return path
    out = subprocess.run(["fc-match", "-f", "%{file}", "Inter:extrabold"], capture_output=True, text=True).stdout
    return out

def wrap(draw, text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= maxw:
            cur = t
        else:
            lines.append(cur); cur = w
    lines.append(cur)
    return lines

def card_png(card, style, path):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fpath, stroke = FONTS[style]
    fpath = find_font(fpath)
    blocks = []  # (lignes, police, couleur, espace_après)
    if card.get("titre"):
        f = ImageFont.truetype(fpath, 92)
        blocks.append((wrap(d, card["titre"], f, W - 140), f, (255, 214, 0), 60))
    f = ImageFont.truetype(fpath, 68)
    for phrase in card.get("phrases", []):
        blocks.append((wrap(d, phrase, f, W - 140), f, (255, 255, 255), 34))
    total = sum(len(l) * int(fo.size * 1.22) + gap for l, fo, c, gap in blocks) - blocks[-1][3]
    y = (H - total) // 2
    for lines, fo, color, gap in blocks:
        for line in lines:
            tw = d.textlength(line, font=fo)
            d.text(((W - tw) / 2, y), line, font=fo, fill=color,
                   stroke_width=7 if stroke else 0, stroke_fill=(0, 0, 0))
            y += int(fo.size * 1.22)
        y += gap
    img.save(path)

def main(folder):
    spec = json.load(open(os.path.join(folder, "spec.json"), encoding="utf-8"))
    style = spec.get("police", "inter")
    tmp = os.path.join(folder, "tmp"); os.makedirs(tmp, exist_ok=True)
    parts = []
    for i, card in enumerate(spec["cartes"]):
        dur = TIMES[i + 1] - TIMES[i]
        png = os.path.join(tmp, f"t{i+1}.png"); card_png(card, style, png)
        bg = os.path.join(folder, "bg", f"carte{i+1}.mp4")
        src = ["-stream_loop", "-1", "-i", bg] if os.path.exists(bg) else \
              ["-f", "lavfi", "-i", f"color=c=0x{card.get('test_color','4a7a9c')}:s={W}x{H}:r=30"]
        out = os.path.join(tmp, f"p{i+1}.mp4"); parts.append(out)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *src, "-loop", "1", "-i", png,
            "-filter_complex",
            f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps=30,setsar=1[b];"
            f"[1:v]format=rgba,fade=in:st=0:d=0.3:alpha=1[t];[b][t]overlay=0:0:shortest=1,format=yuv420p",
            "-t", f"{dur}", "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "20", out], check=True)
    lst = os.path.join(tmp, "list.txt")
    open(lst, "w").write("".join(f"file '{os.path.abspath(p)}'\n" for p in parts))
    final = os.path.join(folder, spec["fichier"])
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-map", "0:v", "-map", "1:a",
        "-c:v", "copy", "-c:a", "aac", "-t", "60", "-movflags", "+faststart", final], check=True)
    print(final)

if __name__ == "__main__":
    main(sys.argv[1])
