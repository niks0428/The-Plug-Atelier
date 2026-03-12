#!/usr/bin/env python3
"""
Generate product card images for The Plug Atelier.
Draws clean silhouette illustrations for each product.
Outputs 800x600 WebP to ./images/
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, math

W, H = 800, 600
OUT = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(OUT, exist_ok=True)

# (bg_dark, bg_light, accent)
SCHEMES = {
    "asics":           ("#0D1B2A", "#162840", "#2176FF"),
    "best-batch":      ("#1A0800", "#2A1200", "#FF6B35"),
    "high-end-shoes":  ("#0A0A14", "#14141E", "#C9A84C"),
    "kids-jordans":    ("#14000E", "#20001A", "#FF3366"),
    "standard-jersey": ("#001A0A", "#002A14", "#00CC66"),
    "private-jersey":  ("#08001A", "#120028", "#9933FF"),
    "fairpods":        ("#0A0A0A", "#141414", "#CCCCCC"),
    "vintage":         ("#180C00", "#281400", "#CC7722"),
    "reselling-guide": ("#001510", "#002018", "#00AA88"),
    "ebay-guide":      ("#180000", "#280000", "#CC3300"),
    "telegram":        ("#001018", "#001C28", "#0099CC"),
    "bundle":          ("#08001A", "#120030", "#FFD700"),
}

PILLS = {
    "asics":           "MOST POPULAR",
    "best-batch":      "HOT",
    "high-end-shoes":  "PREMIUM",
    "kids-jordans":    "NEW",
    "standard-jersey": "POPULAR",
    "private-jersey":  "EXCLUSIVE",
    "fairpods":        "TECH",
    "vintage":         "TRENDING",
    "reselling-guide": "GUIDE",
    "ebay-guide":      "GUIDE",
    "telegram":        "FREE",
    "bundle":          "BEST VALUE",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def lerp(a, b, t):
    return int(a + (b - a) * t)

def lerp_color(c1, c2, t):
    return tuple(lerp(a, b, t) for a, b in zip(c1, c2))

def scale_pts(pts, cx, cy, s):
    return [(cx + x * s, cy + y * s) for x, y in pts]

def bright(rgb, amount=40):
    return tuple(min(255, c + amount) for c in rgb)

def dim(rgb, amount=40):
    return tuple(max(0, c - amount) for c in rgb)

def with_alpha(rgb, a):
    return (*rgb, a)

def gradient_bg(img, c1, c2):
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        draw.line([(0, y), (W, y)], fill=lerp_color(c1, c2, t))

def draw_glow(img, cx, cy, radius, rgb, max_alpha=80):
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    r, g, b = rgb
    steps = 40
    for i in range(steps, 0, -1):
        t = i / steps
        rad = int(radius * t)
        alpha = int(max_alpha * (1 - t) ** 1.0)
        gd.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=(r, g, b, alpha))
    img.paste(glow, mask=glow)

def pill_badge(draw, text, accent_rgb, x=32, y=28):
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    except Exception:
        font = ImageFont.load_default()
    bb = draw.textbbox((0, 0), text, font=font)
    tw = bb[2] - bb[0]
    px, py = 16, 9
    rw, rh = tw + px * 2, 20 + py * 2
    r, g, b = accent_rgb
    draw.rounded_rectangle([x, y, x + rw, y + rh], radius=rh // 2, fill=(r, g, b, 220))
    draw.text((x + px, y + py), text, fill=(255, 255, 255), font=font)

def bottom_label(draw, lines, y_start, accent_rgb):
    try:
        font_lg = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 44)
        font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
    except Exception:
        font_lg = font_sm = ImageFont.load_default()

    # Accent line above text
    r, g, b = accent_rgb
    draw.line([(W // 2 - 50, y_start - 14), (W // 2 + 50, y_start - 14)],
              fill=(r, g, b, 200), width=2)

    y = y_start
    for i, line in enumerate(lines):
        font = font_lg if i == 0 else font_sm
        bb = draw.textbbox((0, 0), line, font=font)
        tw = bb[2] - bb[0]
        x = (W - tw) // 2
        draw.text((x + 1, y + 1), line, fill=(0, 0, 0, 100), font=font)
        draw.text((x, y), line, fill=(255, 255, 255), font=font)
        y += (bb[3] - bb[1]) + 8


# ── Shape drawers ─────────────────────────────────────────────────────────────

def draw_trainer(layer, cx, cy, s, color):
    """Side-view trainer/sneaker silhouette."""
    d = ImageDraw.Draw(layer, "RGBA")
    c = color
    cd = dim(c, 35)
    cb = bright(c, 35)

    # Sole (thick bottom strip)
    sole = scale_pts([
        (-1.05, 0.42), (1.15, 0.42),
        (1.2,   0.6),  (-1.0,  0.6),
    ], cx, cy, s)
    d.polygon(sole, fill=(*c, 255))

    # Midsole stripe (lighter)
    mid = scale_pts([
        (-1.05, 0.28), (1.15, 0.28),
        (1.15,  0.42), (-1.05, 0.42),
    ], cx, cy, s)
    d.polygon(mid, fill=(*cb, 255))

    # Main upper body
    upper = scale_pts([
        (-1.05, 0.28),
        (-1.05, -0.18),
        (-0.7,  -0.42),
        (-0.2,  -0.56),
        ( 0.35, -0.48),
        ( 0.8,  -0.22),
        ( 1.15,  0.05),
        ( 1.15,  0.28),
    ], cx, cy, s)
    d.polygon(upper, fill=(*c, 255))

    # Heel tab (slightly brighter)
    heel = scale_pts([
        (-1.05, -0.18),
        (-1.05, -0.42),
        (-0.85, -0.55),
        (-0.7,  -0.42),
        (-0.7,  -0.18),
    ], cx, cy, s)
    d.polygon(heel, fill=(*cb, 255))

    # Lace panel (darker strip across tongue)
    lace = scale_pts([
        (-0.15, -0.52),
        ( 0.38, -0.44),
        ( 0.38, -0.28),
        (-0.15, -0.36),
    ], cx, cy, s)
    d.polygon(lace, fill=(*cd, 200))

    # Toe cap
    toe = scale_pts([
        ( 0.75, 0.0),
        ( 1.15, 0.0),
        ( 1.15, 0.28),
        ( 0.75, 0.28),
    ], cx, cy, s)
    d.polygon(toe, fill=(*cd, 220))


def draw_heel(layer, cx, cy, s, color):
    """Stiletto heel silhouette."""
    d = ImageDraw.Draw(layer, "RGBA")
    c = color
    cb = bright(c, 30)

    # Platform / toe
    platform = scale_pts([
        (-0.95, 0.55), (0.3, 0.55),
        (0.3,   0.4),  (-0.95, 0.4),
    ], cx, cy, s)
    d.polygon(platform, fill=(*c, 255))

    # Main shoe upper (curves from heel to toe)
    upper = scale_pts([
        (-0.95, 0.4),
        (-0.95, 0.1),
        (-0.5,  -0.55),
        (-0.1,  -0.7),
        ( 0.2,  -0.6),
        ( 0.3,  -0.2),
        ( 0.3,   0.4),
    ], cx, cy, s)
    d.polygon(upper, fill=(*c, 255))

    # Heel (thin spike going down from back)
    heel = scale_pts([
        (-0.85, 0.4),
        (-0.75, 0.4),
        (-0.72, 0.55),
        (-0.88, 0.55),
    ], cx, cy, s)
    d.polygon(heel, fill=(*cb, 255))

    # Ankle strap
    strap = scale_pts([
        (-0.9, -0.1),
        ( 0.3, -0.1),
        ( 0.3,  0.0),
        (-0.9,  0.0),
    ], cx, cy, s)
    d.polygon(strap, fill=(*cb, 180))


def draw_jersey(layer, cx, cy, s, color):
    """Front-view football jersey silhouette."""
    d = ImageDraw.Draw(layer, "RGBA")
    c = color
    cb = bright(c, 35)

    # Main body
    body = scale_pts([
        (-0.55, -0.1), (-0.55, 0.85),
        ( 0.55,  0.85), ( 0.55, -0.1),
    ], cx, cy, s)
    d.polygon(body, fill=(*c, 255))

    # Left sleeve
    sleeve_l = scale_pts([
        (-0.55, -0.1),
        (-0.55, -0.55),
        (-1.0,  -0.3),
        (-1.0,   0.1),
    ], cx, cy, s)
    d.polygon(sleeve_l, fill=(*c, 255))

    # Right sleeve
    sleeve_r = scale_pts([
        ( 0.55, -0.1),
        ( 0.55, -0.55),
        ( 1.0,  -0.3),
        ( 1.0,   0.1),
    ], cx, cy, s)
    d.polygon(sleeve_r, fill=(*c, 255))

    # Collar (V-neck) — draw as bright fill
    collar = scale_pts([
        (-0.22, -0.55),
        ( 0.0,  -0.3),
        ( 0.22, -0.55),
        ( 0.18, -0.72),
        ( 0.0,  -0.5),
        (-0.18, -0.72),
    ], cx, cy, s)
    d.polygon(collar, fill=(*cb, 255))

    # Chest stripe
    stripe = scale_pts([
        (-0.55, 0.1), (0.55, 0.1),
        ( 0.55, 0.3), (-0.55, 0.3),
    ], cx, cy, s)
    d.polygon(stripe, fill=(*cb, 140))

    # Number block in center
    num = scale_pts([
        (-0.18, 0.38), (0.18, 0.38),
        ( 0.18, 0.72), (-0.18, 0.72),
    ], cx, cy, s)
    d.polygon(num, fill=(*cb, 200))


def draw_earbuds(layer, cx, cy, s, color):
    """AirPods-style earbuds silhouette."""
    d = ImageDraw.Draw(layer, "RGBA")
    c = color
    cb = bright(c, 30)

    # Left pod body
    d.ellipse([cx - s*0.72 - s*0.35, cy - s*0.55,
               cx - s*0.72 + s*0.35, cy - s*0.55 + s*0.7],
              fill=(*c, 255))
    # Left stem
    stem_l = scale_pts([
        (-0.82, 0.15), (-0.62, 0.15),
        (-0.62,  0.75), (-0.82,  0.75),
    ], cx, cy, s)
    d.polygon(stem_l, fill=(*c, 255))
    # Left tip
    d.ellipse([cx - s*0.82, cy + s*0.68,
               cx - s*0.62, cy + s*0.88],
              fill=(*cb, 255))

    # Right pod body
    d.ellipse([cx + s*0.72 - s*0.35, cy - s*0.55,
               cx + s*0.72 + s*0.35, cy - s*0.55 + s*0.7],
              fill=(*c, 255))
    # Right stem
    stem_r = scale_pts([
        (0.62, 0.15), (0.82, 0.15),
        (0.82,  0.75), (0.62,  0.75),
    ], cx, cy, s)
    d.polygon(stem_r, fill=(*c, 255))
    # Right tip
    d.ellipse([cx + s*0.62, cy + s*0.68,
               cx + s*0.82, cy + s*0.88],
              fill=(*cb, 255))

    # Case outline (open case behind pods)
    case = scale_pts([
        (-1.05, -0.7), (1.05, -0.7),
        ( 1.05,  0.9), (-1.05,  0.9),
    ], cx, cy, s)
    d.rounded_rectangle(
        [cx - s*1.05, cy - s*0.7, cx + s*1.05, cy + s*0.9],
        radius=int(s*0.25), outline=(*c, 160), width=4
    )


def draw_hanger(layer, cx, cy, s, color):
    """Clothes hanger + jacket silhouette."""
    d = ImageDraw.Draw(layer, "RGBA")
    c = color
    cb = bright(c, 30)

    # Hook (small arc at top)
    for r in range(int(s*0.18), int(s*0.22)):
        d.arc([cx - r, cy - s*0.95 - r, cx + r, cy - s*0.95 + r],
              start=200, end=340, fill=(*c, 220), width=int(s*0.07))

    # Hanger bar (triangle shape)
    hanger = scale_pts([
        (0.0, -0.75),
        (-1.1,  0.05),
        ( 1.1,  0.05),
    ], cx, cy, s)
    d.polygon(hanger, fill=(*c, 0))  # transparent fill
    d.line([
        (cx, cy - s*0.75),
        (cx - s*1.1, cy + s*0.05),
        (cx + s*1.1, cy + s*0.05),
        (cx, cy - s*0.75),
    ], fill=(*c, 255), width=int(s*0.09))

    # Jacket body
    body = scale_pts([
        (-0.7,  0.05), (-0.7,  0.9),
        ( 0.7,  0.9),  ( 0.7,  0.05),
        ( 0.35,-0.05), ( 0.0,  0.2),
        (-0.35,-0.05),
    ], cx, cy, s)
    d.polygon(body, fill=(*c, 240))

    # Lapels
    lapel_l = scale_pts([
        (-0.35,-0.05),
        ( 0.0,  0.2),
        (-0.05, 0.55),
        (-0.4,  0.4),
        (-0.7,  0.05),
    ], cx, cy, s)
    d.polygon(lapel_l, fill=(*cb, 200))

    lapel_r = scale_pts([
        ( 0.35,-0.05),
        ( 0.0,  0.2),
        ( 0.05, 0.55),
        ( 0.4,  0.4),
        ( 0.7,  0.05),
    ], cx, cy, s)
    d.polygon(lapel_r, fill=(*cb, 200))


def draw_open_book(layer, cx, cy, s, color):
    """Open book / document silhouette."""
    d = ImageDraw.Draw(layer, "RGBA")
    c = color
    cb = bright(c, 40)
    cd = dim(c, 20)

    # Left page
    left = scale_pts([
        (-1.05, -0.7), (-0.05, -0.7),
        (-0.05,  0.75), (-1.05,  0.75),
    ], cx, cy, s)
    d.polygon(left, fill=(*c, 255))

    # Right page
    right = scale_pts([
        ( 0.05, -0.7), (1.05, -0.7),
        ( 1.05,  0.75), (0.05,  0.75),
    ], cx, cy, s)
    d.polygon(right, fill=(*cd, 255))

    # Spine
    spine = scale_pts([
        (-0.05, -0.75), (0.05, -0.75),
        ( 0.05,  0.8),  (-0.05,  0.8),
    ], cx, cy, s)
    d.polygon(spine, fill=(*cb, 255))

    # Lines on left page
    for i in range(5):
        yy = cy - s*0.45 + i * s*0.25
        d.line([(cx - s*0.9, yy), (cx - s*0.15, yy)],
               fill=(*cb, 120), width=int(s*0.06))

    # Lines on right page
    for i in range(5):
        yy = cy - s*0.45 + i * s*0.25
        d.line([(cx + s*0.15, yy), (cx + s*0.9, yy)],
               fill=(*cb, 80), width=int(s*0.06))

    # Page curl on right corner
    curl = scale_pts([
        (0.8,  0.75), (1.05, 0.75),
        (1.05,  0.48),
    ], cx, cy, s)
    d.polygon(curl, fill=(*cb, 160))


def draw_speech_bubble(layer, cx, cy, s, color):
    """Chat / speech bubble (Telegram style)."""
    d = ImageDraw.Draw(layer, "RGBA")
    c = color
    cb = bright(c, 30)

    bx1 = cx - s * 1.0
    by1 = cy - s * 0.75
    bx2 = cx + s * 1.0
    by2 = cy + s * 0.45

    # Main bubble
    d.rounded_rectangle([bx1, by1, bx2, by2],
                        radius=int(s * 0.25), fill=(*c, 255))

    # Tail (triangle at bottom-left)
    tail = [
        (cx - s * 0.4, by2),
        (cx - s * 0.7, by2 + s * 0.4),
        (cx - s * 0.1, by2),
    ]
    d.polygon(tail, fill=(*c, 255))

    # Three dots inside (ellipsis)
    for i, dx in enumerate([-0.28, 0, 0.28]):
        bcy = (by1 + by2) / 2 - s * 0.04
        bcx = cx + dx * s
        r = s * 0.1
        d.ellipse([bcx - r, bcy - r, bcx + r, bcy + r], fill=(*cb, 255))


def draw_bundle_stack(layer, cx, cy, s, color):
    """Stack of overlapping product cards."""
    d = ImageDraw.Draw(layer, "RGBA")
    c = color
    cb = bright(c, 40)
    cd = dim(c, 30)

    cards = [
        (cd, -0.25,  0.12, -0.8),  # back card, rotated
        (c,  -0.1,   0.05, -0.3),  # mid card
        (cb,  0.0,   0.0,   0.3),  # front card (brightest)
    ]

    for col, rx, ry, angle in cards:
        # Offset card rectangle
        ox = cx + rx * s
        oy = cy + ry * s
        cw, ch = s * 1.1, s * 1.4
        # Create rotated card
        card_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        cd2 = ImageDraw.Draw(card_img)
        cd2.rounded_rectangle(
            [ox - cw / 2, oy - ch / 2, ox + cw / 2, oy + ch / 2],
            radius=int(s * 0.12), fill=(*col, 230)
        )
        # Stripe at top of card
        cd2.rounded_rectangle(
            [ox - cw / 2, oy - ch / 2, ox + cw / 2, oy - ch / 2 + s * 0.25],
            radius=int(s * 0.1), fill=(*bright(col, 20), 230)
        )
        rotated = card_img.rotate(angle, expand=False, center=(int(ox), int(oy)))
        layer.paste(rotated, mask=rotated)

    # Star / gem shape in center of front card
    gem_pts = []
    for i in range(8):
        angle_rad = math.radians(i * 45 - 22.5)
        r = s * 0.22 if i % 2 == 0 else s * 0.12
        gem_pts.append((cx + r * math.cos(angle_rad), cy + r * math.sin(angle_rad)))
    d.polygon(gem_pts, fill=(*cb, 255))


# ── Main builder ──────────────────────────────────────────────────────────────

DRAW_FNS = {
    "asics":           (draw_trainer, 160),
    "best-batch":      (draw_trainer, 160),
    "high-end-shoes":  (draw_heel,    160),
    "kids-jordans":    (draw_trainer, 130),
    "standard-jersey": (draw_jersey,  130),
    "private-jersey":  (draw_jersey,  130),
    "fairpods":        (draw_earbuds, 120),
    "vintage":         (draw_hanger,  130),
    "reselling-guide": (draw_open_book, 130),
    "ebay-guide":      (draw_open_book, 130),
    "telegram":        (draw_speech_bubble, 140),
    "bundle":          (draw_bundle_stack, 130),
}


def make_image(key):
    bg1, bg2, acc = SCHEMES[key]
    c_bg1   = hex_rgb(bg1)
    c_bg2   = hex_rgb(bg2)
    c_acc   = hex_rgb(acc)
    fn, scale = DRAW_FNS[key]

    # Base image
    img = Image.new("RGBA", (W, H))
    gradient_bg(img, c_bg1, c_bg2)

    # Glow behind illustration
    cx, cy = W // 2, int(H * 0.42)
    draw_glow(img, cx, cy, int(scale * 1.8), c_acc, max_alpha=70)

    # Draw illustration on transparent layer, then composite
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fn(layer, cx, cy, scale, c_acc)
    img.paste(layer, mask=layer)

    # Subtle vignette
    vig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vig)
    for i in range(80):
        t = i / 80
        a = int(100 * t ** 2)
        vd.rectangle([i, i, W - i, H - i], outline=(0, 0, 0, a))
    img.paste(vig, mask=vig)

    # Overlay draw for badge + text
    draw = ImageDraw.Draw(img, "RGBA")
    pill_badge(draw, PILLS[key], c_acc)

    # Bottom label band
    band_y = int(H * 0.72)
    band = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    for y in range(band_y, H):
        t = (y - band_y) / (H - band_y)
        a = int(180 * t)
        bd.line([(0, y), (W, y)], fill=(0, 0, 0, a))
    img.paste(band, mask=band)

    # Output as RGB WebP
    out = Image.new("RGB", (W, H), (0, 0, 0))
    out.paste(img.convert("RGB"))

    path = os.path.join(OUT, f"{key}.webp")
    out.save(path, "WEBP", quality=92)
    print(f"  ✓ {key}.webp")


if __name__ == "__main__":
    print("Generating product images…")
    for key in DRAW_FNS:
        make_image(key)
    print("Done.")
