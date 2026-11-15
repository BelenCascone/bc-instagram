import sys, os, subprocess, shutil
from playwright.sync_api import sync_playwright
FPS=30; DUR=float(sys.argv[1]) if len(sys.argv)>1 else 37.0
only=[float(x) for x in sys.argv[2].split(',')] if len(sys.argv)>2 else None
out='/home/claude/reel2/frames'; shutil.rmtree(out,ignore_errors=True); os.makedirs(out)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--allow-file-access-from-files','--disable-web-security'])
    pg=b.new_page(viewport={'width':1080,'height':1920})
    pg.goto('file:///home/claude/reel2/index.html'); pg.wait_for_timeout(800)
    ts=only if only else [k/FPS for k in range(int(DUR*FPS))]
    for i,t in enumerate(ts):
        pg.evaluate(f'render({t})')
        pg.screenshot(path=f'{out}/f{i:04d}.jpg',type='jpeg',quality=94)
    b.close()
if not only:
    subprocess.run(['ffmpeg','-loglevel','error','-y','-framerate',str(FPS),'-i',f'{out}/f%04d.jpg','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart','/home/claude/reel2/reel-panel-seguimiento.mp4'],check=True)
print('ok')
