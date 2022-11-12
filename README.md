# sparkly
**Swimming-Pool Automation Systen with Raspberry Pi + Home Assistant**

#### Disclaimer: THIS IS VERY MUCH A WORK IN PROGRESS, DO NOT EXPECT TO CLONE THIS AND HAVE A WORKING SYSTEM JUST YET!!!

<img src="/help/media/raspipool_main2.png" height="256">

## Overview:

 A cost-effective, easy-to-build, easy-to-use "Swimming Pool Automation System" with top functions to automate, control and monitor (from web) swimming pools.

- Automatic filter control (single speed pumps) based on turnover, temperature and energy tariffs. Manual scheduling too. The power relay used needs to be able to withstand the Inductive Load of the Pool Pump motor. 
- 3 sensors:
  - tentacle ([whitebox T3](https://atlas-scientific.com/electrical-isolation/whitebox-t3/)) carrier board with
  - [ph](https://www.atlas-scientific.com/product_pages/circuits/ezo_ph.html), [orp](https://www.atlas-scientific.com/product_pages/circuits/ezo_orp.html), and [RTD](https://atlas-scientific.com/embedded-solutions/ezo-rtd-temperature-circuit/). A custom I2C sensor for HA has been developed.
- and [8 relays](https://sequentmicrosystems.com/collections/home-automation/products/raspberry-pi-relays-stackable-card) (custom HA component for sequent 8 board relay). The relays control :
  - pump on/off
  - muriatic acid injection (to regulate pH)
  - bleach injection (to mantain sanitization level) **or** salt chlorinator control


 The system is intended to monitor and *"automagically"* control most important pool functions and notify to mobile all possible events requiring attention.

 Integrated Node Red for advanced automation functionality.
 
 ## Build system (slightly out of date)
 
 Follow instructions in wiki [howto build a bypass to connect sensors to the pool](https://github.com/segalion/raspipool/wiki/Bypass-for-sensors), [howto connect sensors to the raspberry pi](https://github.com/segalion/raspipool/wiki/Sensors-connection-(DS18B20,-and-EZO-pH-and-ORP)) and [howto connect relays between pumps and raspberry pi](https://github.com/segalion/raspipool/wiki/Connection-of-relays-for-pump-control)
 
 ## Install (really needs work!!! - contributions appreciated)
 0. Install [HAOS](https://www.home-assistant.io/installation/raspberrypi#install-home-assistant-operating-system) in a raspberry pi (3 or 4), and setup wifi connection. (If an advanced user, you can instead install [raspberry pi OS](https://www.raspberrypi.com/software/) + [Home Assistant Core](https://www.home-assistant.io/installation/raspberrypi#install-home-assistant-core))
 *PLEASE DO NOT ASK FOR ASSISTANCE IN INSTALLING HA. It is an overly, unnnecesarly complicated process that should be fully suported by HA.*
 1. Install Node-Red
 2. Copy/clone this repository in the homeassistant conf_dir ( i.e. /home/homeassistant/.homeassistant/ or /mnt/data/supervisor/homeassistant/). The following form allows you to initialize a non-empty directory:

    `git init .`

    `git remote add origin <repository-url>`

    `git pull origin master`

 3. Create a 'secrets.yaml' file under the config_dir directory, containing:

    `latitude: <latitude>`

    `longitude: <longitude>`
    
    `openweathermap_api_key: <key>`
    
    `pushbullet_api_key: <key>`

 4. Start HA and access [http://<sparkly.local>:8123](http://sparkly.local:8123)
 5. Because HA is so wise, you'll need to enable the following integrations via UI (TODO: is there a way to fix this?):
   - Scheduler
   - OpenWeatherMap (you'll need to supply your API key, even if you already set it in your secrets file above)
 6. Change your HA panel configuration to point to your NR installation (check panel_iframe in configuration.yaml) (NR runs at [http://<sparkly.local>:46836](http://sparkly.local:46836))
 7. Connect your node red installation to HA.
 - Generate a [long lived token](https://www.atomicha.com/home-assistant-how-to-generate-long-lived-access-token-part-1/).
 - [Configure HA](https://leonardosmarthomemakers.com/how-to-install-node-red-on-a-raspberry-for-your-home-assistant-smart-home/#CREATE_A_LONG-LIVED_ACCESS_TOKEN_IN_HOME_ASSISTANT) node in Node Red UI

 
 ## TODO:
 - Water temperature (1-wire [DS18B20 waterproof](https://aliexpress.com/item/32968031204.html))
 - SWC – Salt Water Chlorinator (instead of bleach injections) - in progress
 - Improve calibration (3-point for pH)
 - Heater control
 - Correction of FC-ORP based on CYA (actually only linear correction)
 - Control Variable Speed Motor via RS485
 - Two speed pumps (re-add support)
  
<sub> This is a fork of [raspipool](https://github.com/huehueteotl/raspipool) HEAVILY modified. Thanks to segalion for the original work. Thanks to Hidromaster, Piscidoc, and all DIY enthusiasts from [hablemosdepisicnas](http://www.hablemosdepiscinas.com/foro/viewtopic.php?f=11&t=3906) and [TFP](https://www.troublefreepool.com/threads/raspipool-pool-automation-system-with-raspberry-pi-home-assistant.188410/) forums.</sub>
