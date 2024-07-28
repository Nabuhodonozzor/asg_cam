killall python3

# python3 services/battery/battery_service.py & 
python3 services/camera/camera_service.py &
python3 services/gpio/gpio_service.py &

sleep 2

python3 controller/controller.py &