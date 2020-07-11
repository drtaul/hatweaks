# Tweaks to add DIY weatherstation

I recently built a remote weatherstation with the core MPU a 8266
running ESPHome. This weatherstation current pushes the following
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


