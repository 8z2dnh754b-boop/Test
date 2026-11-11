"""Trouve le fichier mp4 d'une vidéo Pexels sans clé API, en essayant les noms de fichiers habituels."""
import subprocess, sys
SIZES = ["hd_1080_1920", "uhd_2160_3840", "hd_1920_1080", "uhd_3840_2160", "hd_1280_720", "hd_720_1280", "uhd_2560_1440", "hd_1366_720", "sd_960_540", "sd_540_960"]
FPS = [25, 30, 24, 60, 50]
def find(vid):
    for s in SIZES:
        for f in FPS:
            u = f"https://videos.pexels.com/video-files/{vid}/{vid}-{s}_{f}fps.mp4"
            c = subprocess.run(["curl", "-sI", "-o", "/dev/null", "-w", "%{http_code}", u], capture_output=True, text=True).stdout
            if c == "200":
                return u
    return None
if __name__ == "__main__":
    for v in sys.argv[1:]:
        print(v, find(v))
