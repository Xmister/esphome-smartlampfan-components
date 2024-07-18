#include "ble_adv_fan.h"
#include "esphome/core/log.h"
#include "esphome/components/ble_adv_controller/ble_adv_controller.h"

namespace esphome {
namespace bleadvcontroller {

static const char *TAG = "ble_adv_fan";

fan::FanTraits BleAdvFan::get_traits() {
  auto traits = fan::FanTraits();

  traits.set_direction(true);
  traits.set_speed(this->speed_count_ > 0);
  traits.set_supported_speed_count(this->speed_count_);
  traits.set_oscillation(false);

  return traits;
}

void BleAdvFan::dump_config() {
  ESP_LOGCONFIG(TAG, "BleAdvFan '%s'", this->get_name().c_str());
  BleAdvEntity::dump_config_base(TAG);
}

void BleAdvFan::setup() {
  auto restore = this->restore_state_();
  if (restore.has_value()) {
    restore->apply(*this);
  }
}

void BleAdvFan::loop() {
  if (this->init_done) {
    return;
  }
  if (esphome::millis() > 5000) {
    this->init_done = true;
    auto restore = this->restore_state_();
    if (restore.has_value()) {
      this->_control(restore->to_call(*this), true);
    }
  }
}

void BleAdvFan::_write_speed() {
  this->command(CommandType::FAN_SPEED, this->speed, this->speed_count_);
}

void BleAdvFan::control(const fan::FanCall &call) {
  this->_control(call, false);
}

void BleAdvFan::_control(const fan::FanCall &call, bool force) {

  ESP_LOGD(TAG, "write_state");
  if (call.get_speed().has_value()) {
    if (this->speed != *call.get_speed() || !this->state || force) {
      this->speed = *call.get_speed();
      this->state = true;
      this->_write_speed();
    }
  } else if (call.get_state().has_value()) {
    if (this->state != *call.get_state() || force) {
      this->state = *call.get_state();
      if (this->state) {
        this->_write_speed();
      } else {
        this->command(CommandType::FAN_OFF);
      }
    }
  }
  if (call.get_direction().has_value()) {
    this->direction = *call.get_direction();
    this->command(CommandType::FAN_DIR, this->direction == esphome::fan::FanDirection::FORWARD);
  }
  this->publish_state();

}

} // namespace bleadvcontroller
} // namespace esphome
