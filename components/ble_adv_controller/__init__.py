import esphome.codegen as cg
import esphome.config_validation as cv
from esphome import automation
from esphome.const import (
    CONF_DURATION,
    CONF_ID,
    CONF_NAME,
    CONF_REVERSED,
    CONF_TYPE,
    CONF_INDEX,
    CONF_VARIANT,
    PLATFORM_ESP32,
)
from esphome.cpp_helpers import setup_entity
from .const import (
    CONF_BLE_ADV_CONTROLLER_ID,
    CONF_BLE_ADV_ENCODING,
)


AUTO_LOAD = ["esp32_ble"]
DEPENDENCIES = ["esp32"]
MULTI_CONF = True

bleadvcontroller_ns = cg.esphome_ns.namespace('bleadvcontroller')
BleAdvController = bleadvcontroller_ns.class_('BleAdvController', cg.Component, cg.EntityBase)
BleAdvEntity = bleadvcontroller_ns.class_('BleAdvEntity', cg.Component)
FanLampController = bleadvcontroller_ns.class_('FanLampController', BleAdvController)
ZhijiaController = bleadvcontroller_ns.class_('ZhijiaController', BleAdvController)

FanLampVariant = bleadvcontroller_ns.enum("Variant")
CONTROLLER_VARIANTS = {
    "v3": FanLampVariant.VARIANT_3,
    "v2": FanLampVariant.VARIANT_2,
    "v1a": FanLampVariant.VARIANT_1A,
    "v1b": FanLampVariant.VARIANT_1B,
}

ENTITY_BASE_CONFIG_SCHEMA = cv.Schema(
    {
        cv.Required(CONF_BLE_ADV_CONTROLLER_ID): cv.use_id(BleAdvController),
        #cv.Optional(CONF_TYPE, default=0x0100): cv.hex_uint16_t,
        cv.Optional(CONF_INDEX, default=0): cv.uint8_t,
    }
)

CONFIG_SCHEMA = cv.All(
    cv.ENTITY_BASE_SCHEMA.extend(
        {
            cv.GenerateID(): cv.declare_id(BleAdvController),
            cv.Optional(CONF_BLE_ADV_ENCODING, default="fanlamp_pro"): cv.one_of("fanlamp_pro", "lampsmart_pro", "zhijia"),
            cv.Optional(CONF_VARIANT, default="v3"): cv.enum(CONTROLLER_VARIANTS, lower=True),
            cv.Optional(CONF_DURATION, default=100): cv.positive_int,
            cv.Optional(CONF_REVERSED, default=False): cv.boolean,
        }
    ),
    cv.only_on([PLATFORM_ESP32]),
)

async def entity_base_code_gen(var, config):
    await cg.register_parented(var, config[CONF_BLE_ADV_CONTROLLER_ID])
    cg.add(var.set_setup_priority(300)) # start after Bluetooth
    await cg.register_component(var, config)
    await setup_entity(var, config)
    #cg.add(var.set_type(config[CONF_TYPE]))
    cg.add(var.set_index(config[CONF_INDEX]))

async def to_code(config):
    # Defaulting NAME to ID in case not present, to ease object_id_hash creation
    if not CONF_NAME in config:
        config[CONF_NAME] = config[CONF_ID]
    if config[CONF_BLE_ADV_ENCODING] == "zhijia":
        config[CONF_ID].type = ZhijiaController
        var = cg.new_Pvariable(config[CONF_ID])
    else:
        config[CONF_ID].type = FanLampController
        var = cg.new_Pvariable(config[CONF_ID], config[CONF_VARIANT])  
    cg.add(var.set_setup_priority(300)) # start after Bluetooth
    await cg.register_component(var, config)
    await setup_entity(var, config)
    cg.add(var.set_tx_duration(config[CONF_DURATION]))
    cg.add(var.set_reversed(config[CONF_REVERSED]))


