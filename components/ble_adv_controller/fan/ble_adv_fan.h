#pragma once

#include "esphome/components/fan/fan.h"
#include "../ble_adv_controller.h"

namespace esphome {
namespace bleadvcontroller {

class BleAdvFan : public fan::Fan, public BleAdvEntity
{
 public:
  void dump_config() override;
  fan::FanTraits get_traits() override;
  void control(const fan::FanCall &call) override;
  void setup() override;
  void loop() override;
  void _control(const fan::FanCall &call, bool force);
  void set_speed_count(uint8_t speed_count) { this->speed_count_ = speed_count; }
  void _write_speed();

protected:
  uint8_t speed_count_;
  bool init_done;
};

} //namespace bleadvcontroller
} //namespace esphome
