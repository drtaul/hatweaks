# Tweaks to add DIY weatherstation

I recently built a remote weatherstation with the core MPU a 8266
running ESPHome. This weatherstation currently pushes the following
measurements into my HomeAssistant system via the HA/ESPHome API.
Basic direction for this weatherstation came from [digiblur](https://www.youtube.com/watch?v=VUqOIPVbeF0).

* Outside temperature using BME280 
* Barometric pressure using BME280
* Outside humidity using BME280
* Outside temperature using SHT31-D
* Outside humidity using SHT31-D
* Hacked La Crosse TX58UN tipping bucket raingauge
* Hacked La Crosse LTV-W1 Wind Speed Sensor
* UV Index using VEML6075 UV
* Ambient Light using  MAX44009

This is a remote unattended weather station. Thus included the following
to allow it to be standalone albeit it does connect into my local wifi.

* Wemo D1 mini pro with exernal antenna
* 18650 batter with charging circuit connected to 1.5 watt solar panel.
