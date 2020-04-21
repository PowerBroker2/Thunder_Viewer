<p align="center">
  <img width="325" height="260" src="https://github.com/PowerBroker2/Thunder_Viewer/blob/master/docs/logo.png">
</p>

[![GitHub version](https://badge.fury.io/gh/PowerBroker2%2FThunder_Viewer.svg)](https://badge.fury.io/gh/PowerBroker2%2FThunder_Viewer)

# Description:
Open source Python GUI to stream and log War Thunder match data "real-time"

This program uses vehicle telemetry data **publicly provided by War Thunder [via a localhost server](https://forum.warthunder.com/index.php?/topic/53412-dynamic-battle-map-tactical-map-on-separate-device-great-new-feature/&ct=1577653391)** to do the following:
- Create and save [ACMI log files](https://www.tacview.net/documentation/acmi/en/) for post-match replay
- Stream telemetry to the application [Tacview](https://www.tacview.net/product/en/), simultaneously stream/download telemetry to/from remote allied players (i.e. War Thunder squadron mates)
    - Provides a **real-time** and post-match "AWACS view" of the War Thunder match
- Stream telemetry to a USB IoT device (i.e. [an Arduino](https://www.arduino.cc/en/Guide/Introduction))

# Functional Diagram:
<p align="center">
  <img width="1981" height="600" src="https://github.com/PowerBroker2/Thunder_Viewer/blob/master/docs/Thunder_Viewer_Functional_Diagram.png?raw=true">
</p>

# How to Install and Run:
## .exe:
1. Download the [latest release](https://github.com/PowerBroker2/Thunder_Viewer/releases) (exe in Thunder_Viewer.zip found under "assests" within the release)
2. Extract the Thunder_Viewer.zip where you want
3. Open the extracted file
4. Double click Thunder_Viewer.exe

## Python:
1. Download and install Anaconda3 from https://www.anaconda.com/distribution/
2. [Ensure the path to pip.exe is in your PATH system variable](https://www.youtube.com/watch?v=cm6WDGAzDPM)
3. Download Thunder Viewer from https://github.com/PowerBroker2/Thunder_Viewer (clone or download/extract zip file)
4. Run "src/setup.bat"
5. Double click "src/run.bat" or run "src/Thunder_Viewer.py" via Python

# Graphical User Interface:
![gui](https://raw.githubusercontent.com/PowerBroker2/Thunder_Viewer/master/docs/GUI_Description.PNG)

# FAQ:
## Q: Is this a hack?
No! Thunder Viewer uses only data provided by War Thunder itself and provides no advantage above other players.

## Q: How do I download Tacview?
[Download link](https://www.tacview.net/download/license/en/?file=TacviewSetup.exe&mirror=0)

## Q: What if I don't want to download Tacview? Can I still use this tool?
Yes! Streaming and replaying match data to Tacview are only two of the several features of this tool. Thunder Viewer can also be used to save War Thunder data for processing by other programs (other Python scripts, MATLAB scripts, etc) and to stream data to IoT devices like Arduinos!

## Q: My plane is not displaying pitch correctly in Tacview, is this a bug?
Nope! Some planes in War Thunder historically do not have an artificial horizon (i.e. early Russian biplanes). If the plane does not have an artificial horizon, War Thunder's localhost does not provide pitch data. When flying such vehicles, Thunder Viewer defaults to pitch angle of 0 degrees at all times for that particular plane.

## Q: The War Thunder texture map displayed on Tacview's globe is scaled wrong, is this a bug?
Depends - Sometimes the map served by War Thunder's localhost (which is used by Thunder Viewer and sent to Tacview for display on the globe) is the map used for ground battles instead of the one for air battles. This is a bug with War Thunder. It is possible, however, that the scale of the map is incorrectly set in the Python library [WarThunder](https://github.com/PowerBroker2/WarThunder/blob/master/WarThunder/maps.py). If you think this is the case, please submit an issue ticket either on this repo or the repo for [WarThunder](https://github.com/PowerBroker2/WarThunder).
