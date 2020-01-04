<p align="center">
  <img width="325" height="260" src="https://github.com/PowerBroker2/Thunder_Viewer/blob/master/logo.png">
</p>

# Description:
Open source Python GUI to stream and log War Thunder match data "real-time"

This program uses vehicle telemetry data **publicly provided by War Thunder [via a localhost server](https://forum.warthunder.com/index.php?/topic/53412-dynamic-battle-map-tactical-map-on-separate-device-great-new-feature/&ct=1577653391)** to do the following:
- Create and save [ACMI log files](https://www.tacview.net/documentation/acmi/en/) for post-match replay
- Stream telemetry to the application [Tacview](https://www.tacview.net/product/en/), simultaneously stream/download telemetry to/from remote allied players (i.e. War Thunder squadron mates)
    - Provides a **real-time** and post-match "AWACS view" of the War Thunder match
- Stream telemetry to a USB IoT device (i.e. [an Arduino](https://www.arduino.cc/en/Guide/Introduction))

# Functional Diagram:
<p align="center">
  <img width="1981" height="600" src="https://github.com/PowerBroker2/Thunder_Viewer/blob/master/Thunder_Viewer_Functional_Diagram.png">
</p>

# How to Install:
1. Download and install Anaconda3 from https://www.anaconda.com/distribution/
2. [Ensure the path to pip.exe is in your PATH system variable](https://www.youtube.com/watch?v=cm6WDGAzDPM)
3. Download Thunder Viewer from https://github.com/PowerBroker2/Thunder_Viewer (clone or download/extract zip file)
4. Run "setup.bat"

# How to Run:
1. Double click "run.bat" or run "Thunder_Viewer.py" via Python

# Graphical User Interface:
![gui](https://user-images.githubusercontent.com/20977405/71610000-42be2f80-2b5b-11ea-8781-61b8a3f04bfc.PNG)

# FAQ:
- TODO
