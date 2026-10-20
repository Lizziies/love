/* Heart Formation — a dependency-free WebGL particle sculpture. */
(function () {
  'use strict';

  const VERTEX = `
    precision highp float;
    attribute vec3 aTarget;
    attribute vec4 aData;
    attribute float aKind;
    attribute float aTint;
    uniform float uTime;
    uniform float uFormation;
    uniform float uAspect;
    uniform float uDpr;
    uniform float uScale;
    uniform float uBurst;
    uniform mediump float uGlow;
    uniform vec2 uPointer;
    uniform vec3 uPrimary;
    uniform vec3 uSecondary;
    uniform vec3 uHighlight;
    varying vec3 vColor;
    varying float vAlpha;
    varying float vSparkle;
    const float PI = 3.141592653589793;
    const float TAU = 6.283185307179586;

    vec3 heart(float t) {
      float s = sin(t);
      return vec3(1.6 * s*s*s,
        (13.0*cos(t)-5.0*cos(2.0*t)-2.0*cos(3.0*t)-cos(4.0*t))*0.1+0.22, 0.0);
    }
    vec3 rotateY(vec3 p, float a) {
      return vec3(p.x*cos(a)+p.z*sin(a), p.y, -p.x*sin(a)+p.z*cos(a));
    }
    vec3 rotateX(vec3 p, float a) {
      return vec3(p.x, p.y*cos(a)-p.z*sin(a), p.y*sin(a)+p.z*cos(a));
    }
    vec3 rotateZ(vec3 p, float a) {
      return vec3(p.x*cos(a)-p.y*sin(a), p.x*sin(a)+p.y*cos(a), p.z);
    }
    void main() {
      float t = uTime;
      float progress = smoothstep(0.7 + aData.w*1.5, 10.7 + aData.w*1.3, uFormation);
      float shimmer = 0.73 + 0.27*sin(t*(0.55+aData.z) + aData.x*44.0);
      float size = mix(4.0, 9.0, pow(aData.w, 3.0));
      float alpha = (0.70 + aData.z*0.75)*shimmer;
      vec3 p;
      vec3 color = mix(uPrimary, uSecondary, smoothstep(0.1, 0.85, aTint));
      color = mix(color, uHighlight, 0.10+pow(aTint, 4.0)*0.82);
      float breath = 1.0 + sin(t*1.45)*0.017 + pow(max(sin(t*2.9),0.0),8.0)*0.011;

      if (aKind < 0.5) {
        vec3 target = aTarget * breath;
        target.z += sin(t*0.6 + aData.x*12.0)*0.012;
        target += normalize(aTarget + vec3(0.001)) * uBurst * (0.3 + aData.z*0.8);
        float angle = aData.x*TAU + t*(0.10+aData.z*0.10) + progress*5.4;
        float radius = 2.7 + aData.y*4.7;
        vec3 cloud = vec3(cos(angle)*radius, sin(angle)*radius*0.63,
          sin(aData.z*TAU + t*0.16)*3.1);
        cloud = rotateZ(cloud, 0.12*sin(t*0.15));
        p = mix(cloud, target, progress);
        // Fine helical motion survives until each particle reaches the surface.
        p += vec3(sin(angle*2.0), cos(angle*2.0), sin(angle)) * sin(progress*PI)*0.20;
        alpha *= 0.57 + 0.43*progress;
        size *= 0.85 + 0.15*progress;
      } else if (aKind < 1.5) {
        float phase = aData.x*TAU + t*(0.055+aData.y*0.025);
        p = heart(phase);
        p *= (0.972 + aData.y*0.036) * breath;
        p.z = (aData.y-0.5)*0.18 + sin(phase*3.0+t*0.4)*0.018;
        p += normalize(p+vec3(0.001))*uBurst*0.42;
        float bead = pow(max(sin(phase*2.0-t*1.0+aData.y*3.0),0.0),10.0);
        alpha = (0.30 + bead*0.70) * smoothstep(3.5, 10.5, uFormation);
        size = 4.2 + bead*3.2;
        color = mix(uPrimary, uHighlight, 0.2+bead*0.7);
      } else if (aKind < 2.5) {
        float group = floor(aData.y*3.0);
        float angle = aData.x*TAU + t*(0.16 + group*0.035);
        float radius = 2.05 + group*0.18 + (aData.z-0.5)*0.024;
        p = vec3(cos(angle)*radius, sin(angle)*radius*0.22, sin(angle)*radius*0.66);
        p = rotateZ(p, -0.24 + group*0.64);
        p.y += 0.04*sin(t*0.3+group);
        float trail = pow(0.5+0.5*cos(aData.x*TAU-t*0.22+group), 5.0);
        alpha = (0.055 + trail*0.90) * smoothstep(2.0, 6.0, uFormation)
          * (1.0-smoothstep(7.0,12.0,uFormation));
        size = 3.0 + trail*4.2;
        color = mix(uPrimary, uHighlight, trail*0.75);
        p *= 1.0 + uBurst*0.12;
      } else {
        p = aTarget;
        p.x += sin(t*0.035+aData.x*TAU)*0.18;
        p.y += cos(t*0.025+aData.z*TAU)*0.12;
        alpha = (0.16 + aData.z*0.38) * shimmer * (1.0-smoothstep(3.0,11.0,uFormation));
        size = 2.4 + pow(aData.w,4.0)*4.1;
        color = mix(vec3(0.46,0.43,0.55), uHighlight, aTint*0.6);
      }
      if (aKind < 2.5) {
        p = rotateY(p, sin(t*0.12)*0.10 + uPointer.x*0.19);
        p = rotateX(p, -0.045 + uPointer.y*0.10);
        p *= uScale;
        p.y += 0.05*uScale;
      } else {
        p.x += uPointer.x*0.055;
        p.y += uPointer.y*0.04;
      }
      float distance = 6.25-p.z;
      gl_Position = vec4(p.x/(uAspect*0.445), p.y/0.445,
        distance*1.0050125-0.20050125, distance);
      gl_PointSize = clamp(size*uDpr*(6.25/distance)*(1.0+uGlow*3.2), 1.0, 52.0*uDpr);
      vColor = color;
      vAlpha = alpha * (0.60+0.40*clamp((p.z+0.6)/1.15,0.0,1.0));
      vSparkle = step(0.994, aData.w) * (0.65 + 0.35*sin(t+aData.x*12.0));
    }
  `;

  const FRAGMENT = `
    precision mediump float;
    varying vec3 vColor;
    varying float vAlpha;
    varying float vSparkle;
    uniform mediump float uGlow;
    void main() {
      vec2 q = gl_PointCoord*2.0-1.0;
      float r2 = dot(q,q);
      if (r2 > 1.0) discard;
      float core = exp(-r2*18.0)*1.25;
      float halo = exp(-r2*4.8)*0.20;
      float rays = (exp(-abs(q.x)*38.0)+exp(-abs(q.y)*38.0))
        * exp(-r2*4.0)*vSparkle*0.18;
      float fine = core+halo+rays;
      float diffuse = exp(-r2*3.8)*0.028;
      float light = mix(fine,diffuse,uGlow)*vAlpha;
      gl_FragColor = vec4(vColor*light, light);
    }
  `;

  const PALETTES = {
    rose: [[1.0, 0.13, 0.38], [1.0, 0.48, 0.43], [1.0, 0.92, 0.83]],
    violet: [[0.49, 0.19, 1.0], [0.96, 0.30, 0.74], [0.83, 0.85, 1.0]],
    gold: [[1.0, 0.37, 0.08], [1.0, 0.67, 0.20], [1.0, 0.94, 0.72]]
  };

  function makeRandom(seed) {
    return function () {
      seed |= 0; seed = seed + 0x6D2B79F5 | 0;
      let r = Math.imul(seed ^ seed >>> 15, 1 | seed);
      r = r + Math.imul(r ^ r >>> 7, 61 | r) ^ r;
      return ((r ^ r >>> 14) >>> 0) / 4294967296;
    };
  }

  function buildParticles(mobile) {
    const random = makeRandom(840719);
    // Uniform area sampling avoids the bright seam that polar parameterizations
    // produce around a heart's notch. A polygon retains the exact outer contour.
    const outline=Array.from({length:256},(_,i)=>{
      const a=i/256*Math.PI*2,s=Math.sin(a);
      return [1.6*s*s*s,(13*Math.cos(a)-5*Math.cos(2*a)-2*Math.cos(3*a)-Math.cos(4*a))*0.1+0.22];
    });
    const inside=(x,y)=>{
      let result=false;
      for(let i=0,j=outline.length-1;i<outline.length;j=i++) {
        const a=outline[i],b=outline[j];
        if((a[1]>y)!==(b[1]>y) && x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]) result=!result;
      }
      return result;
    };
    // Radius to the outline along each ray, used only for shell depth.
    const radial=new Float32Array(1024);
    for(let i=0;i<radial.length;i++) {
      const a=i/radial.length*Math.PI*2,c=Math.cos(a),s=Math.sin(a);
      let lo=0,hi=2.5;
      for(let n=0;n<13;n++) { const mid=(lo+hi)*0.5; if(inside(c*mid,s*mid)) lo=mid; else hi=mid; }
      radial[i]=(lo+hi)*0.5;
    }
    const heartCount = mobile ? 10800 : 16000;
    const contourCount = 1400, orbitCount = 1600, starCount = 1000;
    const count = heartCount + contourCount + orbitCount + starCount;
    const data = new Float32Array(count*9);
    for (let i=0; i<count; i++) {
      let x=0, y=0, z=0, kind=0;
      let d0=random(), d1=random(), d2=random(), d3=random();
      if (i < heartCount) {
        do { x=(random()-0.5)*3.2; y=-1.48+random()*2.91; } while(!inside(x,y));
        const angle=(Math.atan2(y,x)+Math.PI*2)%(Math.PI*2);
        const boundary=radial[Math.floor(angle/(Math.PI*2)*radial.length)%radial.length];
        const radius=Math.min(1,Math.hypot(x,y)/boundary);
        z = Math.sqrt(Math.max(0,1-radius*radius))*0.55*(random()<0.5 ? -1 : 1);
        // A thin luminous shell with a little dust suspended within its volume.
        z *= i%5===0 ? random() : 0.86+random()*0.14;
        x += (random()-0.5)*0.010;
        y += (random()-0.5)*0.010;
      } else if (i < heartCount + contourCount) {
        kind=1;
        d0 = (i-heartCount)/contourCount;
        d1 = ((i-heartCount)%4)/3;
      } else if (i < heartCount + contourCount + orbitCount) {
        kind=2;
        const j=i-heartCount-contourCount;
        d0 = (j%534)/534;
        d1 = Math.min(0.999, Math.floor(j/534)/3+0.01);
      } else {
        kind=3;
        x = (random()-0.5)*23;
        y = (random()-0.5)*16;
        z = -8+random()*10;
      }
      const o=i*9;
      data[o]=x; data[o+1]=y; data[o+2]=z;
      data[o+3]=d0; data[o+4]=d1; data[o+5]=d2; data[o+6]=d3;
      data[o+7]=kind; data[o+8]=random();
    }
    return { data, count };
  }

  class HeartEngine {
    constructor(canvas, options={}) {
      if (!canvas || typeof canvas.getContext !== 'function') throw new Error('HeartEngine needs a canvas.');
      this.canvas=canvas;
      this.options=options;
      this.elapsed=0;
      this.paused=false;
      this.speed=1;
      this.reducedMotion=false;
      this._disposed=false;
      this._ready=false;
      this._lost=false;
      this._lastTime=0;
      this._lastPhase='';
      this._lastPhaseProgress=-1;
      this._burstAt=-100;
      this._pointer=[0,0];
      this._pointerTarget=[0,0];
      this._palette='rose';
      this._colors=PALETTES.rose.map(c=>c.slice());
      this._targetColors=PALETTES.rose;

      const gl=canvas.getContext('webgl', { alpha:true, antialias:false, depth:false, stencil:false, premultipliedAlpha:true, powerPreference:'high-performance' });
      if (!gl) throw new Error('WebGL is unavailable in this browser.');
      this.gl=gl;
      this._program=this._createProgram();
      this._uniforms={};
      ['Time','Formation','Aspect','Dpr','Scale','Burst','Glow','Pointer','Primary','Secondary','Highlight'].forEach(name=>{
        this._uniforms[name]=gl.getUniformLocation(this._program,'u'+name);
      });
      const particles=buildParticles(window.innerWidth<700);
      this.particleCount=particles.count;
      this._buffer=gl.createBuffer();
      gl.bindBuffer(gl.ARRAY_BUFFER,this._buffer);
      gl.bufferData(gl.ARRAY_BUFFER,particles.data,gl.STATIC_DRAW);
      this._attributes=[['aTarget',3,0],['aData',4,3],['aKind',1,7],['aTint',1,8]].map(([name,size,offset])=>({ location:gl.getAttribLocation(this._program,name),size,offset }));
      gl.useProgram(this._program);
      gl.enable(gl.BLEND);
      gl.blendFunc(gl.ONE,gl.ONE);
      gl.disable(gl.DEPTH_TEST);
      gl.clearColor(0,0,0,0);

      this._resize=this._resize.bind(this);
      this._frame=this._frame.bind(this);
      this._onPointer=(event)=>{
        if (this.reducedMotion || event.pointerType==='touch') return;
        const rect=this.canvas.getBoundingClientRect();
        this._pointerTarget[0]=Math.max(-1,Math.min(1,(event.clientX-rect.left)/Math.max(rect.width,1)*2-1));
        this._pointerTarget[1]=Math.max(-1,Math.min(1,1-(event.clientY-rect.top)/Math.max(rect.height,1)*2));
      };
      this._onPointerLeave=()=>{ this._pointerTarget[0]=0; this._pointerTarget[1]=0; };
      this._onVisibility=()=>{ this._lastTime=0; };
      this._onContextLost=(event)=>{
        event.preventDefault();
        this._lost=true;
        cancelAnimationFrame(this._raf);
        const error=new Error('The graphics context was interrupted. Reload to restart the animation.');
        if (typeof this.options.onError==='function') this.options.onError(error);
        this.canvas.dispatchEvent(new CustomEvent('heartengineerror',{detail:error}));
      };
      canvas.addEventListener('webglcontextlost',this._onContextLost,false);
      window.addEventListener('pointermove',this._onPointer,{passive:true});
      window.addEventListener('pointerout',this._onPointerLeave,{passive:true});
      window.addEventListener('resize',this._resize,{passive:true});
      document.addEventListener('visibilitychange',this._onVisibility);
      if (typeof ResizeObserver!=='undefined') {
        this._observer=new ResizeObserver(this._resize);
        this._observer.observe(canvas);
      }
      this._resize();
      this._raf=requestAnimationFrame(this._frame);
    }

    _createProgram() {
      const gl=this.gl;
      const shaders=[];
      const compile=(type,source)=>{
        const shader=gl.createShader(type);
        gl.shaderSource(shader,source);
        gl.compileShader(shader);
        if (!gl.getShaderParameter(shader,gl.COMPILE_STATUS)) {
          const log=gl.getShaderInfoLog(shader);
          gl.deleteShader(shader);
          shaders.forEach(s=>gl.deleteShader(s));
          throw new Error('Heart shader could not compile: '+log);
        }
        shaders.push(shader);
        return shader;
      };
      const vertex=compile(gl.VERTEX_SHADER,VERTEX), fragment=compile(gl.FRAGMENT_SHADER,FRAGMENT);
      const program=gl.createProgram();
      gl.attachShader(program,vertex); gl.attachShader(program,fragment); gl.linkProgram(program);
      shaders.forEach(s=>gl.deleteShader(s));
      if (!gl.getProgramParameter(program,gl.LINK_STATUS)) {
        const log=gl.getProgramInfoLog(program); gl.deleteProgram(program);
        throw new Error('Heart shader could not link: '+log);
      }
      return program;
    }

    _resize() {
      if (this._disposed || this._lost) return;
      const rect=this.canvas.getBoundingClientRect();
      const width=Math.max(1,rect.width || window.innerWidth);
      const height=Math.max(1,rect.height || window.innerHeight);
      this._dpr=Math.min(window.devicePixelRatio || 1,1.8);
      const w=Math.round(width*this._dpr), h=Math.round(height*this._dpr);
      if (this.canvas.width!==w || this.canvas.height!==h) { this.canvas.width=w; this.canvas.height=h; }
      this._aspect=width/height;
      this._scale=Math.min(1,this._aspect/0.72);
      this.gl.viewport(0,0,w,h);
    }

    _frame(now) {
      if (this._disposed || this._lost) return;
      const dt=this._lastTime ? Math.min((now-this._lastTime)/1000,0.05) : 0;
      this._lastTime=now;
      if (!this.paused && !document.hidden) this.elapsed+=dt*this.speed;
      const blend=1-Math.exp(-dt*4);
      for (let i=0;i<2;i++) this._pointer[i]+=(this._pointerTarget[i]-this._pointer[i])*blend;
      for (let i=0;i<3;i++) for (let j=0;j<3;j++) this._colors[i][j]+=(this._targetColors[i][j]-this._colors[i][j])*blend;
      if (!document.hidden) this._draw();
      if (!this._ready) { this._ready=true; if (typeof this.options.onReady==='function') this.options.onReady(this); }
      this._notifyPhase();
      this._raf=requestAnimationFrame(this._frame);
    }

    _draw() {
      const gl=this.gl, u=this._uniforms;
      const age=this.elapsed-this._burstAt;
      const burst=this.reducedMotion ? 0 : Math.sin(Math.min(Math.PI,Math.max(0,age)*3.3))*Math.exp(-Math.max(0,age)*1.3)*1.75;
      gl.useProgram(this._program);
      gl.bindBuffer(gl.ARRAY_BUFFER,this._buffer);
      this._attributes.forEach(a=>{ gl.enableVertexAttribArray(a.location); gl.vertexAttribPointer(a.location,a.size,gl.FLOAT,false,36,a.offset*4); });
      gl.uniform1f(u.Time,this.reducedMotion ? 14 : this.elapsed);
      gl.uniform1f(u.Formation,this.reducedMotion ? 14 : this.elapsed);
      gl.uniform1f(u.Aspect,this._aspect);
      gl.uniform1f(u.Dpr,this._dpr);
      gl.uniform1f(u.Scale,this._scale);
      gl.uniform1f(u.Burst,burst);
      gl.uniform2f(u.Pointer,this._pointer[0],this._pointer[1]);
      gl.uniform3fv(u.Primary,this._colors[0]);
      gl.uniform3fv(u.Secondary,this._colors[1]);
      gl.uniform3fv(u.Highlight,this._colors[2]);
      gl.clear(gl.COLOR_BUFFER_BIT);
      gl.uniform1f(u.Glow,1);
      gl.drawArrays(gl.POINTS,0,this.particleCount);
      gl.uniform1f(u.Glow,0);
      gl.drawArrays(gl.POINTS,0,this.particleCount);
    }

    _notifyPhase() {
      const t=this.reducedMotion ? 12 : this.elapsed;
      const progress=Math.min(1,t/12);
      const name=t<2.4 ? 'awakening' : t<6.4 ? 'gathering' : t<12 ? 'forming' : 'alive';
      if (name!==this._lastPhase || Math.abs(progress-this._lastPhaseProgress)>=0.004) {
        this._lastPhase=name; this._lastPhaseProgress=progress;
        if (typeof this.options.onPhase==='function') this.options.onPhase(name,progress);
      }
    }

    setPalette(name) {
      if (!PALETTES[name]) return;
      this._palette=name;
      this._targetColors=PALETTES[name];
    }
    setSpeed(value) {
      const number=Number(value);
      if (Number.isFinite(number)) this.speed=Math.max(0.1,Math.min(3,number));
    }
    togglePause() { this.paused=!this.paused; this._lastTime=0; return this.paused; }
    replay() {
      this.elapsed=0; this._burstAt=-100; this._lastTime=0; this.paused=false;
      this._lastPhase=''; this._lastPhaseProgress=-1;
      this._notifyPhase();
    }
    burst() {
      if (!this.reducedMotion && !this._disposed) this._burstAt=this.elapsed;
    }
    setReducedMotion(value) {
      this.reducedMotion=Boolean(value);
      this._pointerTarget=[0,0];
      this._pointer=[0,0];
      this._lastPhase='';
      this._notifyPhase();
    }
    dispose() {
      if (this._disposed) return;
      this._disposed=true;
      cancelAnimationFrame(this._raf);
      if (this._observer) this._observer.disconnect();
      window.removeEventListener('pointermove',this._onPointer);
      window.removeEventListener('pointerout',this._onPointerLeave);
      window.removeEventListener('resize',this._resize);
      document.removeEventListener('visibilitychange',this._onVisibility);
      this.canvas.removeEventListener('webglcontextlost',this._onContextLost);
      if (!this._lost) { this.gl.deleteBuffer(this._buffer); this.gl.deleteProgram(this._program); }
    }
  }

  window.HeartEngine=HeartEngine;
})();
