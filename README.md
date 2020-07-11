# Adding a DIY weatherstation to Home Assistant

I recently built a remote weatherstation with the core MPU a 8266
running ESPHome. This weatherstation currently pushes the following
measurements into my HomeAssistant system via the HA/ESPHome API.
Basic direction for this weatherstation came from [digiblur](https://www.youtube.com/watch?v=VUqOIPVbeF0).

* Outside temperature using BME280 
* Barometric pressure using BME280
* Outside humidity using BME280
* Outside temperature using SHT31-D
* Outside humidity using SHT31-D
* Hacked La Crosse TX58UN tipping bucket raingauge (ebay purchase)
* Hacked La Crosse LTV-W1 Wind Speed Sensor (ebay purchase)
* UV Index using VEML6075 UV
* Ambient Light using  MAX44009

This is a remote unattended weather station. Thus included the following
to allow it to be standalone albeit it does connect into my local wifi.

* Wemo D1 mini pro with exernal antenna
* 18650 batter with charging circuit connected to 1.5 watt solar panel.

The BME280 has known issues with reliably reporting humity reading. This
is why the SHT31-D is included. It also provides a double reference for
measuring the temperature. Experience with other commonly using temperature
sensors have proven to be much less accurate e.g. DHT22.

## Weewx

As part of this project, a local [weewx](http://weewx.com/) server was
set up alongside Home Assistant on a UNRAID based server using docker.

Home Assistant automations were created to forward the weather station
sensor data to MQTT. A simple generic weewx driver was written to 
transfer directly from the MQTT topics into the weewx loop packet.
By using MQTT topic names that come directly from weewx, the driver
is small and simple.
