// https://github.com/esphome/feature-requests/issues/217#issuecomment-583875043
#include "esphome.h"
#include "SparkFun_VEML6075_Arduino_Library.h"

class VEML6075CustomSensor : public PollingComponent, public Sensor {
 public:
  VEML6075 uv = VEML6075();

  Sensor *uva_sensor = new Sensor();
  Sensor *uvb_sensor = new Sensor();
  Sensor *uvindex_sensor = new Sensor();

  VEML6075CustomSensor() : PollingComponent(15000) {}
  void setup() override {
    Wire.begin();
    uv.begin();
    uv.setIntegrationTime(VEML6075::IT_100MS);
  }

  void update() override {
    float uva = uv.uva();
    float uvb = uv.uvb();
    float index = uv.index();
    ESP_LOGD("custom", "The value of sensor uva is: %.0f", uva);
    ESP_LOGD("custom", "The value of sensor uvb is: %.0f", uvb);
    ESP_LOGD("custom", "The calculated value of UV index is: %.0f", index);
    //publish_state(uva);
    uva_sensor->publish_state(uva);
    uvb_sensor->publish_state(uvb);
    uvindex_sensor->publish_state(index);
  }
};
