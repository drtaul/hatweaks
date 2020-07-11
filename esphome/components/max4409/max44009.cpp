#include "max44009.h"
#include "esphome/core/log.h"

namespace esphome {
namespace max44009 {

static const char *TAG = "max44009.sensor";


void MAX44009Sensor::setup() {
  ESP_LOGCONFIG(TAG, "Setting up Max44009...");
}
void MAX44009Sensor::dump_config() {
  ESP_LOGCONFIG(TAG, "MAX44009:");
  LOG_I2C_DEVICE(this);
}

void MAX44009Sensor::update() {
  // Enable sensor
  ESP_LOGV(TAG, "accessing lux data");
  float lx = read_lux();
  this->publish_state(lx);
  this->status_clear_warning();
}

float MAX44009Sensor::read_lux() {
  uint8_t dhi, dlo;
  float val = 0;
  if (read_byte(MAX44009_LUX_READING_HIGH, &dhi))
    {
      if (read_byte(MAX44009_LUX_READING_LOW, &dlo))
	{
	  uint8_t e = dhi >> 4;
	  if (e == 0x0F)
	    {
	      ESP_LOGE(TAG, "OVERFLOW ERROR");
	      val = MAX44009_ERROR_OVERFLOW;
	      this->status_set_warning();
	    }
	  else
	    {
	      uint32_t m = ((dhi & 0x0F) << 4) + (dlo & 0x0F);
	      m <<= e;
	      val = m * 0.045;
	    }
	}
      else
	{
	  ESP_LOGE(TAG, "READ LOW BYTE ERROR");
	  val = MAX44009_ERROR_LOW_BYTE;
	  this->status_set_warning();
	}
    }
  else
    {
	  ESP_LOGE(TAG, "READ HIGH BYTE ERROR");
	  val = MAX44009_ERROR_HIGH_BYTE;
	  this->status_set_warning();
    }
  return val;
}
  
}  // namespace max44009
}  // namespace esphome
