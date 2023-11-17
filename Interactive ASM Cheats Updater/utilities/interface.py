from asyncio.subprocess import PIPE, STDOUT
import tkinter, os, base64, webbrowser, re, time, json, sys
from tkinter import dialog
from copy import deepcopy
from capstone import *
from keystone import *
from tkinter import *
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from tkinter import filedialog
import tkinter.font as tkFont

from sources.base64_icon import *
from utilities.game_package import GamePackage
from utilities.main_file import *
from utilities.code_structer import CodeStruct, PseudoStack
from utilities.bytes_process import *
from utilities.exception import GamePackageError
from utilities.logger import *

from pathlib import Path


def bytes_to_int(bytearray):
    return int.from_bytes(bytearray, byteorder='big', signed=False)


class Stdout_Redirect:
    def __init__(self, fetched_text_widget):
        self.log_out = fetched_text_widget.log_text_out
        self.stdout_bak = sys.stdout
        self.stderr_bak = sys.stderr
        sys.stdout = self
        sys.stderr = self
        
    def write(self, msg):
        if msg == ' ' or msg == '\n':
            return
        self.log_out(msg, False)

    def restore_std(self):
        self.log_out = None
        sys.stdout = self.stdout_bak
        sys.stderr = self.stderr_bak
    
    def flush(self):
        pass

# Hints: json.dump(any_json, save_path, cls=MyEncoder, indent=1)
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytearray):
            return obj.hex()
        return json.JSONEncoder.default(self, obj)

class LinkLabel(Label):
    def __init__(self, master, link, font=('Arial',9,'underline'), bg='#f0f0f0'):
        super().__init__(master, text=link, font=font, fg='blue', bg=bg)
        self.link='https://github.com/zzpong/Interactive-ASM-Cheats-Updater'
        self.bind('<Enter>',self._changecolor)
        self.bind('<Leave>',self._changecurcor)
        self.bind('<Button-1>',self._golink)
        self.isclick=False
    
    def _changecolor(self, event):
        self['fg']='#D52BC4'
        self['cursor']='hand2'
    
    def _changecurcor(self, event):
        if self.isclick==False:
            self['fg']='blue'
        self['cursor']='xterm'
    
    def _golink(self, event):
        self.isclick=True
        webbrowser.open(self.link)


class MidASMDataContainer():
    def __init__(self, main_file, asm_type) -> None:
        [self.old_main_file, self.new_main_file] = main_file
        self.asm_type = asm_type
        self.flush()

    def update(self, wing_length, extra_wing_length, code_size, org_branch_addr, org_branch_target, branch_addr_list, branch_target_list = None):
        if branch_target_list is None:
            self.branch_wing_length = wing_length
            self.target_wing_length = None
        else:
            self.branch_wing_length = [wing_length[0], wing_length[0]]
            self.target_wing_length = [wing_length[1], wing_length[1]]

        self.is_updated = True  # Hints: Connection between analysis_code() and generate_output()

        self.extra_wing_length = extra_wing_length
        self.code_size = code_size
        self.is_view_target = False
        self.org_branch_addr = org_branch_addr
        self.org_branch_target = org_branch_target
        self.branch_addr_list = branch_addr_list
        self.branch_target_list = branch_target_list
        self.branch_addr_index = 0
        self.branch_target_index = 0

        self.branch_addr_size = 0 if branch_addr_list is None else len(branch_addr_list)
        self.branch_target_size = 0 if branch_target_list is None else len(branch_target_list)

    def flush(self):
        self.is_updated = False
        self.branch_wing_length = None
        self.target_wing_length = None
        self.extra_wing_length = None
        self.code_size = None
        self.is_view_target = False
        self.org_branch_addr = None
        self.org_branch_target = None
        self.branch_addr_list = None
        self.branch_target_list = None
        self.branch_addr_index = 0
        self.branch_target_index = 0
        self.branch_addr_size = 0
        self.branch_target_size = 0

    def set_extra_wing_length(self, extra_wing_length):
        self.extra_wing_length = extra_wing_length

    def set_updated(self):
        self.is_updated = True
        
    def switch(self):
        self.is_view_target = not self.is_view_target
    
    def target_on(self):
        self.is_view_target = True

    def target_off(self):
        self.is_view_target = False

    def next(self):
        if self.is_view_target:
            if self.branch_target_size == 0:
                return
            self.branch_target_index = (self.branch_target_index-1)%len(self.branch_target_list)
        else:
            if self.branch_addr_size == 0:
                return
            self.branch_addr_index = (self.branch_addr_index-1)%len(self.branch_addr_list)

    def previous(self):
        if self.is_view_target:
            if self.branch_target_size == 0:
                return
            self.branch_target_index = (self.branch_target_index+1)%len(self.branch_target_list)
        else:
            if self.branch_addr_size == 0:
                return
            self.branch_addr_index = (self.branch_addr_index+1)%len(self.branch_addr_list)
        
    def get_msg_bundle(self, is_old_file = True) -> (list, list):
        if self.is_view_target and isinstance(self.branch_target_list[0], str):
            return (["[.CheatCode]: " + self.branch_target_list[0]], [0.0, 0.0])

        if ((self.is_view_target and self.branch_target_list[self.branch_target_index] > len(self.new_main_file.mainFuncFile) - 1)
            or (not self.is_view_target and self.branch_addr_list[self.branch_addr_index] > len(self.new_main_file.mainFuncFile) - 1)):
            return (['Outside Address: [.CodeCave] or [.Multimedia]'], [0.0, 0.0])

        if is_old_file:
            main_file = self.old_main_file
            branch_addr = self.org_branch_addr
            branch_target = self.org_branch_target
            if ((self.is_view_target and branch_target is None)
                    or (not self.is_view_target and branch_addr is None)):
                return [None, None]
        else:
            main_file = self.new_main_file
            if ((self.is_view_target and self.branch_target_list is None)
                    or (not self.is_view_target and self.branch_addr_list is None)):
                return [None, None]
            if self.is_view_target:
                branch_target = self.branch_target_list[self.branch_target_index]
            else:
                branch_addr = self.branch_addr_list[self.branch_addr_index]

        if self.is_view_target:
            start_addr = (
                branch_target - 
                (self.target_wing_length[0] + self.extra_wing_length[0]) * 4
            )
            start_addr = start_addr if start_addr >= 0 else 0
            end_addr = (
                branch_target + 1 * 4 +
                (self.target_wing_length[1] + self.extra_wing_length[1]) * 4
            )
            end_addr = end_addr if end_addr <= len(main_file.mainFuncFile) - 1 else len(main_file.mainFuncFile) - 1
            high_light_line = [float((branch_target - start_addr) // 4),  # Hints: branch has only one line
                               float((branch_target - start_addr) // 4)]
        else:
            start_addr = (
                branch_addr - 
                (self.branch_wing_length[0] + self.extra_wing_length[0]) * 4
            )
            start_addr = start_addr if start_addr >= 0 else 0
            end_addr = (
                branch_addr + self.code_size * 4 +
                (self.branch_wing_length[1] + self.extra_wing_length[1]) * 4
            )
            end_addr = end_addr if end_addr <= len(main_file.mainFuncFile) - 1 else len(main_file.mainFuncFile) - 1
            high_light_line = [float((branch_addr - start_addr) // 4),
                               float((branch_addr - start_addr) // 4 + self.code_size - 1)]
    
        return (generate_ASM_code(main_file.mainFuncFile, [start_addr, end_addr], asm_type = self.asm_type), high_light_line)
    
    def get_current_branch_addr(self):
        if self.branch_addr_list is None:
            return None
        return self.branch_addr_list[self.branch_addr_index]

    def get_current_branch_target(self):
        if self.branch_target_list is None:
            return None
        return self.branch_target_list[self.branch_target_index]


class CodeUpdaterInterface:
    def __init__(self, globalInfo):
        self.globalInfo = globalInfo
        self.init_global_param(globalInfo)
        
        self.init_UI(globalInfo)

        self.logger = globalInfo.logger
        self.logger.open()

        self.init_game_package_decomp(globalInfo)

        self.init_UI_param()

        self.mainWin.mainloop()

    def init_global_param(self, globalInfo):
        self.log_path = globalInfo.log_path
        self.back_path = globalInfo.back_path
        self.tool_path = globalInfo.tool_path

        self.hints_map = globalInfo.hints_map
        self.btn_map = globalInfo.btn_map
        self.msg_map = globalInfo.msg_map
        self.wing_length_default = globalInfo.wing_length_default
        self.extra_wing_length_default = globalInfo.extra_wing_length_default
        self.supported_package_type = globalInfo.supported_package_type
        self.code_pattern = globalInfo.code_pattern

    def init_UI(self, globalInfo):
        self.mainWin = tkinter.Tk()
        self.mainWin.title(globalInfo.title)

        self.generate_icon('xcw.ico', xcw_ico)
        self.mainWin.iconbitmap("xcw.ico")
        self.mainWin.geometry('1400x800')
        os.remove("xcw.ico")

        default_font = tkFont.nametofont("TkFixedFont")
        default_font.configure(family="Helvetica")

        # Load file frame
        self.load_file_frame = tkinter.Frame(self.mainWin, width=1000, height=200, bg='LemonChiffon', relief=GROOVE)
        self.load_file_frame.pack(expand='yes', fill='both', anchor='n', side='top', padx=5, pady=5)

        # Old load file frame
        self.old_load_file_frame = tkinter.Frame(self.load_file_frame, bd = 2, highlightthickness = 1, relief=RIDGE)
        self.old_load_file_frame.pack(expand='yes', fill='both', anchor='w', side='left', padx=5, pady=5)

        self.old_file_text = tkinter.Label(self.old_load_file_frame, text=self.hints_map['Old Main File:'])
        self.old_file_text.pack(expand='yes', fill='both', anchor='w', side='left', padx=5, pady=5)

        self.old_file_entry = tkinter.Entry(self.old_load_file_frame, width=60, justify=CENTER, state=DISABLED)
        self.old_file_entry.pack(expand='yes', fill='both', anchor='center', side='left', padx=5, pady=5)

        self.btn_load_old_file = tkinter.Button(self.old_load_file_frame, height=0, text=self.btn_map['Load Old'], relief=RAISED, command=self.load_old_file)
        self.btn_load_old_file.pack(expand='yes', fill='both', anchor='e', side='left', padx=5, pady=5)

        # New load file frame
        self.new_load_file_frame = tkinter.Frame(self.load_file_frame, bd = 2, highlightthickness = 1, relief=RIDGE)
        self.new_load_file_frame.pack(expand='yes', fill='both', anchor='w', side='left', padx=5, pady=5)

        self.new_file_text = tkinter.Label(self.new_load_file_frame, text=self.hints_map['New Main File:'])
        self.new_file_text.pack(expand='yes', fill='both', anchor='w', side='left', padx=5, pady=5)

        self.new_file_entry = tkinter.Entry(self.new_load_file_frame, width=60, justify=CENTER, state=DISABLED)
        self.new_file_entry.pack(expand='yes', fill='both', anchor='center', side='left', padx=5, pady=5)

        self.btn_load_new_file = tkinter.Button(self.new_load_file_frame, height=0, text=self.btn_map['Load New'], relief=RAISED, command=self.load_new_file)
        self.btn_load_new_file.pack(expand='yes', fill='both', anchor='e', side='left', padx=5, pady=5)

        # Debug checkbox
        self.force_ARM64_checkbox_frame = tkinter.Frame(self.load_file_frame, bd = 2, highlightthickness = 1, relief=RIDGE)
        self.force_ARM64_checkbox_frame.pack(expand='yes', fill='x', anchor='e', side='left', padx=5, pady=5)

        self.force_ARM64 = BooleanVar()
        self.force_ARM64_checkbox = Checkbutton(self.force_ARM64_checkbox_frame, text=self.hints_map['ARM64'], variable=self.force_ARM64, onvalue=True, offvalue=False) 
        self.force_ARM64_checkbox.pack()
        self.force_ARM64.set(False)

        # Main cheats frame
        self.main_cheats_frame = tkinter.Frame(self.mainWin, width=1000, height=200, bg='DeepSkyBlue', relief=GROOVE)
        self.main_cheats_frame.pack(expand='yes', fill='both', anchor='s', side='top', padx=5, pady=5)

        # Input cheats frame
        self.input_cheats_frame = tkinter.Frame(self.main_cheats_frame, bd = 2, highlightthickness = 1, relief=RIDGE)
        self.input_cheats_frame.pack(expand='yes', fill='both', anchor='w', side='left', padx=5, pady=5)

        # Input cheats script
        self.input_cheats_script = tkinter.Label(self.input_cheats_frame, text=self.hints_map['Input Old Codes:'])
        self.input_cheats_script.pack(expand='yes', fill='y', anchor='w', side='top', padx=5, pady=5)
        # Input cheats text
        self.input_cheats_text = ScrolledText(self.input_cheats_frame, width=40, height=400, wrap=WORD)
        self.input_cheats_text.pack(expand='yes', fill='both', anchor='w', side='top', padx=5, pady=5)
        # self.input_cheats_text.config(font=font_setting)

        # Middle cheats frame
        self.middle_cheats_frame = tkinter.Frame(self.main_cheats_frame, bd = 2, highlightthickness = 1, relief=RIDGE)
        self.middle_cheats_frame.pack(expand='yes', fill='both', anchor='center', side='left', padx=5, pady=5)

        # Middle cheats up frame
        self.middle_cheats_up_frame = tkinter.Frame(self.middle_cheats_frame, bd = 2, highlightthickness = 1, relief=RIDGE)
        self.middle_cheats_up_frame.pack(expand='yes', fill='both', anchor='center', side='top', padx=5, pady=5)

        # Current cheats script
        self.current_cheats_script = tkinter.Label(self.middle_cheats_up_frame, text=self.hints_map['Current Processing Codes:'])
        self.current_cheats_script.pack(anchor='w', side='top', padx=5, pady=5)
        # Current cheats text
        self.current_cheats_text = ScrolledText(self.middle_cheats_up_frame, width=40, height=15, state=DISABLED, wrap=WORD)
        self.current_cheats_text.pack(expand='yes', fill='both', anchor='w', side='top', padx=5, pady=5)

        # Middle cheats wings frame
        self.middle_cheats_wings_frame = tkinter.Frame(self.middle_cheats_frame, bd = 2, highlightthickness = 1, relief=RIDGE)
        self.middle_cheats_wings_frame.pack(expand='yes', anchor='center', side='top', padx=5, pady=5)
        self.middle_cheats_wings_frame.columnconfigure(0, weight=1)
        # wings script
        self.wings_script = tkinter.Label(self.middle_cheats_wings_frame, text=self.hints_map['Wing Length:'])
        self.wings_script.pack(anchor='w', side='left', padx=5, pady=5)
        self.wings_text = tkinter.Entry(self.middle_cheats_wings_frame, width=15, justify=CENTER)
        self.wings_text.pack(anchor='e', fill='x', side='left', padx=5, pady=5)
        self.wings_text.delete(0, END)
        self.wings_text.insert(0, self.wing_length_default)
        self.btn_regenerate = tkinter.Button(self.middle_cheats_wings_frame, text=self.btn_map['Regenerate'], width=12, command=self.regenerate)
        self.btn_regenerate.pack(padx=5, pady=5)
        self.btn_regenerate.config(state=DISABLED)

        # Middle cheats button frame
        self.middle_cheats_button_frame = tkinter.Frame(self.middle_cheats_frame)
        self.middle_cheats_button_frame.pack(expand='yes', anchor='center', side='top', padx=5, pady=5)
        self.middle_cheats_button_frame.columnconfigure(0, weight=1)
        self.btn_generate = tkinter.Button(self.middle_cheats_button_frame, text=self.btn_map['Generate'], width=10, command=self.generate)
        self.btn_generate.grid(row=0, column=0, sticky="nsew")
        self.btn_generate.config(state=DISABLED)
        self.btn_skip = tkinter.Button(self.middle_cheats_button_frame, text=self.btn_map['Skip'], width=10, command=self.skip)
        self.btn_skip.grid(row=0, column=1, sticky="nsew")
        self.btn_skip.config(state=DISABLED)
        self.btn_undo = tkinter.Button(self.middle_cheats_button_frame, text=self.btn_map['Undo'], width=10, command=self.undo)
        self.btn_undo.grid(row=0, column=2, sticky="nsew")
        self.btn_undo.config(state=DISABLED)
        self.btn_restart = tkinter.Button(self.middle_cheats_button_frame, text=self.btn_map['Restart'], width=10, command=self.restart)
        self.btn_restart.grid(row=0, column=3, sticky="nsew")
        self.btn_restart.config(state=DISABLED)

        # Middle cheats down frame
        self.middle_cheats_down_frame = tkinter.Frame(self.middle_cheats_frame, bd = 2, highlightthickness = 1, relief=RIDGE)
        self.middle_cheats_down_frame.pack(expand='yes', fill='both', anchor='center', side='top', padx=5, pady=5)

        # Log script
        self.log_script = tkinter.Label(self.middle_cheats_down_frame, text=self.hints_map['Logs:'])
        self.log_script.pack(anchor='w', side='top', padx=5, pady=5)
        # Log text
        self.log_text = ScrolledText(self.middle_cheats_down_frame, width=40, height=15, state=DISABLED, wrap=WORD)
        self.log_text.pack(expand='yes', fill='both', anchor='w', side='top', padx=5, pady=5)
    
        # Middle ASM frame
        self.middle_ASM_frame = tkinter.Frame(self.main_cheats_frame, bd = 2, highlightthickness = 1, relief=RIDGE)
        self.middle_ASM_frame.pack(expand='yes', fill='both', anchor='center', side='left', padx=5, pady=5)

        # Middle ASM up frame
        self.middle_ASM_up_frame = tkinter.Frame(self.middle_ASM_frame, bd = 2, highlightthickness = 1, relief=RIDGE)
        self.middle_ASM_up_frame.pack(expand='yes', fill='both', anchor='center', side='top', padx=5, pady=5)

        # Old ASM script
        self.old_ASM_script = tkinter.Label(self.middle_ASM_up_frame, text=self.hints_map['Old Assembly Codes:'])
        self.old_ASM_script.pack(anchor='w', side='top', padx=5, pady=5)
        # Old ASM script
        self.old_ASM_text = ScrolledText(self.middle_ASM_up_frame, width=40, height=15, state=DISABLED, wrap=WORD)
        self.old_ASM_text.pack(expand='yes', fill='both', anchor='w', side='top', padx=5, pady=5)
        self.old_ASM_text.tag_config('high_light_old', foreground='red', background='yellow')

        # Middle ASM wings frame
        self.middle_ASM_wings_frame = tkinter.Frame(self.middle_ASM_frame, bd = 2, highlightthickness = 1, relief=RIDGE)
        self.middle_ASM_wings_frame.pack(expand='yes', anchor='center', side='top', padx=5, pady=5)
        self.middle_ASM_wings_frame.columnconfigure(0, weight=1)
        # ASM wings script
        self.ASM_wings_script = tkinter.Label(self.middle_ASM_wings_frame, text=self.hints_map['Extra Wing Length:'])
        self.ASM_wings_script.pack(anchor='w', side='left', padx=5, pady=5)
        self.ASM_wings_text = tkinter.Entry(self.middle_ASM_wings_frame, width=15, justify=CENTER)
        self.ASM_wings_text.pack(anchor='e', fill='x', side='left', padx=5, pady=5)
        self.ASM_wings_text.delete(0, END)
        self.ASM_wings_text.insert(0, self.extra_wing_length_default)
        self.btn_update = tkinter.Button(self.middle_ASM_wings_frame, text=self.btn_map['Update'], width=12, command=self.update)
        self.btn_update.pack(padx=5, pady=5)
        self.btn_update.config(state=DISABLED)

        # Middle ASM button frame
        self.middle_ASM_button_frame = tkinter.Frame(self.middle_ASM_frame)
        self.middle_ASM_button_frame.pack(expand='yes', anchor='center', side='top', padx=5, pady=5)
        self.middle_ASM_button_frame.columnconfigure(0, weight=1)
        # Middle ASM button frame button
        self.btn_prev_addr = tkinter.Button(self.middle_ASM_button_frame, text=self.btn_map['Prev'], width=10, command=self.previous)
        self.btn_prev_addr.pack(anchor='w', side='left', padx=5, pady=5)
        self.btn_prev_addr.config(state=DISABLED)
        self.btn_next_addr = tkinter.Button(self.middle_ASM_button_frame, text=self.btn_map['Next'], width=10, command=self.next)
        self.btn_next_addr.pack(anchor='w', side='left', padx=5, pady=5)
        self.btn_next_addr.config(state=DISABLED)
        # Middle ASM button frame checkbox
        self.middle_ASM_checkbox_frame = tkinter.Frame(self.middle_ASM_button_frame, bd = 2, highlightthickness = 1, relief=RIDGE)
        self.middle_ASM_checkbox_frame.pack(expand='yes', fill='x', anchor='e', side='right', padx=5, pady=5)
        self.is_check_branch = BooleanVar()
        self.branch_checkbox = Checkbutton(self.middle_ASM_checkbox_frame, text=self.hints_map['Branch'], variable=self.is_check_branch, onvalue=True, offvalue=False, state=DISABLED, command=self.check)
        self.branch_checkbox.pack()
        self.is_check_branch.set(False)

        # Middle ASM up frame
        self.middle_ASM_down_frame = tkinter.Frame(self.middle_ASM_frame, bd = 2, highlightthickness = 1, relief=RIDGE)
        self.middle_ASM_down_frame.pack(expand='yes', fill='both', anchor='center', side='top', padx=5, pady=5)

        # New ASM script
        self.new_ASM_script = tkinter.Label(self.middle_ASM_down_frame, text=self.hints_map['New Assembly Codes:'])
        self.new_ASM_script.pack(anchor='w', side='top', padx=5, pady=5)
        # New ASM script
        self.new_ASM_text = ScrolledText(self.middle_ASM_down_frame, width=40, height=15, state=DISABLED, wrap=WORD)
        self.new_ASM_text.pack(expand='yes', fill='both', anchor='w', side='top', padx=5, pady=5)
        self.new_ASM_text.tag_config('high_light_new', foreground='red', background='yellow')

        # Output cheats frame
        self.output_cheats_frame = tkinter.Frame(self.main_cheats_frame, bd = 2, highlightthickness = 1, relief=RIDGE)
        self.output_cheats_frame.pack(expand='yes', fill='both', anchor='e', side='left', padx=5, pady=5)

        # Output cheats up frame
        self.output_cheats_up_frame = tkinter.Frame(self.output_cheats_frame, bd = 2, highlightthickness = 1, relief=RIDGE)
        self.output_cheats_up_frame.pack(expand='yes', fill='both', anchor='e', side='top', padx=5, pady=5)

        # Output cheats script
        self.output_cheats_script = tkinter.Label(self.output_cheats_up_frame, text=self.hints_map['New Codes Output:'])
        self.output_cheats_script.pack(anchor='w', side='top', padx=5, pady=5)
        # Output cheats text
        self.output_cheats_text = ScrolledText(self.output_cheats_up_frame, width=40, height=32, state=DISABLED, wrap=WORD)
        self.output_cheats_text.pack(expand='yes', fill='both', anchor='w', side='top', padx=5, pady=5)

        # Output cheats down frame
        self.output_cheats_down_frame = tkinter.Frame(self.output_cheats_frame)
        self.output_cheats_down_frame.pack(anchor='center', side='top', padx=5, pady=5)

        # Output cheats down left frame
        self.output_cheats_down_left_frame = tkinter.Frame(self.output_cheats_down_frame)
        self.output_cheats_down_left_frame.pack(anchor='center', side='left', padx=5, pady=5)
        self.output_cheats_down_left_frame.columnconfigure(0, weight=1)
        self.btn_savcht = tkinter.Button(self.output_cheats_down_left_frame, text=self.btn_map['SaveCHT'], width=10, command=self.sav_cht)
        self.btn_savcht.grid(row=0, column=0, sticky="nsew", padx=12)
        self.btn_savcht.config(state=DISABLED)
        self.btn_savnso = tkinter.Button(self.output_cheats_down_left_frame, text=self.btn_map['SaveNSO'], width=10, command=self.sav_nso)
        self.btn_savnso.grid(row=0, column=1, sticky="nsew", padx=12)
        self.btn_savnso.config(state=DISABLED)
        # Output cheats down right frame
        self.output_cheats_down_right_frame = tkinter.Frame(self.output_cheats_down_frame)
        self.output_cheats_down_right_frame.pack(anchor='center', side='left', padx=5, pady=5)
        self.link = LinkLabel(self.output_cheats_down_right_frame, link=self.btn_map['GitHub']).pack(side='left', padx=5, pady=5)

        # input_cheats_text right click window
        self.menu = tkinter.Menu(self.input_cheats_text, tearoff=0)
        self.menu.add_command(label=self.btn_map['copy'], command=self.copy)
        self.menu.add_separator()
        self.menu.add_command(label=self.btn_map['paste'], command=self.paste)
        self.menu.add_separator()
        self.menu.add_command(label=self.btn_map['cut'], command=self.cut)
        self.input_cheats_text.bind("<Button-3>", self.popupmenu)

        # output_cheats_text right click window
        self.menuOut = tkinter.Menu(self.output_cheats_text, tearoff=0)
        self.menuOut.add_command(label="copy", command=self.copyOut)
        self.output_cheats_text.bind("<Button-3>", self.popupmenuOut)

    def init_game_package_decomp(self, globalInfo):
        try:
            self.gamePackage = GamePackage(globalInfo)
        except Exception as e:
            self.logger.exception(e)

    def init_UI_param(self):
        self.old_is_NSO_file = False
        self.new_is_NSO_file = False
        self.is_initialized = False
        self.is_ended = False

    def generate_icon(self, pic_name, pic_base64):
        image = open(pic_name, 'wb')
        image.write(base64.b64decode(pic_base64))
        image.close()
    
    # right-click functions
    def cut(self, event=None):
        self.input_cheats_text.event_generate("<<Cut>>")
    def copy(self, event=None):
        self.input_cheats_text.event_generate("<<Copy>>")
    def paste(self, event=None):
        self.input_cheats_text.event_generate('<<Paste>>')
    def popupmenu(self, event):
        self.menu.post(event.x_root, event.y_root)

    def copyOut(self, event=None):
        self.output_cheats_text.event_generate("<<Copy>>")
    def popupmenuOut(self, event):
        self.menuOut.post(event.x_root, event.y_root)

    def load_file(self, file_path: str, is_old_file = True):
        if file_path == '':
            return
        
        if Path(file_path).suffix.lower() in self.supported_package_type:
            messagebox.showwarning(title='Warning', message='\n'.join(eval(self.msg_map['Unpack Warning'])))
            
            out_redir = Stdout_Redirect(self)  # pipeline redirect
            updated_file_path = self.gamePackage.get_main_file(file_path)
            out_redir.restore_std()
            if updated_file_path is None:
                raise GamePackageError('\n'.join(eval(self.msg_map['.nso extraction failed'])))
            if is_old_file:
                self.update_old_file_entry(updated_file_path)
            else:
                self.update_new_file_entry(updated_file_path)
            file_path = updated_file_path
        
        if is_old_file:
            self.old_main_file = MainNSOStruct(file_path, self.globalInfo)
            self.old_is_NSO_file = self.old_main_file.process_file()
        else:
            self.new_main_file = MainNSOStruct(file_path, self.globalInfo)
            self.new_is_NSO_file = self.new_main_file.process_file()

        if is_old_file:
            messagebox.showinfo(title='Info', message='\n'.join(eval(self.msg_map['BID message'])))

    def update_old_file_entry(self, msg: str):
        self.old_file_entry.config(state=NORMAL)
        self.old_file_entry.delete(0, END)
        self.old_file_entry.insert('insert', msg)
        self.old_file_entry.config(state=DISABLED)
    
    def update_new_file_entry(self, msg: str):
        self.new_file_entry.config(state=NORMAL)
        self.new_file_entry.delete(0, END)
        self.new_file_entry.insert('insert', msg)
        self.new_file_entry.config(state=DISABLED)

    def load_old_file(self):
        file_path = filedialog.askopenfilename(title=self.hints_map['Load Old Main NSO File'], filetypes=[('All Files', '*')])
        self.update_old_file_entry(file_path)

        self.old_is_NSO_file = False
        try:
            self.load_file(file_path, is_old_file = True)
        except Exception as e:
            self.logger.exception(e)
        if self.new_is_NSO_file and self.old_is_NSO_file:
            self.btn_after_load(True)
        else:
            self.btn_after_load(False)

    def load_new_file(self):
        file_path = filedialog.askopenfilename(title=self.hints_map['Load New Main NSO File'], filetypes=[('All Files', '*')])
        self.update_new_file_entry(file_path)

        self.new_is_NSO_file = False
        try:
            self.load_file(file_path, is_old_file = False)
        except Exception as e:
            self.logger.exception(e)
        if self.new_is_NSO_file and self.old_is_NSO_file:
            self.btn_after_load(True)
        else:
            self.btn_after_load(False)

    def input_cheats_text_in(self):
        return self.input_cheats_text.get('1.0', END)
    
    def input_cheats_text_out(self, msg: str):
        self.input_cheats_text.delete(0.1, END)
        self.input_cheats_text.insert('insert', msg)

    def current_cheats_text_out(self, msg: str, need_clear):
        self.current_cheats_text.config(state=NORMAL)
        if need_clear:
            self.current_cheats_text.delete(0.1, END)
        self.current_cheats_text.insert('insert', msg)
        self.current_cheats_text.config(state=DISABLED)
        self.current_cheats_text.see(END)

    def clear_current_cheats_text(self):
        self.current_cheats_text.config(state=NORMAL)
        self.current_cheats_text.delete(0.1, END)
        self.current_cheats_text.config(state=DISABLED)

    def log_text_out(self, msg: str, need_clear):
        self.log_text.config(state=NORMAL)
        if need_clear:
            self.log_text.delete(0.1, END)
        if len(msg) >= 1 and msg[-1] == '\n':
            self.log_text.insert('insert', f'[{time.asctime(time.localtime(time.time()))}] {msg}\n')
        else:
            self.log_text.insert('insert', f'[{time.asctime(time.localtime(time.time()))}] {msg}\n\n')
        self.log_text.config(state=DISABLED)
        self.log_text.see(END)

    def clear_log_text(self):
        self.log_text.config(state=NORMAL)
        self.log_text.delete(0.1, END)
        self.log_text.config(state=DISABLED)

    def output_cheats_text_out(self, msg: str, need_clear, no_insert = False):
        if no_insert:
            return
        self.output_cheats_text.config(state=NORMAL)
        if need_clear:
            self.output_cheats_text.delete(0.1, END)
        self.output_cheats_text.insert('insert', msg)
        self.output_cheats_text.config(state=DISABLED)
        self.output_cheats_text.see(END)

    def wings_text_out(self, msg: str):
        self.wings_text.delete(0, END)
        self.wings_text.insert(0, msg)

    def reset_wings_text(self):
        self.wings_text.delete(0, END)
        self.wings_text.insert(0, self.wing_length_default)

    def reset_ASM_wings_text(self):
        self.ASM_wings_text.delete(0, END)
        self.ASM_wings_text.insert(0, self.extra_wing_length_default)

    def wing_text_update(self, value_text: str, wing_type: str):
        if wing_type == 'normal':
            self.wings_text_out(value_text)
            return
        
        wing_length_text = self.wings_text.get()
        
        pattern_int = re.compile(r'^ *(\d{1,}) *$')
        pattern_list = re.compile(r'^ *\[ *(\d{1,}) *, *(\d{1,}) *\] *$')
        wing_length_int = pattern_int.match(wing_length_text)
        wing_length_list = pattern_list.match(wing_length_text)
        
        if wing_length_int is not None:
            wing_length = [int(wing_length_int.group(1)), int(wing_length_int.group(1))]
        elif wing_length_list is not None:
            wing_length = [int(wing_length_list.group(1)), int(wing_length_list.group(2))]
        else:
            messagebox.showwarning(title='Warning', message='\n'.join(eval(self.msg_map['Wing length check message'])))
            wing_length = eval(self.wing_length_default)
        
        wing_length_new = pattern_list.match(value_text)
        if wing_length_new is not None:
            side_wing_value = min(int(wing_length_new.group(1)), int(wing_length_new.group(2)))
        else:
            side_wing_value = int(value_text)
        
        if wing_type == 'branch_addr':
            self.wings_text_out(f'[{side_wing_value}, {wing_length[1]}]')
        elif wing_type == 'branch_target':
            self.wings_text_out(f'[{wing_length[0]}, {side_wing_value}]')

    def fetch_wings(self):
        wing_length_text = self.wings_text.get()

        pattern_int = re.compile(r'^ *(\d{1,}) *$')
        wing_length_int = pattern_int.match(wing_length_text)
        if wing_length_int is not None:
            return [int(wing_length_int.group(1)), int(wing_length_int.group(1))]
        
        pattern_list = re.compile(r'^ *\[ *(\d{1,}) *, *(\d{1,}) *\] *$')
        wing_length_list = pattern_list.match(wing_length_text)
        if wing_length_list is not None:
            return [int(wing_length_list.group(1)), int(wing_length_list.group(2))]
        
        self.reset_wings_text()
        messagebox.showwarning(title='Warning', message='\n'.join(eval(self.msg_map['Wing length check message'])))
        return eval(self.wing_length_default)

    def fetch_extra_wings(self):
        wing_length_text = self.ASM_wings_text.get()

        pattern_int = re.compile(r'^ *(\d{1,}) *$')
        wing_length_int = pattern_int.match(wing_length_text)
        if wing_length_int is not None:
            return [int(wing_length_int.group(1)), int(wing_length_int.group(1))]
        
        pattern_list = re.compile(r'^ *\[ *(\d{1,}) *, *(\d{1,}) *\] *$')
        wing_length_list = pattern_list.match(wing_length_text)
        if wing_length_list is not None:
            return [int(wing_length_list.group(1)), int(wing_length_list.group(2))]
        
        self.reset_ASM_wings_text()
        messagebox.showwarning(title='Warning', message='\n'.join(eval(self.msg_map['Extra wing length check message'])))
        return eval(self.extra_wing_length_default)

    def old_ASM_text_out(self, msg: list, high_light_line: list):
        if msg is None:
            return
        self.old_ASM_text.config(state=NORMAL)
        self.old_ASM_text.delete(0.1, END)
        for index in range(len(msg)):
            if int(high_light_line[0]) <= index <= int(high_light_line[1]):
                self.old_ASM_text.insert('insert', msg[index]+'\n', 'high_light_old')
            else:
                self.old_ASM_text.insert('insert', msg[index]+'\n')
        # Warning: text_window compressed, sometimes 'text.see()' doesn't work properly
        self.old_ASM_text.see(high_light_line[0])
        self.old_ASM_text.config(state=DISABLED)
        
    def new_ASM_text_out(self, msg: list, high_light_line: list):
        if msg is None:
            return
        self.new_ASM_text.config(state=NORMAL)
        self.new_ASM_text.delete(0.1, END)
        for index in range(len(msg)):
            if int(high_light_line[0]) <= index <= int(high_light_line[1]):
                self.new_ASM_text.insert('insert', msg[index]+'\n', 'high_light_new')
            else:
                self.new_ASM_text.insert('insert', msg[index]+'\n')
        self.new_ASM_text.see(high_light_line[0])
        self.new_ASM_text.config(state=DISABLED)

    def update_middle_ASM_output(self, midASMDataContainer):
        self.btn_update.config(state=NORMAL)
        self.btn_prev_addr.config(state=NORMAL)
        self.btn_next_addr.config(state=NORMAL)
        self.branch_checkbox.config(state=NORMAL)

        if midASMDataContainer.branch_target_size == 0:
            self.branch_checkbox.config(state=DISABLED)

        if midASMDataContainer.branch_addr_size == 0:
            midASMDataContainer.target_on()
            self.is_check_branch.set(True)
            self.branch_checkbox.config(state=DISABLED)

        if midASMDataContainer.branch_target_size == 1 or midASMDataContainer.branch_addr_size == 1:
            self.btn_prev_addr.config(state=DISABLED)
            self.btn_next_addr.config(state=DISABLED)

        [old_ASM, old_highlight] = midASMDataContainer.get_msg_bundle(is_old_file = True)
        self.old_ASM_text_out(old_ASM, old_highlight)
        [new_ASM, new_highlight] = midASMDataContainer.get_msg_bundle(is_old_file = False)
        self.new_ASM_text_out(new_ASM, new_highlight)

    def btn_after_load(self, is_btn_enabled: bool):
        if is_btn_enabled:
            self.btn_generate.config(state=NORMAL)
        else:
            self.btn_generate.config(state=DISABLED)
        self.btn_skip.config(state=DISABLED)
        self.btn_undo.config(state=DISABLED)
        self.btn_restart.config(state=DISABLED)
        self.btn_savcht.config(state=DISABLED)
        self.btn_savnso.config(state=DISABLED)
        self.btn_regenerate.config(state=DISABLED)

    def btn_after_1st_generate(self):
        self.btn_load_old_file.config(state=DISABLED)
        self.btn_load_new_file.config(state=DISABLED)
        self.btn_generate.config(state=NORMAL)
        self.btn_skip.config(state=NORMAL)
        self.btn_undo.config(state=NORMAL)
        self.btn_restart.config(state=NORMAL)
        self.btn_savcht.config(state=NORMAL)
        self.btn_savnso.config(state=NORMAL)
        self.btn_regenerate.config(state=NORMAL)

    def btn_after_restart(self):
        self.btn_load_old_file.config(state=NORMAL)
        self.btn_load_new_file.config(state=NORMAL)
        self.btn_generate.config(state=NORMAL)
        self.btn_skip.config(state=DISABLED)
        self.btn_undo.config(state=DISABLED)
        self.btn_restart.config(state=DISABLED)
        self.btn_savcht.config(state=DISABLED)
        self.btn_savnso.config(state=DISABLED)
        self.btn_regenerate.config(state=DISABLED)

    def reset_major_text_state(self):
        self.force_ARM64.set(False)
        self.force_ARM64_checkbox.config(state=NORMAL)
        self.input_cheats_text.config(state=NORMAL)
        self.current_cheats_text.config(state=NORMAL)
        self.current_cheats_text.delete(0.1, END)
        self.current_cheats_text.config(state=DISABLED)
        self.reset_wings_text()
        self.log_text.config(state=NORMAL)
        self.log_text.delete(0.1, END)
        self.log_text.config(state=DISABLED)
        self.output_cheats_text.config(state=NORMAL)
        self.output_cheats_text.delete(0.1, END)
        self.output_cheats_text.config(state=DISABLED)

    def reset_middle_ASM_state(self):
        self.old_ASM_text.config(state=NORMAL)
        self.old_ASM_text.delete(0.1, END)
        self.old_ASM_text.config(state=DISABLED)
        self.new_ASM_text.config(state=NORMAL)
        self.new_ASM_text.delete(0.1, END)
        self.new_ASM_text.config(state=DISABLED)
        self.ASM_wings_text.delete(0, END)
        self.ASM_wings_text.insert(0, self.extra_wing_length_default)
        self.btn_update.config(state=DISABLED)
        self.btn_prev_addr.config(state=DISABLED)
        self.btn_next_addr.config(state=DISABLED)
        self.is_check_branch.set(False)
        self.branch_checkbox.config(state=DISABLED)

    def reset_UI(self):
        self.btn_after_restart()
        self.reset_major_text_state()
        self.reset_middle_ASM_state()
    
    def reset_param(self, is_restart: bool):
        self.cur_position = [0, 0, 0]  # Hints: [code_num, chunk_num, offset]
        self.initialize_code_cave()

        if is_restart:
            self.is_initialized = False
            self.is_ended = False
            self.output_stack.clear()
            self.output_stack.push({'msg': '', 'code_cave': deepcopy(self.code_cave)})
            self.midASMDataContainer.flush()
        else:  # Hints: Initialize
            self.output_stack = PseudoStack()
            self.output_stack.push({'msg': '', 'code_cave': deepcopy(self.code_cave)})
            self.midASMDataContainer = MidASMDataContainer((self.old_main_file, self.new_main_file), self.code.ASM_type)
            self.force_ARM64_checkbox.config(state=DISABLED)
            self.input_cheats_text.config(state=DISABLED)

    def initialize_code_cave(self):
        if bytes_to_int(self.new_main_file.codeCaveEnd) > bytes_to_int(self.new_main_file.codeCaveStart):
            self.code_cave = [bytes_to_int(self.new_main_file.codeCaveStart),
                                    bytes_to_int(self.new_main_file.codeCaveEnd)]
        else:
            self.code_cave = None

    def allocate_cave(self, cave_size: int):
        if self.code_cave[1] - self.code_cave[0] < cave_size * 4:
            return None
        else:
            return self.code_cave[0]

    def update_cave(self, cave_size: int):
        self.code_cave = [self.code_cave[0] + cave_size * 4, self.code_cave[1]]

    def get_code_chunck_by_pos(self, position: list):
        return self.code.code_struct[str(position[0])][str(position[1])]

    def gen_disam_value_mixture_list(self, code_struct: dict):
        mixture_list = []
        is_value_list = code_struct['contents']['is_value']
        raw_list = code_struct['contents']['raw']

        if not self.code.is_full_of_value(is_value_list):
            disam_list = deepcopy(code_struct['contents']['detail']['disam'])  # Warning: Deepcopy required if "pop()"!

        for index in range(len(is_value_list)):
            if is_value_list[index] == True:
                raw_str_list = re.split(' ', raw_list[index])
                msg = ("0x%s:\t%s" %((hex(int(raw_str_list[1], 16))[2:]).zfill(8).upper(), raw_str_list[2].upper()))
                mixture_list.append(msg)
            else:
                disam = disam_list.pop(0)
                mixture_list.append(disam)

        return mixture_list

    def set_current_cheats_text_out(self, position: list):
        code_struct = self.get_code_chunck_by_pos(position)
        if code_struct['type'] != 'code_type_asm':
            self.current_cheats_text_out('\n'.join(code_struct['contents']['raw']), True)
        else:
            msg = (
                    '=========== RAW ===========\n' +
                    '\n'.join(code_struct['contents']['raw']) + '\n' +
                    '\n' +
                    '\n' +
                    '=========== ASM ===========\n' +
                    '\n'.join(self.gen_disam_value_mixture_list(code_struct))
                )
            self.current_cheats_text_out(msg, True)

    def gen_addr_msg(self, msg_type: str, addr_type: str, addr_str: str):
        return '\n'.join(eval(self.msg_map[msg_type]))
    
    def generate_and_set_log_text_out(self, position: list):
        code_chunk = self.get_code_chunck_by_pos(position)

        if self.code.is_title(code_chunk['type']):  # Hints: Title
            log_text_msg = (  '\n'
                            + '\n'.join(eval(self.msg_map[code_chunk['type']]))
                            + '\n\n'
                            + '\n'.join(eval(self.msg_map['force_generate'])))
        elif code_chunk['type'] in self.code_pattern:  # Hints: Other Types
            log_text_msg = (  '\n'
                            + self.code_pattern[code_chunk['type']]['description']
                            + '\n\n'
                            + '\n'.join(eval(self.code_pattern[code_chunk['type']]['details']))
                            + '\n\n'
                            + '\n'.join(eval(self.msg_map[self.code_pattern[code_chunk['type']]['generate_type']])))
        else:  # Hints: ASM Type
            org_addr = None
            org_addr_branch = None
            addr = None
            addr_branch = None

            if code_chunk['contents']['in_code_cave']:
                addr_type = '[.CodeCave]'
            elif code_chunk['contents']['multimedia_offset'] is not None:
                addr_type = '[.Multimedia]'
            else:
                addr_type = '[.Text]'

            org_addr = code_chunk['contents']['addr'][0]
            addr = self.find_addr(position, is_branch_target = False)
            if addr is None:
                addr_msg = self.gen_addr_msg('none_addr_located', addr_type, '')
            elif isinstance(addr, int):
                addr_str = '0x' + (hex(addr)[2:]).zfill(8).upper()
                addr_msg = self.gen_addr_msg('single_addr_located', addr_type, addr_str)
            else:
                addr_str = list(map(lambda x:'0x'+(hex(x)[2:]).zfill(8).upper(), addr))
                addr_msg = self.gen_addr_msg('multi_addr_located', addr_type, addr_str)

            if code_chunk['contents']['detail'] is not None and code_chunk['contents']['detail']['is_branch']:
                asm_type = ' branch'
                addr_branch = self.find_addr(position, is_branch_target = True)
                branch_chunk = code_chunk['contents']['detail']['branch_detail']

                if branch_chunk['branch_to_cave']:
                    addr_type = 'Branch to [.CodeCave]'
                elif branch_chunk['branch_to_multi']:
                    addr_type = 'Branch to [.Multimedia]'
                else:
                    addr_type = 'Branch to [.Text]'
                    org_addr_branch = branch_chunk['branch_addr']

                if addr_branch is None:
                    extra_addr_msg = self.gen_addr_msg('none_addr_located', addr_type, '')
                elif isinstance(addr_branch, int):
                    addr_str = '0x' + (hex(addr_branch)[2:]).zfill(8).upper()
                    extra_addr_msg = self.gen_addr_msg('single_addr_located', addr_type, addr_str)
                elif isinstance(addr_branch, str):
                    addr_type = 'Branch to [.CheatCode]'
                    addr_str = addr_branch
                    extra_addr_msg = self.gen_addr_msg('single_addr_located', addr_type, addr_str)
                else:
                    addr_str = list(map(lambda x:'0x'+(hex(x)[2:]).zfill(8).upper(), addr_branch))
                    extra_addr_msg = self.gen_addr_msg('multi_addr_located', addr_type, addr_str)

                addr_msg = (  addr_msg
                            + '\n--------------------------------------------------------------------\n'
                            + extra_addr_msg)

                if addr is None or addr_branch is None:
                    gen_msg = '\n'.join(eval(self.msg_map['discard_or_regen']))
                elif isinstance(addr, int) and isinstance(addr_branch, int):
                    gen_msg = '\n'.join(eval(self.msg_map['flat_generate']))
                else:
                    gen_msg = '\n'.join(eval(self.msg_map['choose_or_regen']))
                
                gen_msg = (  gen_msg
                           + '\n\n'
                           + '\n'.join(eval(self.msg_map['wing_length_warn'])))   

            else:
                asm_type = ''

                if addr is None:
                    gen_msg = '\n'.join(eval(self.msg_map['discard_or_regen']))
                elif isinstance(addr, int):
                    gen_msg = '\n'.join(eval(self.msg_map['flat_generate']))
                else:
                    gen_msg = '\n'.join(eval(self.msg_map['choose_or_regen']))   

                if self.code.code_struct[str(position[0])]['info']['is_value_only']:
                    gen_msg = (  gen_msg
                               + '\n\n'
                               + '\n'.join(eval(self.msg_map['value_warn'])))   
            
            log_text_msg = (  '\n'
                            + '\n'.join(eval(self.msg_map['asm_code']))
                            + '\n\n'
                            + addr_msg
                            + '\n\n'
                            + gen_msg
                            )
        
            if addr is not None or addr_branch is not None:
                code_size = len(code_chunk['contents']['raw'])
                addr = [addr] if isinstance(addr, int) and addr is not None else addr
                addr_branch = [addr_branch] if (isinstance(addr_branch, int) or isinstance(addr_branch, str)) and addr_branch is not None else addr_branch
                self.midASMDataContainer.update(self.fetch_wings(), self.fetch_extra_wings(), code_size, org_addr, org_addr_branch, addr, addr_branch)
                self.update_middle_ASM_output(self.midASMDataContainer)

        self.midASMDataContainer.set_updated()
        self.log_text_out(log_text_msg, True)
            
    def find_ready_made_addr(self, addr: int, position: list):
        addr_size = len(self.get_code_chunck_by_pos(position)['contents']['raw'])

        for index in range(addr_size):
            if str(addr + index * 4) not in self.code.addr_booklet:
                continue

            for shared_addr_position in self.code.addr_booklet[str(addr + index * 4)]:
                if (shared_addr_position[0] < position[0] 
                        or (shared_addr_position[0] == position[0] and shared_addr_position[1] < position[1])):  # Caution: 'equal' would affect 'undo'
                    if ('processed' not in self.get_code_chunck_by_pos(shared_addr_position)
                            or 'allocated_addr' not in self.get_code_chunck_by_pos(shared_addr_position)['processed']):
                        continue
                    
                    return (self.get_code_chunck_by_pos(shared_addr_position)['processed']['allocated_addr'] 
                                    + shared_addr_position[2] * 4 - index * 4)
        
        return None

    def find_addr(self, position: list, is_branch_target: bool):
        code_chunk = self.get_code_chunck_by_pos(position)
        
        if not is_branch_target:
            allocated_addr = self.find_ready_made_addr(code_chunk['contents']['addr'][0], position)
            if allocated_addr is not None:
                return allocated_addr

            if code_chunk['contents']['multimedia_offset'] is not None:
                return code_chunk['contents']['multimedia_offset'] + bytes_to_int(self.new_main_file.rodataMemoryOffset)
            
            if code_chunk['contents']['in_code_cave']:
                return self.allocate_cave(len(code_chunk['contents']['raw']))
            
            if code_chunk['contents']['detail'] is None or not code_chunk['contents']['detail']['is_branch']:
                code_type = 'normal'
            else:
                code_type = 'branch_target' if is_branch_target else 'branch_addr'
            addr_list = self.find_main_addr([code_chunk['contents']['addr'][0], code_chunk['contents']['addr'][-1] + 4], code_type)
            if addr_list is not None:
                return addr_list if len(addr_list) != 1 else addr_list[0]
            
            return None
        
        else:
            branch_chunk = code_chunk['contents']['detail']['branch_detail']

            if (branch_chunk['branch_to_cave'] or branch_chunk['branch_to_multi']) and branch_chunk['branch_link'] is None:  # Hints: meaningless pointer
                return None
            
            if branch_chunk['branch_link'] is not None:
                allocated_position = branch_chunk['branch_link'][0]  # Hints: branch to multi code chunk with same addr, choose the first generated one
                if (allocated_position[0] < position[0]
                        or (allocated_position[0] == position[0] and allocated_position[1] < position[1])):
                    if 'processed' in self.get_code_chunck_by_pos(allocated_position):
                        return (self.get_code_chunck_by_pos(allocated_position)['processed']['allocated_addr']
                                        + allocated_position[2] * 4)
                    return None
                else:
                    return f"""C{position[0]}C{position[1]}BLC{allocated_position[0]}C{allocated_position[1]}O{allocated_position[2]}"""
                
            addr_list = self.find_main_addr([branch_chunk['branch_addr'], branch_chunk['branch_addr'] + 4], code_type = 'branch_target')
            if addr_list is not None:
                return addr_list if len(addr_list) != 1 else addr_list[0]

            return None
 
    def find_main_addr(self, addr_range: list, code_type: str):
        wing_length = self.fetch_wings()
        if code_type == 'branch_addr':
            wing_length = [wing_length[0], wing_length[0]]
        elif code_type == 'branch_target':
            wing_length = [wing_length[1], wing_length[1]]

        main_file_bundle = [self.old_main_file.mainFuncFile, self.new_main_file.mainFuncFile]

        [hit_start_addr, wing_length, real_addr_offset] = find_feature_addr(main_file_bundle, addr_range, wing_length, self.code.ASM_type)
        self.wing_text_update(str(wing_length), code_type)
        
        if len(hit_start_addr) == 0:
            return None
        return list(map(lambda x:x+real_addr_offset, hit_start_addr))

    def analysis_code(self, position: list):  # Hints: For left text windows
        try:
            self.set_current_cheats_text_out(position)
            self.generate_and_set_log_text_out(position)
        except Exception as e:
            self.logger.exception(e)
    
    def gen_code_from_code_chunk(self, code_chunk: dict, addr: int) -> str:
        single_line_code = []
        code_length = len(code_chunk['contents']['raw'])

        for index in range(code_length):
            single_line_code.append(
                      code_chunk['contents']['head'][index]
              + ' ' + (hex(addr + index * 4)[2:]).zfill(8).upper()
              + ' ' + code_chunk['contents']['body'][index]
            )

        return '\n'.join(single_line_code)
    
    def gen_branch_code_body(self, b_op, branch_addr, branch_target, ASM_type = 'ARM64'):
        if 'adr' in b_op:
            return keystone_long_adr_fix(b_op, branch_addr, branch_target, ASM_type = ASM_type)
        
        code_str = b_op + ' #' + hex(branch_target)
        return get_branch_code_body(code_str, branch_addr, ASM_type = ASM_type)

    def gen_branch_code_from_code_chunk(self, code_chunk: dict, branch_addr: int, branch_target) -> str:
        if isinstance(branch_target, str):  # Hints: 'BL' not in branch_target_addr
            return ' '.join([
                code_chunk['contents']['head'][0],
                (hex(branch_addr)[2:]).zfill(8).upper(),
                branch_target])
        
        b_op = code_chunk['contents']['detail']['branch_detail']['branch_type']
        code_body = self.gen_branch_code_body(b_op, branch_addr, branch_target, self.code.ASM_type)

        return ' '.join([
              code_chunk['contents']['head'][0],
              (hex(branch_addr)[2:]).zfill(8).upper(),
              code_body])

    def broadcast_link_update(self, output_msg: str, cur_position: list, addr: int):
        code_chunk = self.get_code_chunck_by_pos(cur_position)
        broadcast_list = []
        if 'broadcast' not in code_chunk['contents']:
            return output_msg
        
        for broadcast_target in code_chunk['contents']['broadcast']:
            if (broadcast_target[0] < cur_position[0] 
                    or (broadcast_target[0] == cur_position[0] and broadcast_target[1] < cur_position[1])):
                broadcast_list.append(broadcast_target)
        
        if broadcast_list != [] and not any(isinstance(i, list) for i in broadcast_list):
            broadcast_list = [broadcast_list]

        for tar_position in broadcast_list:
            if 'processed' not in self.get_code_chunck_by_pos(tar_position):
                continue
            
            offset = self.get_code_chunck_by_pos(tar_position)['contents']['detail']['branch_detail']['branch_link'][0][2]  # Hints: branch to multi code chunk with same addr, choose the first generated one
            self.code.code_struct[str(tar_position[0])][str(tar_position[1])]['processed'].update(
                {'allocated_branch_addr': addr + offset * 4})
            
            b_op = self.get_code_chunck_by_pos(tar_position)['contents']['detail']['branch_detail']['branch_type']
            code_body = self.gen_branch_code_body(b_op, self.get_code_chunck_by_pos(tar_position)['processed']['allocated_addr'], (addr + offset * 4), self.code.ASM_type)

            pattern = f"""C{tar_position[0]}C{tar_position[1]}BLC{cur_position[0]}C{cur_position[1]}O{cur_position[2]}"""
            output_msg = output_msg.replace(pattern, code_body)

        return output_msg

    def remove_unlinked_branch(self):
        msg = self.output_cheats_text.get('1.0', END)
        bad_link_pattern = r'04000000 [AaBbCcDdEeFf\d]{8} C\d+C\d+BLC\d+C\d+O\d+\n'
        msg = re.sub(bad_link_pattern, "", msg)
        msg = re.sub('\n+$', "", msg)
        self.output_cheats_text_out(msg, need_clear = True)

    def generate_output(self, position: list, button: str):
        try:
            self.generate_and_set_output_cheats_text(position, button)
        except Exception as e:
            self.logger.exception(e)

    def generate_and_set_output_cheats_text(self, position: list, button: str):  # Hints: For right/output text windows
        if not self.midASMDataContainer.is_updated:  # Hints: For last step with no analysis_code()
            return
        
        code_chunk = self.get_code_chunck_by_pos(position)
        need_linebreak = False if str(position[1]+1) in self.code.code_struct[str(position[0])] else True

        addr = None
        branch_target_addr = None
        output_msg = ''

        if self.code.is_title(code_chunk['type']):  # Hints: Title
            output_msg = '\n'.join(code_chunk['contents']['raw'])

        elif code_chunk['type'] in self.code_pattern:  # Hints: Other Types
            if self.code_pattern[code_chunk['type']]['generate_type'] == 'force_discard':
                output_msg = ''
            elif self.code_pattern[code_chunk['type']]['generate_type'] == 'force_generate':
                output_msg = '\n'.join(code_chunk['contents']['raw'])
            elif self.code_pattern[code_chunk['type']]['generate_type'] == 'flat_generate':
                output_msg = '\n'.join(code_chunk['contents']['raw']) if button == 'generate' else ''

        else:  # Hints: ASM Type
            if code_chunk['contents']['detail'] is not None and code_chunk['contents']['detail']['is_branch']:
                if button == 'generate':
                    addr = self.midASMDataContainer.get_current_branch_addr()
                    branch_target_addr = self.midASMDataContainer.get_current_branch_target()
                    if addr is not None and branch_target_addr is not None:  # Hints: if user choose 'generate' disregarding introduction
                        output_msg = self.gen_branch_code_from_code_chunk(code_chunk, addr, branch_target_addr)
                        if code_chunk['contents']['in_code_cave']:
                            self.update_cave(len(code_chunk['contents']['raw']))
                        if not isinstance(branch_target_addr, str):  # Hints: 'BL' not in branch_target_addr
                            self.code.code_struct[str(position[0])][str(position[1])].update({
                                'processed': {
                                    'allocated_addr': addr,
                                    'allocated_branch_addr': branch_target_addr
                                    }})
                        else:
                            self.code.code_struct[str(position[0])][str(position[1])].update({'processed': {'allocated_addr': addr}})

            else:
                if button == 'generate':
                    addr = self.midASMDataContainer.get_current_branch_addr()
                    if addr is not None:  # Hints: if user choose 'generate' disregarding introduction
                        output_msg = self.gen_code_from_code_chunk(code_chunk, addr)
                        if code_chunk['contents']['in_code_cave']:
                            self.update_cave(len(code_chunk['contents']['raw']))
                        self.code.code_struct[str(position[0])][str(position[1])].update({'processed': {'allocated_addr': addr}})

        no_insert = True if output_msg == '' else False
        output_msg = output_msg + '\n' if need_linebreak else output_msg
        if no_insert:  # Hints: self.output_cheats_text wrap automatically with '\n'
            output_msg = self.output_cheats_text.get('1.0', END)[:-1] + output_msg
        else:
            output_msg = self.output_cheats_text.get('1.0', END) + output_msg
        output_msg = output_msg[1:] if output_msg[0] == '\n' else output_msg

        if 'BL' in output_msg and addr is not None:  # Hints: accelerate broadcast list process speed
            output_msg = self.broadcast_link_update(output_msg, position, addr)
        
        self.output_cheats_text_out(output_msg, need_clear = True, no_insert = no_insert and not need_linebreak)
        self.output_stack.push({'msg': output_msg, 'code_cave': deepcopy(self.code_cave)})
        self.clear_current_cheats_text()
        self.clear_log_text()
        self.reset_middle_ASM_state()
        self.midASMDataContainer.flush()
        self.reset_wings_text()

    def check_next_step(self):
        code_num = self.cur_position[0]
        chunk_num = self.cur_position[1]

        if str(chunk_num+1) in self.code.code_struct[str(code_num)]:
            return True
        
        if str(code_num+1) in self.code.code_struct:
            return True

        return False

    def next_step(self):
        code_num = self.cur_position[0]
        chunk_num = self.cur_position[1]

        if str(chunk_num+1) in self.code.code_struct[str(code_num)]:
            self.cur_position = [code_num, chunk_num+1, 0]
            return True
        
        if str(code_num+1) in self.code.code_struct:
            self.cur_position = [code_num+1, 0, 0]
            return True

        return False

    def check_previous_step(self):
        code_num = self.cur_position[0]
        chunk_num = self.cur_position[1]

        if str(chunk_num-1) in self.code.code_struct[str(code_num)]:
            return True
        
        if str(code_num-1) in self.code.code_struct:
            return True
        
        return False

    def previous_step(self):
        code_num = self.cur_position[0]
        chunk_num = self.cur_position[1]

        if str(chunk_num-1) in self.code.code_struct[str(code_num)]:
            self.cur_position = [code_num, chunk_num-1, 0]
            return True
        
        if str(code_num-1) in self.code.code_struct:
            key_list = list(self.code.code_struct[str(code_num-1)])
            key_list.remove('info')
            last_key = key_list[-1]
            self.cur_position = [code_num-1, int(last_key), 0]
            return True
        
        return False
    
    def generate(self):
        if not self.is_initialized:
            try:
                self.code = CodeStruct(self.input_cheats_text_in(), self.globalInfo, (self.old_main_file, self.new_main_file), self.force_ARM64.get())
                self.input_cheats_text_out(self.code.get_normalized_code())
                print(self.code.code_struct)
            except Exception as e:
                self.logger.exception(e)
                return
            
            if self.code.code_struct == {}:
                return
            
            self.reset_param(is_restart = False)
            self.analysis_code(self.cur_position)
            self.btn_after_1st_generate()
            self.is_initialized = True
            return
        
        if self.is_ended:
            return

        self.generate_output(self.cur_position, 'generate')
        if self.check_next_step():
            self.next_step()
        else:
            self.remove_unlinked_branch()
            self.is_ended = True
            return
        self.analysis_code(self.cur_position)

    def skip(self):
        self.generate_output(self.cur_position, 'skip')
        if self.check_next_step():
            self.next_step()
        else:
            self.remove_unlinked_branch()
            self.is_ended = True
            return
        self.analysis_code(self.cur_position)
    
    def undo(self):
        if not self.check_previous_step():
            self.restart()
        
        if 'processed' in self.code.code_struct[str(self.cur_position[0])][str(self.cur_position[1])]:
            self.code.code_struct[str(self.cur_position[0])][str(self.cur_position[1])].pop('processed')
        
        self.output_stack.pop()
        recover_data = self.output_stack.get()
        if recover_data is not None:
            self.code_cave = deepcopy(recover_data['code_cave'])
            self.output_cheats_text_out(recover_data['msg'], need_clear = True)

        self.reset_middle_ASM_state()
        self.midASMDataContainer.flush()

        if not self.is_ended:
            self.previous_step()
        else:
            self.is_ended = False

        self.analysis_code(self.cur_position)

    def restart(self):
        self.reset_UI()
        self.reset_param(is_restart = True)

    def regenerate(self):
        ### Hints: Robust but not necessary ###
        self.reset_middle_ASM_state()
        self.midASMDataContainer.flush()
        ### ------------------------------- ###
        try:
            self.generate_and_set_log_text_out(self.cur_position)
        except Exception as e:
            self.logger.exception(e)

    def update(self):
        self.midASMDataContainer.set_extra_wing_length(self.fetch_extra_wings())
        self.update_middle_ASM_output(self.midASMDataContainer)
    
    def next(self):
        self.midASMDataContainer.next()
        self.update_middle_ASM_output(self.midASMDataContainer)

    def previous(self):
        self.midASMDataContainer.previous()
        self.update_middle_ASM_output(self.midASMDataContainer)

    def check(self):
        self.midASMDataContainer.switch()
        self.update_middle_ASM_output(self.midASMDataContainer)

    def sav_cht(self):
        file_path = filedialog.asksaveasfilename(title = self.hints_map['Save New Codes'],
                        initialfile = f'{self.new_main_file.ModuleId.upper()}.txt',
                        filetypes = [('text file', '.txt')])
        if file_path == '':
            return
        
        file_text = self.output_cheats_text.get('1.0', END)
        last_index = len(file_text) - 1
        index = last_index
        remove_index = 0
        while index > 0:
            if file_text[index] != '\n':
                remove_index = - (last_index - index)
                break
            index = index - 1
        file_text = file_text[:remove_index]

        with open(file = file_path, mode = 'a+', encoding = 'utf-8') as file:
            file.seek(0)
            file.truncate()
            file.write(file_text)
            dialog.Dialog(None, {'title': '\n'.join(eval(self.msg_map['Cheat Code'])), 'text': '\n'.join(eval(self.msg_map['Saved'])), 'bitmap': 'warning', 'default': 0,
                    'strings': ('\n'.join(eval(self.msg_map['OK'])), '\n'.join(eval(self.msg_map['Cancel'])))})

    def gen_bytes_content(self, code_body: list):
        bytes_content = bytearray()
        for code in code_body:
            bytes_code = bytearray.fromhex(code)
            bytes_code.reverse()
            bytes_content += bytes_code
        return bytes_content

    def sav_nso(self):
        file_path = filedialog.asksaveasfilename(title = self.hints_map['Save New NSO'],
                        initialfile = f'main',
                        filetypes = [('All Files', '*')])

        code_struct = self.code.code_struct
        for code_num in code_struct:
            for chunk_num in code_struct[code_num]:
                if 'processed' not in code_struct[code_num]:
                    continue
                
                code_chunk = code_struct[code_num][chunk_num]
                if code_chunk['contents']['detail'] is not None and code_chunk['contents']['detail']['is_branch']:
                    if 'allocated_addr' in code_chunk['processed'] and 'allocated_branch_addr' in code_chunk['processed']:
                        b_op = code_chunk['contents']['detail']['branch_detail']['branch_type']
                        code_str = b_op + ' #' + hex(code_chunk['processed']['allocated_branch_addr'])
                        if self.code.ASM_type == 'ARM64':
                            Assembler = Ks(KS_ARCH_ARM64, KS_MODE_LITTLE_ENDIAN)
                            encoding_dock, _ = Assembler.asm(code_str, code_chunk['processed']['allocated_addr'])
                        elif self.code.ASM_type == 'ARM32':
                            Assembler = Ks(KS_ARCH_ARM, KS_MODE_ARM | KS_MODE_LITTLE_ENDIAN)
                            encoding_dock, _ = Assembler.asm(code_str, code_chunk['processed']['allocated_addr'])
                        code_body = ''.join('{:02x}'.format(x).upper() for x in reversed(encoding_dock))
                        bytes_content = self.gen_bytes_content([code_body])
                else:
                    bytes_content = self.gen_bytes_content(code_chunk['contents']['body'])

                self.new_main_file.modify(code_chunk['processed']['allocated_addr'], bytes_content, in_code_cave = code_chunk['contents']['in_code_cave'])

        if file_path != '':
            with open(file = file_path, mode = 'wb') as file:
                file.seek(0)
                file.truncate()
                file.write(self.new_main_file.NSORaw4Mod)
                dialog.Dialog(None, {'title': '\n'.join(eval(self.msg_map['NSO File'])), 'text': '\n'.join(eval(self.msg_map['Saved'])), 'bitmap': 'warning', 'default': 0,
                        'strings': ('\n'.join(eval(self.msg_map['OK'])), '\n'.join(eval(self.msg_map['Cancel'])))})
            
            try:
                if os.path.exists(os.path.join(self.tool_path, 'nsnsotool.exe')):
                    process = subprocess.Popen(["cmd"], shell=False, close_fds=True, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
                    commands = ('cd tools\n'
                                f'nsnsotool "{file_path}"\n'
                            )
                    process.communicate(commands.encode('utf-8'))
                else:
                    messagebox.showerror(title='Error', message='\n'.join(eval(self.msg_map['nsnsotool missing'])))

            except Exception as e:
                messagebox.showwarning(title='Warning', message='\n'.join(eval(self.msg_map['nsnsotool warning'])))
                self.logger.exception(e)  