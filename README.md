# Interactive-ASM-Cheats-Updater
![DeviceTag](https://img.shields.io/badge/device-switch-red.svg)  ![LanguageTag](https://img.shields.io/badge/language-python3.9+-blue.svg) ![BuildTag](https://img.shields.io/badge/build-passing-success.svg)  ![LicenseTag](https://img.shields.io/badge/license-GPL_3.0-orange.svg)

This updater unlocks your ability of updating most of the ASM cheats for Nintendo Switch.


## Table of Contents
- [Functions](#functions)
- [Quick Start Guide](#quick-start-guide)
  	- [Pre-Requisites](#pre-requisites)
  	- [Downloading](#downloading)
  	- [Usage](#usage)
- [Building from Source](#building-from-source)
- [Trouble Shooting](#trouble-shooting)
- [Contribution](#contribution)
- [Credits](#credits)
- [License](#license)


## Functions

Now supports (same logic with cheats makers updating their codes like AOB):
- [x] Update game cheats to other locales (if they don't rewrite the game code, then yes)
- [x] Search the whole main file for code features
- [x] Update normal ASM codes
- [x] Update code cave codes
- [x] Skip page/pageoff codes
- [x] Recognize branch codes and modify their pointer
- [x] Auto fill cheat bids when saving .txt file

TODO:
- [ ] Save modified .NSO file base on cheats
- [ ] Updating codes in .rodata or somewhere else (aka. high probability breaking the new game :cold_sweat:)


## Quick Start Guide

### Pre-Requisites

* Better windows platform, mac/linux not tested
* No python environment required

### Downloading

Visit out [releases](https://github.com/zzpong/Interactive-ASM-Cheats-Updater/releases) page or download the [latest](https://github.com/zzpong/Interactive-ASM-Cheats-Updater/releases/tag/latest) version.

### Usage

#### Dump main file from xci/nsp/nsz game/updates
There are lots of excellent works for you to dump the main file, like [hactool](https://github.com/SciresM/hactool) and [NSC_Builder](https://github.com/julesontheroad/NSC_BUILDER). Please choose anyone you familiar with to dump two main files:
* **Old Main File**: dump from the game which old cheat runs on
* **New main File**: dump from the game which you want to update the old cheat to

#### Load main file and copy cheat codes
Build ID of the old main file will be shown after loading. Please make sure it is the same with the old cheat.

#### Interactively updating the cheat codes
Logs window has everything you need when updating cheat codes.
* **Generate**: Generate one code or title
* **Skip**: Skip one code or title, especially for pointer cheats.
* **Undo**: Undo the last operation.
* **Restart**: Restart the whole process.
* **Wing Length**: Decide how many asm code lines are extracted as code features before and after the target address. Supported input type like array [left_side, right_side] and integer "single_input" are listed below:

|  Type  |  Left Side  |  Right Side  |  Support Single Input  |
| :------------------: | :------------------: | :------------------: | :------------------: |
| Normal ASM code | feature lines before ASM address | feature lines after ASM address | :heavy_check_mark: | 
| Branch to code cave | feature lines before bl address | feature lines after bl address | :heavy_check_mark: | 
| Branch with target address | wing length for bl address | wing length for bl target address | :x: | 

* **Regenerate**: Useful when logs window show "address not found". Please change wing length and regenerate until single hit, or maybe double.
* **Debug**: Generate a debug folder with procedure files to show you what happend during the whole progress.

#### Save cheat codes with "SaveCHT" button


## Building from Source

Under construction after a stable release with original codes.


## Trouble Shooting
1. Why my new codes doesn't work?
  
    A: On most cases, they are pointer cheat codes that can be recognized from the logs window. Please update these cheats with [EdiZon SE](https://github.com/tomvita/EdiZon-SE).

2. Why my new codes break the game?

    A: Game developer will make a huge change for some specific version of games, like adding new function or improving code efficiency. In these cases, the ASM cheat codes need to be refind. 


## Contribution

Under construction after a stable release with original codes.


## Credits

**Interactive ASM Cheats Updater** is based on

a.) [Keystone Engine](https://github.com/keystone-engine/keystone) and [Capstone Engine](https://github.com/capstone-engine/capstone): Without their brilliant work, Interactive ASM Cheats Updater will never be born.

b.) [nsnsotool](https://github.com/0CBH0/nsnsotool): This tiny program helps a lot on transforming nso files, made by 0CBH0.

**Also thanks to:**

[Eiffel2018](https://gbatemp.net/members/eiffel2018.536592/), [donghui2199](https://github.com/FantasyDH), [怪盗B](https://www.91tvg.com/space-uid-2230670.html) and [Geminize](https://www.91tvg.com/space-uid-2337434.html) for their testing.

All cheat makers that sparing no effort in writing and updating cheat codes, you ARE the true heros!

All the helpers for bringing this project to life!


## License

This project is licensed under GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
