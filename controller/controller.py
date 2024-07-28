from base.BaseService import BaseService
import helpers.MessageManager as mm
import asyncio
from subprocess import call

class Controller(BaseService):
    def __init__(self, service_name: str, config_path: str, topics: list[str] = [""]):
        super().__init__(service_name, config_path, topics)
        
        self._register_method("print_msg", self.__print_message)
        self._register_method("shutdown", self.__shutdown)
        self._log("Service initiated.")
    
    def __print_message(self, msg: str):
        self._log(msg)

    def __shutdown(self):
        # TODO: Free resources then shutdown the system
        # call("sudo shutdown now")
    
if __name__ == "__main__":
    c = Controller("Controler", "/home/asgcam1/ASGCamSRC/asgcam/src/controller/conf.json")
    c._run()