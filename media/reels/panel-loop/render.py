import sys, os, subprocess, shutil
from playwright.sync_api import sync_playwright
FPS = 60; DUR = 15.0
only = [float(x) for x in sys.argv[1].split(',')] if len(sys.argv) > 1 else None
out = '/home/claude/reel3/frames'; shutil.rmtree(out, ignore_errors=True); os.makedirs(out)
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--allow-file-access-from-files'])
    pg = b.new_page(viewport={'width': 1080, 'height': 1920})
    pg.goto('file:///home/claude/reel3/index.html'); pg.evaluate('window.ready')
    ts = only if only else [k / FPS for k in range(int(DUR * FPS))]
    for i, t in enumerate(ts):
        pg.evaluate(f'seek({t})')
        pg.screenshot(path=f'{out}/f{i:04d}.jpg', type='jpeg', quality=95)
    b.close()
if not only:
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-framerate', str(FPS), '-i', f'{out}/f%04d.jpg', '-c:v', 'libx264',
                    '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
                    '/home/claude/reel3/reel-panel-loop.mp4'], check=True)
print('ok')
