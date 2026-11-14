// Placas "Arte + compu" para @bc.informatica.pna — HTML -> JPG 1080x1350 con Playwright
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const F = (p) => 'file://' + path.resolve(p);
const fonts = `
@font-face{font-family:Playfair;font-weight:400;font-style:normal;src:url(${F('node_modules/@fontsource/playfair-display/files/playfair-display-latin-400-normal.woff2')})}
@font-face{font-family:Playfair;font-weight:400;font-style:italic;src:url(${F('node_modules/@fontsource/playfair-display/files/playfair-display-latin-400-italic.woff2')})}
@font-face{font-family:Playfair;font-weight:700;font-style:normal;src:url(${F('node_modules/@fontsource/playfair-display/files/playfair-display-latin-700-normal.woff2')})}
@font-face{font-family:Playfair;font-weight:700;font-style:italic;src:url(${F('node_modules/@fontsource/playfair-display/files/playfair-display-latin-700-italic.woff2')})}
@font-face{font-family:Caveat;font-weight:600;src:url(${F('node_modules/@fontsource/caveat/files/caveat-latin-600-normal.woff2')})}
@font-face{font-family:InterL;font-weight:500;src:url(${F('node_modules/@fontsource/inter/files/inter-latin-500-normal.woff2')})}
@font-face{font-family:InterL;font-weight:700;src:url(${F('node_modules/@fontsource/inter/files/inter-latin-700-normal.woff2')})}
`;
const C = { crema: '#FBF8E6', crema2: '#F6F1E0', grafito: '#121412', bosque: '#1B4332', gris: '#8F9E8B', lima: '#C6FF00' };

const base = (body, extra = '') => `<!doctype html><html><head><meta charset="utf-8"><style>
${fonts}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1350px;overflow:hidden}
body{position:relative;font-family:Playfair,serif;color:${C.grafito};background:${C.crema}}
.handle{position:absolute;bottom:42px;left:0;right:0;text-align:center;font-family:InterL;font-weight:500;font-size:24px;letter-spacing:.06em}
.grain{position:absolute;inset:0;pointer-events:none;opacity:.10;mix-blend-mode:multiply;
 background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>")}
${extra}
</style></head><body>${body}</body></html>`;

// Portada: cuadro a pantalla completa + frase
function arte({ img, pos = 'center', bg = '', capa = '', texto, lado = 'top', align = 'left', size = 84, maxw = 900, oscuro = true }) {
  const grad = lado === 'top'
    ? 'linear-gradient(180deg,rgba(10,10,8,.78) 0%,rgba(10,10,8,.35) 32%,rgba(10,10,8,0) 52%)'
    : lado === 'left'
      ? 'linear-gradient(90deg,rgba(10,10,8,.55) 0%,rgba(10,10,8,0) 55%)'
      : 'linear-gradient(0deg,rgba(10,10,8,.8) 0%,rgba(10,10,8,.3) 35%,rgba(10,10,8,0) 55%)';
  const box = lado === 'top' ? `top:96px;left:80px;right:80px`
    : lado === 'left' ? `top:120px;left:72px;width:${maxw}px`
      : `bottom:130px;left:80px;right:80px`;
  return base(`
  <div style="position:absolute;inset:0;background:${bg ? bg : `url(${F(img)}) ${pos}/cover no-repeat`}"></div>${capa}
  ${oscuro ? `<div style="position:absolute;inset:0;background:${grad}"></div>` : ''}
  <div style="position:absolute;${box};text-align:${align}">
    <div style="font-style:italic;font-weight:400;font-size:${size}px;line-height:1.08;color:${C.crema};text-shadow:0 2px 18px rgba(0,0,0,.45)">${texto}</div>
  </div>
  <div class="handle" style="color:${C.crema};opacity:.8">@bc.informatica.pna</div>`);
}

// Tip: fondo crema, lista numerada, recorte del cuadro como sticker
function tip({ kicker, titulo, items, sticker, stickerPos = 'center', numerada = true }) {
  const lis = items.map((t, i) => `
    <li style="display:flex;gap:26px;align-items:flex-start;margin-bottom:52px">
      <span style="flex:none;width:64px;height:64px;border-radius:50%;background:${C.bosque};color:${C.crema};font-family:InterL;font-weight:700;font-size:26px;display:flex;align-items:center;justify-content:center;margin-top:2px">${numerada ? i + 1 : '•'}</span>
      <span style="font-size:44px;line-height:1.3">${t}</span>
    </li>`).join('');
  return base(`
  <div class="grain"></div>
  <div style="position:absolute;top:92px;left:84px;right:84px">
    <div style="font-family:InterL;font-weight:700;font-size:24px;letter-spacing:.22em;color:${C.bosque}">${kicker}</div>
    <div style="width:64px;height:6px;background:${C.lima};margin:22px 0 30px"></div>
    <div style="font-weight:700;font-size:76px;line-height:1.06;max-width:680px">${titulo}</div>
  </div>
  <div style="position:absolute;top:88px;right:70px;width:220px;height:270px;transform:rotate(4deg);background:#fff;padding:12px 12px 40px;box-shadow:0 10px 30px rgba(0,0,0,.18)">
    <div style="width:100%;height:100%;background:url(${F(sticker)}) ${stickerPos}/cover"></div>
  </div>
  <ul style="list-style:none;position:absolute;left:84px;right:90px;top:480px">${lis}</ul>
  <div class="handle" style="color:${C.bosque}">@bc.informatica.pna</div>`);
}

function manos() {
  return base(`
  <div style="position:absolute;inset:0;background:url(${F('pinturas/manos.jpg')}) center 55%/cover no-repeat"></div>
  <div style="position:absolute;top:150px;left:78px;width:560px;font-style:italic;font-size:78px;line-height:1.05">Vos ponés<br>la idea.</div>
  <div style="position:absolute;top:960px;right:64px;width:440px;text-align:right;font-style:italic;font-size:74px;line-height:1.05">Yo la<br>convierto<br>en sistema.</div>
  <svg style="position:absolute;left:470px;top:618px" width="120" height="120" viewBox="0 0 120 120">
    <path d="M60 4 L68 52 L116 60 L68 68 L60 116 L52 68 L4 60 L52 52 Z" fill="${C.lima}" opacity=".95"/>
  </svg>
  <div style="position:absolute;bottom:0;left:0;right:0;height:120px;background:rgba(251,248,230,.92)"></div><div style="position:absolute;bottom:46px;left:0;right:0;text-align:center;font-family:InterL;font-weight:700;font-size:24px;letter-spacing:.14em;color:${C.bosque}">BC INFORMÁTICA · SISTEMAS A TU MEDIDA Y A TU ALCANCE</div>`);
}

const piezas = {
  'grito-s1': arte({ img: 'pinturas/munch.jpg', pos: 'center 30%', texto: 'Cuando aparece<br>la pantalla azul', size: 96 }),
  'grito-s2': tip({ kicker: 'PANTALLA AZUL', titulo: '¿Qué hacer?', sticker: 'pinturas/munch.jpg', stickerPos: '52% 62%', items: [
    'No te asustes: sacale una foto al código de error.',
    'Reiniciá y fijate si vuelve a pasar.',
    '¿Instalaste algo hace poco? Suele ser la causa.',
    'Si se repite, puede ser la memoria, el disco o un driver: conviene revisarla.'] }),
  'perla-s1': arte({ img: 'pinturas/vermeer.jpg', pos: 'center 20%', bg: '#050414', capa: `<div style="position:absolute;right:0;bottom:0;width:965px;height:1130px;background:url(${F('pinturas/vermeer.jpg')}) center/cover;-webkit-mask-image:linear-gradient(90deg,transparent 0,#000 18%),linear-gradient(180deg,transparent 0,#000 16%);-webkit-mask-composite:source-in;mask-composite:intersect"></div>`, oscuro: false, texto: 'Cuando alguien<br>te mira mientras<br>escribís tu<br>contraseña', lado: 'left', size: 64, maxw: 520 }),
  'perla-s2': tip({ kicker: 'CONTRASEÑAS', titulo: 'Que no te dé vergüenza la tuya', sticker: 'pinturas/vermeer.jpg', stickerPos: '40% 45%', items: [
    'Usá una frase larga, no una palabra: <i>MiPerroComeMilanesas</i>.',
    'Una distinta para cada cuenta.',
    'Guardalas en un gestor de contraseñas, no en un papelito.',
    'Activá la verificación en dos pasos.'] }),
  'lectora-s1': arte({ img: 'pinturas/lectora.jpg', pos: 'center 30%', texto: 'Cuando la compu<br>te pide actualizar<br>por quinta vez', size: 82 }),
  'lectora-s2': tip({ kicker: 'ACTUALIZACIONES', titulo: '¿Por qué no darle “más tarde”?', sticker: 'pinturas/lectora.jpg', stickerPos: '50% 35%', items: [
    'Tapan agujeros de seguridad que ya se conocen.',
    'Corrigen errores que hacen que se tilde.',
    'Hacelas al final del día, así no te cortan el trabajo.',
    'Antes de una grande, hacé una copia de tus archivos.'] }),
  'manos': manos(),
};

(async () => {
  fs.mkdirSync('out', { recursive: true });
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1350 } });
  for (const [k, html] of Object.entries(piezas)) {
    if (process.argv[2] && !k.startsWith(process.argv[2])) continue;
    fs.writeFileSync(`out/${k}.html`, html);
    await p.goto(F(`out/${k}.html`));
    await p.evaluate(() => document.fonts.ready);
    await p.waitForTimeout(300);
    await p.screenshot({ path: `out/${k}.jpg`, type: 'jpeg', quality: 92 });
    console.log('ok', k);
  }
  await b.close();
})();
