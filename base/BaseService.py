import asyncio
import zmq
import helpers.MessageManager as mm
import json
from datetime import datetime
from queue import Queue
from abc import ABC

class BaseService(ABC):
    __service_name: str
    __ctx: zmq.Context = zmq.Context()
    __pub_sock: zmq.Socket = __ctx.socket(zmq.PUB)
    __sub_sock: zmq.Socket = __ctx.socket(zmq.SUB)
    __loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    __poller: zmq.Poller = zmq.Poller()
    __methods: dict = {}
    __send_queue: Queue = Queue()
    __service_conf: dict = {}

    def __init__(self, service_name: str, config_path: str, topics: list[str] = [""]):
        self.__service_name = service_name
        self.__load_conf(config_path)
        self.__init_sub(topics)
        self.__init_pub()

        asyncio.ensure_future(self.__recv_msg_async(), loop=self.__loop)
        asyncio.ensure_future(self.__send_msg_async(), loop=self.__loop)

    def __init_sub(self, topics: list[str]) -> None:
        host = self.__service_conf["host"]
        sub_services = self.__service_conf["sub"]
        
        for sub_service in sub_services:
            port = sub_service["sport"]
            self.__sub_sock.connect(f"tcp://{host}:{port}")
        
        for topic in topics: 
            self.__sub_sock.subscribe(topic)
            
        self.__poller.register(self.__sub_sock, zmq.POLLIN)

    def __init_pub(self) -> None:
        port = self.__service_conf["pub"]
        host = self.__service_conf["host"]
        self.__pub_sock.bind(f"tcp://{host}:{port}")

    def __load_conf(self, conf_path: str) -> None:
        with open(conf_path, "r") as conf_file:
            conf = conf_file.read()
            self.__service_conf = json.loads(conf)

    def __route_msg(self, msg: mm.ServiceMessage) -> None:
        if msg.method_name in self.__methods.keys():
            self.__methods.get(msg.method_name)(msg.content)
        else:
            self._log("Could not find appropriate method to run.")

    async def __send_msg_async(self) -> None:
        while True:
            await asyncio.sleep(0.01)
            if self.__send_queue.qsize() != 0:
                msg = self.__send_queue.get()
                raw_msg = msg.get_message_bytes()
                self.__pub_sock.send_multipart(raw_msg)

    async def __recv_msg_async(self) -> None:
        while True:
            await asyncio.sleep(0.01)
            events = dict(self.__poller.poll(timeout=100))
            if self.__sub_sock in events:
                raw_msg = self.__sub_sock.recv_multipart()
                msg = mm.get_service_msg_listb(raw_msg)
                self.__route_msg(msg)

    def _register_method(self, method_id: str, method) -> None:
        self.__methods[method_id.encode()] = method

    def _create_task(self, task) -> None:
        asyncio.ensure_future(task, loop=self.__loop)

    def _log(self, msg: str) -> None:
        print(f"[{datetime.now()}][{self.__service_name}]: {msg}")
    
    def _enqueue_message(self, msg: mm.ServiceMessage) -> None:
        self.__send_queue.put(msg)

    def _run(self) -> None:
        self.__loop.run_forever()

   
