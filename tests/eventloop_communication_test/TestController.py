import asyncio
import zmq
import helpers.MessageManager as mm
from datetime import datetime

service_configuration = {
    "host": "localhost",
    "pub": {
        "port": "5000"
    },
    "sub": {
        "port": "5001"
    }
}

class TestController:
    def __init__(self):
        self.service_name = "TestController"
        self.ctx: zmq.Context = zmq.Context()
        self.pub_sock: zmq.Socket = self.ctx.socket(zmq.PUB)
        self.sub_sock: zmq.Socket = self.ctx.socket(zmq.SUB)
        self.loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        self.poller: zmq.Poller = zmq.Poller()
        self.methods: dict = {b"printMsg": self.PrintMessage}
        
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

    async def SendMsgAsync(self) -> None:
        while True:
            await asyncio.sleep(5)
            self.LogInformation("Sending message")
            self.pub_sock.send_multipart([b"", b"printMsg", b"testowa wiadomosc"])

    async def DoSthElseAsync(self) -> None:
        while True:
            await asyncio.sleep(5)
            self.LogInformation("Doing sth else")
            
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
            
    def InitLoop(self) -> None:
        asyncio.ensure_future(self.SendMsgAsync(), loop=self.loop)
        asyncio.ensure_future(self.DoSthElseAsync(), loop=self.loop)
        asyncio.ensure_future(self.RecvMsgAsync(), loop=self.loop)
        
    def RunService(self) -> None:
        self.loop.run_forever()
        
    def LogInformation(self, msg: str) -> None:
        print(f"[{datetime.now()}][{self.service_name}]: {msg}")
        
if __name__ == "__main__":
    tController = TestController()
    tController.InitLoop()
    tController.RunService()

        