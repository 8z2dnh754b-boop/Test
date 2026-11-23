"""On mange quoi ce soir ? — « Le gratin de pâtes avec les restes » (version plus accrocheuse).
Vraies vidéos Pexels + vraies photos Pexels animées quand aucune vidéo libre n'existe.
Nouveautés : phrase d'accroche immédiate, barre de progression, mots clés en couleur, plans plus courts.
Usage : python3 omc03_gratin.py dossier_sortie [numéros de cartes]"""
import os, sys, subprocess
from multiprocessing import Pool
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import mlib as M

W, H, FPS = M.W, M.H, M.FPS
BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../videos/omc-03-gratin-restes"))
TIMES = [0, 4.5, 12, 19.5, 27, 34.5, 42.5, 51, 60]
COLORS = [(214, 48, 49), (230, 110, 0), (46, 125, 50), (0, 120, 150), (190, 120, 0), (205, 70, 20), (120, 60, 160), (214, 48, 49)]
# Mots entre [crochets] = mots clés en couleur. Plan : ("v", id vidéo, début, focale x) ou ("p", id photo, focale x, focale y)
CARDS = [
    ("Ne jette plus tes restes de pâtes !", [
        ("Ce soir, ils deviennent un [gratin doré].", [("p", 6163259, .5, .5)])]),
    ("1. Fouille le frigo", [
        ("Les [pâtes d'hier] et ce qui traîne.", [("v", 5993519, 0.5, .5)]),
        ("Un reste de [saucisse], en rondelles.", [("v", 4311640, 2.0, .5)])]),
    ("2. Les champignons", [
        ("Quelques [champignons]…", [("v", 3196463, 1.0, .5)]),
        ("…coupés en [lamelles].", [("v", 3209212, 1.0, .5)])]),
    ("3. La sauce", [
        ("Casse [2 œufs] dans un bol.", [("v", 8064837, 0.5, .5)]),
        ("Ajoute [20 cl de lait], sel, poivre.", [("v", 6949455, 3.0, .5)])]),
    ("4. Fromage et four", [
        ("Du [fromage râpé] par-dessus.", [("p", 4518841, .5, .35)]),
        ("Le four à [200 °C].", [("p", 7525215, .6, .5)])]),
    ("5. Au four", [
        ("[25 minutes], jusqu'à ce que ça dore.", [("p", 7669757, .55, .5)]),
        ("Et voilà un [gratin tout doré] !", [("p", 37448233, .5, .5)])]),
    ("L'astuce", [
        ("Fais-en plus : il se [réchauffe très bien] le lendemain.", [("p", 9475696, .5, .6)])]),
    ("Tu le testes ce soir ?", [
        ("Dis-le-moi en [commentaire] !", [("p", 5082865, .5, .5), ("v", 7556433, 1.0, .5)]),
        ("[Enregistre] la vidéo pour ne pas l'oublier.", [("v", 13929582, 0.5, .5)])]),
]
WIPE, SLIDE = 0.4, 0.35
FONT = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"


def probe(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                        "-of", "csv=p=0", f], capture_output=True, text=True).stdout.strip().split(",")
    return int(r[0]), int(r[1])


def framed(img, age):
    """Image horizontale : cadre arrondi au centre, sur un fond flouté de la même image (pas assombri)."""
    z = 1.0 + 0.06 * min(1.0, age / 8.0)
    small = img.resize((max(1, img.width // 8), max(1, img.height // 8)), Image.BILINEAR).filter(ImageFilter.GaussianBlur(3))
    bg = M.cover_fill(small, W, H)
    fw = int(1000 * z); fh = int(round(img.height * fw / img.width))
    fr = img.resize((fw, fh), Image.BILINEAR)
    mask = Image.new("L", (fw, fh), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, fw - 1, fh - 1), 36, fill=255)
    cy = 860
    sh = Image.new("L", (fw + 80, fh + 80), 0)
    ImageDraw.Draw(sh).rounded_rectangle((40, 52, fw + 40, fh + 52), 40, fill=110)
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    bg.paste((0, 0, 0), ((W - fw) // 2 - 40, cy - fh // 2 - 40), sh)
    bg.paste(fr, ((W - fw) // 2, cy - fh // 2), mask)
    return bg


class VideoShot:
    def __init__(self, vid, start, fx):
        f = os.path.join(BASE, "clips", f"{vid}.mp4")
        w, h = probe(f)
        self.fr = w > h and w < 3000
        if self.fr:
            vf, self.size = "scale=1000:-2,fps=30", (1000, int(round(1000 * h / w / 2)) * 2)
        else:
            vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}:(iw-{W})*{fx}:(ih-{H})/2,fps=30"
            self.size = (W, H)
        self.p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-ss", str(start), "-stream_loop", "-1", "-i", f,
                                   "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
        self.last = None

    def render(self, age):
        n = self.size[0] * self.size[1] * 3
        b = self.p.stdout.read(n)
        if len(b) == n:
            self.last = Image.frombuffer("RGB", self.size, b)
        img = self.last
        if self.fr:
            return framed(img, age)
        z = 1.0 + 0.06 * min(1.0, age / 8.0)
        cw, ch = int(W / z), int(H / z)
        return img.crop(((W - cw) // 2, (H - ch) // 2, (W + cw) // 2, (H + ch) // 2)).resize((W, H), Image.BILINEAR)

    def close(self):
        self.p.kill()


class PhotoShot:
    """Vraie photo animée : zoom lent et léger glissement (Ken Burns)."""
    def __init__(self, pid, fx, fy):
        self.img = Image.open(os.path.join(BASE, "photos", f"{pid}.jpg")).convert("RGB")
        self.fx, self.fy = fx, fy
        self.land = self.img.width > self.img.height * 1.05
        if not self.land:
            s = max(W * 1.15 / self.img.width, H * 1.15 / self.img.height)
            self.big = self.img.resize((int(self.img.width * s), int(self.img.height * s)), Image.LANCZOS)
        else:
            self.small = self.img.resize((1200, int(1200 * self.img.height / self.img.width)), Image.LANCZOS)

    def render(self, age):
        if self.land:
            return framed(self.small, age)
        q = min(1.0, age / 7.0)
        z = 1.0 + 0.12 * q
        cw, ch = int(self.big.width / 1.15 / z * 1.0), int(self.big.height / 1.15 / z)
        cw, ch = int(W * self.big.width / (W * 1.15) / z), int(H * self.big.height / (H * 1.15) / z)
        cw = min(cw, self.big.width); ch = min(ch, self.big.height)
        # garder le ratio 9:16
        if cw / ch > W / H:
            cw = int(ch * W / H)
        else:
            ch = int(cw * H / W)
        cx = self.fx * self.big.width + (q - 0.5) * 40
        cy = self.fy * self.big.height
        x = int(max(0, min(self.big.width - cw, cx - cw / 2)))
        y = int(max(0, min(self.big.height - ch, cy - ch / 2)))
        return self.big.crop((x, y, x + cw, y + ch)).resize((W, H), Image.BILINEAR)

    def close(self):
        pass


def make(spec):
    return VideoShot(*spec[1:]) if spec[0] == "v" else PhotoShot(*spec[1:])


def bubble_hl(text, size, fg, accent, bg=(255, 255, 255, 255), maxw=920, pad=(38, 22), radius=40):
    """Bulle blanche ; les mots entre [crochets] sont en couleur."""
    for p in "!?:;":
        text = text.replace(" " + p, " " + p)
    toks = []
    hl = False
    for part in text.replace("[", "\x01[").replace("]", "]\x01").split("\x01"):
        if not part:
            continue
        on = part.startswith("[")
        for j, w in enumerate(part.strip("[]").split(" ")):
            if w:
                glue = j == 0 and not part.startswith((" ", "[")) and bool(toks) and w[0] in ".,!?…:;\u00a0"
                toks.append((w, on, glue))
    f = ImageFont.truetype(FONT, size)
    d = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    sp = d.textlength(" ", font=f)
    lines, cur, cw = [], [], 0
    for w, on, glue in toks:
        tw = d.textlength(w, font=f)
        gap = 0 if (glue or not cur) else sp
        if cur and not glue and cw + sp + tw > maxw - 2 * pad[0]:
            lines.append((cur, cw)); cur, cw, gap = [], 0, 0
        cw = cw + gap + tw
        cur.append((w, on, tw, gap))
    lines.append((cur, cw))
    lh = int(size * 1.22)
    bw = int(max(c for _, c in lines) + 2 * pad[0]); bh = lh * len(lines) + 2 * pad[1]
    sh = 24
    img = Image.new("RGBA", (bw + 2 * sh, bh + 2 * sh), (0, 0, 0, 0))
    s = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(s).rounded_rectangle((sh, sh + 8, sh + bw, sh + bh + 8), radius, fill=(0, 0, 0, 55))
    img.alpha_composite(s.filter(ImageFilter.GaussianBlur(9)))
    dd = ImageDraw.Draw(img)
    dd.rounded_rectangle((sh, sh, sh + bw, sh + bh), radius, fill=bg)
    for i, (ws, c) in enumerate(lines):
        x = sh + (bw - c) / 2
        y = sh + pad[1] + i * lh + (lh - size) * 0.3
        for w, on, tw, gap in ws:
            x += gap
            dd.text((x, y), w, font=f, fill=accent if on else fg)
            x += tw
    return img


def progress(cv, t):
    d = ImageDraw.Draw(cv)
    d.rounded_rectangle((40, 40, W - 40, 52), 6, fill=(255, 255, 255))
    d.rounded_rectangle((40, 40, 40 + max(12, int((W - 80) * t / 60.0)), 52), 6, fill=(214, 48, 49))


def make_card(i):
    dur = TIMES[i + 1] - TIMES[i]
    acc = COLORS[i]
    title, items = CARDS[i]
    hook = i == 0
    t_img = M.bubble(title, 86 if hook else 74, (255, 255, 255), acc + (255,), maxw=1010, radius=50, one_line=not hook)
    p_imgs = [bubble_hl(p, 58 if hook else 56, (35, 35, 35), acc) for p, _ in items]
    pt = [0.0 if hook else 0.5] if len(items) == 1 else [0.5, round(dur * 0.5, 2)]
    # plans : chaque phrase a ses plans, répartis sur sa durée
    shots = []
    for k, (_, specs) in enumerate(items):
        t0 = 0.0 if k == 0 else pt[k]
        t1 = dur if k == len(items) - 1 else pt[k + 1]
        for j, sp in enumerate(specs):
            shots.append((t0 + (t1 - t0) * j / len(specs), sp))
    live = [None] * len(shots)

    def frame(t):
        cur = max(k for k, (st, _) in enumerate(shots) if t >= st)
        st = shots[cur][0]
        layers = [(cur - 1, 0)] if cur > 0 and t - st < SLIDE else []
        layers.append((cur, 1))
        cv = None
        for k, _ in layers:
            if live[k] is None:
                live[k] = make(shots[k][1])
            img = live[k].render(t - shots[k][0])
            if cv is None:
                cv = img.copy()
            else:
                q = M.ease_out(M.clamp((t - st) / SLIDE))
                cv.paste(img, (int((1 - q) * W), 0))
        if cur > 0 and live[cur - 1] and t - st >= SLIDE:
            live[cur - 1].close(); live[cur - 1] = None
        tp = 1.0 if hook else M.clamp((t - 0.1) / 0.6)
        if hook:  # accroche : le titre est là dès la 1re image, avec un léger battement
            s = 1.0 + 0.04 * abs(((t * 2.2) % 2) - 1)
            M.put(cv, t_img, 540, 330, s, 0, 1)
        elif tp > 0:
            M.put(cv, t_img, 540, 250 - 160 * (1 - M.ease_back(tp)), 1, 0, M.clamp(tp * 2.5))
        y = 1330
        for img, tk in zip(p_imgs, pt):
            h = img.height - 30
            if t >= tk:
                q = 1.0 if (hook and tk == 0) else M.clamp((t - tk) / 0.45)
                M.put(cv, img, 540, y + h / 2 + 50 * (1 - M.ease_out(q)), 0.7 + 0.3 * M.ease_back(q), 0, M.clamp(q * 2.5))
            y += h + 10
        progress(cv, TIMES[i] + t)
        if i > 0 and t < WIPE:
            M.circle_wipe(cv, t, WIPE, COLORS[i], "out")
        if i < 7 and t > dur - WIPE:
            M.circle_wipe(cv, t - (dur - WIPE), WIPE, COLORS[i + 1], "in")
        return cv

    out = sys.argv[1]
    if os.environ.get("STILLS"):
        ts = [float(x) for x in os.environ["STILLS"].split(",")]
        n = 0
        for fno in range(int(dur * FPS)):
            t = fno / FPS
            img = frame(t)
            if any(abs(t - x) < 0.5 / FPS for x in ts):
                img.resize((360, 640)).save(os.path.join(out, f"still_c{i+1}_{n}.png")); n += 1
        for c in live:
            if c: c.close()
        return None
    path = os.path.abspath(os.path.join(out, f"part{i + 1}.mp4"))
    M.render_segment(path, dur, frame)
    for c in live:
        if c: c.close()
    return path


if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    only = [int(a) for a in sys.argv[2:]] or list(range(8))
    with Pool(4) as pool:
        parts = pool.map(make_card, only)
    if len(only) == 8 and not os.environ.get("STILLS"):
        final = os.path.abspath(os.path.join(out, "omc-03-gratin-restes.mp4"))
        M.concat(parts, final)
        print(final)
