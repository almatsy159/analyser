import subprocess
import mss
import os
from datetime import datetime


def capture_window(window_info, save_dir="data/img"):
    """Capture la fenêtre active et enregistre l'image."""
    if not window_info:
        print("Aucune fenêtre active détectée.")
        return

    x, y = window_info["pos"]
    w, h = window_info["size"]

    os.makedirs(save_dir, exist_ok=True)
    filename = os.path.join(save_dir, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")

    with mss.mss() as sct:
        sct_img = sct.grab({"top": y, "left": x, "width": w, "height": h})
        mss.tools.to_png(sct_img.rgb, sct_img.size, output=filename)

    print(f"Capture enregistrée : {filename}")

    return filename

def get_active_window():
    """Retourne le nom et la géométrie (x, y, w, h) de la fenêtre active."""
    try:
        # ID de la fenêtre active
        wid = subprocess.check_output(["xdotool", "getactivewindow"]).decode().strip()

        # Nom de la fenêtre
        name = subprocess.check_output(["xdotool", "getwindowname", wid]).decode().strip()

        # Géométrie de la fenêtre
        geom = subprocess.check_output(["xdotool", "getwindowgeometry", wid]).decode()
        pos, size = None, None
        for line in geom.splitlines():
            if "Position" in line:
                pos = tuple(map(int, line.split()[1].split(',')))
            if "Geometry" in line:
                size = tuple(map(int, line.split()[1].split('x')))

        return {"id": wid, "name": name, "pos": pos, "size": size}
    except subprocess.CalledProcessError:
        return None