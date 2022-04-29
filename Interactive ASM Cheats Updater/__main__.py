import os

from utilities.interface import ASM_updater_UI
from config.config import localization

def main():
    root_path = os.getcwd()
    _ = ASM_updater_UI(localization['loc_EN'], root_path)

if __name__ == '__main__':
    main()