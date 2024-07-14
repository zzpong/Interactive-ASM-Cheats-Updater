import importlib
import os
import sys

from utilities.interface import CodeUpdaterInterface
from utilities.logger import Logger


def main(language: str):
    root_path = os.getcwd()
    _ = CodeUpdaterInterface(GlobalInfo(root_path, language))


class GlobalInfo:  # Read-ONLY Property
    def __init__(self, root_path: str, language: str):
        self.root_path = root_path
        self.back_path = os.path.join(self.root_path, 'back_up')
        self.tool_path = os.path.join(self.root_path, 'tools')
        self.log_path = os.path.join(self.root_path, 'log')

        self.logger = Logger(root_path)

        sys.path.append(self.root_path)
        config = importlib.import_module('config')

        self.title = config.localization[language]['title']
        self.hints_map = config.localization[language]['hints_map']
        self.btn_map = config.localization[language]['btn_map']
        self.msg_map = config.localization[language]['msg_map']

        self.wing_length_default = config.preference['wing_length_default']
        self.extra_wing_length_default = config.preference['extra_wing_length_default']
        self.max_shown_address = config.preference['max_shown_address']

        self.code_pattern = config.code_pattern[language]

        self.supported_package_type = ['.xci', '.nsp', '.xcz', '.nsz']


if __name__ == '__main__':
    main('loc_EN')