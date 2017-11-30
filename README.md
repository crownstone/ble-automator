# Python binary: ble-automator

Automate interactions with a BLE device.

## Usage

The file `bleAutomator.py` contains some functions to write and read data to a Crownstone and some general BLE devices.

Currently you first have to use encryption by filling in your keys.

To get your keys, log in to the [cloud](https://cloud.crownstone.rocks/), then fill in the token at the [API explorer](https://cloud.crownstone.rocks/explorer).
After that, get your user id, with a [GET on /users/me](https://cloud.crownstone.rocks/explorer/#!/user/user_me).
Finally, get your keys with a [GET on /users/{id}/keys](https://cloud.crownstone.rocks/explorer/#!/user/user_getEncryptionKeys).

Copy the default file `config.public.json` to `config.json` (the latter is the default used by the scripts):

    cp config.public.json config.json

Then fill in the address and keys:

    {
      "addresses":[
        "XX:XX:XX:XX:XX:XX"
      ],
      "sphereId": "1234abcd1234abcd1234abcd",
      "keys": {
        "admin": "1234abcd1234abcd1234abcd1234abcd",
        "member": "1234abcd1234abcd1234abcd1234abcd",
        "guest": "1234abcd1234abcd1234abcd1234abcd"
      }
    }

The send command script is most versatile. For example, to turn on a crownstone:

    ./sendCommand.py -i hci0 -a "00:11:22:33:44:55" -v -e -t 0 -d 100 -n -s 1

Some explanation:

- `-t 0` for command type 0 (see the [protocol](https://github.com/crownstone/bluenet/blob/master/docs/PROTOCOL.md#control_packet)).
- `-d 100` for value 100.
- `-n` interpret value as a number.
- `-s 1` size of the value is 1 byte.

To get data from advertisements:

    ./getAdvertisements.py -i hci0 -a "00:11:22:33:44:55" -v -e

To get the correct data, you need the correct key, or else the data will be scrambled!

Also note that a message like `Failed to execute mgmt cmd 'le on'` means that you need superuser rights to scan for
BLE devices. Run the above with `sudo`.

It might also help to add the address through `hcitool`

    sudo hcitool lewladd "00:11:22:33:44:55"

## Prerequisites

Prior to running, install:

* bluez
* python 2.7
* [bluepy](https://github.com/IanHarvey/bluepy) - Currently you have to get an older version:
  * `sudo apt-get install git build-essential libglib2.0-dev libdbus-1-dev python-dev`
  * `git clone https://github.com/IanHarvey/bluepy.git`
  * `cd bluepy`
  * `git checkout v/0.9.11`
  * `python setup.py build`
  * `sudo python setup.py install`
* intelhex
* matplotlib

On Ubuntu this can be installed through:

```
sudo apt-get install bluez python-pip python-matplotlib
sudo pip install pexpect
sudo pip install intelhex --allow-unverified intelhex
sudo pip install pycrypto
```

# Advanced features

## Create firmware

To create .zip file for the Nordic app to upload new firmware, we will have to wrap a `crownstone.hex` file. 

The following will create a .zip file with a .bin binary, a Manifest file and a .dat file.

	python dfGenPkg.py -a crownstone.hex

This used to create a .zip file with a .hex file, but that doesn't play well with DFU version 0.8.
