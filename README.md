

## Installation

First install libraries:

```
sudo apt-get install libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0
```

Then

```
pip install -r requirements.txt
```


## Auto restart on boot:

Due to Qt dark magic systemctl is having issues, easiest way is root crontab, do `sudo crontab -e` then add

```
@reboot sleep 20; cd /home/box1/opencv-camera-test/recording-demo/ && ./launch.sh
```
