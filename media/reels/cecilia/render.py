import sys, os, subprocess, shutil, threading, http.server, socketserver, functools, time
from playwright.sync_api import sync_playwright
FPS=30; DUR=47.0
only=[float(x) for x in sys.argv[1].split(',')] if len(sys.argv)>1 else None
out='/home/claude/reel6/frames'; shutil.rmtree(out,ignore_errors=True); os.makedirs(out)
Hn=functools.partial(http.server.SimpleHTTPRequestHandler,directory='/home/claude/reel6')
srv=socketserver.TCPServer(('127.0.0.1',0),Hn); srv.RequestHandlerClass.log_message=lambda *a:None
port=srv.server_address[1]; threading.Thread(target=srv.serve_forever,daemon=True).start()
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
    pg=b.new_page(viewport={'width':1080,'height':1920})
    msgs=[]; pg.on('console',lambda m:msgs.append(m.text)); pg.on('pageerror',lambda e:msgs.append(str(e)))
    pg.goto(f'http://127.0.0.1:{port}/index.html'); pg.wait_for_function('window.ready!==undefined',timeout=20000); pg.evaluate('window.ready')
    ts=only if only else [k/FPS for k in range(int(DUR*FPS))]
    t0=time.time()
    for i,t in enumerate(ts):
        pg.evaluate(f'seek({t})'); pg.screenshot(path=f'{out}/f{i:04d}.jpg',type='jpeg',quality=92)
    print('per frame',(time.time()-t0)/len(ts)); print('\n'.join(msgs[:10]))
    b.close()
srv.shutdown()
if not only:
    subprocess.run(['ffmpeg','-loglevel','error','-y','-framerate',str(FPS),'-i',f'{out}/f%04d.jpg','-i','voz.mp3','-af','apad',
      '-c:v','libx264','-preset','veryfast','-crf','21','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart','/home/claude/reel6/reel-cecilia.mp4'],check=True)
print('ok')
