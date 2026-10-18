# Code Updater for Nintendo Switch

![DeviceTag](https://img.shields.io/badge/device-switch-red.svg)  ![LanguageTag](https://img.shields.io/badge/language-python3.9+-blue.svg) [![BuildTag](https://img.shields.io/badge/build-passing-success.svg)](https://github.com/zzpong/Interactive-ASM-Cheats-Updater/releases/tag/latest)  ![LicenseTag](https://img.shields.io/badge/license-GPL_3.0-orange.svg)

Unlocks your ability of updating ASM codes for Nintendo Switch.

This fork provides unofficial compatibility fixes contributed by Eiffel2018.
The original project is by [zzpong](https://github.com/zzpong/Interactive-ASM-Cheats-Updater);
all copyright and ownership of the original project remain with zzpong.
Existing GPL-3.0 and third-party license notices are retained. The application
keeps its upstream v1.1.4 version number; this is not an official zzpong release.

![image](https://github.com/zzpong/Interactive-ASM-Cheats-Updater/blob/Active-Branch/program_capture.png)

## Table of Contents
- [Functions](#functions)
- [Quick Start Guide](#quick-start-guide)
  	- [Pre-Requisites](#pre-requisites)
  	- [Downloading](#downloading)
  	- [Usage](#usage)
- [Building from Source](#building-from-source)
    - [Pre-Requisites For Build](#pre-requisites-for-build)
  	- [Usage For Build](#usage-for-build)
- [Trouble Shooting](#trouble-shooting)
- [Contribution](#contribution)
- [Credits](#credits)
- [License](#license)


## Functions

![image](https://github.com/zzpong/Interactive-ASM-Cheats-Updater/blob/Active-Branch/program_icon.jpg)

Now supports:
- [x] Migrate codes to games from different distribution areas
- [x] Upgrade or degrade codes for all available game versions
- [x] XCZ/XCI/NSP/NSZ game packages auto extraction
- [x] ARM64/ARM32 codes update with automatic sorting
- [x] Recognize branch codes and modify their pointer
- [x] Update multiple code cave codes with precisely structures
- [x] Save modified .txt or .NSO file as you like

What's new:
- [x] Catchy tool title (which is very important)
- [x] Faster code feature localization algorithm
- [x] Support master/normal code cross branches
- [x] Support codes in .rodata
- [x] Customizable code type recognization
- [x] Detailed logs if error occurs


## Quick Start Guide

If you need a Chinese version introduction, please refer [here](https://www.91tvg.com/thread-293794-1-1.html). 中文版请参考[此帖](https://www.91tvg.com/thread-293794-1-1.html)。

### Pre-Requisites

* Windows 10 (:heavy_check_mark:), Windows 7 (:x:), Mac/Linux (❓: rebuild required (thx to [Amuyea](https://gbatemp.net/members/amuyea.437000/)))
* Packaged upstream releases require no Python installation. Running this fork from source requires Python; see [Building from Source](#building-from-source).

### Downloading

Visit out [releases](https://github.com/zzpong/Interactive-ASM-Cheats-Updater/releases) page or download the [latest](https://github.com/zzpong/Interactive-ASM-Cheats-Updater/releases/tag/latest) version.

### Usage

#### Load main file or gamepackages, and then copy your cheat codes to "Input Old Codes"
Build ID of the old main file will be shown after loading. Please make sure it is the same with the old codes file name.
* **Old Main File**: dump from the game which old cheat runs on
* **New main File**: dump from the game which you want to update the old cheat to

** Please unpack game packages and load main files manually if automatic dumping process failed to work.

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
* **Force ARM64**: Force the tool to disassemble codes as ARM64.

#### Save cheat codes with "SaveCHT" button


## Building from Source

### Pre-Requisites For Build

* 64-bit Python; Python 3.9 and 3.12 are covered by the compatibility tests.
* Dependencies listed in `Interactive ASM Cheats Updater/requirements.txt`.
* PyInstaller is only needed when building an EXE; it is included in requirements.

### Usage For Build

#### Install and run globally on Windows (without .venv)

1. Install Python with **Add Python to PATH** enabled, then open a new Command Prompt.
2. Download and extract this fork's source ZIP, or clone the fork. Enter the
   **Interactive ASM Cheats Updater** folder containing `__main__.py` and
   `requirements.txt`. In File Explorer's address bar, type `cmd` and press Enter.
3. Run `python --version`. If that command does not work, try `python3 --version`
   or `py --version`. Use one working interpreter command consistently for every
   install, check, and launch command below. These examples use `python`.
4. Install and check the dependencies in that same Python installation:

   ```bat
   python -m pip install --upgrade pip
   python -m pip install --upgrade -r requirements.txt
   python -m pip check
   python -c "import capstone, keystone, nsz, cryptography, chardet, zbic; print('Dependencies OK')"
   ```

   The checks should report `No broken requirements found` and `Dependencies OK`.
   If you chose `python3` or `py`, replace every `python` above and below with
   that command. Using `-m pip` binds installation to the selected interpreter.
5. For game-package extraction, provide your own `prod.keys` in the application
   folder or `%USERPROFILE%\.switch\prod.keys`. Key files are not supplied by
   this compatibility fix. They are not needed to decode a standalone NSO main.
6. Launch from the application folder:

   ```bat
   python __main__.py
   ```

For future launches, repeat the launch command from that folder. Installing into
one Python and launching with another (including an unconfigured `.venv`) causes
errors such as `ModuleNotFoundError: No module named 'capstone'`.

#### Build an EXE (optional)

From the same application folder, using the same Python:

```bat
python -m PyInstaller -F -w -i xcw.ico __main__.py --collect-all zbic
```

UPX is optional; add `--upx-dir your_upx_root_dir` if you use it. Building an EXE
is separate from running the source. This change does not claim a validated
packaged release.

#### Run the regression tests

From the repository root, one level above the application folder:

```bat
python -m pip install -r "Interactive ASM Cheats Updater/requirements.txt" -r requirements-dev.txt
python -m unittest discover -s tests -v
```

Tests generate synthetic NSOs and dummy keys only. They do not load private keys
or games. A real-game cheat migration and encrypted package extraction still
require separate validation.


## Trouble Shooting
1. Why my new codes doesn't work?
  
    A: On most cases, they are pointer cheat codes that can be recognized from the logs window. Please update these cheats with [EdiZon SE](https://github.com/tomvita/EdiZon-SE) or [SE tools](https://gbatemp.net/threads/se-tools-all-your-game-memory-hacking-needs-in-one-package.575131/).

2. Why my new codes break the game?

    A: Game developer will make a huge change for some specific version of games, like adding new function or improving code efficiency. In these cases, the ASM cheat codes need to be refind. 

3. Why this application repeating same title over and over again?

    A: It happened when capstone in the application failed to recognize bytes features. Here are some major reasons: zero gap in bytes file fail to work in capstone (fixed), nsnsotool decompressing command failed (fixed), application folder structure destroyed. Please re-download this application or [create an issue](https://github.com/zzpong/Interactive-ASM-Cheats-Updater/issues/new). Please note that "out of .text or code cave border" has been fixed from 0.4.0.

4. What does "main file" stand for?

    A: "main file" is the executable game file dumped from NSP or XCI, which is located in the exefs folder. It can be dumped automatically with the latest version.

5. What does "wing length" stand for?

    A: "wing length" represents the number of code lines before and after the target area. Here is the diagram for a better view:
    
    ![image](https://github.com/zzpong/Interactive-ASM-Cheats-Updater/blob/Active-Branch/wing_length.png)

6. What code cave remake brings between version 0.3 and 0.4?

    A: In the new version, the code cave structure strictly follows the one from the original cheat code instead of previous "relocate every code cave automatically". Therefore, code caves in cheat codes like [EXP 2X]/[EXP 4X]/[EXP 8X] will only demand identical addresses and nothing more.

7. I have fully run the program and never see any warning, but still no luck. Why?

    A: In most cases, the "master code" which has a title within "{}" takes the responsibility. Some code creater prefer use them as "default function that should run with the game start". These codes and some non "master code" titled like "recovery code" always have links with other ASM codes like "BL #0xADDR". Please add these code contents to other parts of the cheat codes that don't work properly and run the program again.


## Contributing

Feel free to dive in! [Open an issue](https://github.com/zzpong/Interactive-ASM-Cheats-Updater/issues/new) or [submit PRs](https://github.com/zzpong/Interactive-ASM-Cheats-Updater/pulls).

Thank you for your contribution:

<a href="https://github.com/zzpong/Interactive-ASM-Cheats-Updater/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=zzpong/Interactive-ASM-Cheats-Updater" />
</a>

## Credits

**Interactive ASM Cheats Updater** is based on

a.) [Keystone Engine](https://github.com/keystone-engine/keystone) and [Capstone Engine](https://github.com/capstone-engine/capstone): Without their brilliant work, Interactive ASM Cheats Updater will never be born.

b.) [nsnsotool](https://github.com/0CBH0/nsnsotool): This tiny program helps a lot on transforming nso files, made by 0CBH0.

c.) [nsz](https://github.com/nicoboss/nsz): Light my day, created by nicoboss.

d.) getMain: main file extraction for IDA Pro by [Eiffel2018](https://gbatemp.net/members/eiffel2018.536592/).

e.) python AES128 implementation: written by SciresM.

**Also thanks to:**

[Eiffel2018](https://gbatemp.net/members/eiffel2018.536592/), [donghui2199](https://github.com/FantasyDH), [怪盗B](https://www.91tvg.com/space-uid-2230670.html), [Geminize](https://www.91tvg.com/space-uid-2337434.html), [Konia1234](https://www.91tvg.com/space-uid-2300061.html) and [lulu](https://www.91tvg.com/space-uid-2776736.html) for their testing.

All cheat makers that sparing no effort in creating and updating cheat codes, you ARE the true heros!

All the helpers for bringing this project to life!

## License

This project is licensed under GNU General Public License v3.0.
<a href="https://www.gnu.org/licenses/gpl-3.0.en.html"><image src="http://www.gnu.org/graphics/gplv3-127x51.png" align="right"></a>

Refer the [LICENSE](LICENSE) file for more details.


## Changelog

### v1.1.4 - Unofficial compatibility fixes (2026-10-19)

- Add bounded in-memory decoding for raw, legacy LZ4 and ZBIC NSO0 segments,
  including mixed compressed/uncompressed segments. Opening a main preserves
  the original file, Build ID, segment memory addresses, module name and BSS.
- Fix compression detection: only the three segment compression bits indicate
  compression; hash-only flags do not.
- Save modified mains as uncompressed NSO0 with refreshed checked segment hashes.
  Loading and saving no longer require `nsnsotool.exe`. ELF is not a main input;
  from nso2elf, use the file created by `--export-uncompressed`.
- Require `nsz>=5.0.0,<6`, which recognizes `master_key_14` and `master_key_15`
  checksums. Missing keys and incorrect checksums remain errors. Later key
  generations are not covered by this fix's validation.
- Select keys consistently: app `prod.keys`, then `~/.switch/prod.keys`, then
  legacy app `keys.txt`. The extractor and NSZ use the same selection, with
  canonical key names and cleared state between loads.
- Add English global-Python installation instructions, including `python`,
  `python3` and `py`, and Windows Python 3.9/3.12 regression-test CI.

The decoder is adapted from [HY-Leung/nso2elf](https://github.com/HY-Leung/nso2elf)
with its MIT notice retained in `licenses/nso2elf-MIT.txt`. This project remains
GPL-3.0. Original project: [zzpong/Interactive-ASM-Cheats-Updater](https://github.com/zzpong/Interactive-ASM-Cheats-Updater).
