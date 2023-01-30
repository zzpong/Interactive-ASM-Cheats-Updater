import os

from utilities.interface import ASM_updater_UI
from config.config import localization

## TODO:
# GRANDIA HD Collection: need ARM32 decoder, not ARM64, with double tid
# Only save cht file after click "Ok"
# Frames have no auto-scale function

def main():
    root_path = os.getcwd()
    _ = ASM_updater_UI(localization['loc_EN'], root_path)

if __name__ == '__main__':
    main()