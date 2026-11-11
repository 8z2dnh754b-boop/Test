"""On mange quoi ce soir ? — Vidéo 1 : 5 repas rapides et pas chers (60 s, motion design)."""
import os, sys
from multiprocessing import Pool
from PIL import Image
import mlib as M

TIMES = [0, 4.5, 12, 19.5, 27, 34.5, 42.5, 51, 60]
COLORS = [  # dégradé haut, bas, accent
    ((255, 190, 90), (255, 226, 140), (230, 81, 0)),
    ((255, 236, 150), (255, 208, 100), (205, 110, 0)),
    ((140, 225, 236), (190, 238, 244), (0, 125, 138)),
    ((255, 178, 152), (255, 210, 195), (190, 40, 40)),
    ((255, 206, 135), (255, 228, 185), (220, 90, 0)),
    ((255, 215, 95), (255, 238, 185), (175, 95, 10)),
    ((170, 218, 170), (205, 234, 205), (46, 125, 50)),
    ((250, 192, 212), (228, 196, 236), (170, 25, 90)),
]
CARDS = [
    ("5 repas rapides et pas chers", ["Prêts en 15 minutes."]),
    ("1. Omelette aux pommes de terre", ["Des œufs, une pomme de terre, un oignon.", "15 minutes à la poêle."]),
    ("2. Riz sauté", ["Le riz de la veille, 2 œufs, des petits pois.", "10 minutes à la poêle."]),
    ("3. Pâtes au thon", ["Pâtes, thon en boîte, coulis de tomate.", "La sauce est prête pendant que les pâtes cuisent."]),
    ("4. Soupe express", ["Carottes, pommes de terre, oignon.", "15 minutes de cuisson, puis on mixe."]),
    ("5. Croque-monsieur au four", ["Pain de mie, jambon, fromage.", "10 minutes au four."]),
    ("L'astuce", ["Garde toujours au placard :", "des œufs, du riz, des pâtes et des conserves."]),
    ("Lequel tu fais ce soir ?", ["Dis-le-moi en commentaire !", "Abonne-toi pour une idée chaque jour."]),
]
WIPE = 0.4
OUTDIR = sys.argv[1] if len(sys.argv) > 1 else "out"


def phrase_times(i, dur):
    n = len(CARDS[i][1])
    if i == 7:
        return [2.8, 5.4]
    if n == 1:
        return [0.6]
    return [0.6, round(dur * 0.48, 2)]


def make_card(i):
    dur = TIMES[i + 1] - TIMES[i]
    c1, c2, acc = COLORS[i]
    bg = M.Background(c1, c2, seed=i)
    title, phrases = CARDS[i]
    t_img = M.bubble(title, 70, (255, 255, 255), acc + (255,), maxw=1000, radius=50, one_line=True)
    p_imgs = [M.bubble(p, 56, (35, 35, 35), (255, 255, 255, 255), maxw=920) for p in phrases]
    pt = phrase_times(i, dur)
    acc4 = acc + (255,)

    # --- sprites de la carte ---
    S = {}
    if i == 0:
        S = dict(plate=M.plate())
    elif i == 1:
        S = dict(egg=M.egg(), potato=M.potato(), onion=M.onion(), pan=M.pan(M.omelette_inner))
    elif i == 2:
        S = dict(bowl=M.rice_bowl(), egg=M.egg(), peas=M.peas_pod(), pan=M.pan(M.fried_rice_inner))
    elif i == 3:
        S = dict(penne=M.penne_pile(), tuna=M.tuna_can(), jar=M.coulis_jar(),
                 pot=M.pot(M.water_pasta), sauce=M.pot(M.red_sauce, 320, 260, (215, 80, 60, 255)))
    elif i == 4:
        S = dict(carrot=M.carrot(), potato=M.potato(), onion=M.onion(),
                 pot=M.pot(M.orange_soup, 470, 380), blender=M.hand_blender())
    elif i == 5:
        S = dict(bread=M.bread_slice(), ham=M.ham(), cheese=M.cheese(),
                 ovens=[M.oven(g / 7) for g in range(8)])
    elif i == 6:
        S = dict(cup=M.cupboard(0), doors=[M.cupboard_doors(k / 15) for k in range(16)],
                 carton=M.egg_carton(), rice=M.rice_bag(), jar=M.pasta_jar(),
                 can1=M.can((220, 70, 60, 255)), can2=M.can((80, 150, 90, 255)))
    elif i == 7:
        minis = [M.pan(M.omelette_inner), M.pan(M.fried_rice_inner), M.pot(M.water_pasta),
                 M.soup_bowl(), M.croque()]
        S = dict(minis=[m.resize((int(m.width * k), int(m.height * k)), Image.LANCZOS)
                        for m, k in zip(minis, (0.36, 0.36, 0.5, 0.75, 0.75))],
                 bubble=M.speech_bubble(), btn=M.subscribe_btn(), dot=M.soft_dot(16, (120, 120, 130), 255))

    def scene(cv, t):
        p0 = pt[0]; p1 = pt[1] if len(pt) > 1 else None
        if i == 0:
            M.steam(cv, 520, 560, t, 220)
            M.pop(cv, S["plate"], 500, 760, t, 0.25)
            M.pop(cv, M.timer("15 min", M.clamp((t - 0.8) / 3.0), acc4), 860, 520, t, 0.8, phase=1)
        elif i in (1, 2, 4, 5):
            out = p1 - 0.05
            if i == 1:
                M.pop(cv, S["egg"], 240, 640, t, p0 + 0.1, out, scale=1.25, phase=0.3)
                M.pop(cv, S["egg"], 380, 610, t, p0 + 0.25, out, scale=1.25, phase=1.3)
                M.pop(cv, S["potato"], 780, 640, t, p0 + 0.9, out, scale=1.25, phase=2.1)
                M.pop(cv, S["onion"], 540, 900, t, p0 + 1.7, out, scale=1.25, phase=3.0)
            elif i == 2:
                M.pop(cv, S["bowl"], 290, 650, t, p0 + 0.1, out, scale=1.25, phase=0.3)
                M.pop(cv, S["egg"], 720, 620, t, p0 + 1.0, out, scale=1.25, phase=1.0)
                M.pop(cv, S["egg"], 860, 650, t, p0 + 1.15, out, scale=1.25, phase=2.0)
                M.pop(cv, S["peas"], 540, 910, t, p0 + 1.8, out, scale=1.25, phase=3.0)
            elif i == 4:
                M.pop(cv, S["carrot"], 300, 600, t, p0 + 0.1, out, scale=1.25, phase=0.3, spin=-25)
                M.pop(cv, S["carrot"], 330, 720, t, p0 + 0.25, out, scale=1.25, phase=1.5, spin=20)
                M.pop(cv, S["potato"], 790, 650, t, p0 + 0.9, out, scale=1.25, phase=2.1)
                M.pop(cv, S["onion"], 540, 920, t, p0 + 1.6, out, scale=1.25, phase=3.0)
            elif i == 5:
                M.pop(cv, S["bread"], 280, 650, t, p0 + 0.1, out, scale=1.25, phase=0.3)
                M.pop(cv, S["ham"], 790, 640, t, p0 + 0.8, out, scale=1.25, phase=1.2)
                M.pop(cv, S["cheese"], 540, 910, t, p0 + 1.5, out, scale=1.25, phase=2.4)
            if t >= p1:
                lab = {1: "15 min", 2: "10 min", 4: "15 min", 5: "10 min"}[i]
                prog = M.clamp((t - p1 - 0.5) / (dur - p1 - 1.0))
                if i in (1, 2):
                    M.steam(cv, 470, 560, t, 260)
                    M.pop(cv, S["pan"], 520, 780, t, p1, phase=0.5, float_amp=6, spin=-20)
                    M.pop(cv, M.timer(lab, prog, acc4), 880, 470, t, p1 + 0.5, phase=2)
                elif i == 4:
                    M.steam(cv, 460, 560, t, 280)
                    M.pop(cv, S["pot"], 460, 820, t, p1, phase=0.5, float_amp=4, spin=0)
                    M.pop(cv, M.timer(lab, prog, acc4), 870, 480, t, p1 + 0.5, phase=2)
                    tb = p1 + 1.7
                    if t > tb:
                        k = M.clamp((t - tb) / 0.5)
                        y = 520 - 260 * (1 - M.ease_out(k)) + 18 * abs(M.math.sin((t - tb) * 9))
                        M.put(cv, S["blender"], 470, y, 1, M.math.sin(t * 20) * 2.5 * k, k)
                elif i == 5:
                    g = int(3.5 + 3.5 * M.math.sin(t * 4))
                    M.pop(cv, S["ovens"][g], 520, 790, t, p1, phase=0.5, float_amp=4, spin=0)
                    M.pop(cv, M.timer(lab, prog, acc4), 870, 470, t, p1 + 0.5, phase=2)
        elif i == 3:
            out = p1 - 0.05
            M.pop(cv, S["penne"], 280, 640, t, p0 + 0.1, out, scale=1.25, phase=0.3)
            M.pop(cv, S["tuna"], 790, 640, t, p0 + 0.8, out, scale=1.25, phase=1.2)
            M.pop(cv, S["jar"], 540, 900, t, p0 + 1.6, out, scale=1.25, phase=2.4)
            if t >= p1:
                M.steam(cv, 360, 560, t, 260)
                M.steam(cv, 840, 650, t, 180, n=4)
                M.pop(cv, S["pot"], 360, 820, t, p1, phase=0.5, float_amp=4, spin=0)
                M.pop(cv, S["sauce"], 830, 840, t, p1 + 0.6, phase=1.7, float_amp=4, spin=0)
        elif i == 6:
            k = M.clamp((t - p0 - 0.5) / 0.7)
            M.pop(cv, S["cup"], 540, 740, t, 0.3, float_amp=0, spin=0)
            if t >= 0.3:
                ox, oy = 540 - 320, 740 - 360
                if t >= p1:
                    M.pop(cv, S["carton"], ox + 180, oy + 255, t, p1 + 0.05, float_amp=0, spin=0)
                    M.pop(cv, S["rice"], ox + 470, oy + 220, t, p1 + 0.45, float_amp=0, spin=0)
                    M.pop(cv, S["jar"], ox + 160, oy + 560, t, p1 + 0.85, float_amp=0, spin=0)
                    M.pop(cv, S["can1"], ox + 380, oy + 595, t, p1 + 1.25, float_amp=0, spin=0)
                    M.pop(cv, S["can2"], ox + 500, oy + 595, t, p1 + 1.4, float_amp=0, spin=0)
                sc = M.ease_back(M.clamp((t - 0.3) / 0.55))
                if sc > 0.98:
                    M.put(cv, S["doors"][int(round(M.ease_out(k) * 15))], 540, 740)
        elif i == 7:
            import math
            for j, m in enumerate(S["minis"]):
                a = -math.pi / 2 + j * 2 * math.pi / 5
                M.pop(cv, m, 540 + 300 * math.cos(a), 730 + 280 * math.sin(a), t, 0.4 + j * 0.2, pt[0] - 0.05, phase=j)
            M.pop(cv, S["bubble"], 540, 720, t, pt[0], pt[1] - 0.05, phase=0.5)
            if pt[0] + 0.4 < t < pt[1]:
                for j in range(3):
                    b = abs(math.sin((t * 3 - j * 0.35) * 1.6))
                    M.put(cv, S["dot"], 420 + j * 120, 690 - 14 * b + 18 * math.sin(t * 2.1 + 0.5), 1.6)
            M.pop(cv, S["btn"], 540, 740, t, pt[1], phase=0.7, float_amp=6)
            tt = t - (pt[1] + 1.2)
            if tt > 0:
                ph = (tt % 1.3) / 1.3
                d = M.ImageDraw.Draw(cv)
                r = 30 + 120 * ph
                col = tuple(int(255 * (1 - 0.0)) for _ in range(3))
                d.ellipse((700 - r, 780 - r, 700 + r, 780 + r), outline=col, width=max(1, int(10 * (1 - ph))))

    def frame(t):
        cv = bg.frame(t + i * 3)
        scene(cv, t)
        # titre
        tp = M.clamp((t - 0.1) / 0.6)
        if tp > 0:
            M.put(cv, t_img, 540, 250 - 160 * (1 - M.ease_back(tp)), 1, 0, M.clamp(tp * 2.5))
        # phrases empilées
        y = 1200
        for k, (img, tk) in enumerate(zip(p_imgs, pt)):
            h = img.height - 30
            if t >= tk:
                q = M.clamp((t - tk) / 0.5)
                M.put(cv, img, 540, y + h / 2 + 50 * (1 - M.ease_out(q)), 0.7 + 0.3 * M.ease_back(q), 0, M.clamp(q * 2.5))
            y += h + 10
        # transitions
        if i > 0 and t < WIPE:
            M.circle_wipe(cv, t, WIPE, COLORS[i][2], "out")
        if i < 7 and t > dur - WIPE:
            M.circle_wipe(cv, t - (dur - WIPE), WIPE, COLORS[i + 1][2], "in")
        return cv.convert("RGB") if cv.mode != "RGB" else cv

    if os.environ.get("STILLS"):
        for tt in [float(x) for x in os.environ["STILLS"].split(",")]:
            if tt < dur:
                frame(tt).resize((540, 960)).save(os.path.join(OUTDIR, f"still_c{i+1}_{tt}.png"))
        return None
    path = os.path.abspath(os.path.join(OUTDIR, f"part{i + 1}.mp4"))
    M.render_segment(path, dur, frame)
    return path


if __name__ == "__main__":
    os.makedirs(OUTDIR, exist_ok=True)
    only = [int(a) for a in sys.argv[2:]] if len(sys.argv) > 2 else list(range(8))
    with Pool(4) as pool:
        parts = pool.map(make_card, only)
    if len(only) == 8 and not os.environ.get("STILLS"):
        final = os.path.abspath(os.path.join(OUTDIR, "omc-01-5-repas-rapides.mp4"))
        M.concat(parts, final)
        print(final)
