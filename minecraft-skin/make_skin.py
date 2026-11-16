# Builds the 128x128 Bedrock skin by sampling the reference renders texel by texel.
#   ref/front_close.png  sharp close-up of the front view   (main source)
#   reference.png        overview with 3/4 and back view    (sides, top, back)
from PIL import Image
HI = Image.open("ref/front_close.png").convert("RGB"); KH = HI.width/924      # coords below are in a 924px-wide frame
LO = Image.open("reference.png").convert("RGB")
BK = Image.open("ref/back_close.png").convert("RGB")                          # sharp close-up of the back view
QH = Image.open("ref/head_quarter.png").convert("RGB")                        # sharp close-up of the head, 3/4 from above
GAIN = 1.06

def bright(c): return tuple(min(255, int(v*GAIN+0.5)) for v in c)
def is_hair(c):
    r, g, b = c
    return 40 < r < 200 and (r-b)/r > 0.29
def cell(img, x0, y0, x1, y1):                      # median colour of the inner part of a box
    mx, my = (x1-x0)*0.22, (y1-y0)*0.22
    box = img.crop((int(x0+mx), int(y0+my), max(int(x0+mx)+1, int(x1-mx)), max(int(y0+my)+1, int(y1-my))))
    px = list(box.getdata() if not hasattr(box, "get_flattened_data") else box.get_flattened_data())
    return tuple(sorted(p[k] for p in px)[len(px)//2] for k in range(3))
def grid(img, k, x0, y0, x1, y1, w, h):             # sample a w*h texel grid from a rectangle
    return {(i, j): cell(img, k*(x0+i*(x1-x0)/w), k*(y0+j*(y1-y0)/h), k*(x0+(i+1)*(x1-x0)/w), k*(y0+(j+1)*(y1-y0)/h))
            for j in range(h) for i in range(w)}
def quad(img, tl, tr, br, bl, w, h, r=5):           # sample a perspective quad (924px-frame coords)
    k = img.width/924; out = {}
    for j in range(h):
        for i in range(w):
            a, b = (i+.5)/w, (j+.5)/h
            X = (1-a)*(1-b)*tl[0] + a*(1-b)*tr[0] + a*b*br[0] + (1-a)*b*bl[0]
            Y = (1-a)*(1-b)*tl[1] + a*(1-b)*tr[1] + a*b*br[1] + (1-a)*b*bl[1]
            out[i, j] = cell(img, k*(X-r), k*(Y-r), k*(X+r), k*(Y+r))
    return out
def front(x0, y0, x1, y1, w, h): return grid(HI, KH, x0, y0, x1, y1, w, h)
def back(x0, y0, x1, y1, w, h):  return grid(BK, BK.width/924, x0, y0, x1, y1, w, h)
def fill_rows(g):                                   # replace non-hair / shadow-gap texels by the nearest hair texel in the row
    out = {}
    ok = lambda c: is_hair(c) and c[0] >= 72
    w = max(i for i, _ in g)+1
    for (i, j), c in g.items():
        if ok(c): out[i, j] = c; continue
        near = sorted((abs(i-ii), ii) for ii in range(w) if ok(g[ii, j]))
        out[i, j] = g[near[0][1], j] if near else (121, 95, 72)
    return out
def vsmooth(g, where):                              # vertical median filter -> long calm strands
    out = dict(g); h = max(j for _, j in g)+1
    for (i, j), c in g.items():
        if not where(i, j): continue
        win = sorted(g[i, jj] for jj in range(max(0, j-2), min(h, j+3)) if where(i, jj))
        out[i, j] = win[len(win)//2]
    return out
def chunky(g, n=2):                                 # 8x8 blocks -> 16x16 texels
    return {(i*n+a, j*n+b): c for (i, j), c in g.items() for a in range(n) for b in range(n)}

# ---- hair palette taken from the sharp front view; low-res samples are snapped to it ----
HEAD = (217, 298, 660, 730)                         # measured block grid of the head in the close-up
_hat8 = front(*HEAD, 8, 8)
_bf = front(235, 705, 650, 1345, 16, 24)
_pal = sorted({c for c in list(_hat8.values()) + list(_bf.values()) if is_hair(c) and c[0] >= 70})
def snap(c):
    if not is_hair(c): return c
    return min(_pal, key=lambda p: sum((a-b)**2 for a, b in zip(p, c)))

def build(slim=True):
    img = Image.new("RGBA", (128, 128), (0, 0, 0, 0)); px = img.load()
    def put(x, y, g, keep=None, flip=False, fn=None):
        w = max(i for i, _ in g)+1
        for (i, j), c in g.items():
            if keep and not keep(i, j, c): continue
            c = fn(i, j, c) if fn else c
            px[int(2*x) + (w-1-i if flip else i), int(2*y)+j] = bright(c)+(255,)
    def solid(x, y, w, h, c):
        for j in range(int(2*h)):
            for i in range(int(2*w)): px[int(2*x)+i, int(2*y)+j] = tuple(c)+(255,)

    # ---------------- head ----------------
    fine = front(*HEAD, 16, 16)
    lit = lambda c: is_hair(c) and c[0] >= 78                              # dark blocks are shadowed hair, not hat
    face = {}
    for (i, j), c in fine.items():                                         # hair: one colour per block, like the render;
        blk = _hat8[i//2, j//2]                                            # skin and eyes keep the finer detail
        face[i, j] = blk if is_hair(blk) else c
    for i in range(16):                                                    # below the chin the render shows the shirt
        for j in (14, 15):
            c = face[i, j]
            if not is_hair(c) and (c[0] < 120 or c[0] - c[2] < 25): face[i, j] = face[i, 13]
    put(8, 8, face)                                                        # face + hair (base layer)
    put(40, 8, face, keep=lambda i, j, c: lit(_hat8[i//2, j//2]))          # fringe and locks stand out on the hat layer
    bk = fill_rows(back(262, 374, 694, 806, 16, 16)); bk8 = back(262, 374, 694, 806, 8, 8)
    for (i, j) in list(bk):
        blk = bk8[i//2, j//2]
        if (j < 6 or i < 4 or i > 11) and is_hair(blk) and blk[0] >= 72: bk[i, j] = blk
    bk = vsmooth(bk, lambda i, j: j >= 6 and 4 <= i <= 11)
    put(24, 8, bk)
    put(56, 8, bk, keep=lambda i, j, c: (j < 6 or i < 4 or i > 11) and not (j == 0 and 4 <= i <= 11))
    side = fill_rows(quad(QH, (112, 925), (345, 958), (345, 1425), (115, 1398), 16, 16))
    side = vsmooth(side, lambda i, j: i < 12)                              # calm vertical strands
    for (i, j) in list(side):                                              # the curls next to the face are blocks
        if i >= 12: side[i, j] = side[12 + 2*((i-12)//2), 2*(j//2)]
    ear = lambda i, j, c: j > 0 or i < 4                                   # top edge stays only where the ear is (back)
    put(0, 8, side); put(32, 8, side, keep=ear); put(16, 8, side, flip=True); put(48, 8, side, keep=ear, flip=True)
    top = quad(QH, (112, 925), (570, 895), (810, 925), (345, 958), 16, 16)
    med = sorted(c for c in top.values() if is_hair(c) and c[0] >= 90); med = med[len(med)//2]
    top = {(i, j): (c if (is_hair(c) or c[0] > 150) and c[0] >= 80 and c[0] > c[2]+10 else med) for (i, j), c in top.items()}
    for j in range(16):                                                    # hair runs sideways: one tone per row
        row = sorted(top[i, j] for i in range(16)); rm = row[len(row)//2]
        for i in range(16):
            top[i, j] = tuple(int(v*0.9) for v in rm) if i in (0, 15) else rm
    for i in (2, 3, 12, 13):                                               # the two small highlights near the front
        for j in (11, 12): top[i, j] = (200, 180, 155)
    isear = lambda i, j: i//2 in (0, 1, 6, 7) and j//2 in (0, 1)
    put(8, 0, top, fn=lambda i, j, c: med if isear(i, j) else c)
    earc = quad(QH, (150, 885), (160, 885), (160, 892), (150, 892), 1, 1)[0, 0]
    put(40, 0, top, keep=lambda i, j, c: isear(i, j),                      # ears: caps on the back corners, closed by the hair walls
        fn=lambda i, j, c: earc)
    chin = front(300, 660, 590, 700, 16, 16)
    put(16, 0, chin, fn=lambda i, j, c: c if 2 <= i <= 13 and 2 <= j <= 13 else (95, 74, 58))

    # ---------------- body ----------------
    bf = dict(_bf); bb = back(270, 770, 680, 1398, 16, 24)
    for j in range(24):                                                    # thin zipper sits between two texels
        z = cell(HI, KH*435, KH*(705+j*640/24), KH*445, KH*(705+(j+1)*640/24))
        if z[0] > 95 and abs(z[0]-z[2]) < 14 and j >= 13: bf[7, j] = z
    for i in range(16):                                                    # neck rows are hidden behind the chin in the render
        for j in (0, 1):
            if not is_hair(bf[i, 2]): bf[i, j] = bf[i, 2]
    def under(i, j, c):
        if is_hair(c) or (c[0]-c[2] > 12 and c[0] < 110): return (30, 30, 32)
        return c
    def strand(g):
        h = {k for k, c in g.items() if is_hair(c) and c[0] >= 70}
        nb = lambda i, j: sum((i+a, j+b) in h for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        return {k for k in h if nb(*k) >= 2 or k[1] == 0}
    hf, hb = strand(bf), strand(bb)
    put(20, 20, bf, fn=under); put(32, 20, bb, fn=under)
    put(20, 36, bf, keep=lambda i, j, c: (i, j) in hf); put(32, 36, bb, keep=lambda i, j, c: (i, j) in hb)
    HOOD = bf[0, 20]
    solid(16, 20, 4, 12, bright(HOOD)); solid(28, 20, 4, 12, bright(HOOD))
    solid(20, 16, 8, 4, (48, 49, 52)); solid(28, 16, 8, 4, (26, 26, 28))

    # ---------------- arms ----------------
    aw = 3 if slim else 4
    def arm(x, y, ox, oy, fr, bk):
        nohair = lambda i, j, c: (30, 30, 32) if is_hair(c) else c
        wide = {(i, j): bk[min(2*aw-1, i*2*aw//8), j] for i in range(8) for j in range(24)}
        bulge = lambda i, j, c: j <= 4 or 17 <= j <= 21
        for bx, by, keep in ((x, y, None), (ox, oy, bulge)):
            put(bx, by+4, wide, keep, fn=nohair); put(bx+4, by+4, fr, keep, fn=nohair)
            put(bx+4+aw, by+4, wide, keep, fn=nohair); put(bx+8+aw, by+4, bk, keep, fn=nohair)
            solid(bx+4, by, aw, 4, (50, 51, 54))
        solid(x+4+aw, y, aw, 4, bright(fr[2, 23]))
    arm(40, 16, 40, 32, front(97, 705, 233, 1320, 2*aw, 24), back(687, 750, 806, 1365, 2*aw, 24))
    arm(32, 48, 48, 48, front(652, 705, 798, 1320, 2*aw, 24), back(142, 750, 263, 1365, 2*aw, 24))

    # ---------------- legs ----------------
    def leg(x, y, fr, bk):
        put(x+4, y+4, fr); put(x+12, y+4, bk); put(x, y+4, bk); put(x+8, y+4, bk, flip=True)
        solid(x+4, y, 4, 4, bright(fr[3, 1])); solid(x+8, y, 4, 4, bright(fr[3, 23]))
    leg(0, 16, front(240, 1345, 440, 1920, 8, 24), back(478, 1398, 670, 1945, 8, 24))
    leg(16, 48, front(445, 1345, 650, 1920, 8, 24), back(282, 1398, 474, 1945, 8, 24))
    return img

def v2(img):
    """Personal touches on top of the clean skin: brighter eyes, blonde face-framing strands,
    lighter tips, pearl earrings, heart necklace, cat-ear colours, slightly opened fringe."""
    img = img.copy(); px = img.load()
    def blend(x, y, c, t):
        r, g, b, a = px[x, y]
        if a: px[x, y] = tuple(int(v + (w - v) * t) for v, w in zip((r, g, b), c)) + (255,)
    FX, FY, OX, OY = 16, 16, 80, 16                       # base face / hat-layer face
    for i in (6, 7, 8, 9):                                 # open the fringe a little
        for j in (8, 9):
            px[OX+i, OY+j] = (0, 0, 0, 0); px[FX+i, FY+j] = (196, 160, 140, 255)
    for (i, top, low) in ((4, (96, 142, 192), (140, 182, 212)), (5, (64, 104, 158), (112, 158, 200)),
                          (10, (64, 104, 158), (112, 158, 200)), (11, (96, 142, 192), (140, 182, 212))):
        px[FX+i, FY+11] = (46, 34, 30, 255); px[FX+i, FY+12] = top + (255,); px[FX+i, FY+13] = low + (255,)
    for i in (2, 13): px[OX+i, OY+14] = (248, 244, 238, 255)                       # pearl earrings
    for i in (2, 3, 12, 13):                                                       # blonde strands at the face
        for j in range(16): blend(OX+i, OY+j, (236, 208, 164), .38)
        for j in range(12): blend(40+i, 72+j, (236, 208, 164), .34 * (1 - j/14))
    for i in range(16):                                                            # lighter tips
        for j in range(13, 24): blend(40+i, 72+j, (230, 194, 134), .22)
        for j in range(17, 24): blend(64+i, 72+j, (230, 194, 134), .22)
    for (i, j) in ((6, 1), (9, 1), (7, 2), (8, 2)): px[40+i, 40+j] = (212, 176, 110, 255)   # necklace
    for i in (7, 8): px[40+i, 40+3] = (236, 186, 128, 255)                                   # heart pendant
    GREY, PINK = (146, 136, 128, 255), (244, 228, 226, 255)                        # cat ears: grey fur, light inside
    for ex in (0, 12):
        for i in range(4):
            for j in range(4): px[80+ex+i, j] = PINK if (i in (1, 2) and j in (1, 2)) else GREY
            px[112+ex+i, 16] = GREY                                                # back wall of the ear
    for i in range(4): px[64+i, 16] = GREY; px[96+12+i, 16] = GREY                 # side walls
    return img

if __name__ == "__main__":
    for slim, tag in ((True, "slim"), (False, "classic")):
        clean = build(slim)
        clean.save(f"skin_{tag}_128.png"); v2(clean).save(f"skin_{tag}_128_v2.png")
