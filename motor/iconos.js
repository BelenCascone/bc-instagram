// Íconos propios de BC Informática (SVG original, estilo "sticker" con sombra lima)
// Cada función recibe (tinta, relleno, acento) y devuelve un <svg> 200x200.
module.exports = {
  // Hacker encapuchado con notebook (estafas, virus, seguridad)
  hacker: (t, r, a) => `<svg viewBox="0 0 200 200"><g stroke="${t}" stroke-width="7" stroke-linejoin="round" stroke-linecap="round">
    <path d="M100 14C58 14 40 52 42 96L36 146H164L158 96C160 52 142 14 100 14Z" fill="${r}"/>
    <path d="M70 60C78 44 122 44 130 60" fill="none"/>
    <ellipse cx="100" cy="94" rx="32" ry="38" fill="#0a0b0a"/>
    <path d="M80 92L94 98M120 92L106 98" stroke="${a}" stroke-width="8"/>
    <rect x="44" y="124" width="112" height="58" rx="6" fill="${r}"/>
    <path d="M24 186H176" stroke-width="9"/>
    <path d="M88 152L100 142L112 152M100 142V166" stroke="${a}" stroke-width="6" fill="none"/></g></svg>`,

  // Anzuelo con arroba (phishing, mensajes falsos)
  anzuelo: (t, r, a) => `<svg viewBox="0 0 200 200"><g stroke="${t}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round">
    <path d="M100 6V58" fill="none"/>
    <rect x="26" y="96" width="148" height="92" rx="10" fill="${r}"/>
    <path d="M30 102L100 150L170 102" fill="none"/>
    <path d="M100 58V112C100 132 72 132 72 112L84 118" fill="none" stroke="${a}" stroke-width="9"/>
    <circle cx="100" cy="58" r="7" fill="${t}"/></g></svg>`,

  // Chip con chispa (inteligencia artificial)
  ia: (t, r, a) => `<svg viewBox="0 0 200 200"><g stroke="${t}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round">
    <path d="M70 24V44M100 24V44M130 24V44M70 156V176M100 156V176M130 156V176M24 70H44M24 100H44M24 130H44M156 70H176M156 100H176M156 130H176" fill="none"/>
    <rect x="44" y="44" width="112" height="112" rx="16" fill="${r}"/>
    <path d="M100 66C104 88 112 96 134 100C112 104 104 112 100 134C96 112 88 104 66 100C88 96 96 88 100 66Z" fill="${a}"/>
    <path d="M136 62C137 69 139 71 146 72C139 73 137 75 136 82C135 75 133 73 126 72C133 71 135 69 136 62Z" fill="${a}" stroke-width="4"/></g></svg>`,

  // Monitor con código (PC, sistemas)
  pc: (t, r, a) => `<svg viewBox="0 0 200 200"><g stroke="${t}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round">
    <rect x="18" y="26" width="164" height="112" rx="10" fill="${r}"/>
    <path d="M80 138L74 170H126L120 138M58 172H142" fill="none"/>
    <path d="M70 66L52 82L70 98M130 66L148 82L130 98" fill="none" stroke="${a}" stroke-width="8"/>
    <path d="M108 60L92 104" stroke="${a}" stroke-width="8"/></g></svg>`,

  // Notebook (service, antes y después)
  notebook: (t, r, a) => `<svg viewBox="0 0 200 200"><g stroke="${t}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round">
    <rect x="34" y="40" width="132" height="92" rx="8" fill="${r}"/>
    <path d="M14 152H186L174 168H26Z" fill="${r}"/>
    <path d="M60 106L84 82L100 96L138 62" fill="none" stroke="${a}" stroke-width="9"/>
    <path d="M118 62H138V82" fill="none" stroke="${a}" stroke-width="9"/></g></svg>`,

  // Disco SSD (velocidad, upgrades)
  disco: (t, r, a) => `<svg viewBox="0 0 200 200"><g stroke="${t}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round">
    <rect x="22" y="54" width="156" height="92" rx="10" fill="${r}"/>
    <rect x="40" y="72" width="40" height="32" rx="4" fill="${a}"/><rect x="92" y="72" width="40" height="32" rx="4" fill="${a}"/>
    <path d="M40 124H140M156 72V82" fill="none"/>
    <path d="M150 116L162 104V128Z" fill="${t}"/></g></svg>`,

  // Celular con alerta (estafas por WhatsApp, apps)
  celular: (t, r, a) => `<svg viewBox="0 0 200 200"><g stroke="${t}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round">
    <rect x="52" y="14" width="96" height="172" rx="16" fill="${r}"/>
    <path d="M88 30H112M92 168H108" fill="none"/>
    <path d="M100 60L136 124H64Z" fill="${a}"/>
    <path d="M100 82V102M100 112V114" stroke-width="8"/></g></svg>`,

  // Escudo con candado (seguridad, datos, contraseñas)
  escudo: (t, r, a) => `<svg viewBox="0 0 200 200"><g stroke="${t}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round">
    <path d="M100 14L168 40V96C168 140 138 170 100 186C62 170 32 140 32 96V40Z" fill="${r}"/>
    <rect x="70" y="92" width="60" height="50" rx="6" fill="${a}"/>
    <path d="M80 92V78C80 54 120 54 120 78V92" fill="none"/>
    <path d="M100 110V124" stroke-width="8"/></g></svg>`,

  // Herramienta (arreglos, mantenimiento)
  herramienta: (t, r, a) => `<svg viewBox="0 0 200 200"><g stroke="${t}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round">
    <path d="M128 20C108 20 94 38 98 58L28 128C20 136 20 150 28 158L42 172C50 180 64 180 72 172L142 102C162 106 180 92 180 72C180 66 179 62 177 58L156 80L130 74L124 48L146 26C140 22 134 20 128 20Z" fill="${r}"/>
    <circle cx="50" cy="150" r="9" fill="${a}"/></g></svg>`,
};
