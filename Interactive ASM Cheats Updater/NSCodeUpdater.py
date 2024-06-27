import os

from utilities.interface import CodeUpdaterInterface
from config.config import *
from utilities.logger import Logger


def main(language: str):
    root_path = os.getcwd()
    _ = CodeUpdaterInterface(GlobalInfo(root_path, language))


class GlobalInfo:  # Read-ONLY Property
    def __init__(self, root_path: str, language: str):
        self.root_path = root_path
        self.log_path = os.path.join(self.root_path, 'log')

        self.logger = Logger(root_path)

        self.title = localization[language]['title']
        self.msgbox_title_map = localization[language]['msgbox_title_map']
        self.hints_map = localization[language]['hints_map']
        self.btn_map = localization[language]['btn_map']
        self.msg_map = localization[language]['msg_map']
        self.str_map = localization[language]['str_map']
        self.wing_length_default = configuration['wing_length_default']
        self.extra_wing_length_default = configuration['extra_wing_length_default']
        self.widen_hit_num = int(configuration['widen_hit_num'])
        self.max_hit_num = int(configuration['max_hit_num'])

        self.code_pattern = code_pattern[language]

        self.supported_package_type = ['.xci', '.nsp', '.xcz', '.nsz']


if __name__ == '__main__':
    main('loc_EN')
    # main('loc_CN')