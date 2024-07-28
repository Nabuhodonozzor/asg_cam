import asyncio
import zmq
import queue
import models.MessageManager as mm

service_configuration = {
    "host": "localhost",
    "pub": {
        "port": "5001"
    },
    "sub": {
        "port": "5000"
    }
}

class TestBatteryService:
    def __init__(self):
        self.service_name = "TestBatteryService"
        self.ctx: zmq.Context = zmq.Context()
        self.sub_sock: zmq.Socket = self.ctx.socket(zmq.SUB)
        self.pub_sock: zmq.Socket = self.ctx.socket(zmq.PUB)
        self.loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        self.poller: zmq.Poller = zmq.Poller()
        self.methods:dict = {b"printMsg": self.PrintMessage}
        self.send_queue: queue.Queue = queue.Queue()
        
        self.InitSubscriber()
        self.InitPublisher()
        
    def InitSubscriber(self) -> None:
        port = service_configuration["sub"]["port"]
        host = service_configuration["host"]
        self.sub_sock.bind(f"tcp://{host}:{port}")
        self.sub_sock.subscribe("")
        self.poller.register(self.sub_sock, zmq.POLLIN)
        
    def InitPublisher(self) -> None:
        port = service_configuration["pub"]["port"]
        host = service_configuration["host"]
        self.pub_sock.connect(f"tcp://{host}:{port}")
        
    async def RecvMsgAsync(self) -> None:
        while True:
            await asyncio.sleep(0.1)
            events = dict(self.poller.poll(timeout=100))
            if self.sub_sock in events:
                raw_msg = self.sub_sock.recv_multipart()
                msg = mm.get_service_msg_listb(raw_msg)
                self.RouteMsg(msg)
                
    def RouteMsg(self, msg: mm.ServiceMessage)-> None:
        if msg.method_name in self.methods.keys():
            self.methods.get(msg.method_name)(msg.content)
        else:
            print("Could not find appropriate method to run.")
    
    def PrintMessage(self, msg) -> None:
        print(msg.decode())

    async def DoSthElseAsync(self) -> None:
        while True:
            await asyncio.sleep(5)
            print("[RX] Robię coś innego")
            
    async def SendMsgAsync(self) -> None:
        while True:
            await asyncio.sleep(0.5)
            if self.send_queue.qsize() != 0:
                msg = self.send_queue.get()
                raw_msg = msg.get_message_bytes()
                self.pub_sock.send_multipart(raw_msg)
                
    async def EnqueueMessage(self) -> None:
        await asyncio.sleep(1)
        msg: mm.ServiceMessage = mm.get_service_msg_params("", "printMsg", "test service message")
        self.send_queue.put(msg)
        
    def InitTasks(self) -> None:
        asyncio.ensure_future(self.RecvMsgAsync(), loop=self.loop)
        asyncio.ensure_future(self.DoSthElseAsync(), loop=self.loop)
        asyncio.ensure_future(self.EnqueueMessage(), loop=self.loop)
        asyncio.ensure_future(self.SendMsgAsync(), loop=self.loop)
        
    def RunService(self) -> None:
        self.loop.run_forever()

if __name__ == "__main__":
    tBMS = TestBatteryService()
    tBMS.InitTasks()
    tBMS.RunService()