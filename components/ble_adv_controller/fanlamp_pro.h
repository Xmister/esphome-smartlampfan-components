#pragma once

#include "ble_adv_controller.h"

namespace esphome {
namespace bleadvcontroller {

enum Variant : int {VARIANT_3, VARIANT_2, VARIANT_1A, VARIANT_1B};

class FanLampController: public BleAdvController
{
public:
  FanLampController(Variant variant): variant_(variant) {}
  virtual bool is_supported(CommandType cmd_type) override;
  virtual void get_adv_data(uint8_t * buf, Command &cmd) override;

protected:
  virtual uint8_t translate_cmd(CommandType cmd_type);

  void build_packet_v1a(uint8_t* buf, Command &cmd);
  void build_packet_v1b(uint8_t* buf, Command &cmd);
  void build_packet_v1(uint8_t* buf, Command &cmd);
  void build_packet_v2(uint8_t* buf, Command &cmd, bool with_sign);

  Variant variant_;
};

} //namespace bleadvcontroller
} //namespace esphome
