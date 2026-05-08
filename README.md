# Facetracking minbitt head

# setup
```bash
pip install -r requirements.txt
circuitpython_setboard raspberry_pi_pico_w   
```

# running
```bash
python3 run_demo.py
```

## for syncing code
```bash
rsync -avz --exclude="*.kra" --exclude="*.aseprite" --exclude="*.kra~" --exclude="*.bmp~" --exclude="__pycache__/" ./minbitt_pkg/ /media/agmui/CIRCUITPY/minbitt_head/
```

# Uploading CircuitPython
from: https://adafruit.github.io/Adafruit_WebSerial_ESPTool/

esptool.js
Serial port WebSerial VendorID 0x10c4 ProductID 0xea60
Connecting... Detecting chip type... ESP32
Chip Revision: 3
Chip is ESP32-D0WD-V3 (revision 3)
Features: Wi-Fi, BT, Dual Core, 240MHz, VRef calibration in efuse, Coding Scheme None
WARNING: Unsupported crystal in use
Crystal is 26MHz
MAC: 30:76:f5:b9:f6:c8
Uploading stub...
Running stub...
Stub running...
Flash ID: 16405e


# Link dump:

## esp links
random adafruit guides:
* https://learn.adafruit.com/circuitpython-with-esp32-quick-start/neopixel-example
* https://learn.adafruit.com/circuitpython-nrf52840/bluefruit-le-connect-basics
* https://learn.adafruit.com/adafruit-pyportal/circuitpython-ble
* https://www.rototron.info/circuitpython-ble-client-server-tutorial/

idk rand arduio ble stuff:
* https://randomnerdtutorials.com/esp32-bluetooth-classic-arduino-ide/
* https://discussions.apple.com/thread/254852858?sortBy=rank
* https://www.reddit.com/r/esp32/comments/1agqlsu/is_there_anyway_to_pair_an_esp32_with_an_iphone/
* https://github.com/T-vK/ESP32-BLE-Keyboard

## vtuber links 
* [original redit post](https://www.reddit.com/r/CosplayHelp/comments/17sfyyq/tv_head_help/)
* https://hinzka.hatenablog.com/entry/2021/12/21/222635
* [def checkout](https://hinzka.hatenablog.com/entry/2021/05/08/105733)
* https://vtuberlab.com/2025/06/27/vtuber-expressions-explained-how-blend-shapes-bring-your-avatar-to-life/?utm_source=chatgpt.com
* https://melindaozel.com/arkit-to-facs-cheat-sheet/#jumphere
* https://drive.google.com/drive/folders/1i9lPxJ_fNvOUFwDxsFC8gpfgkT9A559w
* https://cdn.akamai.steamstatic.com/steam/apps/1898830/manuals/VBridger_Manual_1.06.pdf?t=1649617257
* https://docs.live2d.com/en/cubism-sdk-manual/mouthmovement-unity/
* https://pbs.twimg.com/media/FQcQFjGVkAQVnWp?format=jpg&name=4096x4096
* https://developer.apple.com/documentation/arkit/arfaceanchor/blendshapelocation/browdownleft
* https://cdn-learn.adafruit.com/downloads/pdf/32x16-32x32-rgb-led-matrix.pdf
* https://www.ifacialmocap.com/for-developer/
* https://www.facemotion3d.net/english/for-developer/
* https://www.tiktok.com/@koa_pool/video/7573449438656580895
* https://www.tiktok.com/@minbitts/video/7243259388339686657
* https://pbs.twimg.com/media/FLmC-ccVQAQNaf3?format=jpg&name=small
* https://github.com/DenchiSoft/VTubeStudio/wiki/Lipsync

