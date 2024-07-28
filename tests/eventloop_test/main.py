import asyncio

async def MyCoro():
    while True:
        await asyncio.sleep(1)
        print("My Coro jeden")

async def MyCoro2():
    while True:
        await asyncio.sleep(1)
        print("My Coro dwa")
            
loop = asyncio.get_event_loop()

try:
    asyncio.ensure_future(MyCoro())
    asyncio.ensure_future(MyCoro2())
    loop.run_forever()
finally:
    loop.close()