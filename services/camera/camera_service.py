from base.BaseService import BaseService
import helpers.MessageManager as mm
import asyncio
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from datetime import datetime as dt

class CameraService(BaseService):
    __is_recording: bool = False
    __cam = Picamera2()
    __encoder = H264Encoder(10000000)

    def __init__(self, service_name: str, config_path: str, topics: list[str] = [""]):
        super().__init__(service_name, config_path, topics)
        self.__cam.resolution = (1280, 720)
        self.__cam.configure(self.__cam.create_video_configuration())

        self._register_method("recording", self.__start_stop_recording)
        self._log("Service initiated.")
        
    def __start_stop_recording(self, message: str):
        if self.__is_recording:
            self._log("Recording stopped")
            self.__cam.stop_recording()
            self.__is_recording = False
        else:
            self.__is_recording = True
            file_name = f'/home/asgcam1/Pictures/{dt.now()}.h264'
            self._log("Recording started")
            self.__cam.start_recording(self.__encoder, file_name)
        
if __name__ == "__main__":
    cs = CameraService("CameraService", "/home/asgcam1/ASGCamSRC/asgcam/src/services/camera/conf.json", ["camera"])
    cs._run()