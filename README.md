

## Installation

First install libraries:

```
sudo apt-get install libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0
```

Then

```
pip install -r requirements.txt
```

Autorun on boot:

```
sudo crontab -e
@reboot cd /home/box1/opencv-camera-test/recording-demo/ && python3 main.py
```