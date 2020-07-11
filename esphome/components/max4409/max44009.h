#pragma once

#include "esphome/core/component.h"
#include "esphome/components/sensor/sensor.h"
#include "esphome/components/i2c/i2c.h"

namespace esphome {
namespace max44009 {

enum MAX44009Constants {
  MAX44009_DEFAULT_ADDRESS = 0x4A,
  MAX44009_ALT_ADDRESS     = 0x4B,
  MAX44009_OK = 0,
  MAX44009_ERROR_WIRE_REQUEST = -10,
  MAX44009_ERROR_OVERFLOW     = -20,
  MAX44009_ERROR_HIGH_BYTE    = -30,
  MAX44009_ERROR_LOW_BYTE     = -31,
};

enum MAX44009Registers {
  MAX44009_INTERRUPT_STATUS = 0x00,
  MAX44009_INTERRUPT_ENABLE = 0x01,
  MAX44009_CONFIGURATION    = 0x02,
  MAX44009_LUX_READING_HIGH = 0x03,
  MAX44009_LUX_READING_LOW  = 0x04,
  MAX44009_THRESHOLD_HIGH   = 0x05,
  MAX44009_THRESHOLD_LOW    = 0x06,
  MAX44009_THRESHOLD_TIMER  = 0x07,
};

enum MAX44009CfgMasks {
  MAX44009_CFG_CONTINUOUS = 0x80,
  MAX44009_CFG_MANUAL     = 0x40,
  MAX44009_CFG_CDR        = 0x08,
  MAX44009_CFG_TIMER      = 0x07,
};


/** Provide support for MAX44009 i2c ambient light sensor
 * Two key features of the IC analog design are its ultra-low
 * current consumption (typically 0.65µA) and an extremely
 * wide dynamic light range that extends from 0.045 lux to
 * 188,000 lux—more than a 4,000,000 to 1 range.
 */
class MAX44009Sensor : public sensor::Sensor, public PollingComponent, public i2c::I2CDevice {
 public:
  void setup() override;
  void dump_config() override;
  void update() override;
 protected:
  float   read_lux();
};

}  // namespace max44009
}  // namespace esphome
