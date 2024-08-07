CONF_BLE_ADV_CONTROLLER_ID = "ble_adv_controller_id"
CONF_BLE_ADV_CMD = "cmd"
CONF_BLE_ADV_ARGS = "args"
CONF_BLE_ADV_NB_ARGS = "nb_args"
CONF_BLE_ADV_ENCODING = "encoding"
CONF_BLE_ADV_COMMANDS = {
  "pair" : {CONF_BLE_ADV_CMD: 1, CONF_BLE_ADV_NB_ARGS : 0},
  "unpair" : {CONF_BLE_ADV_CMD: 2, CONF_BLE_ADV_NB_ARGS : 0},
  "custom" : {CONF_BLE_ADV_CMD: 3, CONF_BLE_ADV_NB_ARGS : 5},
  "light_on" : {CONF_BLE_ADV_CMD: 13, CONF_BLE_ADV_NB_ARGS : 0},
  "light_off" : {CONF_BLE_ADV_CMD: 14, CONF_BLE_ADV_NB_ARGS : 0},
  "light_dim" : {CONF_BLE_ADV_CMD: 15, CONF_BLE_ADV_NB_ARGS : 1},
  "light_cct" : {CONF_BLE_ADV_CMD: 16, CONF_BLE_ADV_NB_ARGS : 1},
  "light_dimcct" : {CONF_BLE_ADV_CMD: 17, CONF_BLE_ADV_NB_ARGS : 2},
  "fan_on" : {CONF_BLE_ADV_CMD: 30, CONF_BLE_ADV_NB_ARGS : 0},
  "fan_off" : {CONF_BLE_ADV_CMD: 31, CONF_BLE_ADV_NB_ARGS : 0},
  "fan_speed" : {CONF_BLE_ADV_CMD: 32, CONF_BLE_ADV_NB_ARGS : 1},
  "fan_dir" : {CONF_BLE_ADV_CMD: 33, CONF_BLE_ADV_NB_ARGS : 1},
}
CONF_BLE_ADV_SPEED_COUNT = "speed_count"
CONF_BLE_ADV_FORCED_ID = "forced_id"
