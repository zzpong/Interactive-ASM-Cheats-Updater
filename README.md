# Interactive-ASM-Cheats-Updater

![DeviceTag](https://img.shields.io/badge/device-switch-red.svg)  ![LanguageTag](https://img.shields.io/badge/language-python3.8+-blue.svg) [![BuildTag](https://img.shields.io/badge/build-passing-success.svg)](https://github.com/zzpong/Interactive-ASM-Cheats-Updater/releases/tag/latest)  ![LicenseTag](https://img.shields.io/badge/license-GPL_3.0-orange.svg)

This updater unlocks your ability of updating most of the ASM cheats for Nintendo Switch.

![image](https://github.com/zzpong/Interactive-ASM-Cheats-Updater/blob/Stable-Branch/program_capture.png)

## Table of Contents
- [Functions](#functions)
- [Quick Start Guide](#quick-start-guide)
  	- [Pre-Requisites](#pre-requisites)
  	- [Downloading](#downloading)
  	- [Usage](#usage)
- [Building from Source](#building-from-source)
    - [Pre-Requisites For Build](#pre-requisites-for-build)
  	- [Hints For Pre-Requisites](#hints-for-pre-requisites)
  	- [Usage For Build](#usage-for-build)
- [Trouble Shooting](#trouble-shooting)
- [Contribution](#contribution)
- [Credits](#credits)
- [License](#license)


## Functions

![image](https://github.com/zzpong/Interactive-ASM-Cheats-Updater/blob/Stable-Branch/program_icon.jpg)

Now supports (same logic with code makers updating their codes like AOB from Cheat Engine):
- [x] Upgrade or degrade cheat codes
- [x] Update game cheat codes to other locales (if they don't rewrite the game code, then yes)
- [x] Search the whole main file for code features
- [x] Update normal ASM/code cave codes
- [x] Skip page/pageoff codes
- [x] Recognize branch codes and modify their pointer
- [x] Auto fill cheat bids when saving .txt file
- [x] Self-adapting inner parameters

TODO:
- [x] ASM code display
- [x] Output address sync with ASM code display
- [ ] Save modified .NSO file base on cheats
- [ ] Updating codes in .rodata or somewhere else (aka. high probability breaking the new game :cold_sweat:)


## Quick Start Guide

If you need a Chinese version introduction, please refer [here](https://www.91tvg.com/thread-293794-1-1.html). ??????????????????[??????](https://www.91tvg.com/thread-293794-1-1.html)???

### Pre-Requisites

* Windows 10 (:heavy_check_mark:), Windows 7 (:x: if ver < 0.2), Mac/Linux (???: rebuild required (thx to [Amuyea](https://gbatemp.net/members/amuyea.437000/)))
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

### Pre-Requisites For Build
* Python 3.9
* Packages in requirements.txt
* [upx](https://github.com/upx/upx) (if bundling to one file need)
* Spec file for pyinstaller (refer [here](https://pyinstaller.org/en/stable/spec-files.html) for more info)

### Hints For Pre-Requisites
* Choose any python version lower than 3.9 will unleash the support of Windows 7, but not tested. Please use at your own risk.
* There is a main.spec template in project root directory, please change demanded parameters before use.

### Usage For Build

#### Install Python and upx
* Don't forget to add environment variables.

#### Download source code

#### Use any command shell you familar with to install support packages
    cd your_source_code_root_dir
    py -3.9 -m pip install -r requirements.txt

#### Run the project
    py -3.9 __main__.py
    
#### OR build the project
    pyinstaller -F -w your_spec_name.spec --upx-dir your_upx_dir


## Trouble Shooting
1. Why my new codes doesn't work?
  
    A: On most cases, they are pointer cheat codes that can be recognized from the logs window. Please update these cheats with [EdiZon SE](https://github.com/tomvita/EdiZon-SE) or [SE tools](https://gbatemp.net/threads/se-tools-all-your-game-memory-hacking-needs-in-one-package.575131/).

2. Why my new codes break the game?

    A: Game developer will make a huge change for some specific version of games, like adding new function or improving code efficiency. In these cases, the ASM cheat codes need to be refind. 

3. Why this application repeating same title over and over again?

    A: It happened when capstone in the application failed to recognize bytes features. Here are some major reasons: zero gap in bytes file fail to work in capstone (fixed), nsnsotool decompressing command failed (fixed), application folder structure destroyed, cheat codes BID different from old main file. Please re-download this application or [create an issue](https://github.com/zzpong/Interactive-ASM-Cheats-Updater/issues/new).


## Contributing

Feel free to dive in! [Open an issue](https://github.com/zzpong/Interactive-ASM-Cheats-Updater/issues/new) or [submit PRs](https://github.com/zzpong/Interactive-ASM-Cheats-Updater/pulls).


## Credits

**Interactive ASM Cheats Updater** is based on

a.) [Keystone Engine](https://github.com/keystone-engine/keystone) and [Capstone Engine](https://github.com/capstone-engine/capstone): Without their brilliant work, Interactive ASM Cheats Updater will never be born.

b.) [nsnsotool](https://github.com/0CBH0/nsnsotool): This tiny program helps a lot on transforming nso files, made by 0CBH0.

**Also thanks to:**

[Eiffel2018](https://gbatemp.net/members/eiffel2018.536592/), [donghui2199](https://github.com/FantasyDH), [??????B](https://www.91tvg.com/space-uid-2230670.html), [Geminize](https://www.91tvg.com/space-uid-2337434.html) and [Konia1234](https://www.91tvg.com/space-uid-2300061.html) for their testing.

All cheat makers that sparing no effort in writing and updating cheat codes, you ARE the true heros!

All the helpers for bringing this project to life!


## License

This project is licensed under GNU General Public License v3.0.
<a href="https://www.gnu.org/licenses/gpl-3.0.en.html"><image src="http://www.gnu.org/graphics/gplv3-127x51.png" align="right"></a>

Refer the [LICENSE](LICENSE) file for more details.
