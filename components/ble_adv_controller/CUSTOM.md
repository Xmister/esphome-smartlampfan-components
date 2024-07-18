# ble_adv_controller - Details and Custom commands

This component is reproducing the BLE advertising messages sent by android applications and/or remotes in order to control a device, itself composed of one or several lights / fans. In order to do so, some dev guys have uncompiled the software of those applications and extracted the command they supported as well as how those applications were encoding the BLE advertising messages issued and tried to reproduce them.

# What we know of the android applications using BLE advertising

## The bases
There are a few basics to know about android applications exchanging messages with devices:
* BLE advertising is a kind of **broadcast**: it sends messages in the air and not specifically to a given target, meaning that **ALL** BLE devices near to the controlling phone will receive the messages. Each device will then try to decode it, check if it is the effective target of the message and process the action in case it is or ignore it if it is not.
* Each message advertising is working as followed from the app point of view:
  - **Encoding**: A message is prepared based on the command issued and given to BLE advertising stack
  - **Start**: The advertising is started
  - **Wait**: wait for a few milliseconds (duration in the config) during which the message is repeatidly delivered to whoever listens
  - **Stop**: The advertising is stopped, the message is no more emitted
* The device listens to any BLE Advertising message emited with the following process:
  - if the message cannot be interpreted (wrong encoding), discard it
  - if the message is not containing the correct identifier, discard it
  - if the same message was already processed, discard it
  - else process it
* **Pairing** consists in having the phone (or controller) and the device agreeing on an identifier to be sent in all messages and that would indicate the device is the effective target of the message. This is done by sending a pairing message including an identifier generated by the app/controller to the device. When the device receives this message with an identifier it does not know it will just ... ignore it ... EXCEPT if it has been restarted (power off/on) less than 5 seconds ago, in this case it will accept the new identifier. This is the choosen way to have a specific device accepting a new identifer, and not all the devices in the roomm...
* Pairing with several controllers is possible, at least a remote and a phone, but it seems the phone apps and our apps may have to share the same identifier, which for now is not supported as the ID is generated differently.
* When the device is delivered to the end-user, it will no more change, meaning that the messages it receives to be controlled will have to be always the same. This particularly means that if an application is able to control it at a given time, any new version of this application in the future (new android version, bug fix, ...) will have to support the send of those exact same messages.


## The messages
The BLE Advertising messages are composed of different parts:
* The BLE Advertising Parameters (esp_ble_adv_params_t) which are always the same and part of the BLE standard
* The BLE Advertising data (usually 31 bytes) composed of:
  * A Header (esp_ble_adv_data_t) also part of the BLE standard
  * A **Manufacturer Data** section, usually composed of 26 bytes

The goal of this component is to convert each entity action into this Manufacturer Data section (encoding) and emit it. Still this is not so simple as there are several applications using this methodology, and for each application different ways of encoding the data that evovled in the last years.

Supported Applications:
* **Zhi jia**, only for the light part
* **FanLamp Pro** / **LampSmart Pro**, for the light and fan part. Includes several encoding variant: v1a / v1b / v2 / v3

To build the Manufacturer Data section corresponding to a command, the encoding is done as follow:
* Convert the command and its parameters into a base 26 bytes structure containing among other:
  * A **type**: a 2 bytes code. No one found out yet the use of it, seems to be always 0x0100 but can be set to anything it seems
  * An **index** / group_index: a 1 byte code allowing to identify sub entities. 0 for the main light, 1 for another light, ... (NOT TESTED YET)
  * A **command id**: a code based on one byte identifying a command. Different in between applications but usually common between variants of a same app.
  * Command **arguments**: 0 to 4 bytes containing parameters of the command (fan speed value, light brigthness, ...)
* Add parameters from the controller part:
  * An **identifier**: a 2 or 4 bytes code generated and exchanged during pairing, identifying a device in a 'unique' way
  * A **transaction count**: a 1 byte code increased by 1 on each transaction. Allows the device to identify if a message was already read and processed, and not re-process it (guess)
* Signing: compute an id based on a hard coded key allowing the device to be sure the message is coming only from the allowed app and would not be an interference from another message from another app (or a way to try to prevent smart people to reproduce the message...)
* CRC computing: to be sure the message is complete and not corrupted
* Whitening: to avoid the message to be mostly zeros

# Custom Command Service
if you are using 'api' component to communicate with HA, for each ble_adv_controller a HA service is available:
* name of the service:
```
esphome: <device_name>_cmd_<ble_adv_controller_id>
```
![screenshot](../../docs/images/BleAdvService.jpg)

It uses as a bases the ble_adv_controller, and then its associated parameters and features (encoding, variant, identifier, transaction count). It allows to specify directly command parameters (type, index, cmd, arg0..3) skipping the 'Convert' part and processing the encoding from there (add controller params, Signing, CRC, Whitening and emitting command).

## Known commands
For info here are the "known" commands already extracted from code and their corresponding command id and parameter values when known, for each main encoding sets:
* **ZhiJia**: 
  * uses ZhiJia encoding, no variant. 
  * Only arg0 used for known commands, BUT arg1 and arg2 available in message structure
* **FanLamp v1**: 
  * for FanLamp Pro / SmartLamp Pro, with variant v1a and v1b using the same data structure.
  * arg0 and arg1 used for known commands, but arg2 available (and used by pair command btw...)
* **FanLamp v2**: 
  * for FanLamp Pro / SmartLamp Pro, with variant v2 and v3 (v3 is v2 plus a signing step)
  * arg0 never used but available.
  * arg1, arg2 and arg3 used depending on the commands

| Command      | ZhiJia      | FanLamp v1        | FanLamp v2        |
|--------------|-------------|-------------------|-------------------|
| pair         | 0xA2        | 0x28, garbage in args...  | 0x28              |
| unpair       | 0x45?       | 0x45              | 0x45              |
| light_on     | 0xA5        | 0x10              | 0x10              |
| light_off    | 0xA6        | 0x11              | 0x11              |
| light_dim    | 0xAD, arg0  | N/A               | N/A ?             |
| light_cct    | 0xAE, arg0  | N/A               | N/A ?             |
| light_dimcct | N/A         | 0x21, arg0 arg1   | 0x21, arg2, arg3  |
| fan_on(3)    | N/A         | 0x31, arg0=0      | 0x31, arg2=0      |
| fan_off(3)   | N/A         | 0x31, arg0=0      | 0x31, arg2=0      |
| fan_speed(3) | N/A         | 0x31, arg0=1..3           | 0x31, arg2=1..3   |
| fan_on(6)    | N/A         | 0x32, arg0=0, arg1=6      | 0x31, arg2=0, arg1=0x20      |
| fan_off(6)   | N/A         | 0x32, arg0=0, arg1=6      | 0x31, arg2=0, arg1=0x20      |
| fan_speed(6) | N/A         | 0x32, arg0=1..3, arg1=6   | 0x31, arg2=1..3, arg1=0x20   |
| fan_dir      | N/A         | 0x15, arg0=0..1   | 0x15, arg1=0..1   |

NOTE: the cmd code given are hexa codes, **you have to translate them into decimal for use in HA service**, use Windows Calculator in programmer mode.

## Guessing commands
Well one can try all options and values... Or try to read the decompiled software !

### ZhiJia
TODO, commands and codes are coming from the repo 'ble_adv_light'

### FanLamp v1 (v1a and v1b)
* Base source available [HERE](https://gist.github.com/NicoIIT/527f21f7bbbd766b9844d5efbef86959)
* Commands are calling function 'getMessage' with 3, 4 or 5 parameters most of the time:
```
getMessage(cmd, index, tx_count)
getMessage(cmd, index, value1, tx_count)
getMessage(cmd, index, value1, value2, tx_count)
```
All are at the end calling the same encoding function with 7 params, for info only:
```
getmessage(cmd, LampData.mMasterControlAddr, index, value1, value2, LampConfig.UNK1, tx_count)
```
For the custom command, the mapping is the following:
* cmd -> cmd
* index -> index
* value1 -> arg0
* value2 -> arg1
* unused: type, arg2, arg3

Example custom commands:
* Fan Level to 3 for fan with index 0: 
  * software:
  ```
      public void sendFanLevelMessage(int i, int i2, int i3) {
        startSendData(getMessage(49, i, i2, i3));
    }
  ```
  * custom command parameters: {type: 0, index: 0, cmd: 49, arg0: 3, arg1: 0, arg2: 0, arg3: 0}
* Fan Gear to 5 for fan with index 0: 
  ```
    public void sendFanGearMessage(int i, int i2, int i3) {
        startSendData(getMessage(50, LampData.mMasterControlAddr, i, i2, 6, LampConfig.UNK1, i3));
    }
  ```
  * custom command parameters: {type: 0, index: 0, cmd: 50, arg0: 5, arg1: 6, arg2: 0, arg3: 0}.

Note that the Fan Gear command is the same as Fan Level but it gives 6 levels instead of 3. Depend on the device to be controlled.

### FanLamp v2 (v2 and v3)
* Base source available [HERE](https://gist.github.com/aronsky/f433de654f008fedb5161e08eb32c33e) and [HERE](https://gist.github.com/aronsky/f2d8afab134d15f34256187a82a53a9c)
* Commands are feeding the following data structure:
  * blev2para.type -> type (but with no impact...);
  * blev2para.group_index -> index;
  * blev2para.cmd -> cmd;
  * blev2para.para[0] -> arg0;
  * blev2para.para[1] -> arg1;
  * blev2para.para[2] -> arg2;
  * blev2para.para[3] -> arg3;

Example custom commands:
* Fan Level to 3 for fan with index 0: 
  * software:
  ```
  jbyteArray Java_com_alllink_encodelib_Tool_blevbFanSpeed(JNIEnv *env,jclass jobj,jint type,jlong addr,jint index,jshort generic_flag,jshort value)
  {
    ...
    memset(&blev2para,0,0x18);
    blev2para.type = (uint16_t)type;
    blev2para.addr = (uint32_t)addr;
    blev2para.group_index = (uint8_t)index;
    blev2para.cmd = 0x31;
    blev2para.para[1] = (uint8_t)generic_flag;
    blev2para.para[2] = (uint8_t)value;
    ble_v2_encode(&blev2para,decoded_data);
    ...
  }  
  ```
  * custom command parameters: {type: 0, index: 0, cmd: 49, arg0: 0, arg1: 32, arg2: 3, arg3: 0}

Note that arg1 should take the 'generic_flag' value, but no idea how to build this one, this is where the '**guess**' happens: after 31 unsuccessful tries, the 32nd worked!