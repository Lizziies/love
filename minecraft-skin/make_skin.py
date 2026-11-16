# Generates the 128x128 Bedrock skin (slim arms) modelled on the reference render.
from PIL import Image

C = {
 'H':(205,172,138),'L':(176,140,106),'M':(152,119,90),'D':(118,90,68),'S':(72,54,44),
 'm':(164,130,98),'d':(135,104,79),
 'k':(236,198,178),'b':(228,176,162),'c':(60,50,46),
}
SHIRT_T,SHIRT=(240,236,230),(214,204,192)
HOOD,HOOD_L,POCKET,HOOD_D=(30,30,32),(42,43,46),(47,48,52),(22,22,24)
J_L,J_M,J_B,J_I=(74,84,100),(63,72,89),(54,62,78),(42,48,62)
SOLE,SOLE_G,TONGUE,SHOE,CUFF=(226,218,206),(168,166,162),(190,190,190),(22,22,24),(228,218,205)
EYE_T,EYE_B=(112,134,154),(160,184,198)

def build(slim=True):
    img = Image.new("RGBA",(128,128),(0,0,0,0)); px = img.load()
    def fill(x,y,w,h,fn):                      # x,y,w,h in 64-res units; fn gets half-pixel coords
        X,Y,W,Hh = int(2*x),int(2*y),int(2*w),int(2*h)
        for v in range(Hh):
            for u in range(W):
                c = fn(u,v,W,Hh)
                if c: px[X+u,Y+v] = tuple(c)+(255,)
    def chunky(rows):                          # 8x8 char map -> fn
        rows=[r.split() for r in rows]
        return lambda u,v,w,h: C.get(rows[v//2][u//2])

    # ---------------- HEAD ----------------
    FRONT = ["D M M M M M M D",
             "M H D M M M H M",
             "D M D M L D M D",
             "M L D M L D L M",
             "L L S M L S L L",
             "D S S k k S S D",
             "L b e k k e b L",
             "M L b k k b L M"]
    fr = chunky(FRONT)
    def front(u,v,w,h):
        r=FRONT[v//2].split()[u//2]
        if r=='e': return EYE_T if v%2==0 else EYE_B
        return fr(u,v,w,h)
    def front_o(u,v,w,h):
        cx,cy=u//2,v//2
        r=FRONT[cy].split()[cx]
        if r in 'ekbS': return None
        if cy<=4 or cx in (0,7) or cy==7: return C[r]
    fill(8,8,8,8,front); fill(40,8,8,8,front_o)

    STR = "MmMdMmLmdMmMdM"                      # fine vertical strands
    EDGE = "DMDMLDLM"
    def side(mirror):
        def f(u,v,w,h):
            uf = 15-u if mirror else u          # distance from the front edge
            if uf<2: return C[EDGE[v//2]]
            t = STR[uf-2]
            if v<2: t = {'L':'M','m':'d','M':'d','d':'D','D':'D'}[t]
            if v in (7,8) and t=='L': t='H'
            return C[t]
        return f
    def side_o(mirror):
        def f(u,v,w,h):
            uf = 15-u if mirror else u
            if uf<2 and v>=6: return C[EDGE[v//2]]
            if 6<=uf<=11 and v<4: return C['L'] if v<2 else C['M']      # ear
            if uf>=14 and v in (6,7): return C['c']                      # clip
            if uf>=14 and 10<=v<=13: return C['L']
        return f
    fill(0,8,8,8,side(True));  fill(32,8,8,8,side_o(True))    # right side: front edge at its right
    fill(16,8,8,8,side(False)); fill(48,8,8,8,side_o(False))

    BACK = ["D M M M M M M D",
            "M H M M M M H M",
            "D M M M M M M D",
            "M L . . . . L M",
            "M L . . . . M M",
            "L M . . . . L M",
            "M H . . . . H M",
            "M L . . . . L M"]
    BSTR = "dMmLLmMd"
    def back(u,v,w,h):
        r=BACK[v//2].split()[u//2]
        if r!='.': return C[r]
        t=BSTR[u-4]
        if u in (7,8): t='H' if 7<=v<=11 else 'L'
        return C[t]
    def back_o(u,v,w,h):
        r=BACK[v//2].split()[u//2]
        if r!='.' : return C[r]
    fill(24,8,8,8,back); fill(56,8,8,8,back_o)

    TOPR = "DMMMLLLHHLLLMMMM"                   # back -> front
    def top(u,v,w,h):
        t=TOPR[v]
        if v>=14 and u//2 in (1,6): t='H'
        if u in (0,15): t='D' if t in 'MD' else 'M'
        return C[t]
    def top_o(u,v,w,h):
        if u//2 in (0,1,6,7) and 2<=v//2<=4:
            return C['H'] if (u//2 in (1,6) and v//2==3) else C['L']
    fill(8,0,8,8,top); fill(40,0,8,8,top_o)
    fill(16,0,8,8,lambda u,v,w,h: C['k'] if 2<=u<=13 and 2<=v<=13 else C['D'])

    # ---------------- BODY ----------------
    def bfront(u,v,w,h):
        if v<=4 and 6<=u<=9: return SHIRT_T if v<2 else SHIRT
        if 5<=v<=13 and u in (7,8): return SHIRT
        if v>=14 and u==7: return (196,196,198) if v%2==0 else (150,150,152)
        if v>=14 and u==8: return (120,120,124) if v%2==0 else (92,92,96)
        if v<=21:
            for cols,rows in (((4,5),(18,19)),((2,5),(20,20)),((1,5),(21,21))):
                if rows[0]<=v<=rows[1] and (cols[0]<=u<=cols[1] or cols[0]<=15-u<=cols[1]): return POCKET
        if v>=22: return HOOD_D
        if v<2: return HOOD_L
        return HOOD
    def bplain(u,v,w,h): return HOOD_D if v>=22 else HOOD_L if v<2 else HOOD
    fill(20,20,8,12,bfront); fill(32,20,8,12,bplain)
    fill(16,20,4,12,bplain); fill(28,20,4,12,bplain)
    fill(20,16,8,4,lambda u,v,w,h: SHIRT_T if 6<=u<=9 and v>=5 else HOOD_L)
    fill(28,16,8,4,lambda u,v,w,h: HOOD_D)

    def seg(t,u,v):                             # long soft blocks along a strand
        order="DdMmLH"; i=order.index(t)
        k=((v+u*5)//7)%3
        return order[max(0,min(5,i+(1 if k==0 else 0)-(1 if k==2 else 0)))]
    FL = [9,18,18,16,16,14]; FT="MLLmMd"        # hair lengths / tones over the chest
    def ofront(u,v,w,h):
        c = u if u<6 else 15-u if u>9 else None
        if c is None: return
        L = FL[c] - (1 if (u>9 and c in (3,5)) else 0)
        start = 1 if c==0 else 0
        if start<=v<L:
            t = seg(FT[c],u,v)
            if v==L-1: t={'H':'L','L':'m','m':'M','M':'d','d':'D','D':'D'}[t]
            return C[t]
    BL=[12,12,17,17,19,22,22,20,20,22,22,19,17,17,14,14]; BT="MdmLmMdmmdMmLmdM"
    def oback(u,v,w,h):
        if v<BL[u]:
            t=BT[u]
            if u in (7,8): t='H' if 8<=v<=17 else 'L'
            else: t=seg(t,u,v)
            if u in (2,3) and 6<=v<=12: t='H' if u==3 else 'L'
            if u in (12,13) and 8<=v<=13: t='H' if u==12 else 'L'
            return C[t]
    fill(20,36,8,12,ofront); fill(32,36,8,12,oback)

    # ---------------- ARMS ----------------
    aw = 3 if slim else 4
    def sleeve(u,v,w,h): return CUFF if v>=22 else HOOD
    def sleeve_o(u,v,w,h):
        if v<=4: return HOOD_L
        if 17<=v<=21: return (36,36,39)
    def arm(x,y,ox,oy):
        for (bx,by,fn,top_c,bot_c) in ((x,y,sleeve,HOOD_L,CUFF),(ox,oy,sleeve_o,HOOD_L,None)):
            fill(bx+4,by,aw,4,lambda u,v,w,h: top_c)
            if bot_c: fill(bx+4+aw,by,aw,4,lambda u,v,w,h: bot_c)
            fill(bx,by+4,4,12,fn); fill(bx+4,by+4,aw,12,fn)
            fill(bx+4+aw,by+4,4,12,fn); fill(bx+8+aw,by+4,aw,12,fn)
    arm(40,16,40,32); arm(32,48,48,48)

    # ---------------- LEGS ----------------
    def jeans(u,v,inner=None):
        if u==inner: return J_I
        lvl = (1 if 2<=u<=5 else 0) + (1 if (2<=v<=7 or 12<=v<=15) else 0)
        if u in (0,7): lvl = 0
        return (J_B,J_M,J_L)[lvl]
    def legface(kind,inner):
        def f(u,v,w,h):
            if v>=22: return SOLE_G if u==inner else SOLE
            if v>=20:
                if kind=='front' and v==20 and 2<=u<=5: return TONGUE
                return SHOE
            return jeans(u,v,inner)
        return f
    def leg(x,y,ox,oy,right):
        inn_f = 7 if right else 0               # inner column on the front face
        inn_b = 0 if right else 7
        fill(x+4,y,4,4,lambda u,v,w,h: J_B); fill(x+8,y,4,4,lambda u,v,w,h: SOLE_G)
        fill(x,y+4,4,12,legface('side',None)); fill(x+4,y+4,4,12,legface('front',inn_f))
        fill(x+8,y+4,4,12,legface('side',None)); fill(x+12,y+4,4,12,legface('back',inn_b))
        hem=lambda u,v,w,h: (58,67,84) if v in (18,19) else None
        for fx in (ox,ox+4,ox+8,ox+12): fill(fx,oy+4,4,12,hem)
    leg(0,16,0,32,True); leg(16,48,0,48,False)
    return img, aw

def preview(img, aw):
    A=2*aw; W=16+2*A
    out=Image.new("RGBA",(W*2+16,68),(92,100,120,255))
    def paste(x,y,w,h,dx,dy,ox):
        r=img.crop((int(2*x),int(2*y),int(2*x+2*w),int(2*y+2*h))); out.alpha_composite(r,(ox+dx,dy+2))
    ox=2
    paste(8,8,8,8,A,0,ox)
    paste(20,20,8,12,A,16,ox); paste(44,20,aw,12,0,16,ox); paste(36,52,aw,12,A+16,16,ox)
    paste(44,36,aw,12,0,16,ox); paste(52,52,aw,12,A+16,16,ox)
    paste(4,20,4,12,A,40,ox); paste(20,52,4,12,A+8,40,ox); paste(4,36,4,12,A,40,ox); paste(4,52,4,12,A+8,40,ox)
    paste(20,36,8,12,A,16,ox); paste(40,8,8,8,A,0,ox)
    ox=W+14
    paste(24,8,8,8,A,0,ox)
    paste(32,20,8,12,A,16,ox); paste(48+aw,20,aw,12,A+16,16,ox); paste(40+aw,52,aw,12,0,16,ox)
    paste(48+aw,36,aw,12,A+16,16,ox); paste(56+aw,52,aw,12,0,16,ox)
    paste(12,20,4,12,A+8,40,ox); paste(28,52,4,12,A,40,ox); paste(12,36,4,12,A+8,40,ox); paste(12,52,4,12,A,40,ox)
    paste(32,36,8,12,A,16,ox); paste(56,8,8,8,A,0,ox)
    return out.resize((out.width*8,out.height*8),Image.NEAREST)

if __name__=="__main__":
    for slim in (True,False):
        img,aw=build(slim); tag="slim" if slim else "classic"
        img.save(f"skin_{tag}_128.png"); preview(img,aw).save(f"preview_{tag}.png")
