// BC Informática · motor de plantillas para Instagram (v2: fondos lisos + íconos)
// Uso: node render.js spec.json salida.png
// spec = {
//   "tipo": "novedad" | "carrusel_portada" | "carrusel_slide" | "reel_portada" | "como_trabajo",
//   "fondo": "grafito" | "bosque" | "crema" | "lima",          (opcional, cada tipo tiene uno por defecto)
//   "icono": "hacker" | "anzuelo" | "ia" | "pc" | "notebook" | "disco" | "celular" | "escudo" | "herramienta",  (opcional)
//   ...campos de texto. *palabra* = resaltado
// }
// Requiere en la misma carpeta: logo_crema.png, logo_negro.png, logo_lima.png, iconos.js
// y npm i @fontsource/anton @fontsource/inter @fontsource/jetbrains-mono   (playwright ya instalado)
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const ICON = require('./iconos.js');
const RETRO = JSON.parse(fs.readFileSync(path.join(__dirname,'iconos_retro.json'),'utf8'));
const pixel = (name) => { const g = RETRO.iconos[name]; let r='';
  g.forEach((row,y)=>[...row].forEach((c,x)=>{ if(c!=='.') r+=`<rect x="${x}" y="${y}" width="1.02" height="1.02" fill="${RETRO.pal[c]}"/>`; }));
  return `<svg viewBox="0 0 16 16" shape-rendering="crispEdges">${r}</svg>`; };
// Ventanita retro (barra de título + botones) para cajas de texto
const VENTANA = (titulo, cuerpo, th) => `<div class="win"><div class="wbar"><span>${titulo}</span><i></i><i></i><i class="x"></i></div><div class="wbody">${cuerpo}</div></div>`;

const D = __dirname;
const f = (p) => 'file://' + path.join(D, p);
const FONTS = `
@font-face{font-family:Anton;src:url(${f('node_modules/@fontsource/anton/files/anton-latin-400-normal.woff2')})}
@font-face{font-family:Anton;src:url(${f('node_modules/@fontsource/anton/files/anton-latin-ext-400-normal.woff2')});unicode-range:U+0100-024F}
@font-face{font-family:Inter;font-weight:400;src:url(${f('node_modules/@fontsource/inter/files/inter-latin-400-normal.woff2')})}
@font-face{font-family:Inter;font-weight:600;src:url(${f('node_modules/@fontsource/inter/files/inter-latin-600-normal.woff2')})}
@font-face{font-family:Inter;font-weight:800;src:url(${f('node_modules/@fontsource/inter/files/inter-latin-800-normal.woff2')})}
@font-face{font-family:Mono;font-weight:500;src:url(${f('node_modules/@fontsource/jetbrains-mono/files/jetbrains-mono-latin-500-normal.woff2')})}
@font-face{font-family:Mono;font-weight:700;src:url(${f('node_modules/@fontsource/jetbrains-mono/files/jetbrains-mono-latin-700-normal.woff2')})}`;

const C = { crema:'#FBF8E6', crema2:'#F6F1E0', grafito:'#121412', bosque:'#1B4332', gris:'#8F9E8B', lima:'#C6FF00' };
const HANDLE = '@bc.informatica.pna';

// Temas: fondo, texto, resaltado, chip, caja, logo, ícono (tinta, relleno, acento, sombra)
const TEMA = {
  grafito: { bg:C.grafito, tx:C.crema, hl:`color:${C.lima}`, mut:C.gris, chipBg:C.lima, chipTx:C.grafito, box:C.bosque, boxTx:C.crema, boxB:C.lima, logo:'logo_negro.png', ic:[C.crema, C.bosque, C.lima, C.lima] },
  bosque:  { bg:C.bosque, tx:C.crema, hl:`color:${C.lima}`, mut:'#9fb59b', chipBg:C.lima, chipTx:C.grafito, box:C.grafito, boxTx:C.crema, boxB:C.lima, logo:'logo_negro.png', ic:[C.crema, C.grafito, C.lima, C.lima] },
  crema:   { bg:C.crema, tx:C.grafito, hl:`background:linear-gradient(transparent 58%, ${C.lima} 58%, ${C.lima} 92%, transparent 92%);padding:0 6px`, mut:C.gris, chipBg:C.bosque, chipTx:C.crema, box:C.crema2, boxTx:C.grafito, boxB:C.bosque, logo:'logo_crema.png', ic:[C.grafito, C.crema2, C.lima, C.bosque] },
  lima:    { bg:C.lima, tx:C.grafito, hl:`color:${C.bosque}`, mut:C.bosque, chipBg:C.grafito, chipTx:C.lima, box:C.grafito, boxTx:C.crema, boxB:C.bosque, logo:'logo_lima.png', ic:[C.grafito, C.crema, C.bosque, C.grafito] },
};

const hl = (s) => (s||'').replace(/\*(.+?)\*/g, `<span class="hl">$1</span>`);
const icono = (d, th, size, css='') => {
  if (!d.icono) return '';
  const [t, r, a, sh] = th.ic;
  if (RETRO.iconos[d.icono] && !d.icono_vector)
    { const dark = (th.bg===C.grafito||th.bg===C.bosque);
      const tile = dark ? `background:${C.crema2};padding:${Math.round(size*0.12)}px;border:5px solid;border-color:#FFFFFF ${C.gris} ${C.gris} #FFFFFF;box-sizing:border-box;box-shadow:10px 10px 0 ${sh};` : `filter:drop-shadow(10px 10px 0 ${sh});`;
      return `<div class="ico" style="width:${size}px;height:${size}px;${tile}${css}">${pixel(d.icono)}</div>`; }
  if (!ICON[d.icono]) return '';
  return `<div class="ico" style="width:${size}px;height:${size}px;filter:drop-shadow(12px 12px 0 ${sh});${css}">${ICON[d.icono](t, r, a)}</div>`;
};

const BASE = (th) => `
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:var(--w);height:var(--h)}
body{font-family:Inter;-webkit-font-smoothing:antialiased;position:relative;overflow:hidden;background:${th.bg};color:${th.tx}}
.ico{position:absolute}.ico svg{width:100%;height:100%;display:block}
.chip{font-family:Mono;font-weight:700;font-size:26px;letter-spacing:.06em;text-transform:uppercase;display:inline-block;padding:10px 18px;background:${th.chipBg};color:${th.chipTx}}
.h{font-family:Anton;text-transform:uppercase;line-height:.98;letter-spacing:.005em}
.hl{${th.hl}}
.foot{position:absolute;left:80px;right:80px;bottom:64px;display:flex;justify-content:space-between;align-items:center}
.foot img{height:56px}
.handle{font-family:Mono;font-weight:500;font-size:22px;letter-spacing:.08em;color:${th.mut}}
.mut{color:${th.mut}}
.win{background:#C3C7CB;border:4px solid;border-color:#FFFFFF #121412 #121412 #FFFFFF;box-shadow:10px 10px 0 ${th.ic[3]};color:${C.grafito}}
.wbar{background:${C.bosque};color:${C.crema};display:flex;align-items:center;gap:8px;padding:8px 10px 8px 16px;font-family:Mono;font-weight:700;font-size:22px;letter-spacing:.04em}
.wbar span{flex:1}
.wbar i{width:30px;height:28px;background:#C3C7CB;border:3px solid;border-color:#FFFFFF #121412 #121412 #FFFFFF}
.wbar i.x{position:relative}.wbar i.x:after{content:"×";position:absolute;inset:-6px 0 0 0;text-align:center;color:${C.grafito};font-family:Inter;font-weight:800;font-size:26px}
.wbody{background:#FFFFFF;margin:8px;border:3px solid;border-color:#7B7F84 #FFFFFF #FFFFFF #7B7F84;padding:28px 32px;font-size:32px;line-height:1.38}
`;
const FOOT = (th) => `<div class="foot"><img src="${f(th.logo)}"><span class="handle">${HANDLE}</span></div>`;

const T = {
  // 1 · NOVEDAD
  novedad: (d, th) => ({ w:1080, h:1350, html:`
  <style>
   .top{position:absolute;left:80px;right:80px;top:80px;display:flex;justify-content:space-between;align-items:center}
   .date{font-family:Mono;font-size:22px;letter-spacing:.06em}
   .mid{position:absolute;left:80px;right:80px;top:${d.icono?400:170}px;bottom:190px;display:flex;flex-direction:column;justify-content:center;gap:50px}
   .h{font-size:${d.tam||(d.icono?104:118)}px}
   .box{background:${th.box};color:${th.boxTx};padding:40px 46px;border-left:10px solid ${th.boxB}}
   .box b{font-family:Mono;font-weight:700;font-size:24px;letter-spacing:.06em;color:${th.boxB==C.lima?C.lima:C.lima};text-transform:uppercase;display:block;margin-bottom:16px}
   .box p{font-size:33px;line-height:1.35}
   .wt{display:block;font-family:Mono;font-size:24px;letter-spacing:.05em;text-transform:uppercase;color:${C.bosque};margin-bottom:12px}
   .src{position:absolute;left:80px;bottom:150px;font-family:Mono;font-size:20px}
  </style>
  <div class="top"><span class="chip">// ${d.etiqueta||'novedad'}</span><span class="date mut">${d.fecha||''}</span></div>
  ${icono(d, th, 250, 'right:92px;top:150px')}
  <div class="mid"><div class="h">${hl(d.titulo)}</div>
  ${VENTANA((d.ventana||'para_vos.txt'), `<b class="wt">${d.bajada_titulo||'¿Qué cambia para vos?'}</b>${d.bajada||''}`, th)}</div>
  <div class="src mut">Fuente: ${d.fuente||''}</div>
  ${FOOT(th)}`}),

  // 2a · CARRUSEL – portada
  carrusel_portada: (d, th) => ({ w:1080, h:1350, html:`
  <style>
   .chip{position:absolute;left:80px;top:80px}
   .corner{position:absolute;right:80px;top:84px;font-family:Mono;font-weight:700;font-size:26px}
   .h{position:absolute;left:80px;right:80px;top:220px;font-size:${d.tam||148}px}
   .sub{position:absolute;left:80px;right:${d.icono?430:180}px;bottom:300px;font-size:36px;line-height:1.35}
   .swipe{position:absolute;left:80px;bottom:190px;background:${th.tx};color:${th.bg==C.lima?C.lima:th.bg};font-family:Mono;font-weight:700;font-size:26px;padding:16px 26px;letter-spacing:.04em}
  </style>
  <span class="chip">// ${d.etiqueta||'tips'}</span><span class="corner mut">${d.contador||''}</span>
  <div class="h">${hl(d.titulo)}</div>
  ${icono(d, th, 300, 'right:92px;bottom:200px')}
  <div class="sub">${d.subtitulo||''}</div>
  ${d.sin_swipe?"":`<div class="swipe">Deslizá →</div>`}
  ${FOOT(th)}`}),

  // 2b · CARRUSEL – slide interior
  carrusel_slide: (d, th) => ({ w:1080, h:1350, html:`
  <style>
   .n{position:absolute;left:68px;top:40px;font-family:Anton;font-size:300px;line-height:1;color:${th.mut};opacity:.6}
   .h{position:absolute;left:80px;right:80px;top:420px;font-size:96px}
   .p{position:absolute;left:80px;right:110px;top:${d.top_texto||720}px;font-size:38px;line-height:1.42}
   .p b{font-weight:800}
   .tipw{position:absolute;left:80px;right:80px;bottom:180px}
   .tip{position:absolute;left:80px;right:80px;bottom:190px;display:flex;gap:22px;align-items:flex-start;font-size:30px;line-height:1.35;padding:30px 34px;background:${th.box};color:${th.boxTx};border:2px solid ${th.boxB}}
   .tip span{font-family:Mono;font-weight:700;font-size:22px;background:${C.lima};color:${C.grafito};padding:6px 12px;white-space:nowrap}
  </style>
  <div class="n">${d.numero||'01'}</div>
  ${icono(d, th, 220, 'right:92px;top:110px')}
  <div class="h">${hl(d.titulo)}</div>
  <div class="p">${d.texto||''}</div>
  ${d.tip?`<div class="tipw">${VENTANA('tip.txt', d.tip, th)}</div>`:''}
  ${FOOT(th)}`}),

  // 3 · PORTADA / CUADRO DE REEL (9:16; todo centrado dentro del recorte 3:4, y=240..1680)
  reel_portada: (d, th) => ({ w:1080, h:1920, html:`
  <style>
   .col{position:absolute;left:80px;right:80px;top:260px;bottom:260px;display:flex;flex-direction:column;justify-content:center;align-items:flex-start;gap:48px}
   .col .ico{position:static}
   .h{font-size:${d.tam||140}px;width:100%}
   .sub{font-size:42px;line-height:1.35;opacity:.92;max-width:860px}
   .play{width:120px;height:120px;border-radius:50%;background:${th.bg==C.lima?C.grafito:C.lima};display:flex;align-items:center;justify-content:center}
   .play:after{content:"";border-left:38px solid ${th.bg==C.lima?C.lima:C.grafito};border-top:24px solid transparent;border-bottom:24px solid transparent;margin-left:10px}
   .foot{bottom:150px}
  </style>
  <div class="col">
   <span class="chip">// ${d.etiqueta||'reel'}</span>
   ${icono(d, th, 260)}
   <div class="h">${hl(d.titulo)}</div>
   ${d.subtitulo?`<div class="sub">${d.subtitulo}</div>`:''}
   ${d.sin_play?"":`<div class="play"></div>`}
  </div>
  ${FOOT(th)}`}),

  // 4 · CÓMO TRABAJO (sin precios)
  como_trabajo: (d, th) => ({ w:1080, h:1350, html:`
  <style>
   .chip{position:absolute;left:80px;top:80px}
   .h{position:absolute;left:80px;right:80px;top:205px;font-size:112px}
   .steps{position:absolute;left:80px;right:80px;top:${d.top_pasos||470}px;display:flex;flex-direction:column;gap:22px}
   .s{display:flex;gap:28px;align-items:center;background:${th.box};color:${th.boxTx};padding:24px 30px;border-left:8px solid ${th.boxB}}
   .s i{font-style:normal;font-family:Mono;font-weight:700;font-size:30px;width:66px;height:66px;flex:none;border-radius:50%;background:${C.grafito};color:${C.lima};display:flex;align-items:center;justify-content:center}
   .s b{font-weight:800;font-size:34px;display:block}
   .s span{font-size:27px;opacity:.85}
   .tags{position:absolute;left:80px;right:80px;bottom:170px;display:flex;flex-wrap:wrap;gap:14px}
   .tags span{font-family:Mono;font-weight:700;font-size:22px;padding:12px 18px;background:${th.chipBg};color:${th.chipTx};letter-spacing:.03em}
  </style>
  <span class="chip">// ${d.etiqueta||'cómo trabajo'}</span>
  ${icono(d, th, 170, 'right:92px;top:200px')}
  <div class="h">${hl(d.titulo)}</div>
  <div class="steps">${(d.pasos||[]).map((p,i)=>`<div class="s"><i>${i+1}</i><div><b>${p[0]}</b><span>${p[1]}</span></div></div>`).join('')}</div>
  <div class="tags">${(d.etiquetas||[]).map(t=>`<span>✓ ${t}</span>`).join('')}</div>
  ${FOOT(th)}`}),
};
const DEF = { novedad:'grafito', carrusel_portada:'crema', carrusel_slide:'crema', reel_portada:'bosque', como_trabajo:'crema' };

(async () => {
  const [specPath, out] = process.argv.slice(2);
  const d = JSON.parse(fs.readFileSync(specPath, 'utf8'));
  const th = TEMA[d.fondo || DEF[d.tipo]];
  const t = T[d.tipo](d, th);
  const html = `<!doctype html><html><head><meta charset="utf-8"><style>:root{--w:${t.w}px;--h:${t.h}px}${FONTS}${BASE(th)}</style></head><body>${t.html}</body></html>`;
  const tmp = path.join(D, '.tmp_' + path.basename(out) + '.html');
  fs.writeFileSync(tmp, html);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: t.w, height: t.h }, deviceScaleFactor: 1 });
  await p.goto('file://' + tmp);
  await p.evaluate(() => document.fonts.ready);
  await p.screenshot({ path: out });
  await b.close();
  fs.unlinkSync(tmp);
  console.log('ok', out);
})();
