#pragma once

#include "ble_adv_controller.h"

namespace esphome {
namespace bleadvcontroller {

class ZhijiaController: public BleAdvController
{
public:
  virtual bool is_supported(CommandType cmd_type) override;
  virtual void get_adv_data(uint8_t * buf, Command &cmd) override;

protected:
  virtual uint8_t translate_cmd(CommandType cmd_type);
};

} //namespace bleadvcontroller
} //namespace esphome
