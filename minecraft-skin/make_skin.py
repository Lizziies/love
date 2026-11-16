import math, random, sys
from PIL import Image

def build(slim=True):
    img = Image.new("RGBA", (128,128), (0,0,0,0))
    px = img.load()
    rng = random.Random(7)
    tab = [[rng.uniform(-1,1) for _ in range(64)] for _ in range(16)]
    def noise(a,b,s=0):
        return random.Random(a*928371 + b*1237 + s*77).uniform(-1,1)
    def lerp(a,b,t): return tuple(int(round(a[i]+(b[i]-a[i])*t)) for i in range(3))
    HD,HM,HL = (120,86,56),(176,136,96),(216,182,136)
    def hair(u,v,seed=0,lighten=0.0):
        c = u + int(round(math.sin(v/2.6+seed*1.7)))
        t = 0.5 + 0.33*tab[seed%16][(c+20)%64] + 0.07*noise(u,v,seed) + lighten
        t = max(0,min(1,t))
        col = lerp(HD,HM,t*2) if t<0.5 else lerp(HM,HL,(t-0.5)*2)
        return col+(255,)
    SK,SKS = (238,200,172),(220,176,150)
    def skin(u,v,s=0):
        n = noise(u,v,40+s)*3
        return tuple(int(c+n) for c in SK)+(255,)
    def hood(u,v,s=0,light=0.0):
        n = noise(u,v,60+s)*3
        b = 30+n+light
        return (int(b),int(b),int(b+4),255)
    def fill(x,y,w,h,fn):
        x,y,w,h = 2*x,2*y,int(2*w),int(2*h)
        for v in range(h):
            for u in range(w):
                c = fn(u,v,w,h)
                if c: px[x+u,y+v] = c

    # ---------- HEAD ----------
    def fmask(u,v):
        lim = {5:5,6:4,7:3,8:2,9:2}.get(v,1)
        return v<=4 or u<=lim or u>=15-lim
    def face(u,v,w,h):
        if fmask(u,v): return hair(u,v,1, 0.08 if v<3 else 0)
        eyes = {
          (3,9):(74,48,38),(4,9):(74,48,38),(5,9):(74,48,38),(2,9):(74,48,38),
          (3,10):(246,246,250),(4,10):(104,150,190),(5,10):(58,96,142),
          (3,11):(246,246,250),(4,11):(150,190,216),(5,11):(104,150,190),
        }
        for (a,b),c in list(eyes.items()): eyes[(15-a,b)] = c
        if (u,v) in eyes: return eyes[(u,v)]+(255,)
        if v==12 and (2<=u<=4 or 11<=u<=13): return (242,168,158,255)
        if v==13 and u in (7,8): return (208,128,124,255)
        if v==12 and u in (7,8): return SKS+(255,)
        if fmask(u,v-1) or fmask(u-1,v) or fmask(u+1,v): return SKS+(255,)
        return skin(u,v)
    def top(u,v,w,h):
        c = hair(v, u if u<8 else 15-u, 2, 0.1)   # strands flow sideways from parting
        if u in (7,8) and v>=5: c = hair(u,v,2,-0.3)
        return c
    for ox in (0,32):
        fill(ox+8,8,8,8, face if ox==0 else (lambda u,v,w,h: hair(u,v,1,0.08 if v<3 else 0) if fmask(u,v) else None))
        fill(ox+8,0,8,8, top)
        fill(ox+0,8,8,8, lambda u,v,w,h: hair(u,v,3))
        fill(ox+16,8,8,8, lambda u,v,w,h: hair(u,v,4))
        fill(ox+24,8,8,8, lambda u,v,w,h: hair(u,v,5))
    fill(16,0,8,8, lambda u,v,w,h: skin(u,v,1) if 2<=u<=13 and v>=2 else hair(u,v,6,-0.2))

    # ---------- BODY ----------
    def bfront(u,v,w,h):
        half = 3 if v<=9 else 2 if v<=12 else 1 if v<=14 else 0
        if half and 8-half<=u<=7+half:
            g = 240 - (6 if u in (8-half,7+half) else 0) + noise(u,v,9)*3
            return (int(g),int(g),int(g-4),255)
        if u in (7,8) and v>=15: return (150,152,160,255) if (v+u)%2 else (110,112,120,255)
        if half and u in (7-half,8+half): return hood(u,v,0,10)       # lapel edge
        if v>=22: return hood(u,v,0,-8 if u%2 else -3)               # ribbed hem
        if 16<=v<=20 and (u-2==(v-16)//2+0 or 13-u==(v-16)//2): return hood(u,v,0,12)  # pockets
        return hood(u,v,0, 6 if v<2 else 0)
    def bback(u,v,w,h):
        if v<=7 and abs(u-7.5)<=6.5-max(0,v-4)*1.2: return hood(u,v,1,9 if v==7 or abs(u-7.5)>5 else 5)
        if v>=22: return hood(u,v,1,-8 if u%2 else -3)
        return hood(u,v,1)
    def bside(u,v,w,h): return hood(u,v,2,-8 if v>=22 and u%2 else 0)
    fill(20,20,8,12,bfront); fill(32,20,8,12,bback)
    fill(16,20,4,12,bside); fill(28,20,4,12,bside)
    fill(20,16,8,4, lambda u,v,w,h: (238,236,232,255) if 5<=u<=10 and v>=3 else hood(u,v,3,6))
    fill(28,16,8,4, lambda u,v,w,h: hood(u,v,4,-8))
    # hair falling over body (jacket layer)
    LF = [16,19,18,14,9]; RF = [17,20,16,13,8]
    def ofront(u,v,w,h):
        if u<5 and v<LF[u]: return hair(u,v,7, 0.1 if v>LF[u]-4 else 0)
        if u>10 and v<RF[15-u]: return hair(u,v,8, 0.1 if v>RF[15-u]-4 else 0)
    def oback(u,v,w,h):
        L = 23 - abs(u-7.5)*1.3 + (1 if u%3==0 else 0)
        if 1<=u<=14 and v<L: return hair(u,v,5, 0.12 if v>L-5 else 0)
    fill(20,36,8,12,ofront); fill(32,36,8,12,oback)

    # ---------- ARMS ----------
    aw = 3 if slim else 4
    def sleeve(s):
        def f(u,v,w,h):
            if v>=22: return skin(u,v,s)
            if v==21: return (240,238,232,255)
            if v>=19: return hood(u,v,s,-8 if u%2 else -3)
            return hood(u,v,s, 7 if v<2 else (4 if (u+v//5)%5==0 else 0))
        return f
    def arm(x,y,s):
        fill(x+4,y,aw,4, lambda u,v,w,h: hood(u,v,s,7))
        fill(x+4+aw,y,aw,4, lambda u,v,w,h: skin(u,v,s))
        fill(x,y+4,4,12,sleeve(s)); fill(x+4,y+4,aw,12,sleeve(s+1))
        fill(x+4+aw,y+4,4,12,sleeve(s+2)); fill(x+8+aw,y+4,aw,12,sleeve(s+3))
    arm(40,16,10); arm(32,48,20)

    # ---------- LEGS ----------
    def leg(s, front=False, side=False):
        def f(u,v,w,h):
            if v>=22: return (232,228,220,255) if v==22 else (200,196,190,255)
            if v>=20:
                if front and v==20 and u in (3,4): return (225,225,225,255)
                b = 28+noise(u,v,s)*3; return (int(b),int(b),int(b+3),255)
            fade = 10*math.exp(-((v-8)**2)/30.0) if 2<=u<=5 else 0
            chk = 5 if ((u//2)+(v//3))%2==0 else -3
            edge = -10 if u in (0,7) else 0
            n = noise(u,v,s)*4
            k = fade+chk+edge+n - (8 if v>=18 else 0)
            return (int(80+k),int(102+k),int(134+k),255)
        return f
    def legs(x,y,s):
        fill(x+4,y,4,4, lambda u,v,w,h:(74,94,124,255))
        fill(x+8,y,4,4, lambda u,v,w,h:(196,192,186,255))
        fill(x,y+4,4,12,leg(s)); fill(x+4,y+4,4,12,leg(s+1,front=True))
        fill(x+8,y+4,4,12,leg(s+2)); fill(x+12,y+4,4,12,leg(s+3))
    legs(0,16,30); legs(16,48,40)
    return img, aw

def preview(img, aw):
    A = 2*aw
    W = 16+2*A; H = 64
    out = Image.new("RGBA",(W*2+12,H+4),(92,100,120,255))
    def paste(x,y,w,h,dx,dy,ox):
        r = img.crop((2*x,2*y,2*x+int(2*w),2*y+int(2*h)))
        out.alpha_composite(r,(ox+dx,dy+2))
    # front
    ox=2
    for o in (0,):
        paste(8,8,8,8,A,0,ox); paste(40,8,8,8,A,0,ox)
        paste(20,20,8,12,A,16,ox); paste(44,20,aw,12,0,16,ox); paste(36,52,aw,12,A+16,16,ox)
        paste(4,20,4,12,A,40,ox); paste(20,52,4,12,A+8,40,ox)
        paste(20,36,8,12,A,16,ox)
    ox = W+10
    paste(24,8,8,8,A,0,ox); paste(56,8,8,8,A,0,ox)
    paste(32,20,8,12,A,16,ox)
    paste(44+aw+4+ (0),20,aw,12,A+16,16,ox)          # right arm back
    paste(36+aw+4,52,aw,12,0,16,ox)                  # left arm back
    paste(12,20,4,12,A+8,40,ox); paste(28,52,4,12,A,40,ox)
    paste(32,36,8,12,A,16,ox)
    return out.resize((out.width*8,out.height*8),Image.NEAREST)

for slim in (True,False):
    img,aw = build(slim)
    name = "skin_slim_128.png" if slim else "skin_classic_128.png"
    img.save(name)
    preview(img,aw).save("preview_"+("slim" if slim else "classic")+".png")
