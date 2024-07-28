from base.BaseService import BaseService
import helpers.MessageManager as mm
import asyncio
import RPi.GPIO as GPIO
import time

BUTTON = 14
CLICK_TIME_MS = 500

class GpioService(BaseService):
    __last_click: int = -1
    __click_counter: int = 0
    
    def __init__(self, service_name: str, config_path: str, topics: list[str] = [""]):
        super().__init__(service_name, config_path, topics)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(BUTTON, GPIO.IN)
        GPIO.add_event_detect(BUTTON, GPIO.RISING, callback=self.__button_clicked, bouncetime=50)
        
        self._create_task(self.__poll_click_count())
        self._log("Service initiated.")
    
    async def __poll_click_count(self):
        while True:
            await asyncio.sleep(0.1)
            if time.time_ns() - self.__last_click > CLICK_TIME_MS*1e6 and self.__click_counter != 0:
                self.__click_action()
                self.__click_counter = 0
            
    def __button_clicked(self, button):
        current_click = time.time_ns()
        if current_click - self.__last_click > CLICK_TIME_MS*1e6:
            self.__click_counter = 1
            
        else:
            self.__click_counter += 1
            
        self.__last_click = current_click
            
    def __click_action(self):
        match self.__click_counter:
            case 2:
                self._enqueue_message(
                    mm.get_service_msg_params("camera", "recording", ""))
            case 5:
                self._enqueue_message(
                    mm.get_service_msg_params("controller", "shutdown", ""))
            case _:
                self._log("No action")
        
if __name__ == "__main__":
    gpio = GpioService("GpioService", "/home/asgcam1/ASGCamSRC/asgcam/src/services/gpio/conf.json", ["gpio"])
    gpio._run()