ble-automator
======================================
Automate interactions with a BLE device.

Some of the scripts have hardcoded addresses.


## How to use:

The file bleAutomator.py contains handy function to write and read data to a BLE device.

Currently you first have to use encryption by filling in your keys.

To get your keys, log in to the [cloud](https://cloud.crownstone.rocks/), then fill in the token at the [API explorer](https://crownstone-cloud.herokuapp.com/explorer).
After that, get your user id, with a [GET on /users/me](https://crownstone-cloud.herokuapp.com/explorer/#!/user/user_me).
Finally, get your keys with a [GET on /users/{id}/keys](https://crownstone-cloud.herokuapp.com/explorer/#!/user/user_getEncryptionKeys).

Then fill in the keys in the scripts, like so:

    adminKey  = "61646d696e4b6579466f7243726f776e".decode("hex")
    memberKey = "6d656d6265724b6579466f72486f6d65".decode("hex")
    guestKey  = "67756573744b6579466f724769726c73".decode("hex")

The send command script is most versatile. For example, to turn on a crownstone:

    ./sendCommand.py -i hci0 -a 00:11:22:33:44:55 -v -e -t 0 -d 100 -n -s 1

Some explanation:

- `-t 0` for command type 0 (see the [protocol](https://github.com/crownstone/bluenet/blob/master/docs/PROTOCOL.md#control_packet)).
- `-d 100` for value 100.
- `-n` interpret value as a number.
- `-s 1` size of the value is 1 byte.



To get data from advertisements:

    ./getAdvertisements.py -i hci0 -a 00:11:22:33:44:55 -v -e

To get the correct data, you need the correct key.

### How to use the Powermate

To run the script that connects with the PowerMate button, you will first need to add it:

    sudo hcitool lewladd 00:12:92:08:05:16

If you set a random address for yourself, with for example `-t random` as argument you will need to do this again. Or else you will encounter this error:

    [   ][00:12:92:08:05:16][LE]> connect
    Connecting... connect error: Transport endpoint is not connected (107)

During the connection attempt you will have to press the button!

## Prerequisite:

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

```
sudo apt-get install bluez python-pip python-matplotlib
sudo pip install pexpect
sudo pip install intelhex --allow-unverified intelhex
sudo pip install pycrypto
```

======================================

## Create .zip file for Nordic app

The following will create a .zip file with a .bin binary, a Manifest file and a .dat file.

	python dfGenPkg.py -a crownstone.hex

This used to create a .zip file with a .hex file, but that doesn't play well with DFU version 0.8.
