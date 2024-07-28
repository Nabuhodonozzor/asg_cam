class ServiceMessage:
    topic: bytes = ''
    method_name: bytes = ''
    content: bytes | None = ''
         
    def __init__(
            self, 
            raw_msg: list[bytes] | None = None, 
            topic: str | None = None, 
            method_name: str | None = None, 
            content: str | None = None
        ):
        if raw_msg is not None:
            self.__init_with_raw_list(raw_msg)
        else:
            self.__init_with_parameters(topic, method_name, content)

    def __init_with_raw_list(self, raw_msg: list[bytes]) -> None:
        self.topic = raw_msg[0]
        self.method_name = raw_msg[1]
        if raw_msg[2]:
            self.content = raw_msg[2]
        else: 
            self.content = None

    def __init_with_parameters(self,
                topic: str, 
                method_name: str, 
                content: str
            ) -> None:
        self.topic = topic.encode()
        self.method_name = method_name.encode()
        self.content = content.encode()

    def get_message_bytes(self) -> list[bytes]:
        return [self.topic, self.method_name, self.content]

    def get_message_str(self) -> list[str]:
        return [self.topic.decode(), self.method_name.decode(), self.content.decode()]
    
def get_service_msg_listb(raw_msg: list[bytes]):
    return ServiceMessage(raw_msg=raw_msg)

def get_service_msg_params(topic: str, method_name:str, content: str):
    return ServiceMessage(topic=topic, method_name=method_name, content=content)
