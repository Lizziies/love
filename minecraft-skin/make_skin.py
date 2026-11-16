# Builds the 128x128 Bedrock skin by sampling the reference render (reference.png) texel by texel.
import sys
from PIL import Image
REF = Image.open("reference.png").convert("RGB"); RP = REF.load()
GAIN = 1.22
HOOD = (37,37,39)

def med(x, y, r=1):
    xs = [RP[int(x)+i, int(y)+j] for i in range(-r, r+1) for j in range(-r, r+1)]
    return tuple(sorted(c[k] for c in xs)[len(xs)//2] for k in range(3))
def bright(c): return tuple(min(255, int(v*GAIN+0.5)) for v in c)
def is_hair(c):
    r, g, b = c
    return r > 40 and (r-b)/r > 0.29 and r < 200

class View:                                    # zoomed-crop coordinates -> reference pixels
    def __init__(s, ox, oy, z=4): s.ox, s.oy, s.z = ox, oy, z
    def rect(s, x0, y0, x1, y1, w, h):         # sample a w*h grid of texels
        out = {}
        for j in range(h):
            for i in range(w):
                X = s.ox + (x0 + (i+.5)*(x1-x0)/w)/s.z
                Y = s.oy + (y0 + (j+.5)*(y1-y0)/h)/s.z
                out[i, j] = med(X, Y)
        return out
    def quad(s, tl, tr, br, bl, w, h):
        out = {}
        for j in range(h):
            for i in range(w):
                a, b = (i+.5)/w, (j+.5)/h
                X = (1-a)*(1-b)*tl[0] + a*(1-b)*tr[0] + a*b*br[0] + (1-a)*b*bl[0]
                Y = (1-a)*(1-b)*tl[1] + a*(1-b)*tr[1] + a*b*br[1] + (1-a)*b*bl[1]
                out[i, j] = med(s.ox + X/s.z, s.oy + Y/s.z)
        return out
F = View(90, 940); B = View(700, 940); M = View(390, 940, 3)

def build(slim=True):
    img = Image.new("RGBA", (128, 128), (0, 0, 0, 0)); px = img.load()
    def put(x, y, grid, keep=None, flip=False, fn=None):
        w = max(i for i, _ in grid)+1
        for (i, j), c in grid.items():
            if keep and not keep(i, j, c): continue
            c = fn(i, j, c) if fn else c
            px[int(2*x) + (w-1-i if flip else i), int(2*y)+j] = bright(c)+(255,)
    def solid(x, y, w, h, c):
        for j in range(int(2*h)):
            for i in range(int(2*w)): px[int(2*x)+i, int(2*y)+j] = tuple(c)+(255,)

    # ---- head ----
    FACE = ["........", "........", "........", "........", "..S..S..", ".SSkkSS.", ".kkkkkk.", "..kkkk.."]
    put(8, 8, F.rect(240, 180, 710, 650, 16, 16))                         # base face
    put(40, 8, F.rect(210, 150, 739, 679, 16, 16),
        keep=lambda i, j, c: FACE[j//2][i//2] == '.' and is_hair(c),
        fn=lambda i, j, c: (112, 88, 66) if (j < 6 and c[0] < 70) else c)  # fringe / side locks
    back = B.rect(253, 150, 755, 665, 16, 16)
    put(24, 8, back); put(56, 8, back, keep=lambda i, j, c: j < 6 or i < 4 or i > 11)
    side = M.quad((130, 95), (355, 150), (355, 470), (135, 415), 16, 16)
    def rowmed(g, j):
        v = sorted(c for (i, jj), c in g.items() if jj == j and c[0] >= 85 and c[0] > c[2] + 8)
        return v[len(v)//2] if v else (121, 95, 72)
    side = {(i, j): (c if (c[0] >= 85 and c[0] > c[2] + 8) else rowmed(side, j)) for (i, j), c in side.items()}
    put(0, 8, side); put(32, 8, side); put(16, 8, side, flip=True); put(48, 8, side, flip=True)
    TONE = {'D': (88, 68, 52), 'M': (121, 95, 72), 'm': (133, 105, 80), 'L': (144, 115, 88),
            'H': (168, 141, 113), 'W': (200, 180, 155)}
    ROWS = "DMMmmLLHHLLmLmMM"                                              # back -> front
    def top_c(i, j):
        t = ROWS[j]
        if i in (0, 15): t = {'H': 'L', 'L': 'm', 'm': 'M', 'M': 'D', 'D': 'D'}[t]
        if j in (12, 13) and i in (3, 4, 11, 12): t = 'W'
        return TONE[t]
    top = {(i, j): top_c(i, j) for i in range(16) for j in range(16)}
    put(8, 0, top)
    put(40, 0, top, keep=lambda i, j, c: i//2 in (0, 1, 6, 7) and j//2 in (2, 3),
        fn=lambda i, j, c: TONE['H'] if j == 7 else TONE['L'])            # ear slabs
    skin = F.rect(300, 600, 650, 640, 16, 16)
    put(16, 0, skin, fn=lambda i, j, c: c if 2 <= i <= 13 and 2 <= j <= 13 else (95, 74, 58))

    # ---- body ----
    bf = F.rect(240, 650, 710, 1370, 16, 24); bb = B.rect(270, 650, 750, 1370, 16, 24)
    def under(i, j, c):                                                    # hoodie hidden under the hair
        if is_hair(c) or (c[0] - c[2] > 12 and c[0] < 110): return (30, 30, 32)   # hair / hair-edge smudge
        return c
    def strand(g):                                                         # solid hair only, no stray pixels
        h = {k for k, c in g.items() if is_hair(c) and c[0] >= 78}
        nb = lambda i, j: sum((i+a, j+b) in h for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        return {k for k in h if nb(*k) >= 2 or k[1] == 0}
    hf, hb = strand(bf), strand(bb)
    put(20, 20, bf, fn=under); put(32, 20, bb, fn=under)
    put(20, 36, bf, keep=lambda i, j, c: (i, j) in hf); put(32, 36, bb, keep=lambda i, j, c: (i, j) in hb)
    solid(16, 20, 4, 12, HOOD); solid(28, 20, 4, 12, HOOD); solid(20, 16, 8, 4, (48, 49, 52)); solid(28, 16, 8, 4, (26, 26, 28))

    # ---- arms ----
    aw = 3 if slim else 4
    def arm(x, y, ox, oy, front, back):
        nohair = lambda i, j, c: (30, 30, 32) if is_hair(c) else c
        wide = {(i, j): back[min(2*aw-1, i*2*aw//8), j] for i in range(8) for j in range(24)}
        bulge = lambda i, j, c: j <= 4 or 17 <= j <= 21
        for bx, by, keep in ((x, y, None), (ox, oy, bulge)):
            put(bx, by+4, wide, keep, fn=nohair); put(bx+4, by+4, front, keep, fn=nohair)
            put(bx+4+aw, by+4, wide, keep, fn=nohair); put(bx+8+aw, by+4, back, keep, fn=nohair)
            solid(bx+4, by, aw, 4, (50, 51, 54))
        solid(x+4+aw, y, aw, 4, bright(front[2, 23]))
    arm(40, 16, 40, 32, F.rect(70, 625, 240, 1345, 2*aw, 24), B.rect(750, 625, 905, 1345, 2*aw, 24))
    arm(32, 48, 48, 48, F.rect(710, 625, 880, 1345, 2*aw, 24), B.rect(100, 625, 270, 1345, 2*aw, 24))

    # ---- legs ----
    def leg(x, y, front, back):
        put(x+4, y+4, front); put(x+12, y+4, back); put(x, y+4, back); put(x+8, y+4, back, flip=True)
        solid(x+4, y, 4, 4, bright(front[3, 1])); solid(x+8, y, 4, 4, bright(front[3, 23]))
    leg(0, 16, F.rect(240, 1375, 470, 2030, 8, 24), B.rect(505, 1375, 740, 2030, 8, 24))
    leg(16, 48, F.rect(475, 1375, 710, 2030, 8, 24), B.rect(270, 1375, 505, 2030, 8, 24))
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
    for ex in (0, 12):                                                             # cat ears: grey fur, light inside
        for i in range(4):
            for j in range(4, 8):
                inner = i in (1, 2) and j in (5, 6)
                px[80+ex+i, j] = (244, 232, 228, 255) if inner else (146, 136, 128, 255)
    return img

if __name__ == "__main__":
    for slim, tag in ((True, "slim"), (False, "classic")):
        clean = build(slim)
        clean.save(f"skin_{tag}_128.png"); v2(clean).save(f"skin_{tag}_128_v2.png")
