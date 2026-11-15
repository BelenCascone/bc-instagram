import sys, os, subprocess, shutil, threading, http.server, socketserver, functools
from playwright.sync_api import sync_playwright
FPS=12; DUR=48.5
only=[float(x) for x in sys.argv[1].split(',')] if len(sys.argv)>1 else None
out='/home/claude/reel5/frames'; shutil.rmtree(out,ignore_errors=True); os.makedirs(out)
srv=socketserver.TCPServer(('127.0.0.1',0),functools.partial(http.server.SimpleHTTPRequestHandler,directory='/home/claude/reel5'))
srv.RequestHandlerClass.log_message=lambda *a:None
port=srv.server_address[1]; threading.Thread(target=srv.serve_forever,daemon=True).start()
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome')
    pg=b.new_page(viewport={'width':1080,'height':1920})
    pg.goto(f'http://127.0.0.1:{port}/index.html'); pg.evaluate('window.ready')
    ts=only if only else [k/FPS for k in range(int(DUR*FPS))]
    for i,t in enumerate(ts):
        pg.evaluate(f'seek({t})'); pg.screenshot(path=f'{out}/f{i:04d}.jpg',type='jpeg',quality=93)
    b.close()
srv.shutdown()
if not only:
    subprocess.run(['ffmpeg','-loglevel','error','-y','-framerate',str(FPS),'-i',f'{out}/f%04d.jpg','-i','voz.mp3',
      '-af','apad','-r','24','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart','/home/claude/reel5/reel-clementina.mp4'],check=True)
print('ok')
