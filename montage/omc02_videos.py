"""On mange quoi ce soir ? — « 5 dîners express », montage en vraies vidéos Pexels (style After Effects).
Une séquence par phrase. Vidéos verticales ou 4K : plein écran recadré. Vidéos HD horizontales : cadre arrondi
au centre sur un fond flouté de la même vidéo (pas assombri)."""
import os, sys, subprocess
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import mlib as M

W, H, FPS = M.W, M.H, M.FPS
CLIPS = os.path.abspath(os.path.join(os.path.dirname(__file__), "../videos/omc-02-5-diners-express/clips"))
TIMES = [0, 4.5, 12, 19.5, 27, 34.5, 42.5, 51, 60]
COLORS = [(230, 81, 0), (205, 110, 0), (190, 40, 40), (0, 125, 138), (175, 95, 10), (220, 90, 0), (46, 125, 50), (170, 25, 90)]
# (titre, [(phrase, id vidéo, début dans la vidéo, focale x)])
CARDS = [
    ("5 dîners express", [("Quand on n'a pas le temps de cuisiner.", 7423603, 2.0, .5)]),
    ("1. Œufs brouillés", [("Bats quelques œufs dans un bol.", 8051989, 1.0, .5),
                           ("5 minutes à la poêle, c'est prêt !", 13324080, 1.0, .5)]),
    ("2. Pâtes au fromage", [("Les pâtes dans l'eau bouillante.", 6289336, 0.5, .5),
                             ("Du fromage râpé par-dessus.", 3195970, 1.0, .5)]),
    ("3. Riz aux petits pois", [("Un bol de riz.", 1841002, 1.0, .62),
                                ("Des petits pois et des légumes à la poêle.", 4398966, 0.5, .5)]),
    ("4. Croque-monsieur", [("Pain, jambon et fromage qui fond.", 4584746, 0.5, .4),
                              ("Quelques minutes au four, et on surveille.", 5309777, 1.0, .5)]),
    ("5. Salade de carottes", [("Des carottes coupées en rondelles.", 5645055, 3.0, .5),
                               ("Des tomates cerises, et c'est prêt.", 5645056, 3.0, .5)]),
    ("L'astuce", [("Garde toujours au placard :", 8580856, 1.0, .5),
                  ("des bocaux de céréales et de légumes secs.", 8581284, 0.5, .5)]),
    ("Lequel tu fais ce soir ?", [("Dis-le-moi en commentaire !", 7976535, 1.0, .45),
                                  ("Abonne-toi pour une idée chaque jour.", 6611945, 0.5, .5)]),
]
END_FAMILY = (3198161, 2.0, .5)  # plan d'ouverture de la dernière carte (titre seul)
WIPE, SLIDE = 0.4, 0.35


def probe(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                        "-of", "csv=p=0", f], capture_output=True, text=True).stdout.strip().split(",")
    return int(r[0]), int(r[1])


class Clip:
    """Lit une vidéo image par image, déjà mise en forme 1080x1920."""
    def __init__(self, vid, start, fx):
        f = os.path.join(CLIPS, f"{vid}.mp4")
        w, h = probe(f)
        self.framed = (w > h and w < 3000)
        if self.framed:
            vf = "scale=1000:-2,fps=30"
        else:
            vf = (f"scale={W}:{H}:force_original_aspect_ratio=increase,"
                  f"crop={W}:{H}:(iw-{W})*{fx}:(ih-{H})/2,fps=30")
        self.p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-ss", str(start), "-stream_loop", "-1", "-i", f,
                                   "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
        if self.framed:
            self.size = (1000, int(round(1000 * h / w / 2)) * 2)
        else:
            self.size = (W, H)
        self.n, self.last = 0, None
        if self.framed:
            mask = Image.new("L", self.size, 0)
            ImageDraw.Draw(mask).rounded_rectangle((0, 0, self.size[0] - 1, self.size[1] - 1), 36, fill=255)
            self.mask = mask

    def read(self):
        b = self.p.stdout.read(self.size[0] * self.size[1] * 3)
        if len(b) == self.size[0] * self.size[1] * 3:
            self.last = Image.frombuffer("RGB", self.size, b)
        self.n += 1
        return self.last

    def render(self, age):
        img = self.read()
        z = 1.0 + 0.06 * min(1.0, age / 8.0)  # zoom avant lent
        if not self.framed:
            cw, ch = int(W / z), int(H / z)
            return img.crop(((W - cw) // 2, (H - ch) // 2, (W + cw) // 2, (H + ch) // 2)).resize((W, H), Image.BILINEAR)
        # fond flouté (même luminosité) + vidéo dans un cadre arrondi avec ombre douce
        small = img.resize((img.width // 8, img.height // 8), Image.BILINEAR).filter(ImageFilter.GaussianBlur(3))
        bg = M.cover_fill(small, W, H)
        fw, fh = int(self.size[0] * z), int(self.size[1] * z)
        fr = img.resize((fw, fh), Image.BILINEAR)
        mask = self.mask.resize((fw, fh), Image.BILINEAR)
        cy = 880
        sh = Image.new("L", (fw + 80, fh + 80), 0)
        ImageDraw.Draw(sh).rounded_rectangle((40, 52, fw + 40, fh + 52), 40, fill=110)
        sh = sh.filter(ImageFilter.GaussianBlur(18))
        bg.paste((0, 0, 0), ((W - fw) // 2 - 40, cy - fh // 2 - 40), sh)
        bg.paste(fr, ((W - fw) // 2, cy - fh // 2), mask)
        return bg

    def close(self):
        self.p.kill()


def make_card(i):
    dur = TIMES[i + 1] - TIMES[i]
    acc = COLORS[i]
    title, items = CARDS[i]
    t_img = M.bubble(title, 74, (255, 255, 255), acc + (255,), maxw=1000, radius=50, one_line=True)
    p_imgs = [M.bubble(p, 56, (35, 35, 35), (255, 255, 255, 255), maxw=920) for p, *_ in items]
    if i == 7:
        pt = [2.8, 5.6]
        shots = [(0.0, END_FAMILY)] + [(pt[k], items[k][1:]) for k in range(2)]
    else:
        pt = [0.6] if len(items) == 1 else [0.6, round(dur * 0.48, 2)]
        shots = [(0.0, items[0][1:])] + ([(pt[1], items[1][1:])] if len(items) > 1 else [])
    clips = [None] * len(shots)

    def frame(t):
        cur = max(k for k, (st, _) in enumerate(shots) if t >= st)
        st = shots[cur][0]
        layers = []
        if cur > 0 and t - st < SLIDE and clips[cur - 1]:
            layers.append((cur - 1, 0))
        layers.append((cur, 1))
        cv = None
        for k, top in layers:
            if clips[k] is None:
                clips[k] = Clip(*shots[k][1])
            img = clips[k].render(t - shots[k][0])
            if cv is None:
                cv = img.copy()
            else:
                q = M.ease_out(M.clamp((t - st) / SLIDE))
                cv.paste(img, (int((1 - q) * W), 0))
        if cur > 0 and clips[cur - 1] and t - st >= SLIDE:
            clips[cur - 1].close(); clips[cur - 1] = None
        tp = M.clamp((t - 0.1) / 0.6)
        if tp > 0:
            M.put(cv, t_img, 540, 250 - 160 * (1 - M.ease_back(tp)), 1, 0, M.clamp(tp * 2.5))
        y = 1300
        for img, tk in zip(p_imgs, pt):
            h = img.height - 30
            if t >= tk:
                q = M.clamp((t - tk) / 0.5)
                M.put(cv, img, 540, y + h / 2 + 50 * (1 - M.ease_out(q)), 0.7 + 0.3 * M.ease_back(q), 0, M.clamp(q * 2.5))
            y += h + 10
        if i > 0 and t < WIPE:
            M.circle_wipe(cv, t, WIPE, COLORS[i], "out")
        if i < 7 and t > dur - WIPE:
            M.circle_wipe(cv, t - (dur - WIPE), WIPE, COLORS[i + 1], "in")
        return cv

    out = sys.argv[1]
    if os.environ.get("STILLS"):
        ts = [float(x) for x in os.environ["STILLS"].split(",")]
        n = 0
        for f in range(int(dur * FPS)):
            t = f / FPS
            img = frame(t)
            if any(abs(t - x) < 0.5 / FPS for x in ts):
                img.resize((540, 960)).save(os.path.join(out, f"still_c{i+1}_{n}.png")); n += 1
        return None
    path = os.path.abspath(os.path.join(out, f"part{i + 1}.mp4"))
    M.render_segment(path, dur, frame)
    for c in clips:
        if c:
            c.close()
    return path


if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    only = [int(a) for a in sys.argv[2:]] or list(range(8))
    with Pool(4) as pool:
        parts = pool.map(make_card, only)
    if len(only) == 8 and not os.environ.get("STILLS"):
        final = os.path.abspath(os.path.join(out, "omc-02-5-diners-express.mp4"))
        M.concat(parts, final)
        print(final)
