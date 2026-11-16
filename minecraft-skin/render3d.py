# Tiny software renderer: draws a skin as a 3D figure (front, 3/4, back) for checking.
import math, sys
from PIL import Image, ImageDraw
def render(path, out, slim=True, S=14, views=((0,8),(35,8),(180,8))):
    tex = Image.open(path).convert("RGBA"); T = tex.load(); R = tex.width//64
    aw = 3 if slim else 4; ax = 4 + aw/2
    parts = [((0,28,0),(8,8,8),(0,0),(32,0),.5), ((0,18,0),(8,12,4),(16,16),(16,32),.25),
             ((-ax,18,0),(aw,12,4),(40,16),(40,32),.25), ((ax,18,0),(aw,12,4),(32,48),(48,48),.25),
             ((-2,6,0),(4,12,4),(0,16),(0,32),.25), ((2,6,0),(4,12,4),(16,48),(0,48),.25)]
    W, H = 26*S, 40*S
    img = Image.new("RGB", (W*len(views), H), (96,104,122))
    for vi, (yaw, pitch) in enumerate(views):
        a = math.radians(yaw); p = math.radians(pitch); polys = []
        def proj(P):
            x, y, z = P
            x, z = x*math.cos(a)+z*math.sin(a), -x*math.sin(a)+z*math.cos(a)
            y, z = y*math.cos(p)-z*math.sin(p), y*math.sin(p)+z*math.cos(p)
            return (vi*W + W/2 + x*S, H/2 + 17*S*math.cos(p) - y*S, z)
        for (c, (w,h,d), uv, ouv, inf) in parts:
            for (U, V), g in ((uv, 0), (ouv, inf)):
                k = [(s+2*g)/s for s in (w,h,d)]
                hw, hh, hd = w/2+g, h/2+g, d/2+g
                faces = [  # tex origin, tex size, 3D origin, du, dv, normal
                 ((U,V+d),(d,h),(-hw,hh,-hd),(0,0,k[2]),(0,-k[1],0),(-1,0,0)),
                 ((U+d,V+d),(w,h),(-hw,hh,hd),(k[0],0,0),(0,-k[1],0),(0,0,1)),
                 ((U+d+w,V+d),(d,h),(hw,hh,hd),(0,0,-k[2]),(0,-k[1],0),(1,0,0)),
                 ((U+2*d+w,V+d),(w,h),(hw,hh,-hd),(-k[0],0,0),(0,-k[1],0),(0,0,-1)),
                 ((U+d,V),(w,d),(-hw,hh,-hd),(k[0],0,0),(0,0,k[2]),(0,1,0)),
                 ((U+d+w,V),(w,d),(-hw,-hh,-hd),(k[0],0,0),(0,0,k[2]),(0,-1,0))]
                for (tu,tv),(tw,th),O,du,dv,n in faces:
                    nz = proj(n)[2] - proj((0,0,0))[2]
                    if nz <= 0.01: continue
                    lit = 0.78 + 0.22*nz if n[1] == 0 else 1.0
                    for j in range(int(th*R)):
                        for i in range(int(tw*R)):
                            col = T[int(tu*R)+i, int(tv*R)+j]
                            if col[3] < 128: continue
                            q = []
                            for (di, dj) in ((0,0),(1,0),(1,1),(0,1)):
                                P = [c[m] + O[m] + du[m]*(i+di)/R + dv[m]*(j+dj)/R for m in range(3)]
                                q.append(proj(P))
                            polys.append((sum(t[2] for t in q)/4 + (0.01 if g else 0), [(t[0], t[1]) for t in q],
                                          tuple(int(v*lit) for v in col[:3])))
        dr = ImageDraw.Draw(img)
        for _, q, col in sorted(polys, key=lambda t: t[0]): dr.polygon(q, fill=col)
    img.save(out)
if __name__ == "__main__":
    allv = "--all" in sys.argv
    v = ((0,8),(35,8),(90,8),(180,8),(270,8),(325,8),(20,60),(200,60)) if allv else ((0,8),(35,8),(180,8))
    render(sys.argv[1], sys.argv[2], slim="classic" not in sys.argv[1], views=v, S=10 if allv else 14)
