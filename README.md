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
* **Skip**: Skip one code or title, especially for pointer cheats. You can update pointer cheats with [EdiZon SE](https://github.com/tomvita/EdiZon-SE).
* **Undo**: Undo the last operation.
* **Restart**: Restart the whole process.
* **Wing Length**: Decide how many asm code lines are extracted as code features before and after the target address. Supported input type like array [left_side, right_side] and integer "single_input" are listed below:

|  Type  |  Left Side  |  Right Side  |  Support Single Input  |
| :------------------: | :------------------: | :------------------: | :------------------: |
| Normal ASM code | feature lines before ASM address | feature lines after ASM address | :heavy_check_mark: | 
| Branch to code cave | feature lines before bl address | feature lines after bl address | :heavy_check_mark: | 
| Branch with target address | wing length for bl address | wing length for bl target address | :x: | 

* **Regenerate**: Useful when logs window show "address not found". Please change wing length and regenerate until single hit, or maybe double.

#### Save cheat codes with "SaveCHT" button


## Building from Source

Under construction after a stable release with original codes.
