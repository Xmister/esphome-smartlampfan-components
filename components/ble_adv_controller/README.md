# ble_adv_light

## Known issues

* Only tested with Marpou Ceiling CCT light, and a certain aftermarket LED driver (definitely doesn't support RGB lights currently, but that could be added in the future).
* ZhiJia based lights pairing functionality hasn't been tested - if controlling a light that's been paired using the ZhiJia app doesn't work, please let me know. Unpairing will definitely not work (not supported in the app).

## How to try it

1. Create an ESPHome configuration that references the repo (using `external_components`)
2. Add a lamp controller `ble_adv_controller` specifying its ID to be referenced by entities it controls. The ID is the referenced used to pair with the device: if it is changed the device needs to be re-paired with the new ID.
3. Add one or several light or fan entities to the configuration with the `ble_adv_controller` platform
4. Add a `pair` configuration button to ease the pairing action from HA
5. Build the configuration and flash it to an ESP32 device (since BLE is used, ESP8266-based devices are a no-go)
6. Add the new ESPHome node to your Home Assistant instance
7. Use the newly created button to pair with your light (press the button withing 5 seconds of powering it with a switch).
6. Enjoy controlling your BLE light with Home Assistant!

## Example configuration: basic lamp using ZhiJia encoding and Pair button

```yaml
ble_adv_controller:
  - id: my_controller
    encoding: zhijia
    duration: 500

light:
  - platform: ble_adv_controller
    ble_adv_controller_id: my_controller
    name: Kitchen Light
    default_transition_length: 0s

button:
  - platform: ble_adv_controller
    ble_adv_controller_id: my_controller
    name: Pair
    cmd: pair
```

## Example configuration: Complex composed lamp using fanlamp_pro with 2 lights, a fan and a Pair button

```yaml
ble_adv_controller:
  # A controller per device, or per remote in fact as it has the same role
  - id: my_controller
    # encoding: could be any of 'zhijia', 'fanlamp_pro', 'smartlamp_pro'
    encoding: fanlamp_pro
    # variant: variant of the encoding (useless for zhijia). Can be any of 'v1a', 'v1b', 'v2' or 'v3', depending on how old your lamp is... Default is 'v3'
    variant: v3
    # the duration during which the command is sent. Increasing this parameter will make the combination of commands slower, but it may be needed if your light is taking time to process a command
    duration: 500
    # reversed: true

light:
  - platform: ble_adv_controller
    # ble_adv_controller_id: the ID of your controller
    ble_adv_controller_id: my_controller
    # name: the name as it will appear in 1A
    name: First Light
    # index: the index of the light in case several lights are part of the same device
    # this option was NOT TESTED yet, it MAY work for fanlamp_pro / smartlamp_pro. Not available for zhijia.
    index: 0
    # min_brightness: minimum brightness supported by the light before it shuts done
    # just test your lamp by decreasing the brightness percent by percent. 
    # when it switches off, you can find the 'cw' value in the logs, add 1 and you have your setting
    min_brightness: 21

  - platform: ble_adv_controller
    ble_adv_controller_id: my_controller
    name: Second Light
    index: 1

fan:
  - platform: ble_adv_controller
    ble_adv_controller_id: my_controller
    name: my fan

button:
  - platform: ble_adv_controller
    ble_adv_controller_id: my_controller
    name: Pair
    # cmd: the action to be executed when the button is pressed
    # any of 'pair', 'unpair', 'custom', 'light_on', ...
    cmd: pair
```

## Potentially fixable issues

If this component works, but the cold and warm temperatures are reversed (that is, setting the temperature in Home Assistant to warm results in cold/blue light, and setting it to cold results in warm/yellow light), add a `reversed: true` line to your `ble_adv_controller` config.

If the minimum brightness is too bright, and you know that your light can go darker - try changing the minimum brightness via the `min_brightness` configuration option (it takes a number between 1 and 255).

## For the very tecki ones

If you want to discover new features for your lamp and that you are able to understand the code of this component as well as the code of the applications that generate commands, you can try to send custom commands specifying the parameters manually using the api service <device name>_cmd_<controller_id> with the following parameters:
* type: 256 by default (0x100), a priori it has no incidence, but who knows
* index: 0 by default, should be changed to control other lights than the main one
* cmd: 16 to switch on the light (for a smartlamp_pro controller... 17 to switch off)
* arg0 to arg3: the parameters of the command

Note that the 'encoding' and 'variant' are defined by the controller.
You can also generate custom buttons for the command you discovered.