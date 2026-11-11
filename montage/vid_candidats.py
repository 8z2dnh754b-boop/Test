"""Vidéos Pexels sans clé : écarte les numéros déjà utilisés, trouve le fichier, prend 2 images de contrôle, fait une planche."""
import sys, os, subprocess, json
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
used = set(open(os.path.join(HERE, "../data/pexels_videos_utilisees.txt")).read().split())
SIZES = ["hd_1080_1920", "uhd_2160_3840", "uhd_1440_2560", "hd_720_1280", "uhd_3840_2160", "uhd_4096_2160", "uhd_2560_1440",
         "hd_1920_1080", "hd_2048_1080", "hd_1280_720", "sd_960_540", "sd_640_360", "sd_540_960", "sd_360_640"]
FPS = [25, 30, 24, 60, 50, 29, 23, 59]

def head(u):
    return subprocess.run(["curl", "-sI", "-o", "/dev/null", "-w", "%{http_code}", u], capture_output=True, text=True).stdout == "200"

PREVIEW = ["sd_640_360", "sd_360_640", "sd_960_540", "sd_540_960", "sd_506_960", "sd_640_338", "hd_1280_720", "hd_720_1280"] + SIZES

def find(vid, order=None):
    for s in (order or SIZES):
        for f in FPS:
            u = f"https://videos.pexels.com/video-files/{vid}/{vid}-{s}_{f}fps.mp4"
            if head(u):
                return u
    return None

def probe(u):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=width,height", "-of", "json", u], capture_output=True, text=True)
    j = json.loads(r.stdout or "{}")
    st = [s for s in j.get("streams", []) if "width" in s][0]
    return float(j["format"]["duration"]), st["width"], st["height"]

def grab(u, t, out):
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(t), "-i", u, "-frames:v", "1", "-vf", "scale=320:-2", out])

def work(vid, outdir):
    if vid in used:
        return vid, None, "DÉJÀ UTILISÉE"
    u = find(vid, PREVIEW)
    if not u:
        return vid, None, "introuvable"
    loc = os.path.join(outdir, f"{vid}.mp4")
    if not os.path.exists(loc):
        subprocess.run(["curl", "-sSf", "-o", loc, u])
    try:
        d, w, h = probe(loc)
    except Exception as e:
        return vid, None, f"erreur {e}"
    u = loc
    fs = []
    for k, t in enumerate((d * 0.2, d * 0.7)):
        f = os.path.join(outdir, f"{vid}_{k}.jpg"); grab(u, t, f); fs.append(f)
    return vid, (u, d, w, h, fs), "ok"

if __name__ == "__main__":
    outdir = sys.argv[1]; os.makedirs(outdir, exist_ok=True)
    ids = list(dict.fromkeys(sys.argv[2:]))
    with ThreadPoolExecutor(8) as ex:
        res = list(ex.map(lambda v: work(v, outdir), ids))
    cache = os.path.join(HERE, "../data/pexels_video_urls.json")
    db = json.load(open(cache)) if os.path.exists(cache) else {}
    ok = []
    for vid, info, st in res:
        if info:
            ok.append((vid, info))
            print(vid, f"{info[2]}x{info[3]}", f"{info[1]:.0f}s")
        else:
            print(vid, st)
    json.dump(db, open(cache, "w"), indent=0)
    tw, th, cols = 340, 260, 4
    font = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf", 22)
    sheet = Image.new("RGB", (cols * tw * 2 // 2 * 2 // 2 * 1 + 0 if False else cols * 2 * 170, ((len(ok) + cols - 1) // cols) * 200), "white")
    for k, (vid, info) in enumerate(ok):
        x, y = (k % cols) * 340, (k // cols) * 200
        for j, f in enumerate(info[4]):
            if os.path.exists(f):
                im = Image.open(f); im.thumbnail((166, 196)); sheet.paste(im, (x + j * 170, y + 2))
        ImageDraw.Draw(sheet).text((x + 4, y + 4), f"{vid} {'V' if info[3] > info[2] else 'H'}", font=font, fill="yellow", stroke_width=3, stroke_fill="black")
    sheet.save(os.path.join(outdir, "planche.jpg"), quality=85)
