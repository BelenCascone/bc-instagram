import asyncio,subprocess,sys,os
from playwright.async_api import async_playwright
FPS=60;DUR=27;OUT='frames';os.makedirs(OUT,exist_ok=True)
async def main():
    srv=subprocess.Popen([sys.executable,'-m','http.server','8767'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    await asyncio.sleep(1)
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        pg=await b.new_page(viewport={'width':1080,'height':1920})
        pg.on('pageerror',lambda e:print('ERR',e))
        await pg.goto('http://localhost:8767/film.html'); await pg.evaluate('init()')
        el=pg.locator('#c')
        for i in range(FPS*DUR):
            await pg.evaluate(f'seek({i/FPS})')
            await el.screenshot(path=f'{OUT}/{i:05d}.jpg',type='jpeg',quality=94)
        await b.close()
    srv.kill()
asyncio.run(main())
