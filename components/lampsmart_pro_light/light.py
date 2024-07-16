import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import light, output
from esphome.components import esp32_ble
from esphome import automation
from esphome.const import (
    CONF_DURATION,
    CONF_CONSTANT_BRIGHTNESS,
    CONF_OUTPUT_ID,
    CONF_COLD_WHITE_COLOR_TEMPERATURE,
    CONF_WARM_WHITE_COLOR_TEMPERATURE,
    CONF_REVERSED,
    CONF_MIN_BRIGHTNESS, # New in 2023.5
    CONF_ID,
    CONF_VARIANT,
    PLATFORM_ESP32,
)

from . import LampSmartProQueue, CONF_QUEUE_ID

AUTO_LOAD = ["esp32_ble", "."]
DEPENDENCIES = ["esp32", "lampsmart_pro_light"]

lampsmartpro_ns = cg.esphome_ns.namespace('lampsmartpro')
LampSmartProLight = lampsmartpro_ns.class_('LampSmartProLight', cg.Component, light.LightOutput, 
    cg.Parented.template(LampSmartProQueue))
PairAction = lampsmartpro_ns.class_("PairAction", automation.Action)
UnpairAction = lampsmartpro_ns.class_("UnpairAction", automation.Action)

ACTION_ON_PAIR_SCHEMA = cv.All(
    automation.maybe_simple_id(
        {
            cv.Required(CONF_ID): cv.use_id(light.LightState),
        }
    )
)

ACTION_ON_UNPAIR_SCHEMA = cv.All(
    automation.maybe_simple_id(
        {
            cv.Required(CONF_ID): cv.use_id(light.LightState),
        }
    )
)

LampSmartProVariant = lampsmartpro_ns.enum("LampSmartProVariant")
LAMP_VARIANTS = {
    "v3": LampSmartProVariant.VARIANT_3,
    "v2": LampSmartProVariant.VARIANT_2,
    "v1a": LampSmartProVariant.VARIANT_1A,
    "v1b": LampSmartProVariant.VARIANT_1B,
}

CONFIG_SCHEMA = cv.All(
    light.RGB_LIGHT_SCHEMA.extend(
        {
            cv.GenerateID(CONF_OUTPUT_ID): cv.declare_id(LampSmartProLight),
            cv.Optional(CONF_DURATION, default=100): cv.positive_int,
            cv.Optional(CONF_COLD_WHITE_COLOR_TEMPERATURE): cv.color_temperature,
            cv.Optional(CONF_WARM_WHITE_COLOR_TEMPERATURE): cv.color_temperature,
            cv.Optional(CONF_CONSTANT_BRIGHTNESS, default=False): cv.boolean,
            cv.Optional(CONF_REVERSED, default=False): cv.boolean,
            cv.Optional(CONF_MIN_BRIGHTNESS, default=0x7): cv.hex_uint8_t,
            cv.GenerateID(CONF_QUEUE_ID): cv.use_id(LampSmartProQueue),
            cv.Optional(CONF_VARIANT, default="v3"): cv.enum(LAMP_VARIANTS, lower=True)
        }
    ),
    cv.has_none_or_all_keys(
        [CONF_COLD_WHITE_COLOR_TEMPERATURE, CONF_WARM_WHITE_COLOR_TEMPERATURE]
    ),
    light.validate_color_temperature_channels,
    cv.only_on([PLATFORM_ESP32]),
)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_OUTPUT_ID])

    parent = await cg.get_variable(config[CONF_QUEUE_ID])
    cg.add(var.set_parent(parent))

    await cg.register_component(var, config)
    await light.register_light(var, config)

    if CONF_COLD_WHITE_COLOR_TEMPERATURE in config:
        cg.add(
            var.set_cold_white_temperature(config[CONF_COLD_WHITE_COLOR_TEMPERATURE])
        )

    if CONF_WARM_WHITE_COLOR_TEMPERATURE in config:
        cg.add(
            var.set_warm_white_temperature(config[CONF_WARM_WHITE_COLOR_TEMPERATURE])
        )

    cg.add(var.set_constant_brightness(config[CONF_CONSTANT_BRIGHTNESS]))
    cg.add(var.set_reversed(config[CONF_REVERSED]))
    cg.add(var.set_min_brightness(config[CONF_MIN_BRIGHTNESS]))
    cg.add(var.set_tx_duration(config[CONF_DURATION]))
    cg.add(var.set_variant(config[CONF_VARIANT]))


@automation.register_action(
    "lampsmartpro.pair", PairAction, ACTION_ON_PAIR_SCHEMA
)
@automation.register_action(
    "lampsmartpro.unpair", UnpairAction, ACTION_ON_UNPAIR_SCHEMA
)
async def lampsmartpro_pair_to_code(config, action_id, template_arg, args):
    parent = await cg.get_variable(config[CONF_ID])
    return cg.new_Pvariable(action_id, template_arg, parent)
