from base.BaseService import BaseService
import helpers.MessageManager as mm
import asyncio
import board
import adafruit_ads7830.ads7830 as ADC
from adafruit_ads7830.analog_in import AnalogIn

ADC_MAX_BITS = 65535
ADC_ADDR = 0x48
BAT_LOW_TRESH = 3.0

class BatteryMgmtService(BaseService):
    __i2c = board.I2C()
    __adc: ADC.ADS7830 = ADC.ADS7830(__i2c)
    __adc_channel = AnalogIn(__adc, 0)
    
    def __init__(self, service_name: str, config_path: str, topics: list[str] = [""]):
        super().__init__(service_name, config_path, topics)
        
        self._create_task(self.__s2s_heartbeat())
        self._create_task(self.__check_battery_voltage())
        
        self._log("Service initiated.")
        
    async def __check_battery_voltage(self):
        while True:
            await asyncio.sleep(5)
            bat_voltage: float = (self.__adc_channel.value * 5) / ADC_MAX_BITS
            
            if bat_voltage < BAT_LOW_TRESH:
                self._enqueue_message(mm.get_service_msg_params("controller", "low_battery", ""))
        
if __name__ == "__main__":
    bms = BatteryMgmtService("BatteryMgmtService", "/home/asgcam1/ASGCamSRC/asgcam/src/services/battery/conf.json", ["bms"])
    bms._run()