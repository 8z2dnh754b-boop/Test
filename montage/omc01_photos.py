"""On mange quoi ce soir ? — « 5 repas rapides et pas chers », version vraies photos Pexels.
Style After Effects : zoom lent (Ken Burns), écrans partagés qui glissent, titres et phrases animés."""
import os, sys, subprocess
from multiprocessing import Pool
from PIL import Image
import mlib as M
from omc01_5_repas import TIMES, COLORS, CARDS, WIPE, phrase_times

W, H = M.W, M.H
PHOTOS = os.path.abspath(os.path.join(os.path.dirname(__file__), "../videos/omc-01-5-repas-15-minutes/photos"))
# Une liste de « plans » par carte ; un plan = les photos d'une phrase (id, focale x, focale y)
SHOTS = [
    [[(8055161, .5, .5)]],
    [[(2985167, .45, .5), (4110462, .5, .45), (4197445, .5, .3)], [(7129733, .62, .3)]],
    [[(8956718, .55, .5), (19891628, .5, .5), (768089, .5, .3)], [(17910326, .5, .5)]],
    [[(8108151, .5, .5), (12001951, .4, .55), (9475288, .5, .6)], [(6294468, .5, .6), (9475275, .5, .55)]],
    [[(143133, .5, .5), (4110464, .5, .5), (25037071, .5, .5)], [(15505487, .5, .55), (15108369, .5, .5)]],
    [[(19953736, .5, .5), (9670682, .5, .4), (9193534, .5, .6)], [(6760851, .55, .5), (1391301, .58, .65)]],
    [[(8580793, .5, .5)], [(2831799, .3, .4), (3737639, .5, .5), (7055120, .5, .6), (9898352, .45, .5)]],
    [[(8507673, .5, .5)], [(6963601, .5, .5)], [(6669795, .5, .5)]],
]


def fetch(pid):
    f = os.path.join(PHOTOS, f"{pid}.jpg")
    if not os.path.exists(f):
        os.makedirs(PHOTOS, exist_ok=True)
        subprocess.run(["curl", "-sSf", "-o", f,
                        f"https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg?auto=compress&cs=tinysrgb&h=2200"], check=True)
    return f


def cover(img, w, h, fx, fy):
    s = max(w / img.width, h / img.height)
    im = img.resize((int(img.width * s + 1), int(img.height * s + 1)), Image.LANCZOS)
    x = int(max(0, min(im.width - w, fx * im.width - w / 2)))
    y = int(max(0, min(im.height - h, fy * im.height - h / 2)))
    return im.crop((x, y, x + w, y + h))


def layout(n):
    """Rectangles (x, y, w, h) des panneaux d'un plan."""
    g = 8
    if n == 1:
        return [(0, 0, W, H)]
    if n == 2:
        h = (H - g) // 2
        return [(0, 0, W, h), (0, h + g, W, H - h - g)]
    if n == 3:
        h = (H - 2 * g) // 3
        return [(0, i * (h + g), W, h) for i in range(3)]
    w, h = (W - g) // 2, (H - g) // 2
    return [(0, 0, w, h), (w + g, 0, W - w - g, h), (0, h + g, w, H - h - g), (w + g, h + g, W - w - g, H - h - g)]


ZOOM = 1.14


class Panel:
    def __init__(self, pid, fx, fy, rect):
        self.rect = rect
        x, y, w, h = rect
        self.big = cover(Image.open(fetch(pid)).convert("RGB"), int(w * ZOOM), int(h * ZOOM), fx, fy)

    def frame(self, age, life):
        x, y, w, h = self.rect
        k = M.clamp(age / max(life, 0.1))
        z = 1.0 + (ZOOM - 1.0) * k  # zoom avant lent
        cw, ch = int(w * ZOOM / z), int(h * ZOOM / z)
        ox, oy = (self.big.width - cw) // 2, (self.big.height - ch) // 2
        return self.big.crop((ox, oy, ox + cw, oy + ch)).resize((w, h), Image.BILINEAR)


def make_card(i):
    dur = TIMES[i + 1] - TIMES[i]
    acc = COLORS[i][2]
    title, phrases = CARDS[i]
    t_img = M.bubble(title, 70, (255, 255, 255), acc + (255,), maxw=1000, radius=50, one_line=True)
    p_imgs = [M.bubble(p, 56, (35, 35, 35), (255, 255, 255, 255), maxw=920) for p in phrases]
    pt = phrase_times(i, dur)
    starts = [0.0] + (pt if i == 7 else pt[1:])
    shots = []
    for s, spec in enumerate(SHOTS[i]):
        rects = layout(len(spec))
        shots.append((starts[s], [Panel(pid, fx, fy, r) for (pid, fx, fy), r in zip(spec, rects)]))

    def frame(t):
        cv = Image.new("RGB", (W, H), (255, 255, 255))
        for s, (st, panels) in enumerate(shots):
            nxt = shots[s + 1][0] if s + 1 < len(shots) else dur
            if t < st or t > nxt + 0.8:
                continue
            life = nxt - st + 0.8
            for k, p in enumerate(panels):
                first = (st == 0 and k == 0)
                d = st + 0.22 * k
                if t < d:
                    continue
                x, y, w, h = p.rect
                img = p.frame(t - st, life)
                if first:
                    cv.paste(img, (x, y))
                elif len(panels) == 4:
                    sc = 0.6 + 0.4 * M.ease_back(M.clamp((t - d) / 0.45))
                    if abs(sc - 1) > 0.002:
                        img = img.resize((max(1, int(w * sc)), max(1, int(h * sc))), Image.BILINEAR)
                    cv.paste(img, (int(x + (w - img.width) / 2), int(y + (h - img.height) / 2)))
                else:
                    q = M.ease_out(M.clamp((t - d) / 0.45))
                    side = -1 if k % 2 == 0 else 1
                    cv.paste(img, (int(x + side * (1 - q) * W), y))
        tp = M.clamp((t - 0.1) / 0.6)
        if tp > 0:
            M.put(cv, t_img, 540, 250 - 160 * (1 - M.ease_back(tp)), 1, 0, M.clamp(tp * 2.5))
        y = 1250
        for img, tk in zip(p_imgs, pt):
            h = img.height - 30
            if t >= tk:
                q = M.clamp((t - tk) / 0.5)
                M.put(cv, img, 540, y + h / 2 + 50 * (1 - M.ease_out(q)), 0.7 + 0.3 * M.ease_back(q), 0, M.clamp(q * 2.5))
            y += h + 10
        if i > 0 and t < WIPE:
            M.circle_wipe(cv, t, WIPE, COLORS[i][2], "out")
        if i < 7 and t > dur - WIPE:
            M.circle_wipe(cv, t - (dur - WIPE), WIPE, COLORS[i + 1][2], "in")
        return cv

    out = sys.argv[1]
    if os.environ.get("STILLS"):
        for tt in [float(x) for x in os.environ["STILLS"].split(",")]:
            if tt < dur:
                frame(tt).resize((540, 960)).save(os.path.join(out, f"still_c{i+1}_{tt}.png"))
        return None
    path = os.path.abspath(os.path.join(out, f"part{i + 1}.mp4"))
    M.render_segment(path, dur, frame)
    return path


if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for card in SHOTS:
        for shot in card:
            for pid, _, _ in shot:
                fetch(pid)
    only = [int(a) for a in sys.argv[2:]] or list(range(8))
    with Pool(4) as pool:
        parts = pool.map(make_card, only)
    if len(only) == 8 and not os.environ.get("STILLS"):
        final = os.path.abspath(os.path.join(out, "omc-01-5-repas-rapides-photos.mp4"))
        M.concat(parts, final)
        print(final)
