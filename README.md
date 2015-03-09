ble-automator
======================================
Automate interactions with a BLE device. 

Some of the scripts have hardcoded addresses.


## How to use:

The file bleAutomator.py contains handy function to write and read data to a BLE device.
An example usage is recorder.py which uses it to sample current usage of the crownstone.

Use the scripts like:

    ./turnoff.py -i hci0 -a E5:C8:68:8A:BB:9C

## Prerequisite:

Prior to running, install:

* bluez
* python 2.7
* pexpect
* intelhex

```
sudo apt-get install bluez python-pip
sudo pip install pexpect
sudo pip install intelhex --allow-unverified intelhex
```
