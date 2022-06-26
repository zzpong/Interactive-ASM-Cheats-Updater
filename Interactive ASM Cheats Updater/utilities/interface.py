from asyncio.subprocess import PIPE, STDOUT
import tkinter, os, base64, webbrowser, shutil, re, time, json, subprocess
from copy import deepcopy
from capstone import *
from keystone import *
from tkinter import *
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from tkinter import dialog, filedialog

from sources.memory_pic import *
from utilities.code_process import *
from utilities.main_file import *

def get_pic(pic_code, pic_name):
    image = open(pic_name, 'wb')
    image.write(base64.b64decode(pic_code))
    image.close()

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytearray):
            return obj.hex()
        return json.JSONEncoder.default(self, obj)

class ScrolledTextRightClick:
    def __init__(self, scrolledTextHandle):
        self.scrolledTextHandle = scrolledTextHandle

    def onPaste(self):
        try:
            self.text = self.scrolledTextHandle.clipboard_get()
        except tkinter.TclError:
            pass
        self.scrolledTextHandle.insert('insert', str(self.text))

    def onCopy(self):
        self.scrolledTextHandle.clipboard_clear()
        self.text = self.scrolledTextHandle.get('1.0', END)
        try:
            self.scrolledTextHandle.clipboard_append(self.text)
        except tkinter.TclError:
            pass

    def onCut(self):
        self.onCopy()
        try:
            self.scrolledTextHandle.delete('1.0', END)
        except tkinter.TclError:
            pass

class LinkLabel(Label):
    def __init__(self,master,link,font=('Arial',9,'underline'),bg='#f0f0f0'):
        super().__init__(master,text=link,font=font,fg='blue',bg=bg)
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

class ASM_updater_UI:
    def __init__(self, loc: dict, root_path: str):
        self.mainWin = tkinter.Tk()
        self.loc_hints_map = loc['hints_map']
        self.loc_btn_map = loc['btn_map']
        self.loc_msg_map = loc['msg_map']
        self.loc_wing_length_default = loc['wing_length_default']
        self.loc_extra_wing_length_default = loc['loc_extra_wing_length_default']

        self.mainWin.title(loc['title'])
        get_pic(xcw_ico, 'xcw.ico')
        self.mainWin.iconbitmap("xcw.ico")
        self.mainWin.geometry('1400x800')
        # self.mainWin.resizable(False, False)  # Debug: plugin will not shrink with window size
        os.remove("xcw.ico")

        # Load file frame
        self.load_file_frame = tkinter.Frame(self.mainWin, width=1000, height=200, bg='LemonChiffon', relief=GROOVE)
        self.load_file_frame.pack(expand='yes', fill='both', anchor='n', side='top', padx=5, pady=5)

        # Old load file frame
        self.old_load_file_frame = tkinter.Frame(self.load_file_frame, bd = 2, highlightthickness = 1, relief=RIDGE)
        self.old_load_file_frame.pack(expand='yes', fill='both', anchor='w', side='left', padx=5, pady=5)

        self.old_file_text = tkinter.Label(self.old_load_file_frame, text=self.loc_hints_map['Old Main File:'])
        self.old_file_text.pack(expand='yes', fill='both', anchor='w', side='left', padx=5, pady=5)

        self.old_file_entry = tkinter.Entry(self.old_load_file_frame, width=60, justify=CENTER, state=DISABLED)
        self.old_file_entry.pack(expand='yes', fill='both', anchor='center', side='left', padx=5, pady=5)

        self.old_file_button = tkinter.Button(self.old_load_file_frame, height=0, text=self.loc_btn_map['Load Old'], relief=RAISED, command=self.load_old_file)
        self.old_file_button.pack(expand='yes', fill='both', anchor='e', side='left', padx=5, pady=5)

        # New load file frame
        self.new_load_file_frame = tkinter.Frame(self.load_file_frame, bd = 2, highlightthickness = 1, relief=RIDGE)
        self.new_load_file_frame.pack(expand='yes', fill='both', anchor='w', side='left', padx=5, pady=5)

        self.new_file_text = tkinter.Label(self.new_load_file_frame, text=self.loc_hints_map['New Main File:'])
        self.new_file_text.pack(expand='yes', fill='both', anchor='w', side='left', padx=5, pady=5)

        self.new_file_entry = tkinter.Entry(self.new_load_file_frame, width=60, justify=CENTER, state=DISABLED)
        self.new_file_entry.pack(expand='yes', fill='both', anchor='center', side='left', padx=5, pady=5)

        self.new_file_button = tkinter.Button(self.new_load_file_frame, height=0, text=self.loc_btn_map['Load New'], relief=RAISED, command=self.load_new_file)
        self.new_file_button.pack(expand='yes', fill='both', anchor='e', side='left', padx=5, pady=5)

        # Debug checkbox
        self.debug_checkbox_frame = tkinter.Frame(self.load_file_frame, bd = 2, highlightthickness = 1, relief=RIDGE)
        self.debug_checkbox_frame.pack(expand='yes', fill='x', anchor='e', side='left', padx=5, pady=5)

        self.is_debug_mode = BooleanVar()
        self.debug_checkbox = Checkbutton(self.debug_checkbox_frame, text=self.loc_hints_map['Debug'], variable=self.is_debug_mode, onvalue=True, offvalue=False) 
        self.debug_checkbox.pack()

        # Main cheats frame
        self.main_cheats_frame = tkinter.Frame(self.mainWin, width=1000, height=200, bg='DeepSkyBlue', relief=GROOVE)
        self.main_cheats_frame.pack(expand='yes', fill='both', anchor='s', side='top', padx=5, pady=5)

        # Input cheats frame
        self.input_cheats_frame = tkinter.Frame(self.main_cheats_frame, bd = 2, highlightthickness = 1, relief=RIDGE)
        self.input_cheats_frame.pack(expand='yes', fill='both', anchor='w', side='left', padx=5, pady=5)

        # Input cheats script
        self.input_cheats_script = tkinter.Label(self.input_cheats_frame, text=self.loc_hints_map['Copy old cheats here:'])
        self.input_cheats_script.pack(expand='yes', fill='y', anchor='w', side='top', padx=5, pady=5)
        # Input cheats text
        self.input_cheats_text = ScrolledText(self.input_cheats_frame, width=40, height=400)
        self.input_cheats_text.pack(expand='yes', fill='both', anchor='w', side='top', padx=5, pady=5)

        # Middle cheats frame
        self.middle_cheats_frame = tkinter.Frame(self.main_cheats_frame, bd = 2, highlightthickness = 1, relief=RIDGE)
        self.middle_cheats_frame.pack(expand='yes', fill='both', anchor='center', side='left', padx=5, pady=5)

        # Middle cheats up frame
        self.middle_cheats_up_frame = tkinter.Frame(self.middle_cheats_frame, bd = 2, highlightthickness = 1, relief=RIDGE)
        self.middle_cheats_up_frame.pack(expand='yes', fill='both', anchor='center', side='top', padx=5, pady=5)

        # Current cheats script
        self.current_cheats_script = tkinter.Label(self.middle_cheats_up_frame, text=self.loc_hints_map['Current processing cheat:'])
        self.current_cheats_script.pack(anchor='w', side='top', padx=5, pady=5)
        # Current cheats text
        self.current_cheats_text = ScrolledText(self.middle_cheats_up_frame, width=40, height=20, state=DISABLED)
        self.current_cheats_text.pack(expand='yes', fill='both', anchor='w', side='top', padx=5, pady=5)

        # Middle cheats wings frame
        self.middle_cheats_wings_frame = tkinter.Frame(self.middle_cheats_frame, bd = 2, highlightthickness = 1, relief=RIDGE)
        self.middle_cheats_wings_frame.pack(expand='yes', anchor='center', side='top', padx=5, pady=5)
        self.middle_cheats_wings_frame.columnconfigure(0, weight=1)
        # wings script
        self.wings_script = tkinter.Label(self.middle_cheats_wings_frame, text=self.loc_hints_map['Wing Length:'])
        self.wings_script.pack(anchor='w', side='left', padx=5, pady=5)
        self.wings_text = tkinter.Entry(self.middle_cheats_wings_frame, width=15, justify=CENTER)
        self.wings_text.pack(anchor='e', fill='x', side='left', padx=5, pady=5)
        self.wings_text.delete(0, END)
        self.wings_text.insert(0, self.loc_wing_length_default)
        self.btn_regenerate = tkinter.Button(self.middle_cheats_wings_frame, text=self.loc_btn_map['Regenerate'], width=12, command=self.regenerate)
        self.btn_regenerate.pack(padx=5, pady=5)
        self.btn_regenerate.config(state=DISABLED)

        # Middle cheats button frame
        self.middle_cheats_button_frame = tkinter.Frame(self.middle_cheats_frame)
        self.middle_cheats_button_frame.pack(expand='yes', anchor='center', side='top', padx=5, pady=5)
        self.middle_cheats_button_frame.columnconfigure(0, weight=1)
        self.btn_generate = tkinter.Button(self.middle_cheats_button_frame, text=self.loc_btn_map['Generate'], width=10, command=self.generate)
        self.btn_generate.grid(row=0, column=0, sticky="nsew")
        self.btn_generate.config(state=DISABLED)
        self.btn_skip = tkinter.Button(self.middle_cheats_button_frame, text=self.loc_btn_map['Skip'], width=10, command=self.skip)
        self.btn_skip.grid(row=0, column=1, sticky="nsew")
        self.btn_skip.config(state=DISABLED)
        self.btn_undo = tkinter.Button(self.middle_cheats_button_frame, text=self.loc_btn_map['Undo'], width=10, command=self.undo)
        self.btn_undo.grid(row=0, column=2, sticky="nsew")
        self.btn_undo.config(state=DISABLED)
        self.btn_restart = tkinter.Button(self.middle_cheats_button_frame, text=self.loc_btn_map['Restart'], width=10, command=self.restart)
        self.btn_restart.grid(row=0, column=3, sticky="nsew")
        self.btn_restart.config(state=DISABLED)

        # Middle cheats down frame
        self.middle_cheats_down_frame = tkinter.Frame(self.middle_cheats_frame, bd = 2, highlightthickness = 1, relief=RIDGE)
        self.middle_cheats_down_frame.pack(expand='yes', fill='both', anchor='center', side='top', padx=5, pady=5)

        # Log script
        self.log_script = tkinter.Label(self.middle_cheats_down_frame, text=self.loc_hints_map['Logs:'])
        self.log_script.pack(anchor='w', side='top', padx=5, pady=5)
        # Log text
        self.log_text = ScrolledText(self.middle_cheats_down_frame, width=40, height=20, state=DISABLED)
        self.log_text.pack(expand='yes', fill='both', anchor='w', side='top', padx=5, pady=5)
    
        # Middle ASM frame
        self.middle_ASM_frame = tkinter.Frame(self.main_cheats_frame, bd = 2, highlightthickness = 1, relief=RIDGE)
        self.middle_ASM_frame.pack(expand='yes', fill='both', anchor='center', side='left', padx=5, pady=5)

        # Middle ASM up frame
        self.middle_ASM_up_frame = tkinter.Frame(self.middle_ASM_frame, bd = 2, highlightthickness = 1, relief=RIDGE)
        self.middle_ASM_up_frame.pack(expand='yes', fill='both', anchor='center', side='top', padx=5, pady=5)

        # Old ASM script
        self.old_ASM_script = tkinter.Label(self.middle_ASM_up_frame, text=self.loc_hints_map['Old Main ASM:'])
        self.old_ASM_script.pack(anchor='w', side='top', padx=5, pady=5)
        # Old ASM script
        self.old_ASM_text = ScrolledText(self.middle_ASM_up_frame, width=40, height=20, state=DISABLED)
        self.old_ASM_text.pack(expand='yes', fill='both', anchor='w', side='top', padx=5, pady=5)
        self.old_ASM_text.tag_config('high_light_old', foreground='red', background='yellow')

        # Middle ASM wings frame
        self.middle_ASM_wings_frame = tkinter.Frame(self.middle_ASM_frame, bd = 2, highlightthickness = 1, relief=RIDGE)
        self.middle_ASM_wings_frame.pack(expand='yes', anchor='center', side='top', padx=5, pady=5)
        self.middle_ASM_wings_frame.columnconfigure(0, weight=1)
        # ASM wings script
        self.ASM_wings_script = tkinter.Label(self.middle_ASM_wings_frame, text=self.loc_hints_map['Extra Wing Length:'])
        self.ASM_wings_script.pack(anchor='w', side='left', padx=5, pady=5)
        self.ASM_wings_text = tkinter.Entry(self.middle_ASM_wings_frame, width=15, justify=CENTER)
        self.ASM_wings_text.pack(anchor='e', fill='x', side='left', padx=5, pady=5)
        self.ASM_wings_text.delete(0, END)
        self.ASM_wings_text.insert(0, self.loc_extra_wing_length_default)
        self.btn_update = tkinter.Button(self.middle_ASM_wings_frame, text=self.loc_btn_map['Update'], width=12, command=self.update)
        self.btn_update.pack(padx=5, pady=5)
        self.btn_update.config(state=DISABLED)

        # Middle ASM button frame
        self.middle_ASM_button_frame = tkinter.Frame(self.middle_ASM_frame)
        self.middle_ASM_button_frame.pack(expand='yes', anchor='center', side='top', padx=5, pady=5)
        self.middle_ASM_button_frame.columnconfigure(0, weight=1)
        # Middle ASM button frame button
        self.btn_prev_addr = tkinter.Button(self.middle_ASM_button_frame, text=self.loc_btn_map['Prev'], width=10, command=self.previous)
        self.btn_prev_addr.pack(anchor='w', side='left', padx=5, pady=5)
        self.btn_prev_addr.config(state=DISABLED)
        self.btn_next_addr = tkinter.Button(self.middle_ASM_button_frame, text=self.loc_btn_map['Next'], width=10, command=self.next)
        self.btn_next_addr.pack(anchor='w', side='left', padx=5, pady=5)
        self.btn_next_addr.config(state=DISABLED)
        # Middle ASM button frame checkbox
        self.middle_ASM_checkbox_frame = tkinter.Frame(self.middle_ASM_button_frame, bd = 2, highlightthickness = 1, relief=RIDGE)
        self.middle_ASM_checkbox_frame.pack(expand='yes', fill='x', anchor='e', side='right', padx=5, pady=5)
        self.is_check_branch = False
        self.branch_checkbox = Checkbutton(self.middle_ASM_checkbox_frame, text=self.loc_hints_map['Branch'], variable=self.is_check_branch, onvalue=True, offvalue=False, state=DISABLED, command=self.check)
        self.branch_checkbox.pack()

        # Middle ASM up frame
        self.middle_ASM_down_frame = tkinter.Frame(self.middle_ASM_frame, bd = 2, highlightthickness = 1, relief=RIDGE)
        self.middle_ASM_down_frame.pack(expand='yes', fill='both', anchor='center', side='top', padx=5, pady=5)

        # New ASM script
        self.new_ASM_script = tkinter.Label(self.middle_ASM_down_frame, text=self.loc_hints_map['New Main ASM:'])
        self.new_ASM_script.pack(anchor='w', side='top', padx=5, pady=5)
        # New ASM script
        self.new_ASM_text = ScrolledText(self.middle_ASM_down_frame, width=40, height=20, state=DISABLED)
        self.new_ASM_text.pack(expand='yes', fill='both', anchor='w', side='top', padx=5, pady=5)
        self.new_ASM_text.tag_config('high_light_new', foreground='red', background='yellow')

        # Output cheats frame
        self.output_cheats_frame = tkinter.Frame(self.main_cheats_frame, bd = 2, highlightthickness = 1, relief=RIDGE)
        self.output_cheats_frame.pack(expand='yes', fill='both', anchor='e', side='left', padx=5, pady=5)

        # Output cheats up frame
        self.output_cheats_up_frame = tkinter.Frame(self.output_cheats_frame, bd = 2, highlightthickness = 1, relief=RIDGE)
        self.output_cheats_up_frame.pack(expand='yes', fill='both', anchor='e', side='top', padx=5, pady=5)

        # Output cheats script
        self.output_cheats_script = tkinter.Label(self.output_cheats_up_frame, text=self.loc_hints_map['New cheats will be here:'])
        self.output_cheats_script.pack(anchor='w', side='top', padx=5, pady=5)
        # Output cheats text
        self.output_cheats_text = ScrolledText(self.output_cheats_up_frame, width=40, height=38, state=DISABLED)
        self.output_cheats_text.pack(expand='yes', fill='both', anchor='w', side='top', padx=5, pady=5)

        # Output cheats down frame
        self.output_cheats_down_frame = tkinter.Frame(self.output_cheats_frame)
        self.output_cheats_down_frame.pack(anchor='center', side='top', padx=5, pady=5)

        # Output cheats down left frame
        self.output_cheats_down_left_frame = tkinter.Frame(self.output_cheats_down_frame)
        self.output_cheats_down_left_frame.pack(anchor='center', side='left', padx=5, pady=5)
        self.output_cheats_down_left_frame.columnconfigure(0, weight=1)
        self.btn_savcht = tkinter.Button(self.output_cheats_down_left_frame, text=self.loc_btn_map['SaveCHT'], width=10, command=self.sav_cht)
        self.btn_savcht.grid(row=0, column=0, sticky="nsew", padx=12)
        self.btn_savcht.config(state=DISABLED)
        self.btn_savnso = tkinter.Button(self.output_cheats_down_left_frame, text=self.loc_btn_map['SaveNSO'], width=10, command=self.sav_nso)
        self.btn_savnso.grid(row=0, column=1, sticky="nsew", padx=12)
        self.btn_savnso.config(state=DISABLED)
        # Output cheats down right frame
        self.output_cheats_down_right_frame = tkinter.Frame(self.output_cheats_down_frame)
        self.output_cheats_down_right_frame.pack(anchor='center', side='left', padx=5, pady=5)
        self.link = LinkLabel(self.output_cheats_down_right_frame, link=self.loc_btn_map['GitHub']).pack(side='left', padx=5, pady=5)

        # input_cheats_text right click window
        self.menu = tkinter.Menu(self.input_cheats_text, tearoff=0)
        self.menu.add_command(label=self.loc_btn_map['copy'], command=self.copy)
        self.menu.add_separator()
        self.menu.add_command(label=self.loc_btn_map['paste'], command=self.paste)
        self.menu.add_separator()
        self.menu.add_command(label=self.loc_btn_map['cut'], command=self.cut)
        self.input_cheats_text.bind("<Button-3>", self.popupmenu)

        # output_cheats_text right click window
        self.menuOut = tkinter.Menu(self.output_cheats_text, tearoff=0)
        self.menuOut.add_command(label="copy", command=self.copyOut)
        self.output_cheats_text.bind("<Button-3>", self.popupmenuOut)

        # Initialize parameters
        self.script_path = root_path
        self.log_path = os.path.join(self.script_path, 'log')
        self.back_path = os.path.join(self.script_path, 'back_up')
        self.tool_path = os.path.join(self.script_path, 'tools')
        #self.main_old_file = None
        self.old_is_NSO_file = False
        #self.main_new_file = None
        self.new_is_NSO_file = False
        self.stage_detail_json = {'raw':'','processed':'','step':{}}  # main pipeline, plz deepcopy then edit
        self.stage = 0  # cheat codes nums (title included)
        self.stage_max = 0
        self.step = 0  # process steps (one cheat codes contains multiple steps for asm codes)
        self.end_flag = False  # end_flag for the last code
        self.is_asm_title_part = True
        self.is_asm_finished = True
        self.asm_cache_json = {}
        self.bl_addr_and_target_addr = {}  # recorded in stage_detail_json
        self.bl_step = 0  # special inner step counts for asm part
        self.code_cave = {}

        self.mainWin.mainloop()

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

    def load_old_file(self):
        file_path = filedialog.askopenfilename(title=self.loc_hints_map['Load Old Main NSO File'], filetypes=[('All Files', '*')])
        self.old_file_entry.config(state=NORMAL)
        self.old_file_entry.delete(0, END)
        self.old_file_entry.insert('insert', file_path)
        self.old_file_entry.config(state=DISABLED)
        
        if file_path != '':
            self.main_old_file = Main_File(file_path)
            if not self.main_old_file.is_NSO_file():
                self.log_out('\n'.join(eval(self.loc_msg_map['NOT NSO File'])), False)
                self.old_is_NSO_file = False
                self.btn_enable_after_load(False)
                return
            if self.main_old_file.is_Compressed():
                file_name = file_path.split('/')[-1]
                try:
                    os.makedirs(self.back_path)
                except:
                    self.log_out('\n'.join(eval(self.loc_msg_map['DIR already exists'])), False)
                debug_path = os.path.join(self.script_path, 'back_up', f'{file_name}_old.bak')
                shutil.copyfile(file_path, debug_path)
                try:
                    if os.path.exists(os.path.join(self.tool_path, 'nsnsotool.exe')):
                        # os.system(f'cd tools && nsnsotool "{file_path}"')  # Hints: Recognized as virus by Windows Defender, pyinstaller -w or --noconsole to remove it
                        process = subprocess.Popen(["cmd"], shell=False, close_fds=True, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
                        commands = ('cd tools\n'
                                    f'nsnsotool "{file_path}"\n'
                                )
                        outs, errs = process.communicate(commands.encode('gbk'))
                        content = [z.strip() for z in outs.decode('gbk').split('\n') if z]
                        print(*content, sep="\n")
                    else:
                        messagebox.showerror(title='Error', message='\n'.join(eval(self.loc_msg_map['nsnsotool missing'])))
                        return
                except:
                    messagebox.showwarning(title='Warning', message='\n'.join(eval(self.loc_msg_map['nsnsotool warning'])))
                self.log_out('\n'.join(eval(self.loc_msg_map['NSO file decompressed'])), False)
            self.main_old_file.get_struct_from_file()
            self.main_old_file.get_mainfunc_file()
            self.old_is_NSO_file = True
            messagebox.showinfo(title='Info', message='\n'.join(eval(self.loc_msg_map['BID message'])))
            if self.new_is_NSO_file:
                self.btn_enable_after_load(True)
            if self.is_debug_mode.get():
                try:
                    os.makedirs(self.log_path)
                except:
                    print("DIR already exists.")
                print(self.main_old_file.to_Json(os.path.join(self.log_path, 'old_main_nso_info')))
            else:
                print(self.main_old_file.to_Json())
        else:
            self.btn_enable_after_load(False)
        return

    def load_new_file(self):
        file_path = filedialog.askopenfilename(title=self.loc_hints_map['Load New Main NSO File'], filetypes=[('All Files', '*')])
        self.new_file_entry.config(state=NORMAL)
        self.new_file_entry.delete(0, END)
        self.new_file_entry.insert('insert', file_path)
        self.new_file_entry.config(state=DISABLED)
        
        if file_path != '':
            self.main_new_file = Main_File(file_path)
            if not self.main_new_file.is_NSO_file():
                self.log_out('\n'.join(eval(self.loc_msg_map['NOT NSO File'])), False)
                self.new_is_NSO_file = False
                self.btn_enable_after_load(False)
                return
            if self.main_new_file.is_Compressed():
                file_name = file_path.split('/')[-1]
                try:
                    os.makedirs(self.back_path)
                except:
                    self.log_out('\n'.join(eval(self.loc_msg_map['DIR already exists'])), False)
                debug_path = os.path.join(self.script_path, 'back_up', f'{file_name}_new.bak')
                shutil.copyfile(file_path, debug_path)
                try:
                    if os.path.exists(os.path.join(self.tool_path, 'nsnsotool.exe')):
                        # os.system(f'cd tools && nsnsotool "{file_path}"')
                        process = subprocess.Popen(["cmd"], shell=False, close_fds=True, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
                        commands = ('cd tools\n'
                                    f'nsnsotool "{file_path}"\n'
                                )
                        outs, errs = process.communicate(commands.encode('gbk'))
                        content = [z.strip() for z in outs.decode('gbk').split('\n') if z]
                        print(*content, sep="\n")
                    else:
                        messagebox.showerror(title='Error', message='\n'.join(eval(self.loc_msg_map['nsnsotool missing'])))
                        return
                except:
                    messagebox.showwarning(title='Warning', message='\n'.join(eval(self.loc_msg_map['nsnsotool warning'])))
                self.log_out('\n'.join(eval(self.loc_msg_map['NSO file decompressed'])), False)
            self.main_new_file.get_struct_from_file()
            self.main_new_file.get_mainfunc_file()
            self.new_is_NSO_file = True
            if self.old_is_NSO_file:
                self.btn_enable_after_load(True)
            if self.is_debug_mode.get():
                try:
                    os.makedirs(self.log_path)
                except:
                    print("DIR already exists.")
                print(self.main_new_file.to_Json(os.path.join(self.log_path, 'new_main_nso_info')))
            else:
                print(self.main_new_file.to_Json())
        else:
            self.btn_enable_after_load(False)
        return

    def current_out(self, message: str, need_clear):
        self.current_cheats_text.config(state=NORMAL)
        if need_clear:
            self.current_cheats_text.delete(0.1, END)
        self.current_cheats_text.insert('insert', message)
        self.current_cheats_text.config(state=DISABLED)
        self.current_cheats_text.see(END)

    def log_out(self, message: str, need_clear):
        self.log_text.config(state=NORMAL)
        if need_clear:
            self.log_text.delete(0.1, END)
        self.log_text.insert('insert', f'[{time.asctime(time.localtime(time.time()))}] {message}\n')
        self.log_text.config(state=DISABLED)
        self.log_text.see(END)

    def output_out(self, message: str, need_clear):
        self.output_cheats_text.config(state=NORMAL)
        if need_clear:
            self.output_cheats_text.delete(0.1, END)
        self.output_cheats_text.insert('insert', message)
        self.output_cheats_text.config(state=DISABLED)
        self.output_cheats_text.see(END)

    def wing_length_out(self, message: str):
        self.wings_text.delete(0, END)
        self.wings_text.insert(0, message)

    def wing_length_out_re(self, msg: str, wing_type):  # better use decorator
    # wing_type: 0: normal, 1: bl addr, 2: bl target
        if wing_type == 0:
            self.wing_length_out(msg)
        else:
            wing_length_old = self.wings_text.get()
            pattern_int = re.compile(r'^ *(\d{1,}) *$')
            pattern_list = re.compile(r'^ *\[ *(\d{1,}) *, *(\d{1,}) *\] *$')
            wing_length_int = pattern_int.match(wing_length_old)
            wing_length_list = pattern_list.match(wing_length_old)
            wing_length_new = pattern_list.match(msg)
            if wing_length_new is not None:
                wing_side = max(eval(wing_length_new.group(1)), eval(wing_length_new.group(2)))
            else:
                wing_side = int(msg)
            if wing_type == 1:
                if wing_length_int is not None:  # single input will split into list
                    self.wing_length_out(f'[{wing_side}, {int(wing_length_int.group(1))}]')
                elif wing_length_list is not None:
                    self.wing_length_out(f'[{wing_side}, {eval(wing_length_list.group(2))}]')
            elif wing_type == 2:
                if wing_length_int is not None:
                    self.wing_length_out(f'[{int(wing_length_int.group(1))}, {wing_side}]')
                elif wing_length_list is not None:
                    self.wing_length_out(f'[{eval(wing_length_list.group(1))}, {wing_side}]')

    def old_ASM_text_out(self, message: list, high_light_line: list):
        self.old_ASM_text.config(state=NORMAL)
        self.old_ASM_text.delete(0.1, END)
        for index in range(len(message)):
            if int(high_light_line[0]) <= index <= int(high_light_line[1]):
                self.old_ASM_text.insert('insert', message[index]+'\n', 'high_light_old')
            else:
                self.old_ASM_text.insert('insert', message[index]+'\n')
        # Warning: text_window compressed, sometimes 'text.see()' doesn't work properly
        self.old_ASM_text.see(high_light_line[0])
        self.old_ASM_text.config(state=DISABLED)
        
    def new_ASM_text_out(self, message: list, high_light_line: list):
        self.new_ASM_text.config(state=NORMAL)
        self.new_ASM_text.delete(0.1, END)
        for index in range(len(message)):
            if int(high_light_line[0]) <= index <= int(high_light_line[1]):
                self.new_ASM_text.insert('insert', message[index]+'\n', 'high_light_new')
            else:
                self.new_ASM_text.insert('insert', message[index]+'\n')
        self.new_ASM_text.see(high_light_line[0])
        self.new_ASM_text.config(state=DISABLED)

    def btn_enable_after_load(self, is_btn_enabled: bool):
        if is_btn_enabled:
            self.btn_generate.config(state=NORMAL)
            self.btn_skip.config(state=DISABLED)
            self.btn_undo.config(state=DISABLED)
            self.btn_restart.config(state=DISABLED)
            self.btn_savcht.config(state=DISABLED)
            self.btn_savnso.config(state=DISABLED)
            self.btn_regenerate.config(state=DISABLED)
        else:
            self.btn_generate.config(state=DISABLED)
            self.btn_skip.config(state=DISABLED)
            self.btn_undo.config(state=DISABLED)
            self.btn_restart.config(state=DISABLED)
            self.btn_savcht.config(state=DISABLED)
            self.btn_savnso.config(state=DISABLED)
            self.btn_regenerate.config(state=DISABLED)

    def btn_enable_after_cur_cheat_gen(self, is_btn_enabled: bool):
        if is_btn_enabled:
            self.btn_generate.config(state=NORMAL)
            self.btn_skip.config(state=NORMAL)
            self.btn_undo.config(state=NORMAL)
            self.btn_restart.config(state=NORMAL)
            self.btn_savcht.config(state=NORMAL)
            self.btn_savnso.config(state=NORMAL)
            self.btn_regenerate.config(state=NORMAL)
        else:
            self.btn_generate.config(state=DISABLED)
            self.btn_skip.config(state=DISABLED)
            self.btn_undo.config(state=DISABLED)
            self.btn_restart.config(state=DISABLED)
            self.btn_savcht.config(state=DISABLED)
            self.btn_savnso.config(state=DISABLED)
            self.btn_regenerate.config(state=DISABLED)

    def pre_processing(self):
        is_splited = False
        text_line = self.input_cheats_text.get('1.0', END)
        text_line_list = re.split('\n', text_line)
        text_line_out = ''
        pattern_target_code = re.compile(r'^ *080([abcdef\d])0000 *([abcdef\d]{8}) *([abcdef\d]{8}) *([abcdef\d]{8}) *$', re.I)
        for text_line in text_line_list:
            pattern = pattern_target_code.match(text_line)
            if pattern is None:
                if text_line == '':
                    text_line_out += '\n'
                else:
                    text_line_out += text_line + '\n'
            else:
                text_line_out += f'040{pattern.group(1).upper()}0000 {pattern.group(2).upper()} {pattern.group(4).upper()}' + '\n'
                next_addr = hex(int(pattern.group(2), 16) + 4)[2:].zfill(8).upper()
                text_line_out += f'040{pattern.group(1).upper()}0000 {next_addr} {pattern.group(3).upper()}' + '\n'
                is_splited = True
        self.input_cheats_text.delete(0.1, END)
        self.input_cheats_text.insert('insert', text_line_out)
        if is_splited:
            messagebox.showinfo(title='Info', message='\n'.join(eval(self.loc_msg_map['Pre-process message'])))
        return

    def check_wings(self):
        wing_length_test = self.wings_text.get()
        pattern_int = re.compile(r'^ *(\d{1,}) *$')
        pattern_list = re.compile(r'^ *\[ *(\d{1,}) *, *(\d{1,}) *\] *$')
        wing_length_int = pattern_int.match(wing_length_test)
        wing_length_list = pattern_list.match(wing_length_test)
        if wing_length_int is not None:
            wing_length = int(wing_length_int.group(1))
        elif wing_length_list is not None:
            wing_length = [eval(wing_length_list.group(1)), eval(wing_length_list.group(2))]
        else:
            messagebox.showwarning(title='Warning', message='\n'.join(eval(self.loc_msg_map['Wing length check message'])))
            wing_length = eval(self.loc_wing_length_default)
            self.wings_text.delete(0, END)
            self.wings_text.insert(0, self.loc_wing_length_default)
        return wing_length
    
    def reset_wings(self):
        self.wings_text.delete(0, END)
        self.wings_text.insert(0, self.loc_wing_length_default)

    def check_extra_wings(self):
        wing_length_test = self.ASM_wings_text.get()
        pattern_int = re.compile(r'^ *(\d{1,}) *$')
        pattern_list = re.compile(r'^ *\[ *(\d{1,}) *, *(\d{1,}) *\] *$')
        wing_length_int = pattern_int.match(wing_length_test)
        wing_length_list = pattern_list.match(wing_length_test)
        if wing_length_int is not None:
            extra_wing_length = int(wing_length_int.group(1))
        elif wing_length_list is not None:
            extra_wing_length = [eval(wing_length_list.group(1)), eval(wing_length_list.group(2))]
        else:
            messagebox.showwarning(title='Warning Extend', message='\n'.join(eval(self.loc_msg_map['Extra wing length check message'])))
            extra_wing_length = eval(self.loc_extra_wing_length_default)
            self.ASM_wings_text.delete(0, END)
            self.ASM_wings_text.insert(0, self.loc_extra_wing_length_default)
        return extra_wing_length

    def check_line(self, cheat_line: str):
    # check one single line from cheat codes, filter format and return info
        pattern_code_title = re.compile(r'^ *(\[.*\]) *$')
        pattern_master_code_title = re.compile(r'^ *(\{.*\}) *$')
        pattern_code = re.compile(r'([abcdef\d]{8})', re.I)
        pattern_asm_code = re.compile(r'^0([48])0[abcdef\d]0000$', re.I)
        is_code_title = pattern_code_title.match(cheat_line)
        is_master_code_title = pattern_master_code_title.match(cheat_line)
        is_code = pattern_code.findall(cheat_line)
        if is_code_title is not None:
            return {
                'type': 'code_title',
                'contents': is_code_title.group(1)
            }
        elif is_master_code_title is not None:
            return {
                'type': 'master_code_title',
                'contents': is_master_code_title.group(1)
            }
        elif len(is_code) != 0 and len(is_code) <= 3:
            if pattern_asm_code.match(is_code[0]) is not None:
                asm_code_head = is_code[0]
                asm_code_addr = int(is_code[1], 16)
                asm_code_main = is_code[2]
                asm_code_disam = None
                is_asm_code = False
                is_code_cave = False
                is_bl = False
                jump_addr = 0
                bl_to_cave = False
                bl_to_outer = False
                bl_offset_to_main = 0
                bl_type = None
                Disassembler = Cs(CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN)
                code_bytes = bytearray.fromhex(asm_code_main)
                code_bytes.reverse()
                for i in Disassembler.disasm(code_bytes, asm_code_addr):
                    is_asm_code = True
                    asm_code_disam = ("0x%x:\t%s\t%s" %(i.address, i.mnemonic, i.op_str))
                    if (asm_code_addr >= int.from_bytes(self.main_old_file.codeCaveStart, byteorder='big', signed=False)
                    and asm_code_addr < int.from_bytes(self.main_old_file.codeCaveEnd, byteorder='big', signed=False)):
                        is_code_cave = True
                    if i.mnemonic == 'bl' or i.mnemonic == 'b' or ('b.' in i.mnemonic):
                        is_bl = True
                        bl_type = i.mnemonic
                        jump_addr = int(i.op_str[1:], 16)
                        if (jump_addr >= int.from_bytes(self.main_old_file.codeCaveStart, byteorder='big', signed=False)
                        and jump_addr < int.from_bytes(self.main_old_file.codeCaveEnd, byteorder='big', signed=False)):
                            bl_to_cave = True
                        if jump_addr >= int.from_bytes(self.main_old_file.rodataMemoryOffset, byteorder='big', signed=False):
                            bl_to_outer = True
                            bl_offset_to_main = jump_addr - int.from_bytes(self.main_old_file.textMemoryOffset, byteorder='big', signed=False)
                if is_asm_code:
                    return {
                            'type': 'code',
                            'contents':
                            {
                                'code_type': 'ASM',
                                'memory_width': 4,
                                'is_code_cave': is_code_cave,
                                'is_bl': is_bl,
                                'bl_type': bl_type,
                                'bl_addr': jump_addr,
                                'bl_to_cave': bl_to_cave,
                                'bl_to_outer': bl_to_outer,
                                'bl_offset_to_main': bl_offset_to_main,
                                'code_head': asm_code_head,
                                'code_addr': asm_code_addr,
                                'code_main': asm_code_main,
                                'code_disam': asm_code_disam,
                                'code_raw': is_code
                            }
                    }
                else:
                    return {
                            'type': 'code',
                            'contents': 
                            {
                                'code_type': 'Normal',
                                'code_raw': is_code
                            }
                    }
            else:
                return {
                    'type': 'code',
                    'contents': 
                    {
                        'code_type': 'Normal',
                        'code_raw': is_code
                    }
                }
        else:
            return {
                'type': 'unknown',
                'contents': cheat_line
            }

    def generate_cheats_script_json(self):
        cheats_script_json = {}
        cheats_count = 0
        input_cheats_list = []
        input_cheats_list = re.split('\n', self.input_cheats_text.get('1.0', END))
        input_cheats_list = [i for i in input_cheats_list if (not i.isspace() and i != '')]
        for line in input_cheats_list[::-1]:
            if self.check_line(line)['type'] == 'unknown':
                if not (line.isspace() or line ==''):
                    messagebox.showwarning(title='Warning', message='\n'.join(eval(self.loc_msg_map['Unknown cheat format'])))
                input_cheats_list.remove(line)

        title_cache = []
        code_cache = []
        json_code_cache = {}
        code_type = ''
        has_asm_code = False
        input_cheats_list_cache = []
        # remove codes without title
        for index in range(len(input_cheats_list)):
            if self.check_line(input_cheats_list[index])['type'] != 'code':
                input_cheats_list_cache = input_cheats_list[index:]
                break
        input_cheats_list = input_cheats_list_cache
        input_cheats_list_property = list(map(lambda x:0 if self.check_line(x)['type'] != 'code' else 1, input_cheats_list))
        # find title
        try:
            index = input_cheats_list_property.index(1)
            if index != 1:
                json_cache = {
                        f'{cheats_count}':
                            {
                                'type': 'title',
                                'contents': input_cheats_list[:(index-1)]
                            }
                        }
                input_cheats_list = input_cheats_list[(index-1):]
                input_cheats_list_property = input_cheats_list_property[(index-1):]
                cheats_script_json.update(json_cache)
                cheats_count += 1
            else:
                pass
        except:
            if len(input_cheats_list) != 0:
                json_cache = {
                        f'{cheats_count}':
                            {
                                'type': 'title',
                                'contents': input_cheats_list
                            }
                        }
                input_cheats_list = []
                input_cheats_list_property = []
                cheats_script_json.update(json_cache)
                cheats_count += 1

        while len(input_cheats_list) != 0:
            try:
                index = input_cheats_list_property.index(1)
                title_cache = input_cheats_list[:index]
                input_cheats_list = input_cheats_list[index:]
                input_cheats_list_property = input_cheats_list_property[index:]
                try:
                    index = input_cheats_list_property.index(0)
                    code_cache = input_cheats_list[:index]
                    input_cheats_list = input_cheats_list[index:]
                    input_cheats_list_property = input_cheats_list_property[index:]
                except:
                    code_cache = input_cheats_list
                    input_cheats_list = []
                    input_cheats_list_property = []
                code_type = self.check_line(title_cache[-1])['type']
                json_asm_combine_code_cache = {}
                searching_next_flag = False
                current_index = 0
                for index in range(len(code_cache)):
                    code_json = self.check_line(code_cache[index])

                    if code_json['contents']['code_type'] != 'ASM':
                        if searching_next_flag == True:
                            json_code_cache.update(json_asm_combine_code_cache)
                            json_asm_combine_code_cache = {}
                            searching_next_flag = False
                        json_code_cache.update(
                            {f'{index}': {
                                'code_type': 'Normal',
                                'contents':
                                    {
                                        'code_raw': code_cache[index]
                                    }
                                }
                            }
                        )
                    elif code_json['contents']['code_type'] == 'ASM':
                        has_asm_code = True
                        code = ''.join(code_json['contents']['code_main'])
                        code_bytes = bytearray.fromhex(code)
                        code_bytes.reverse()
                        if searching_next_flag == False:
                            json_asm_combine_code_cache.update(
                                {f'{index}': {
                                    'code_type': 'ASM',
                                    'contents':
                                        {
                                            'is_code_cave': code_json['contents']['is_code_cave'],
                                            'is_bl': code_json['contents']['is_bl'],
                                            'bl_type': code_json['contents']['bl_type'],
                                            'bl_addr': code_json['contents']['bl_addr'],
                                            'bl_to_cave': code_json['contents']['bl_to_cave'],
                                            'bl_to_outer': code_json['contents']['bl_to_outer'],
                                            'bl_offset_to_main': code_json['contents']['bl_offset_to_main'],
                                            'base_addr': code_json['contents']['code_addr'],
                                            'next_addr': code_json['contents']['code_addr'] + int(code_json['contents']['memory_width']),
                                            'code_bytes': code_bytes,
                                            'offset': [code_json['contents']['memory_width']],
                                            'code_head': [code_json['contents']['code_head']],
                                            'code_addr': [code_json['contents']['code_addr']],
                                            'code_main': [code_json['contents']['code_main']],
                                            'code_disam': [code_json['contents']['code_disam']],
                                            'code_raw': [code_json['contents']['code_raw']]
                                        }
                                    }
                                }
                            )
                            searching_next_flag = True
                            current_index = index
                        elif (json_asm_combine_code_cache[f'{current_index}']['contents']['next_addr'] == code_json['contents']['code_addr'] 
                        and json_asm_combine_code_cache[f'{current_index}']['contents']['is_code_cave'] == code_json['contents']['is_code_cave']
                        and not json_asm_combine_code_cache[f'{current_index}']['contents']['is_bl']
                        and not code_json['contents']['is_bl']
                        ):
                            json_asm_combine_code_cache[f'{current_index}']['contents']['next_addr'] = (
                                json_asm_combine_code_cache[f'{current_index}']['contents']['next_addr'] +
                                int(code_json['contents']['memory_width'])
                            )
                            json_asm_combine_code_cache[f'{current_index}']['contents']['code_bytes'] += code_bytes
                            json_asm_combine_code_cache[f'{current_index}']['contents']['offset'].append(code_json['contents']['memory_width'])
                            json_asm_combine_code_cache[f'{current_index}']['contents']['code_head'].append(code_json['contents']['code_head'])
                            json_asm_combine_code_cache[f'{current_index}']['contents']['code_addr'].append(code_json['contents']['code_addr'])
                            json_asm_combine_code_cache[f'{current_index}']['contents']['code_main'].append(code_json['contents']['code_main'])
                            json_asm_combine_code_cache[f'{current_index}']['contents']['code_disam'].append(code_json['contents']['code_disam'])
                            json_asm_combine_code_cache[f'{current_index}']['contents']['code_raw'].append(code_json['contents']['code_raw'])
                        else:
                            json_code_cache.update(json_asm_combine_code_cache)
                            json_asm_combine_code_cache = {}
                            json_asm_combine_code_cache.update(
                                {f'{index}': {
                                    'code_type': 'ASM',
                                    'contents':
                                        {
                                            'is_code_cave': code_json['contents']['is_code_cave'],
                                            'is_bl': code_json['contents']['is_bl'],
                                            'bl_type': code_json['contents']['bl_type'],
                                            'bl_addr': code_json['contents']['bl_addr'],
                                            'bl_to_cave': code_json['contents']['bl_to_cave'],
                                            'bl_to_outer': code_json['contents']['bl_to_outer'],
                                            'bl_offset_to_main': code_json['contents']['bl_offset_to_main'],
                                            'base_addr': code_json['contents']['code_addr'],
                                            'next_addr': code_json['contents']['code_addr'] + int(code_json['contents']['memory_width']),
                                            'code_bytes': code_bytes,
                                            'offset': [code_json['contents']['memory_width']],
                                            'code_head': [code_json['contents']['code_head']],
                                            'code_addr': [code_json['contents']['code_addr']],
                                            'code_main': [code_json['contents']['code_main']],
                                            'code_disam': [code_json['contents']['code_disam']],
                                            'code_raw': [code_json['contents']['code_raw']]
                                        }
                                    }
                                }
                            )
                            current_index = index

                if searching_next_flag == True:
                    json_code_cache.update(json_asm_combine_code_cache)
                    json_asm_combine_code_cache = {}
                    searching_next_flag = False
                current_index = 0
                json_cache = {
                        f'{cheats_count}':
                            {
                                'type': 'code' if code_type == 'code_title' else 'master_code',
                                'contents':
                                {
                                    'title': title_cache,
                                    'has_asm_code': has_asm_code,
                                    'codes': json_code_cache
                                }
                            }
                        }
                
                # modify code index from "1, 4, 7" to "1, 2, 3"
                _index = 0
                _dict_single_cheat = {}
                for key in json_cache[str(cheats_count)]['contents']['codes']:
                    _dict_single_cheat.update({str(_index):json_cache[str(cheats_count)]['contents']['codes'][key]})
                    _index += 1
                json_cache[str(cheats_count)]['contents']['codes'] = deepcopy(_dict_single_cheat)

                # record branch index for the new json
                for key in json_cache[str(cheats_count)]['contents']['codes']:
                    json_cache[str(cheats_count)]['contents']['codes'][key]['contents']['bl_line'] = None
                    json_cache[str(cheats_count)]['contents']['codes'][key]['contents']['bl_shift'] = 0
                    if json_cache[str(cheats_count)]['contents']['codes'][key]['code_type'] == 'ASM':
                        if json_cache[str(cheats_count)]['contents']['codes'][key]['contents']['is_bl']:
                            bl_addr = json_cache[str(cheats_count)]['contents']['codes'][key]['contents']['bl_addr']
                            has_bl_link = False
                            for inner_key in json_cache[str(cheats_count)]['contents']['codes']:
                                if json_cache[str(cheats_count)]['contents']['codes'][inner_key]['code_type'] == 'ASM':
                                    if (bl_addr >= json_cache[str(cheats_count)]['contents']['codes'][inner_key]['contents']['base_addr'] and
                                        bl_addr < json_cache[str(cheats_count)]['contents']['codes'][inner_key]['contents']['next_addr']):
                                        bl_line = int(inner_key)
                                        bl_shift = int((bl_addr - json_cache[str(cheats_count)]['contents']['codes'][inner_key]['contents']['base_addr'])/4)
                                        json_cache[str(cheats_count)]['contents']['codes'][key]['contents']['bl_line'] = bl_line
                                        json_cache[str(cheats_count)]['contents']['codes'][key]['contents']['bl_shift'] = bl_shift
                                        has_bl_link = True
                                        break
                            if not has_bl_link:
                                json_cache[str(cheats_count)]['contents']['codes'][key]['contents']['bl_line'] = None
                                json_cache[str(cheats_count)]['contents']['codes'][key]['contents']['bl_shift'] = 0

                cheats_script_json.update(json_cache)
                cheats_count += 1
                title_cache = []
                code_cache = []
                json_code_cache = {}
                code_type = ''
                has_asm_code = False
            except:
                json_cache = {
                    f'{cheats_count}':
                        {
                            'type': 'comments',
                            'contents': input_cheats_list
                        }
                    }
                input_cheats_list = []
                input_cheats_list_property = []
                cheats_script_json.update(json_cache)
                cheats_count += 1

        print(cheats_script_json)
        return cheats_script_json

    def find_addr(self, addr_range, wing_length):
        json_bytes_feature = find_bytes_feature(self.main_old_file.mainFuncFile, addr_range, wing_length)
        bytes_feature = bytes(bytearray.fromhex(json_bytes_feature["bytes_feature"]))
        hit_start_addr = bytesarray_refindall(self.main_new_file.mainFuncFile, bytes_feature)
        hit_start_addr = list(map(lambda x:hex(x+int(json_bytes_feature["taget_start_offset"],16)), hit_start_addr))
        return hit_start_addr

    def find_addr_re(self, addr_range, wing_length, wing_type):  # massive decrease search when no addr find is meaningless
        json_bytes_feature = find_bytes_feature(self.main_old_file.mainFuncFile, addr_range, wing_length)
        bytes_feature = bytes(bytearray.fromhex(json_bytes_feature["bytes_feature"]))
        hit_start_addr = bytesarray_refindall(self.main_new_file.mainFuncFile, bytes_feature)
        if isinstance(wing_length, int):
            hit_end_addr = list(map(lambda x:x+int(json_bytes_feature["taget_end_offset"],16)+wing_length*4, hit_start_addr))
        else:
            hit_end_addr = list(map(lambda x:x+int(json_bytes_feature["taget_end_offset"],16)+wing_length[1]*4, hit_start_addr))

        wing_step = 1  # recovery rate
        left_side_available = True
        right_side_available = True

        if len(hit_start_addr) != 0:
            while len(hit_start_addr) != 1:
                if isinstance(wing_length, int):
                    hit_start_addr_next = []
                    hit_end_addr_next = []
                    wing_length_next = wing_length
                    wing_length_next += wing_step  # check both
                    for index in range(len(hit_start_addr)):
                        bytes_file = self.main_new_file.mainFuncFile[hit_start_addr[index]-wing_step*4 : hit_end_addr[index]+wing_step*4]
                        if self.check_addr(addr_range, wing_length_next, bytes_file):
                            hit_start_addr_next.append(hit_start_addr[index]-wing_step*4)
                            hit_end_addr_next.append(hit_end_addr[index]+wing_step*4)
                        else:
                            pass
                    if len(hit_start_addr_next) != 0:
                        hit_start_addr = deepcopy(hit_start_addr_next)
                        hit_end_addr = deepcopy(hit_end_addr_next)
                        wing_length = wing_length_next
                        self.wing_length_out_re(str(wing_length), wing_type)
                        if len(hit_start_addr_next) == 1:
                            # log_out('Single address found.')
                            break
                    else:
                        break
                else:
                    if left_side_available:
                        hit_start_addr_next = []
                        hit_end_addr_next = []
                        wing_length_next = deepcopy(wing_length)
                        wing_length_next[0] += wing_step  # check left
                        for index in range(len(hit_start_addr)):
                            bytes_file = self.main_new_file.mainFuncFile[hit_start_addr[index]-wing_step*4 : hit_end_addr[index]]
                            if self.check_addr(addr_range, wing_length_next, bytes_file):
                                hit_start_addr_next.append(hit_start_addr[index]-wing_step*4)
                                hit_end_addr_next.append(hit_end_addr[index])
                            else:
                                pass
                        if len(hit_start_addr_next) != 0:
                            hit_start_addr = deepcopy(hit_start_addr_next)
                            hit_end_addr = deepcopy(hit_end_addr_next)
                            wing_length = deepcopy(wing_length_next)
                            self.wing_length_out_re(f'[{wing_length[0]}, {wing_length[1]}]', wing_type)
                            if len(hit_start_addr_next) == 1:
                                # log_out('Single address found.')
                                break
                        else:
                            left_side_available = False

                    if right_side_available:
                        hit_start_addr_next = []
                        hit_end_addr_next = []
                        wing_length_next = deepcopy(wing_length)
                        wing_length_next[1] += wing_step  # check right
                        for index in range(len(hit_start_addr)):
                            bytes_file = self.main_new_file.mainFuncFile[hit_start_addr[index] : hit_end_addr[index]+wing_step*4]
                            if self.check_addr(addr_range, wing_length_next, bytes_file):
                                hit_start_addr_next.append(hit_start_addr[index])
                                hit_end_addr_next.append(hit_end_addr[index]+wing_step*4)
                            else:
                                pass
                        if len(hit_start_addr_next) != 0:
                            hit_start_addr = deepcopy(hit_start_addr_next)
                            hit_end_addr = deepcopy(hit_end_addr_next)
                            wing_length = deepcopy(wing_length_next)
                            self.wing_length_out_re(f'[{wing_length[0]}, {wing_length[1]}]', wing_type)
                            if len(hit_start_addr_next) == 1:
                                # log_out('Single address found.')
                                break
                        else:
                            right_side_available = False
                    
                    if not left_side_available and not right_side_available:
                        break
              
        if isinstance(wing_length, int):
            hit_code_start_addr = list(map(lambda x:hex(x+wing_length*4), hit_start_addr))
        else:
            hit_code_start_addr = list(map(lambda x:hex(x+wing_length[0]*4), hit_start_addr))
       
        return hit_code_start_addr
    
    def check_addr(self, addr_range, wing_length, bytes_file):
        json_bytes_feature = find_bytes_feature(self.main_old_file.mainFuncFile, addr_range, wing_length)
        bytes_feature = bytes(bytearray.fromhex(json_bytes_feature["bytes_feature"]))
        hit_start_addr = bytesarray_refindall(bytes_file, bytes_feature)
        if len(hit_start_addr) == 0:
            return False
        else:
            return True

    def generate_current_output(self, cheats_json):
        raw_cache = []
        for raw in cheats_json['code_raw']:
            raw_cache.append(' '.join(raw))
        return (
            '=========== ORG ===========\n' +
            '\n'.join(raw_cache) +
            '\n\n\n' + '=========== ASM ===========\n' +
            '\n'.join(cheats_json['code_disam'])
        )

    def reset_middle_ASM_state(self):
        self.old_ASM_text.config(state=NORMAL)
        self.old_ASM_text.delete(0.1, END)
        self.old_ASM_text.config(state=DISABLED)
        self.new_ASM_text.config(state=NORMAL)
        self.new_ASM_text.delete(0.1, END)
        self.new_ASM_text.config(state=DISABLED)
        self.ASM_wings_text.delete(0, END)
        self.ASM_wings_text.insert(0, self.loc_extra_wing_length_default)
        self.btn_update.config(state=DISABLED)
        self.btn_prev_addr.config(state=DISABLED)
        self.btn_next_addr.config(state=DISABLED)
        self.is_check_branch = False
        self.branch_checkbox.deselect()
        self.branch_checkbox.config(state=DISABLED)

    def update_middle_ASM_output(self, _asm_cache_json, update_type):
    # update_type: 0: current, 1: previous, 2: next, 3: update
        if update_type == 0:
            self.reset_middle_ASM_state()  # refresh undo state

        org_addr = _asm_cache_json['contents']['org_addr']
        bl_org_addr = _asm_cache_json['contents']['bl_org_addr']
        hit_addr = _asm_cache_json['contents']['hit_addr']
        addr_chosen = _asm_cache_json['contents']['addr_chosen']
        bl_target_hit_addr = _asm_cache_json['contents']['bl_target_hit_addr']
        bl_target_addr_chosen = _asm_cache_json['contents']['bl_target_addr_chosen']
        wing_length = _asm_cache_json['contents']['wing_length']
        bl_target_wing_length = _asm_cache_json['contents']['bl_target_wing_length']
        extra_wing_length = self.check_extra_wings()  # for update button

        if bl_target_addr_chosen is None and addr_chosen is None:
            return

        if type(wing_length) == int:
             wing_length = [wing_length, wing_length]
        if type(bl_target_wing_length) == int:
             bl_target_wing_length = [bl_target_wing_length, bl_target_wing_length]

        if type(extra_wing_length) == int:
            extra_wing_length = [extra_wing_length, extra_wing_length]
        if ((bl_target_addr_chosen is not None and addr_chosen is None) or  # only bl target
        (bl_target_addr_chosen is not None and addr_chosen is not None and self.is_check_branch)):  # both but choose bl
            if bl_target_addr_chosen is not None and addr_chosen is None:
                self.is_check_branch = True
                self.branch_checkbox.select()
                self.branch_checkbox.config(state=DISABLED)
            else:
                self.is_check_branch = True
                self.branch_checkbox.select()
                self.branch_checkbox.config(state=NORMAL)
            if len(bl_target_hit_addr) > 1:  
                self.btn_prev_addr.config(state=NORMAL)
                self.btn_next_addr.config(state=NORMAL)
            else:
                self.btn_prev_addr.config(state=DISABLED)
                self.btn_next_addr.config(state=DISABLED)
            self.btn_update.config(state=NORMAL)
            org_wing_range = [bl_org_addr[0]-(bl_target_wing_length[0]+extra_wing_length[0])*4,
                    bl_org_addr[1]+(bl_target_wing_length[1]+extra_wing_length[1])*4,
                ]  # Warning: no boundary detection

            if update_type == 1:
                bl_target_addr_chosen = (bl_target_addr_chosen-1)%len(bl_target_hit_addr)
            elif update_type == 2:
                bl_target_addr_chosen = (bl_target_addr_chosen+1)%len(bl_target_hit_addr)

            bl_target_hit_start_addr = int(bl_target_hit_addr[bl_target_addr_chosen], 16)
            
            _asm_cache_json['contents']['bl_target_addr_chosen'] = bl_target_addr_chosen
            _asm_cache_json['contents']['bl_addr'] = bl_target_hit_start_addr

            tag_wing_range = [bl_target_hit_start_addr-(bl_target_wing_length[0]+extra_wing_length[0])*4,
                            (bl_target_hit_start_addr+4)+(bl_target_wing_length[1]+extra_wing_length[1])*4,
                        ]  # Warning: no boundary detection
            
            high_light_line = [float(bl_target_wing_length[0] + extra_wing_length[0]),  # bl has only one line
                                float(bl_target_wing_length[0] + extra_wing_length[0])]


        if ((bl_target_addr_chosen is None and addr_chosen is not None) or  # only asm
        (bl_target_addr_chosen is not None and addr_chosen is not None and not self.is_check_branch)):  # both but choose asm
            if bl_target_addr_chosen is None and addr_chosen is not None:
                self.is_check_branch = False
                self.branch_checkbox.deselect()
                self.branch_checkbox.config(state=DISABLED)
            else:
                self.is_check_branch = False
                self.branch_checkbox.deselect()
                self.branch_checkbox.config(state=NORMAL)
            if len(hit_addr) > 1:  
                self.btn_prev_addr.config(state=NORMAL)
                self.btn_next_addr.config(state=NORMAL)
            else:
                self.btn_prev_addr.config(state=DISABLED)
                self.btn_next_addr.config(state=DISABLED)
            self.btn_update.config(state=NORMAL)

            org_wing_range = [org_addr[0]-(wing_length[0]+extra_wing_length[0])*4,
                            org_addr[1]+(wing_length[1]+extra_wing_length[1])*4,
                        ]  # Warning: no boundary detection

            if update_type == 1:
                addr_chosen = (addr_chosen-1)%len(hit_addr)
            elif update_type == 2:
                addr_chosen = (addr_chosen+1)%len(hit_addr)

            hit_start_addr = int(hit_addr[addr_chosen], 16)
            
            _asm_cache_json['contents']['addr_chosen'] = addr_chosen
            _asm_cache_json['contents']['base_addr'] = hit_start_addr
            _high_light_count = 0
            for _index in range(len(_asm_cache_json['contents']['offset'])):
                _asm_cache_json['contents']['code_addr'][_index] = hex(hit_start_addr)[2:].zfill(8).upper()
                hit_start_addr += _asm_cache_json['contents']['offset'][_index]
                _high_light_count += 1
            _asm_cache_json['contents']['next_addr'] = hit_start_addr

            tag_wing_range = [int(hit_addr[addr_chosen], 16)-(wing_length[0]+extra_wing_length[0])*4,
                            hit_start_addr+(wing_length[1]+extra_wing_length[1])*4,
                        ]  # Warning: no boundary detection
            
            high_light_line = [float(wing_length[0] + extra_wing_length[0]),
                                float(wing_length[0] + extra_wing_length[0] + _high_light_count - 1)]

        self.old_ASM_text_out(get_ASM_code(self.main_old_file.mainFuncFile, org_wing_range), high_light_line)
        self.new_ASM_text_out(get_ASM_code(self.main_new_file.mainFuncFile, tag_wing_range), high_light_line)

        return _asm_cache_json

    def process(self, is_skip: bool):
        if not is_skip:
            if self.step == 0:  # pre-process & restart everthing
                self.pre_processing()
                self.stage_detail_json = {'raw':'','processed':'','step':{}}
                self.stage = 0
                self.end_flag = False
                if self.input_cheats_text.get('1.0', END) == '\n':
                    return
                cheats_script_json = self.generate_cheats_script_json()
                self.stage_detail_json['raw'] = self.input_cheats_text.get('1.0', END)
                self.stage_detail_json['processed'] = cheats_script_json
                self.stage_max = len(cheats_script_json)
                self.input_cheats_text.config(state=DISABLED)
                self.bl_addr_and_target_addr = {}
                self.bl_step = 0
                self.btn_enable_after_cur_cheat_gen(True)
                self.reset_wings()
                if int.from_bytes(self.main_new_file.codeCaveEnd, byteorder='big', signed=False) > int.from_bytes(self.main_new_file.codeCaveStart, byteorder='big', signed=False):
                    self.code_cave = [int.from_bytes(self.main_new_file.codeCaveStart, byteorder='big', signed=False),
                    int.from_bytes(self.main_new_file.codeCaveEnd, byteorder='big', signed=False)]
                else:
                    self.code_cave = None

        if self.step > 0 and self.end_flag == False:  # output procedure
            if not is_skip:
                if self.stage >= self.stage_max:
                    self.end_flag = True
                if self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['type'] == 'title':
                    self.output_out(self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['contents'] + '\n\n', False)
                elif self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['type'] == 'normal_code':
                    self.output_out(self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['contents']['title'] + 
                    '\n' + (self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['contents']['codes']).upper() + '\n\n', False)
                elif self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['type'] == 'asm_title':
                    self.output_out(self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['contents']['current_out_text'] + '\n', False)
                else:
                    is_shown = True
                    self.bl_addr_and_target_addr = deepcopy(self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['contents']['bl_addr_and_target_addr'])
                    _bl_step = self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['contents']['bl_step'] - 1
                    if self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['type'] == 'asm_normal_code':
                        self.output_out((self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['contents']['current_out_text'] + '\n').upper(), False)
                        self.bl_addr_and_target_addr[list(self.bl_addr_and_target_addr)[-1]]['contents']['is_shown'] = is_shown
                        self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['contents']['bl_addr_and_target_addr'] = deepcopy(self.bl_addr_and_target_addr)
                    elif (self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['type'] == 'asm_cave_code'
                        or self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['type'] == 'asm_normal_asm_code'):
                        if not self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['contents']['is_generate_button_discard']:
                            code_line = ''
                            _asm_cache_json = deepcopy(self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['contents']['bl_addr_and_target_addr'])
                            _asm_cache_json = deepcopy(_asm_cache_json[list(_asm_cache_json)[-1]])
                            for index in range(len(_asm_cache_json['contents']['code_head'])):
                                code_line += (_asm_cache_json['contents']['code_head'][index] + ' ' +
                                    _asm_cache_json['contents']['code_addr'][index] + ' ' +
                                    _asm_cache_json['contents']['code_main'][index]) + '\n'
                            code_line = code_line[:-1].upper()
                            if len(self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['contents']['asm_cache_json']) == 0:
                                code_line += '\n'
                            self.output_out(code_line + '\n', False)
                        else:
                            is_shown = False
                        self.bl_addr_and_target_addr[str(_bl_step)]['contents']['is_shown'] = is_shown
                        self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['contents']['bl_addr_and_target_addr'] = deepcopy(self.bl_addr_and_target_addr)
                    
                    elif (self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['type'] == 'asm_bl_code'
                        or self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['type'] == 'asm_bl_cave_code'):
                        if not self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['contents']['is_generate_button_discard']:
                            code_line = ''
                            _asm_cache_json = deepcopy(self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['contents']['bl_addr_and_target_addr'])
                            _asm_cache_json = deepcopy(_asm_cache_json[list(_asm_cache_json)[-1]])
                            for index in range(len(_asm_cache_json['contents']['code_head'])):
                                code_line += (_asm_cache_json['contents']['code_head'][index] + ' ' +
                                    _asm_cache_json['contents']['code_addr'][index] + ' ' +
                                    'xxxxxxxx') + '\n'
                            code_line = code_line[:-1].upper()
                            if len(self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['contents']['asm_cache_json']) == 0:
                                code_line += '\n'
                            self.output_out(code_line + '\n', False)
                        else:
                            is_shown = False
                        self.bl_addr_and_target_addr[str(_bl_step)]['contents']['is_shown'] = is_shown
                        self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['contents']['bl_addr_and_target_addr'] = deepcopy(self.bl_addr_and_target_addr)
                    
                    if len(self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['contents']['asm_cache_json']) == 0:
                        output_text_previous = self.output_cheats_text.get('1.0', END)
                        try:
                            code_start_index_master = output_text_previous.rindex('}')
                        except:
                            code_start_index_master = 0
                        try:
                            code_start_index_normal = output_text_previous.rindex(']')
                        except:
                            code_start_index_normal = 0
                        code_start_index = max(code_start_index_master, code_start_index_normal) + 1
                        output_text_previous = output_text_previous[:(code_start_index+1)]
                        new_code = create_bl_links(self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['contents']['bl_addr_and_target_addr'])
                        output_text_now = output_text_previous + new_code
                        self.output_out(output_text_now, True)
                        self.bl_step = 0
                        self.bl_addr_and_target_addr = {}
            else:
                if self.stage >= self.stage_max:
                    self.end_flag = True
                if self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['type'] == 'title':
                    pass
                elif self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['type'] == 'normal_code':
                    self.output_out(self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['contents']['title'] + '\n\n', False)
                elif self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['type'] == 'asm_title':
                    self.output_out(self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['contents']['current_out_text'] + '\n', False)
                else:
                    is_shown = True
                    self.bl_addr_and_target_addr = deepcopy(self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['contents']['bl_addr_and_target_addr'])
                    _bl_step = self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['contents']['bl_step'] - 1
                    if self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['type'] == 'asm_normal_code':
                        is_shown = False
                        self.bl_addr_and_target_addr[list(self.bl_addr_and_target_addr)[-1]]['contents']['is_shown'] = is_shown
                        self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['contents']['bl_addr_and_target_addr'] = deepcopy(self.bl_addr_and_target_addr)
                    elif (self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['type'] == 'asm_cave_code'
                        or self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['type'] == 'asm_normal_asm_code'):
                        is_shown = False
                        self.bl_addr_and_target_addr[str(_bl_step)]['contents']['is_shown'] = is_shown
                        self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['contents']['bl_addr_and_target_addr'] = deepcopy(self.bl_addr_and_target_addr)
                    elif (self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['type'] == 'asm_bl_code'
                        or self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['type'] == 'asm_bl_cave_code'):
                        is_shown = False
                        self.bl_addr_and_target_addr[str(_bl_step)]['contents']['is_shown'] = is_shown
                        self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['contents']['bl_addr_and_target_addr'] = deepcopy(self.bl_addr_and_target_addr)
                    
                    if len(self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['contents']['asm_cache_json']) == 0:
                        output_text_previous = self.output_cheats_text.get('1.0', END)
                        try:
                            code_start_index_master = output_text_previous.rindex('}')
                        except:
                            code_start_index_master = 0
                        try:
                            code_start_index_normal = output_text_previous.rindex(']')
                        except:
                            code_start_index_normal = 0
                        code_start_index = max(code_start_index_master, code_start_index_normal) + 1
                        output_text_previous = output_text_previous[:(code_start_index+1)]
                        new_code = create_bl_links(self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['contents']['bl_addr_and_target_addr'])
                        output_text_now = output_text_previous + new_code
                        self.output_out(output_text_now, True)
                        self.bl_step = 0
                        self.bl_addr_and_target_addr = {}

        if self.stage < self.stage_max:  # inner processing
            if self.stage_detail_json['processed'][str(self.stage)]['type'] != 'code' and self.stage_detail_json['processed'][str(self.stage)]['type'] != 'master_code':  # not code
                current_text_type = 'title'  # 'comments' included
                current_out_text = '\n'.join(self.stage_detail_json['processed'][str(self.stage)]['contents'])
                current_out_json = current_out_text
                self.current_out(current_out_text, True)
                log_out_text = '\n'.join(eval(self.loc_msg_map['no_code']))
                self.log_out(log_out_text, True)
                self.reset_middle_ASM_state()
                self.reset_wings()
                self.stage += 1
            elif not self.stage_detail_json['processed'][str(self.stage)]['contents']['has_asm_code']:  # code but no asm (master code equals code here)
                current_text_type = 'normal_code'
                code_cache = []
                for index in range(len(self.stage_detail_json['processed'][str(self.stage)]['contents']['codes'])):
                    code_cache.append(self.stage_detail_json['processed'][str(self.stage)]['contents']['codes'][str(index)]['contents']['code_raw'])
                current_out_json = {
                    'title': '\n'.join(self.stage_detail_json['processed'][str(self.stage)]['contents']['title']),
                    'codes': '\n'.join(code_cache),
                    'code_cave': deepcopy(self.code_cave)
                }
                current_out_text = current_out_json['title'] + '\n' + current_out_json['codes']
                self.current_out(current_out_text, True)
                log_out_text = '\n'.join(eval(self.loc_msg_map['code_but_no_asm']))
                self.log_out(log_out_text, True)
                self.reset_middle_ASM_state()
                self.reset_wings()
                self.stage += 1
            else:  # asm code
                if self.is_asm_title_part:
                    self.bl_step = 0
                    self.bl_addr_and_target_addr = {}
                    self.asm_cache_json = deepcopy(self.stage_detail_json['processed'][str(self.stage)]['contents']['codes'])
                    self.is_asm_title_part = False
                    self.is_asm_finished = False
                    current_text_type = 'asm_title'
                    current_out_text = '\n'.join(self.stage_detail_json['processed'][str(self.stage)]['contents']['title'])
                    current_out_json = {
                        'current_out_text': current_out_text,
                        'asm_cache_json': deepcopy(self.stage_detail_json['processed'][str(self.stage)]['contents']['codes']),
                        'bl_addr_and_target_addr': deepcopy(self.bl_addr_and_target_addr),
                        'bl_step': self.bl_step,
                        'code_cave': deepcopy(self.code_cave)
                    }
                    self.current_out(current_out_text, True)
                    log_out_text = '\n'.join(eval(self.loc_msg_map['asm_title']))
                    self.log_out(log_out_text, True)
                    self.reset_middle_ASM_state()
                    self.reset_wings()
                elif len(self.asm_cache_json) != 0:
                    if self.asm_cache_json[next(iter(self.asm_cache_json.keys()))]['code_type'] == 'Normal':
                        current_out_text = ''
                        _bl_step = self.bl_step
                        while len(self.asm_cache_json) != 0:
                            if self.asm_cache_json[next(iter(self.asm_cache_json.keys()))]['code_type'] == 'Normal':
                                current_out_text += self.asm_cache_json[next(iter(self.asm_cache_json.keys()))]['contents']['code_raw'] + '\n'
                                del self.asm_cache_json[next(iter(self.asm_cache_json.keys()))]
                                self.bl_step += 1
                            else:
                                break
                        current_out_text = current_out_text[:-1]
                        self.bl_addr_and_target_addr.update({
                            str(_bl_step):
                            {
                                'code_type': 'Normal',
                                'contents': {'code_raw': current_out_text}
                            }})
                        
                        if len(self.asm_cache_json) == 0:
                            current_out_text += '\n'
                        current_text_type = 'asm_normal_code'
                        current_out_json = {
                            'current_out_text': current_out_text,
                            'asm_cache_json': deepcopy(self.asm_cache_json),
                            'bl_addr_and_target_addr': deepcopy(self.bl_addr_and_target_addr),
                            'bl_step': self.bl_step,
                            'code_cave': deepcopy(self.code_cave)
                        }
                        self.current_out(current_out_text, True)
                        log_out_text = '\n'.join(eval(self.loc_msg_map['asm_normal_code']))
                        self.log_out(log_out_text, True)
                        self.reset_middle_ASM_state()
                    elif self.asm_cache_json[next(iter(self.asm_cache_json.keys()))]['code_type'] == 'ASM':
                        if not self.asm_cache_json[next(iter(self.asm_cache_json.keys()))]['contents']['is_bl']:  # not bl/branch
                            if self.asm_cache_json[next(iter(self.asm_cache_json.keys()))]['contents']['is_code_cave']:
                                current_out_text = self.generate_current_output(self.asm_cache_json[next(iter(self.asm_cache_json.keys()))]['contents'])
                                current_text_type = 'asm_cave_code'
                                self.current_out(current_out_text, True)
                                print(f'Before: {hex(self.code_cave[0])},{hex(self.code_cave[1])}')
                                
                                _asm_cache_json = deepcopy(self.asm_cache_json[next(iter(self.asm_cache_json.keys()))])
                                is_generate_button_discard = False
                                if self.code_cave == None:
                                    is_generate_button_discard = True
                                    log_out_text = '\n'.join(eval(self.loc_msg_map['asm_cave_code_no_cave']))
                                elif self.code_cave[0] + sum(_asm_cache_json['contents']['offset']) > self.code_cave[1]:
                                    is_generate_button_discard = True
                                    log_out_text = '\n'.join(eval(self.loc_msg_map['asm_cave_code_no_space']))
                                elif self.code_cave[0] + sum(_asm_cache_json['contents']['offset']) <= self.code_cave[1]:
                                    code_cave_addr = '0x' + hex(self.code_cave[0])[2:].zfill(8).upper()
                                    _asm_cache_json['contents']['base_addr'] = self.code_cave[0]
                                    for _index in range(len(_asm_cache_json['contents']['offset'])):
                                        _asm_cache_json['contents']['code_addr'][_index] = hex(self.code_cave[0])[2:].zfill(8).upper()
                                        self.code_cave[0] += _asm_cache_json['contents']['offset'][_index]
                                    _asm_cache_json['contents']['next_addr'] = self.code_cave[0]
                                    log_out_text = '\n'.join(eval(self.loc_msg_map['asm_cave_code_has_space']))
                                print(f'After: {hex(self.code_cave[0])},{hex(self.code_cave[1])}')
                                self.bl_addr_and_target_addr.update({str(self.bl_step):_asm_cache_json})
                                self.bl_step += 1
                                del self.asm_cache_json[next(iter(self.asm_cache_json.keys()))]
                                if len(self.asm_cache_json) == 0:
                                    current_out_text += '\n'
                                self.log_out(log_out_text, True)
                                self.reset_middle_ASM_state()
                                current_out_json = {
                                    'current_out_text': current_out_text,
                                    'asm_cache_json': deepcopy(self.asm_cache_json),
                                    'bl_addr_and_target_addr': deepcopy(self.bl_addr_and_target_addr),
                                    'bl_step': self.bl_step,
                                    'code_cave': deepcopy(self.code_cave),
                                    'is_generate_button_discard': is_generate_button_discard
                                }
                            else:  # not bl and not code cave, should be normal asm code
                                hit_start_addr = []
                                wing_length = self.check_wings()
                                current_out_text = self.generate_current_output(self.asm_cache_json[next(iter(self.asm_cache_json.keys()))]['contents'])
                                current_text_type = 'asm_normal_asm_code'
                                self.current_out(current_out_text, True)
                                
                                _asm_cache_json = deepcopy(self.asm_cache_json[next(iter(self.asm_cache_json.keys()))])
                                hit_start_addr = self.find_addr_re([_asm_cache_json['contents']['base_addr'], _asm_cache_json['contents']['next_addr']], wing_length, 0)
                                hit_start_addr_str = ', '.join(hit_start_addr)
                                print(hit_start_addr_str)

                                is_generate_button_discard = False
                                if len(hit_start_addr) == 0:
                                    is_generate_button_discard = True
                                    log_out_text = '\n'.join(eval(self.loc_msg_map['asm_normal_asm_no_addr']))
                                    self.reset_middle_ASM_state()
                                else:
                                    if len(hit_start_addr) > 1:
                                        log_out_text = '\n'.join(eval(self.loc_msg_map['asm_normal_asm_multi_addr']))
                                    else:
                                        log_out_text = '\n'.join(eval(self.loc_msg_map['asm_normal_asm_single_addr']))
                                
                                    _asm_cache_json['contents'].update(
                                    {
                                        'org_addr': [_asm_cache_json['contents']['base_addr'], _asm_cache_json['contents']['next_addr']],
                                        'bl_org_addr': None,
                                        'hit_addr': deepcopy(hit_start_addr),
                                        'addr_chosen': 0,
                                        'bl_target_hit_addr': [],
                                        'bl_target_addr_chosen': None,
                                        'wing_length': deepcopy(self.check_wings()),  # only for ver 0.2 and upper, auto wing_length update
                                        'bl_target_wing_length': None
                                    })
                                    _asm_cache_json = deepcopy(self.update_middle_ASM_output(_asm_cache_json, 0))
                                self.bl_addr_and_target_addr.update({str(self.bl_step):_asm_cache_json})
                                self.bl_step += 1
                                del self.asm_cache_json[next(iter(self.asm_cache_json.keys()))]
                                if len(self.asm_cache_json) == 0:
                                    current_out_text += '\n'
                                self.log_out(log_out_text, True)
                                current_out_json = {
                                    'current_out_text': current_out_text,
                                    'asm_cache_json': deepcopy(self.asm_cache_json),
                                    'bl_addr_and_target_addr': deepcopy(self.bl_addr_and_target_addr),
                                    'bl_step': self.bl_step,
                                    'code_cave': deepcopy(self.code_cave),
                                    'is_generate_button_discard': is_generate_button_discard
                                }
                        else:  # is_bl
                            current_out_text = self.generate_current_output(self.asm_cache_json[next(iter(self.asm_cache_json.keys()))]['contents'])

                            _asm_cache_json = deepcopy(self.asm_cache_json[next(iter(self.asm_cache_json.keys()))])
                            is_generate_button_discard = False

                            if self.asm_cache_json[next(iter(self.asm_cache_json.keys()))]['contents']['is_code_cave']:  # bl in code cave
                                current_text_type = 'asm_bl_cave_code'
                                self.current_out(current_out_text, True)
                                
                                if self.code_cave is None:
                                    is_generate_button_discard = True
                                    log_out_text = '\n'.join(eval(self.loc_msg_map['asm_bl_cave_no_cave']))
                                    self.reset_middle_ASM_state()
                                elif self.code_cave[0] + sum(_asm_cache_json['contents']['offset']) > self.code_cave[1]:
                                    is_generate_button_discard = True
                                    log_out_text = '\n'.join(eval(self.loc_msg_map['asm_bl_cave_no_space']))
                                    self.reset_middle_ASM_state()
                                elif self.code_cave[0] + sum(_asm_cache_json['contents']['offset']) <= self.code_cave[1]:
                                    code_cave_addr = '0x' + hex(self.code_cave[0])[2:].zfill(8).upper()
                                    _asm_cache_json['contents']['base_addr'] = self.code_cave[0]
                                    for _index in range(len(_asm_cache_json['contents']['offset'])):
                                        _asm_cache_json['contents']['code_addr'][_index] = hex(self.code_cave[0])[2:].zfill(8).upper()
                                        self.code_cave[0] += _asm_cache_json['contents']['offset'][_index]
                                    _asm_cache_json['contents']['next_addr'] = self.code_cave[0]
                                    if self.asm_cache_json[next(iter(self.asm_cache_json.keys()))]['contents']['bl_line'] is not None:
                                        log_out_text = '\n'.join(eval(self.loc_msg_map['asm_bl_cave_has_space']))
                                        self.reset_middle_ASM_state()
                                    else:
                                        if self.asm_cache_json[next(iter(self.asm_cache_json.keys()))]['contents']['bl_to_outer'] == True:
                                            is_generate_button_discard = True
                                            log_out_text = '\n'.join(eval(self.loc_msg_map['asm_bl_cave_to_outer']))
                                            self.reset_middle_ASM_state()
                                        elif (self.asm_cache_json[next(iter(self.asm_cache_json.keys()))]['contents']['bl_to_cave'] == True and
                                            self.asm_cache_json[next(iter(self.asm_cache_json.keys()))]['contents']['bl_line'] is None):
                                            is_generate_button_discard = True
                                            log_out_text = '\n'.join(eval(self.loc_msg_map['asm_bl_cave_to_cave']))
                                            self.reset_middle_ASM_state()
                                        elif self.asm_cache_json[next(iter(self.asm_cache_json.keys()))]['contents']['bl_line'] is None:
                                            bl_target_hit_start_addr = []
                                            bl_target_wing_length = self.check_wings()
                                            bl_target_hit_start_addr = self.find_addr_re([self.asm_cache_json[next(iter(self.asm_cache_json.keys()))]['contents']['bl_addr'], self.asm_cache_json[next(iter(self.asm_cache_json.keys()))]['contents']['bl_addr']+4], bl_target_wing_length, 0)
                                            bl_target_hit_start_addr_str = ', '.join(bl_target_hit_start_addr)
                                            if len(bl_target_hit_start_addr_str) == 0:
                                                log_out_text = '\n'.join(eval(self.loc_msg_map['asm_bl_cave_no_addr']))
                                                self.reset_middle_ASM_state()
                                            else:
                                                if len(bl_target_hit_start_addr) > 1:
                                                    log_out_text = '\n'.join(eval(self.loc_msg_map['asm_bl_cave_multi_addr']))
                                                else:
                                                    log_out_text = '\n'.join(eval(self.loc_msg_map['asm_bl_cave_single_addr']))
                                                
                                                _asm_cache_json['contents'].update(
                                                {
                                                    'org_addr': None,
                                                    'bl_org_addr': [_asm_cache_json['contents']['bl_addr'], _asm_cache_json['contents']['bl_addr']+4],
                                                    'hit_addr': [],
                                                    'addr_chosen': None,
                                                    'bl_target_hit_addr': deepcopy(bl_target_hit_start_addr),
                                                    'bl_target_addr_chosen': 0,
                                                    'wing_length': None,
                                                    'bl_target_wing_length': deepcopy(self.check_wings())  # fetch new wing_length
                                                })
                                                _asm_cache_json = deepcopy(self.update_middle_ASM_output(_asm_cache_json, 0))

                            else:  # bl in main code
                                current_text_type = 'asm_bl_code'
                                self.current_out(current_out_text, True)
                                hit_start_addr = []
                                wing_length = self.check_wings()

                                if (self.asm_cache_json[next(iter(self.asm_cache_json.keys()))]['contents']['bl_line'] is None and
                                self.asm_cache_json[next(iter(self.asm_cache_json.keys()))]['contents']['bl_to_cave'] == False and
                                self.asm_cache_json[next(iter(self.asm_cache_json.keys()))]['contents']['bl_to_outer'] == False):
                                    if type(wing_length) == int:
                                        bl_target_wing_length = wing_length
                                    else:
                                        bl_target_wing_length = deepcopy(wing_length)
                                        bl_target_wing_length[0] = bl_target_wing_length[1]
                                        wing_length[1] = wing_length[0] 
                                
                                    bl_target_hit_start_addr = self.find_addr_re([self.asm_cache_json[next(iter(self.asm_cache_json.keys()))]['contents']['bl_addr'], self.asm_cache_json[next(iter(self.asm_cache_json.keys()))]['contents']['bl_addr']+4], bl_target_wing_length, 2)
                                    bl_target_hit_start_addr_str = ', '.join(bl_target_hit_start_addr)

                                hit_start_addr = self.find_addr_re([_asm_cache_json['contents']['base_addr'], _asm_cache_json['contents']['next_addr']], wing_length, 1)
                                hit_start_addr_str = ', '.join(hit_start_addr)
                                
                                if len(hit_start_addr) == 0:
                                    is_generate_button_discard = True
                                    log_out_text = '\n'.join(eval(self.loc_msg_map['asm_bl_no_addr']))
                                    self.reset_middle_ASM_state()
                                elif self.asm_cache_json[next(iter(self.asm_cache_json.keys()))]['contents']['bl_to_outer'] == True:
                                    is_generate_button_discard = True
                                    log_out_text = '\n'.join(eval(self.loc_msg_map['asm_bl_to_outer']))
                                    self.reset_middle_ASM_state()
                                elif (self.asm_cache_json[next(iter(self.asm_cache_json.keys()))]['contents']['bl_to_cave'] == True and
                                    self.asm_cache_json[next(iter(self.asm_cache_json.keys()))]['contents']['bl_line'] is None):
                                    is_generate_button_discard = True
                                    log_out_text = '\n'.join(eval(self.loc_msg_map['asm_bl_to_cave']))
                                    self.reset_middle_ASM_state()
                                else:
                                    if (self.asm_cache_json[next(iter(self.asm_cache_json.keys()))]['contents']['bl_line'] is None and
                                    self.asm_cache_json[next(iter(self.asm_cache_json.keys()))]['contents']['bl_to_cave'] == False and
                                    self.asm_cache_json[next(iter(self.asm_cache_json.keys()))]['contents']['bl_to_outer'] == False): 
                                    
                                        if len(bl_target_hit_start_addr) == 0:

                                            if len(hit_start_addr) > 1:
                                                log_out_text = '\n'.join(eval(self.loc_msg_map['asm_bl_multi_to_none']))
                                            else:
                                                log_out_text = '\n'.join(eval(self.loc_msg_map['asm_bl_single_to_none']))

                                            wing_length = self.check_wings()  # only for ver 0.2 and upper, auto wing_length update
                                            if type(wing_length) == int:
                                                wing_length = [wing_length, wing_length]
                                            else:
                                                wing_length = [wing_length[0], wing_length[0]]
                                            _asm_cache_json['contents'].update(
                                            {
                                                'org_addr': [_asm_cache_json['contents']['base_addr'], _asm_cache_json['contents']['next_addr']],
                                                'bl_org_addr': None,
                                                'hit_addr': deepcopy(hit_start_addr),
                                                'addr_chosen': 0,
                                                'bl_target_hit_addr': [],
                                                'bl_target_addr_chosen': None,
                                                'wing_length': deepcopy(wing_length),
                                                'bl_target_wing_length': None
                                            })
                                            _asm_cache_json = deepcopy(self.update_middle_ASM_output(_asm_cache_json, 0))
                                        
                                        else:
                                            if len(bl_target_hit_start_addr) > 1:
                                                
                                                if len(hit_start_addr) > 1:
                                                    log_out_text = '\n'.join(eval(self.loc_msg_map['asm_bl_multi_to_multi']))
                                                else:
                                                    log_out_text = '\n'.join(eval(self.loc_msg_map['asm_bl_single_to_multi']))

                                            elif len(bl_target_hit_start_addr) == 1:
                                                
                                                if len(hit_start_addr) > 1:
                                                    log_out_text = '\n'.join(eval(self.loc_msg_map['asm_bl_multi_to_single']))
                                                else:
                                                    log_out_text = '\n'.join(eval(self.loc_msg_map['asm_bl_single_to_single']))

                                            # bl addr not exist already discard, default update_middle_ASM_output() will update bl addr
                                            wing_length = self.check_wings()  # only for ver 0.2 and upper, auto wing_length update
                                            if type(wing_length) == int:
                                                bl_target_wing_length = [wing_length, wing_length]
                                                wing_length = [wing_length, wing_length]
                                            else:
                                                bl_target_wing_length = [wing_length[1], wing_length[1]]
                                                wing_length = [wing_length[0], wing_length[0]]
                                            _asm_cache_json['contents'].update(
                                            {
                                                'org_addr': [_asm_cache_json['contents']['base_addr'], _asm_cache_json['contents']['next_addr']],
                                                'bl_org_addr': [_asm_cache_json['contents']['bl_addr'], _asm_cache_json['contents']['bl_addr']+4],
                                                'hit_addr': deepcopy(hit_start_addr),
                                                'addr_chosen': 0,
                                                'bl_target_hit_addr': deepcopy(bl_target_hit_start_addr),
                                                'bl_target_addr_chosen': 0,
                                                'wing_length': deepcopy(wing_length),
                                                'bl_target_wing_length': deepcopy(bl_target_wing_length),
                                            })
                                            # update_middle_ASM_output() will not update bl and target addr at the same time, so this line remains
                                            _asm_cache_json['contents']['bl_addr'] = int(bl_target_hit_start_addr[0], 16)
                                            _asm_cache_json = deepcopy(self.update_middle_ASM_output(_asm_cache_json, 0))
                                    else:  # bl_line is not None. no need to spare bl target addr space from wing length actually

                                        if len(hit_start_addr) > 1:
                                            log_out_text = '\n'.join(eval(self.loc_msg_map['asm_bl_multi_to_exist']))
                                        else:
                                            log_out_text = '\n'.join(eval(self.loc_msg_map['asm_bl_single_to_exist']))

                                        wing_length = self.check_wings()  # only for ver 0.2 and upper, auto wing_length update
                                        if type(wing_length) == int:
                                            wing_length = [wing_length, wing_length]
                                        else:
                                            wing_length = [wing_length[0], wing_length[0]]
                                        _asm_cache_json['contents'].update(
                                        {
                                            'org_addr': [_asm_cache_json['contents']['base_addr'], _asm_cache_json['contents']['next_addr']],
                                            'bl_org_addr': None,
                                            'hit_addr': deepcopy(hit_start_addr),
                                            'addr_chosen': 0,
                                            'bl_target_hit_addr': [],
                                            'bl_target_addr_chosen': None,
                                            'wing_length': deepcopy(wing_length),
                                            'bl_target_wing_length': None
                                        })
                                        _asm_cache_json = deepcopy(self.update_middle_ASM_output(_asm_cache_json, 0))

                            self.bl_addr_and_target_addr.update({str(self.bl_step):_asm_cache_json})
                            self.bl_step += 1
                            del self.asm_cache_json[next(iter(self.asm_cache_json.keys()))]
                            if len(self.asm_cache_json) == 0:
                                current_out_text += '\n'
                            self.log_out(log_out_text, True)
                            current_out_json = {
                                'current_out_text': current_out_text,
                                'asm_cache_json': deepcopy(self.asm_cache_json),
                                'bl_addr_and_target_addr': deepcopy(self.bl_addr_and_target_addr),
                                'bl_step': self.bl_step,
                                'code_cave': deepcopy(self.code_cave),
                                'is_generate_button_discard': is_generate_button_discard
                            }

                if len(self.asm_cache_json) == 0:
                    self.is_asm_title_part = True
                    self.is_asm_finished = True
                    self.stage += 1 
            
            output_text = self.output_cheats_text.get('1.0', END)
            output_text = output_text[:-1]
            self.stage_detail_json['step'].update(
                {str(self.step):{
                    'current_out_text': 
                    {
                        'type': current_text_type,
                        'raw': current_out_text,
                        'contents': current_out_json
                    },
                    'log_out_text': log_out_text,
                    'output_text': output_text
                }}
            )
            self.step += 1
        
    def generate(self):
        self.process(False)

    def skip(self):
        self.process(True)
    
    def regenerate(self):
        if (self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['type'] != 'asm_normal_asm_code' and
        self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['type'] != 'asm_bl_code' and
        self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['type'] != 'asm_bl_cave_code'):
            pass
        else:
            if self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['type'] == 'asm_normal_asm_code':
                hit_start_addr = []
                wing_length = self.check_wings()

                cache_regenerate = deepcopy(self.stage_detail_json['step'][str(self.step-2)]['current_out_text']['contents']['asm_cache_json'])
                _asm_cache_json = deepcopy(cache_regenerate[next(iter(cache_regenerate.keys()))])
                hit_start_addr = self.find_addr_re([_asm_cache_json['contents']['base_addr'], _asm_cache_json['contents']['next_addr']], wing_length, 0)
                hit_start_addr_str = ', '.join(hit_start_addr)
                print(hit_start_addr_str)
                is_generate_button_discard = False
                if len(hit_start_addr) == 0:
                    is_generate_button_discard = True
                    log_out_text = '\n'.join(eval(self.loc_msg_map['asm_normal_asm_no_addr']))
                    self.reset_middle_ASM_state()
                else:
                    if len(hit_start_addr) > 1:
                        log_out_text = '\n'.join(eval(self.loc_msg_map['asm_normal_asm_multi_addr']))
                    else:
                        log_out_text = '\n'.join(eval(self.loc_msg_map['asm_normal_asm_single_addr']))
                                    
                    _asm_cache_json['contents'].update(
                    {
                        'org_addr': [_asm_cache_json['contents']['base_addr'], _asm_cache_json['contents']['next_addr']],
                        'bl_org_addr': None,
                        'hit_addr': deepcopy(hit_start_addr),
                        'addr_chosen': 0,
                        'bl_target_hit_addr': [],
                        'bl_target_addr_chosen': None,
                        'wing_length': deepcopy(self.check_wings()),  # only for ver 0.2 and upper, auto wing_length update
                        'bl_target_wing_length': None
                    })
                    _asm_cache_json = deepcopy(self.update_middle_ASM_output(_asm_cache_json, 0))

            else:
                cache_regenerate = deepcopy(self.stage_detail_json['step'][str(self.step-2)]['current_out_text']['contents']['asm_cache_json'])
                _code_cave = deepcopy(self.stage_detail_json['step'][str(self.step-2)]['current_out_text']['contents']['code_cave'])
                _asm_cache_json = deepcopy(cache_regenerate[next(iter(cache_regenerate.keys()))])
                is_generate_button_discard = False
                if cache_regenerate[next(iter(cache_regenerate.keys()))]['contents']['is_code_cave']:  # bl in code cave
                    if _code_cave is None:
                        is_generate_button_discard = True
                        log_out_text = '\n'.join(eval(self.loc_msg_map['asm_bl_cave_no_cave']))
                        self.reset_middle_ASM_state()
                    elif _code_cave[0] + sum(_asm_cache_json['contents']['offset']) > _code_cave[1]:
                        is_generate_button_discard = True
                        log_out_text = '\n'.join(eval(self.loc_msg_map['asm_bl_cave_no_space']))
                        self.reset_middle_ASM_state()
                    elif _code_cave[0] + sum(_asm_cache_json['contents']['offset']) <= _code_cave[1]:
                        code_cave_addr = '0x' + hex(_code_cave[0])[2:].zfill(8).upper()  # only for log message
                        _asm_cache_json['contents']['base_addr'] = _code_cave[0]
                        for _index in range(len(_asm_cache_json['contents']['offset'])):
                            _asm_cache_json['contents']['code_addr'][_index] = hex(_code_cave[0])[2:].zfill(8).upper()
                            _code_cave[0] += _asm_cache_json['contents']['offset'][_index]
                            _asm_cache_json['contents']['next_addr'] = _code_cave[0]
                            if cache_regenerate[next(iter(cache_regenerate.keys()))]['contents']['bl_line'] is not None:
                                log_out_text = '\n'.join(eval(self.loc_msg_map['asm_bl_cave_has_space']))
                                self.reset_middle_ASM_state()
                            else:
                                if cache_regenerate[next(iter(cache_regenerate.keys()))]['contents']['bl_to_outer'] == True:
                                    is_generate_button_discard = True
                                    log_out_text = '\n'.join(eval(self.loc_msg_map['asm_bl_cave_to_outer']))
                                    self.reset_middle_ASM_state()
                                elif (cache_regenerate[next(iter(cache_regenerate.keys()))]['contents']['bl_to_cave'] == True and
                                        cache_regenerate[next(iter(cache_regenerate.keys()))]['contents']['bl_line'] is None):
                                    is_generate_button_discard = True
                                    log_out_text = '\n'.join(eval(self.loc_msg_map['asm_bl_cave_to_cave']))
                                    self.reset_middle_ASM_state()
                                elif cache_regenerate[next(iter(cache_regenerate.keys()))]['contents']['bl_line'] is None:  # to main addr that not in cheat codes
                                    bl_target_hit_start_addr = []
                                    bl_target_wing_length = self.check_wings()
                                    bl_target_hit_start_addr = self.find_addr_re([cache_regenerate[next(iter(cache_regenerate.keys()))]['contents']['bl_addr'], cache_regenerate[next(iter(cache_regenerate.keys()))]['contents']['bl_addr']+4], bl_target_wing_length, 0)
                                    bl_target_hit_start_addr_str = ', '.join(bl_target_hit_start_addr)
                                    if len(bl_target_hit_start_addr_str) == 0:
                                        log_out_text = '\n'.join(eval(self.loc_msg_map['asm_bl_cave_no_addr']))
                                        self.reset_middle_ASM_state()
                                    else:
                                        if len(bl_target_hit_start_addr) > 1:
                                            log_out_text = '\n'.join(eval(self.loc_msg_map['asm_bl_cave_multi_addr']))
                                        else:
                                            log_out_text = '\n'.join(eval(self.loc_msg_map['asm_bl_cave_single_addr']))
                                        _asm_cache_json['contents'].update(
                                        {
                                            'org_addr': None,
                                            'bl_org_addr': [_asm_cache_json['contents']['bl_addr'], _asm_cache_json['contents']['bl_addr']+4],
                                            'hit_addr': [],
                                            'addr_chosen': None,
                                            'bl_target_hit_addr': deepcopy(bl_target_hit_start_addr),
                                            'bl_target_addr_chosen': 0,
                                            'wing_length': None,
                                            'bl_target_wing_length': deepcopy(self.check_wings())  # fetch new wing_length
                                        })
                                        _asm_cache_json = deepcopy(self.update_middle_ASM_output(_asm_cache_json, 0))
                                self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['contents']['code_cave'] = deepcopy(_code_cave)
                else:  # bl in main code, bl to exist cave code or cheat code will process in create_bl_links()
                    hit_start_addr = []
                    wing_length = self.check_wings()

                    if (cache_regenerate[next(iter(cache_regenerate.keys()))]['contents']['bl_line'] is None and
                    cache_regenerate[next(iter(cache_regenerate.keys()))]['contents']['bl_to_cave'] == False and
                    cache_regenerate[next(iter(cache_regenerate.keys()))]['contents']['bl_to_outer'] == False):
                        if type(wing_length) == int:
                            bl_target_wing_length = wing_length
                        else:
                            bl_target_wing_length = deepcopy(wing_length)
                            bl_target_wing_length[0] = bl_target_wing_length[1]
                            wing_length[1] = wing_length[0]
                                    
                        bl_target_hit_start_addr = self.find_addr_re([cache_regenerate[next(iter(cache_regenerate.keys()))]['contents']['bl_addr'], cache_regenerate[next(iter(cache_regenerate.keys()))]['contents']['bl_addr']+4], bl_target_wing_length, 2)
                        bl_target_hit_start_addr_str = ', '.join(bl_target_hit_start_addr)

                    hit_start_addr = self.find_addr_re([_asm_cache_json['contents']['base_addr'], _asm_cache_json['contents']['next_addr']], wing_length, 1)
                    hit_start_addr_str = ', '.join(hit_start_addr)
                                
                    if len(hit_start_addr) == 0:
                        is_generate_button_discard = True
                        log_out_text = '\n'.join(eval(self.loc_msg_map['asm_bl_no_addr']))
                        self.reset_middle_ASM_state()
                    elif cache_regenerate[next(iter(cache_regenerate.keys()))]['contents']['bl_to_outer'] == True:
                        is_generate_button_discard = True
                        log_out_text = '\n'.join(eval(self.loc_msg_map['asm_bl_to_outer']))
                        self.reset_middle_ASM_state()
                    elif (cache_regenerate[next(iter(cache_regenerate.keys()))]['contents']['bl_to_cave'] == True and
                        cache_regenerate[next(iter(cache_regenerate.keys()))]['contents']['bl_line'] is None):
                        is_generate_button_discard = True
                        log_out_text = '\n'.join(eval(self.loc_msg_map['asm_bl_to_cave']))
                        self.reset_middle_ASM_state()
                    else:
                        if (cache_regenerate[next(iter(cache_regenerate.keys()))]['contents']['bl_line'] is None and
                        cache_regenerate[next(iter(cache_regenerate.keys()))]['contents']['bl_to_cave'] == False and
                        cache_regenerate[next(iter(cache_regenerate.keys()))]['contents']['bl_to_outer'] == False): 
                                    
                            if len(bl_target_hit_start_addr) == 0:

                                if len(hit_start_addr) > 1:
                                    log_out_text = '\n'.join(eval(self.loc_msg_map['asm_bl_multi_to_none']))
                                else:
                                    log_out_text = '\n'.join(eval(self.loc_msg_map['asm_bl_single_to_none']))

                                wing_length = self.check_wings()  # only for ver 0.2 and upper, auto wing_length update
                                if type(wing_length) == int:
                                    wing_length = [wing_length, wing_length]
                                else:
                                    wing_length = [wing_length[0], wing_length[0]]
                                _asm_cache_json['contents'].update(
                                {
                                    'org_addr': [_asm_cache_json['contents']['base_addr'], _asm_cache_json['contents']['next_addr']],
                                    'bl_org_addr': None,
                                    'hit_addr': deepcopy(hit_start_addr),
                                    'addr_chosen': 0,
                                    'bl_target_hit_addr': [],
                                    'bl_target_addr_chosen': None,
                                    'wing_length': deepcopy(wing_length),
                                    'bl_target_wing_length': None
                                })
                                _asm_cache_json = deepcopy(self.update_middle_ASM_output(_asm_cache_json, 0))
                                        
                            else:
                                if len(bl_target_hit_start_addr) > 1:
                                                
                                    if len(hit_start_addr) > 1:
                                        log_out_text = '\n'.join(eval(self.loc_msg_map['asm_bl_multi_to_multi']))
                                    else:
                                        log_out_text = '\n'.join(eval(self.loc_msg_map['asm_bl_single_to_multi']))

                                elif len(bl_target_hit_start_addr) == 1:
                                                
                                    if len(hit_start_addr) > 1:
                                        log_out_text = '\n'.join(eval(self.loc_msg_map['asm_bl_multi_to_single']))
                                    else:
                                        log_out_text = '\n'.join(eval(self.loc_msg_map['asm_bl_single_to_single']))
                                                
                                # bl addr not exist already discard, default update_middle_ASM_output() will update bl addr
                                wing_length = self.check_wings()  # only for ver 0.2 and upper, auto wing_length update
                                if type(wing_length) == int:
                                    bl_target_wing_length = [wing_length, wing_length]
                                    wing_length = [wing_length, wing_length]
                                else:
                                    bl_target_wing_length = [wing_length[1], wing_length[1]]
                                    wing_length = [wing_length[0], wing_length[0]]
                                _asm_cache_json['contents'].update(
                                {
                                    'org_addr': [_asm_cache_json['contents']['base_addr'], _asm_cache_json['contents']['next_addr']],
                                    'bl_org_addr': [_asm_cache_json['contents']['bl_addr'], _asm_cache_json['contents']['bl_addr']+4],
                                    'hit_addr': deepcopy(hit_start_addr),
                                    'addr_chosen': 0,
                                    'bl_target_hit_addr': deepcopy(bl_target_hit_start_addr),
                                    'bl_target_addr_chosen': 0,
                                    'wing_length': deepcopy(wing_length),
                                    'bl_target_wing_length': deepcopy(bl_target_wing_length),
                                })
                                # update_middle_ASM_output() will not update bl and target addr at the same time, so this line remains
                                _asm_cache_json['contents']['bl_addr'] = int(bl_target_hit_start_addr[0], 16)
                                _asm_cache_json = deepcopy(self.update_middle_ASM_output(_asm_cache_json, 0))

                        else:

                            if len(hit_start_addr) > 1:
                                log_out_text = '\n'.join(eval(self.loc_msg_map['asm_bl_multi_to_exist']))
                            else:
                                log_out_text = '\n'.join(eval(self.loc_msg_map['asm_bl_single_to_exist']))
                        
                            wing_length = self.check_wings()  # only for ver 0.2 and upper, auto wing_length update
                            if type(wing_length) == int:
                                wing_length = [wing_length, wing_length]
                            else:
                                wing_length = [wing_length[0], wing_length[0]]
                            _asm_cache_json['contents'].update(
                            {
                                'org_addr': [_asm_cache_json['contents']['base_addr'], _asm_cache_json['contents']['next_addr']],
                                'bl_org_addr': None,
                                'hit_addr': deepcopy(hit_start_addr),
                                'addr_chosen': 0,
                                'bl_target_hit_addr': [],
                                'bl_target_addr_chosen': None,
                                'wing_length': deepcopy(wing_length),
                                'bl_target_wing_length': None
                            })
                            _asm_cache_json = deepcopy(self.update_middle_ASM_output(_asm_cache_json, 0))

            # pack and update data
            self.bl_addr_and_target_addr = deepcopy(self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['contents']['bl_addr_and_target_addr'])
            _bl_step = self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['contents']['bl_step']
            self.bl_addr_and_target_addr[str(_bl_step-1)] = deepcopy(_asm_cache_json)

            self.log_out(log_out_text, True)

            self.stage_detail_json['step'][str(self.step-1)]['log_out_text'] = log_out_text
            self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['contents']['bl_addr_and_target_addr'] = deepcopy(self.bl_addr_and_target_addr)
            self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['contents']['is_generate_button_discard'] = is_generate_button_discard

    def undo(self):
        if self.step == 0:
            pass
        elif self.step == 1:
            self.restart()
        else:
            self.reset_middle_ASM_state()
            if self.end_flag == True:
                self.end_flag = False
                self.output_out(self.stage_detail_json['step'][str(self.step-1)]['output_text'], True)
            else:
                self.step -= 1
                if self.is_asm_finished == True:
                    self.stage -= 1
                if self.stage_detail_json['step'][str(self.step)]['current_out_text']['type'] == 'asm_title':
                    self.is_asm_title_part = True
                    self.is_asm_finished = True
                    self.bl_step = 0
                    self.bl_addr_and_target_addr = {}
                    self.code_cave = self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['contents']['code_cave']
                elif (self.stage_detail_json['step'][str(self.step)]['current_out_text']['type'] == 'asm_normal_code' or
                    self.stage_detail_json['step'][str(self.step)]['current_out_text']['type'] == 'asm_cave_code' or
                    self.stage_detail_json['step'][str(self.step)]['current_out_text']['type'] == 'asm_normal_asm_code'or
                    self.stage_detail_json['step'][str(self.step)]['current_out_text']['type'] == 'asm_bl_code' or
                    self.stage_detail_json['step'][str(self.step)]['current_out_text']['type'] == 'asm_bl_cave_code'):
                    self.is_asm_title_part = False
                    self.is_asm_finished = False
                    self.asm_cache_json = deepcopy(self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['contents']['asm_cache_json'])
                    self.bl_step = self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['contents']['bl_step']
                    self.bl_addr_and_target_addr = deepcopy(self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['contents']['bl_addr_and_target_addr'])
                    self.code_cave = deepcopy(self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['contents']['code_cave'])
                print(f'Undo: {hex(self.code_cave[0])},{hex(self.code_cave[1])}')
                pop_obj = self.stage_detail_json['step'][str(self.step)]
                self.current_out(self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['raw'], True)
                self.log_out(self.stage_detail_json['step'][str(self.step-1)]['log_out_text'], True)
                self.output_out(self.stage_detail_json['step'][str(self.step-1)]['output_text'], True)
                del self.stage_detail_json['step'][str(self.step)]
                pop_obj.clear()

    def restart(self):
        self.reset_middle_ASM_state()
        self.stage_detail_json = {'raw':'','processed':'','step':{}}
        self.stage = 0
        self.stage_max = 0
        self.step = 0
        self.end_flag = False
        self.is_asm_title_part = True
        self.is_asm_finished = True
        self.asm_cache_json = {}
        self.bl_addr_and_target_addr = {}
        self.bl_step = 0
        self.code_cave = {}
        
        self.log_text.config(state=NORMAL)
        self.log_text.delete(0.1, END)
        self.log_text.config(state=DISABLED)
        self.current_cheats_text.config(state=NORMAL)
        self.current_cheats_text.delete(0.1, END)
        self.current_cheats_text.config(state=DISABLED)
        self.output_cheats_text.config(state=NORMAL)
        self.output_cheats_text.delete(0.1, END)
        self.output_cheats_text.config(state=DISABLED)

        self.input_cheats_text.config(state=NORMAL)
        self.btn_enable_after_load(True)

    def update(self):
        cache_regenerate = deepcopy(self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['contents']['bl_addr_and_target_addr'])
        _asm_cache_json = deepcopy(cache_regenerate[next(iter(cache_regenerate.keys()))])  # Caution: use first dict not last one, harmless for NOW
        self.update_middle_ASM_output(_asm_cache_json, 3)
    
    def check(self):
        if not self.is_check_branch:
            self.is_check_branch = True
            self.branch_checkbox.select()
        else:
            self.is_check_branch = False
            self.branch_checkbox.deselect()
        cache_regenerate = deepcopy(self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['contents']['bl_addr_and_target_addr'])
        _asm_cache_json = deepcopy(cache_regenerate[next(iter(cache_regenerate.keys()))])
        self.update_middle_ASM_output(_asm_cache_json, 3)

    def next(self):
        cache_regenerate = deepcopy(self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['contents']['bl_addr_and_target_addr'])
        _asm_cache_json = deepcopy(cache_regenerate[next(iter(cache_regenerate.keys()))])
        cache_regenerate[next(iter(cache_regenerate.keys()))] = deepcopy(self.update_middle_ASM_output(_asm_cache_json, 2))
        self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['contents']['bl_addr_and_target_addr'] = deepcopy(cache_regenerate)

    def previous(self):
        cache_regenerate = deepcopy(self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['contents']['bl_addr_and_target_addr'])
        _asm_cache_json = deepcopy(cache_regenerate[next(iter(cache_regenerate.keys()))])
        cache_regenerate[next(iter(cache_regenerate.keys()))] = deepcopy(self.update_middle_ASM_output(_asm_cache_json, 1))
        self.stage_detail_json['step'][str(self.step-1)]['current_out_text']['contents']['bl_addr_and_target_addr'] = deepcopy(cache_regenerate)

    def sav_cht(self):
        if self.is_debug_mode.get():
            try:
                os.makedirs(self.log_path)
            except:
                print("DIR already exists.")
            file_name = os.path.join(self.log_path, 'cheats_procedure_json')
            with open(f'{file_name}.json', 'w') as result_file:
                json.dump(self.stage_detail_json, result_file, cls=MyEncoder, indent=1)
        file_path = filedialog.asksaveasfilename(title=self.loc_hints_map['Save new cheats'],
                        initialfile=f'{self.main_new_file.ModuleId.upper()}.txt',
                        filetypes=[('text file', '.txt'), ('All Files', '*')])
        file_text = self.output_cheats_text.get('1.0', END)
        length = len(file_text) - 1
        index = length
        remove_index = 0
        while index > 0:
            if file_text[index] != '\n':
                remove_index = -(length-index)
                break
            index = index - 1
        file_text = file_text[:remove_index]
        if file_path != '':
            with open(file=file_path, mode='a+', encoding='utf-8') as file:
                file.seek(0)
                file.truncate()
                file.write(file_text)
                dialog.Dialog(None, {'title': '\n'.join(eval(self.loc_msg_map['Cheat Code'])), 'text': '\n'.join(eval(self.loc_msg_map['Saved'])), 'bitmap': 'warning', 'default': 0,
                        'strings': ('\n'.join(eval(self.loc_msg_map['OK'])), '\n'.join(eval(self.loc_msg_map['Cancel'])))})
        return

    def sav_nso(self):
        messagebox.showinfo(title='Sorry', message='Under Construction')