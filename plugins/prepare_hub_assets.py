from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent
WEB = ROOT.parent.parent / "STGSERIES - website"
OUT = ROOT / "assets" / "img"
OUT.mkdir(parents=True, exist_ok=True)


def _is_green_screen(r: int, g: int, b: int) -> bool:
    return g > 90 and g >= r and g >= b and (g - min(r, b)) > 24


def _logo_pixel(r: int, g: int, b: int) -> tuple[int, int, int, int]:
    if _is_green_screen(r, g, b):
        return (0, 0, 0, 0)
    if g > max(r, b) + 18 and g > 70:
        spill_alpha = max(r, b)
        if spill_alpha < 14:
            return (0, 0, 0, 0)
        return (0, 0, 0, min(255, spill_alpha * 3))
    if max(r, g, b) < 18:
        return (0, 0, 0, 255)
    alpha = min(255, max(255 - g, max(r, b)))
    if alpha < 20:
        return (0, 0, 0, 0)
    alpha = min(255, int(alpha * 1.45 + 28))
    return (0, 0, 0, alpha)


def compress_bg() -> None:
    img = Image.open(WEB / "image.png").convert("RGB")
    max_w = 1920
    if img.width != max_w:
        ratio = max_w / img.width
        img = img.resize((max_w, int(img.height * ratio)), Image.Resampling.LANCZOS)
    img.save(OUT / "bg.jpg", "JPEG", quality=82, optimize=True, progressive=True)


def key_header() -> None:
    img = Image.open(WEB / "header.png").convert("RGBA")
    px = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            px[x, y] = _logo_pixel(*px[x, y][:3])
    img.save(OUT / "hub-header.png", "PNG", optimize=True)


def copy_icons() -> None:
    for name in ("ecostg.png", "strikesstg.png", "catfightstg.png", "logsstg.png"):
        src = WEB / name
        if src.exists():
            Image.open(src).save(OUT / name, "PNG", optimize=True)


def copy_stg() -> None:
    src = ROOT / "ecostg" / "assets" / "img" / "stg-series.png"
    if src.exists():
        Image.open(src).save(OUT / "stg-series.png", "PNG", optimize=True)


if __name__ == "__main__":
    compress_bg()
    key_header()
    copy_icons()
    copy_stg()
    print("done", OUT)
