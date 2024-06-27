configuration = {
    "wing_length_default": "[2, 2]",
    "extra_wing_length_default": "[2, 2]",
    "widen_hit_num": "8",
    "max_hit_num": "512",
}

code_pattern = {
    "loc_EN":
    {
        "code_type_0x0":
        {
            "pattern": "r'^ *0[1248][abcdef\d]{6} *( * [abcdef\d]{8}){0,3} *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0x0: Store Static Value to Memory',
            "details":
                """[f'Code type 0x0 allows writing a static value to a memory address.']"""
        },
        "code_type_0x1":
        {
            "pattern": "r'^ *1[1248][0123][123456]00[abcdef\d]{2} *( * [abcdef\d]{8}){2,3} *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0x1: Begin Conditional Block',
            "details":
                """[f'Code type 0x1 performs a comparison of the contents of memory to a static value.',
                    'If the condition is not met, all instructions until the appropriate End or Else conditional block terminator are skipped.']"""
        },
        "code_type_0x2":
        {
            "pattern": "r'^ *2[01]000000 *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0x2: End Conditional Block',
            "details":
                """[f'Code type 0x2 marks the end of a conditional block (started by Code Type 0x1 or Code Type 0x8).',
                    'When an Else is executed, all instructions until the appropriate End conditional block terminator are skipped.']"""
        },
        "code_type_0x3":
        {
            "pattern": "r'^ *3[01]0[abcdef\d]0000 *( * [abcdef\d]{8}){0,1} *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0x3: Start/End Loop',
            "details":
                """[f'Code type 0x3 allows for iterating in a loop a fixed number of times.']"""
        },
        "code_type_0x4":
        {
            "pattern": "r'^ *400[abcdef\d]0000 *( * [abcdef\d]{8}){2} *$'",
            "generate_type": 'force_generate',
            "description": 'Code Type 0x4: Load Register with Static Value',
            "details":
                """[f'Code type 0x4 allows setting a register to a constant value.']"""
        },
        "code_type_0x5":
        {
            "pattern": "r'^ *5[1248][0123][abcdef\d][01]0[abcdef\d]{2} * [abcdef\d]{8} *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0x5: Load Register with Memory Value',
            "details":
                """[f'Code type 0x5 allows loading a value from memory into a register, either using a fixed address or by dereferencing the destination register.']"""
        },
        "code_type_0x6":
        {
            "pattern": "r'^ *6[1248]0[abcdef\d][01][01][abcdef\d]0 *( * [abcdef\d]{8}){2} *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0x6: Store Static Value to Register Memory Address',
            "details":
                """[f'Code type 0x6 allows writing a fixed value to a memory address specified by a register.']"""
        },
        "code_type_0x7":
        {
            "pattern": "r'^ *7[1248]0[abcdef\d][01234]000 * [abcdef\d]{8} *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0x7: Legacy Arithmetic',
            "details":
                """[f'Code type 0x7 allows performing arithmetic on registers.',
                    'However, it has been deprecated by Code type 0x9, and is only kept for backwards compatibility.']"""
        },
        "code_type_0x8":
        {
            "pattern": "r'^ *8[abcdef\d]{7} *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0x8: Begin Keypress Conditional Block',
            "details":
                """[f'Code type 0x8 enters or skips a conditional block based on whether a key combination is pressed.']"""
        },
        "code_type_0x9":
        {
            "pattern": "r'^ *9[1248][\d][abcdef\d][abcdef\d][01][abcdef\d]0 *( * [abcdef\d]{8}){0,2} *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0x9: Perform Arithmetic',
            "details":
                """[f'Code type 0x9 allows performing arithmetic on registers.']"""
        },
        "code_type_0xA":
        {
            "pattern": "r'^ *A[1248][abcdef\d]{2}[01][012345][abcdef\d]{2} *( * [abcdef\d]{8}){0,1} *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0xA: Store Register to Memory Address',
            "details":
                """[f'Code type 0xA allows writing a register to memory.']"""
        },
        "code_type_0xC0":
        {
            "pattern": "r'^ *C0[1248][123456][abcdef\d][012345][abcdef\d]{2} *( * [abcdef\d]{8}){0,2} *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0xC0: Begin Register Conditional Block',
            "details":
                """[f'Code type 0xC0 performs a comparison of the contents of a register and another value.'
                    'If the condition is not met, all instructions until the appropriate conditional block terminator are skipped.']"""
        },
        "code_type_0xC1":
        {
            "pattern": "r'^ *C10[abcdef\d]0[abcdef\d][0123]0 *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0xC1: Save or Restore Register',
            "details":
                """[f'Code type 0xC1 performs saving or restoring of registers.']"""
        },
        "code_type_0xC2":
        {
            "pattern": "r'^ *C2[0123]0[abcdef\d]{4} *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0xC2: Save or Restore Register with Mask',
            "details":
                """[f'Code type 0xC2 performs saving or restoring of multiple registers using a bitmask.']"""
        },
        "code_type_0xC3":
        {
            "pattern": "r'^ *C3000[078F][0F][abcdef\d] *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0xC3: Read or Write Static Register',
            "details":
                """[f'Code type 0xC3 reads or writes a static register with a given register.']"""
        },
        "code_type_0xF0":
        {
            "pattern": "r'^ *F0[abcdef\d]{6} *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0xF0: Double Extended-Width Instruction',
            "details":
                """[f'Code type 0xF0 signals to the VM to treat the upper three nybbles of the first dword as instruction type, instead of just the upper nybble.']"""
        },
        "code_type_0xFF0":
        {
            "pattern": "r'^ *FF0[abcdef\d]{5} *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0xFF0: Pause Process',
            "details":
                """[f'Code type 0xFF0 pauses the current process.']"""
        },
        "code_type_0xFF1":
        {
            "pattern": "r'^ *FF1[abcdef\d]{5} *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0xFF1: Resume Process',
            "details":
                """[f'Code type 0xFF1 resumes the current process.']"""
        },
        "code_type_0xFFF":
        {
            "pattern": "r'^ *FFF[1248][abcdef\d]{4} *( * [abcdef\d]{8}){0,1} *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0xFFF: Debug Log',
            "details":
                """[f'Code type 0xFFF writes a debug log.']"""
        },
        "code_type_padding":
        {
            "pattern": "r'^ *00000000.*$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type Padding: Padding characters',
            "details":
                """[f'Code type padding has no actual meaning. it is just for placeholder purposes.']"""
        },
        "code_type_unknown":
        {
            "pattern": "r'^NEVER MATCH$'",
            "generate_type": 'force_discard',
            "description": 'Code Type Unknown: Unknown Type',
            "details":
                """[f'Unknown code type, unable to process.']"""
        }
    },
    "loc_CN":
    {
        "code_type_0x0":
        {
            "pattern": "r'^ *0[1248][abcdef\d]{6} *( * [abcdef\d]{8}){0,3} *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0x0: 向内存地址写入数据',
            "details":
                """[f'Code type 0x0 会向指定内存地址写入一些静态数据。']"""
        },
        "code_type_0x1":
        {
            "pattern": "r'^ *1[1248][0123][123456]00[abcdef\d]{2} *( * [abcdef\d]{8}){2,3} *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0x1: 条件分支开始标志',
            "details":
                """[f'Code type 0x1 是条件分支的开始标志，将特定内存地址的数据与静态数据进行数值比较。',
                    '如果条件不满足，则跳过本指令至 Code type 0x2 之间的所有指令。']"""
        },
        "code_type_0x2":
        {
            "pattern": "r'^ *2[01]000000 *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0x2: 条件分支结束标志',
            "details":
                """[f'Code type 0x2 是条件分支的结束标志 (始于 Code Type 0x1 或 Code Type 0x8)。',
                    '在使用 Else 指令时，则跳过本指令至 End 条件结束标志之间的所有指令。']"""
        },
        "code_type_0x3":
        {
            "pattern": "r'^ *3[01]0[abcdef\d]0000 *( * [abcdef\d]{8}){0,1} *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0x3: 开始/结束循环标志',
            "details":
                """[f'Code type 0x3 将执行指定次数的循环体内的指令（开始循环标志和结束循环标志之间的指令）。']"""
        },
        "code_type_0x4":
        {
            "pattern": "r'^ *400[abcdef\d]0000 *( * [abcdef\d]{8}){2} *$'",
            "generate_type": 'force_generate',
            "description": 'Code Type 0x4: 静态数据写入寄存器',
            "details":
                """[f'Code type 0x4 会向指定寄存器写入指定的静态数据。']"""
        },
        "code_type_0x5":
        {
            "pattern": "r'^ *5[1248][0123][abcdef\d][01]0[abcdef\d]{2} * [abcdef\d]{8} *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0x5: 内存地址上的数据写入寄存器',
            "details":
                """[f'Code type 0x5 会向指定寄存器写入指定（或寄存器数据指向）的内存地址上的数据。']"""
        },
        "code_type_0x6":
        {
            "pattern": "r'^ *6[1248]0[abcdef\d][01][01][abcdef\d]0 *( * [abcdef\d]{8}){2} *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0x6: 向寄存器（数据）指向的内存地址写入静态数据',
            "details":
                """[f'Code type 0x6 会向指定寄存器（数据）指向的内存地址写入指定的静态数据。']"""
        },
        "code_type_0x7":
        {
            "pattern": "r'^ *7[1248]0[abcdef\d][01234]000 * [abcdef\d]{8} *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0x7: 算术运算（旧版）',
            "details":
                """[f'Code type 0x7 是（寄存器数据）算术运算指令。',
                    '但本指令已被 Code type 0x9 替代，此处仅为向下兼容。']"""
        },
        "code_type_0x8":
        {
            "pattern": "r'^ *8[abcdef\d]{7} *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0x8: 按键条件触发标志',
            "details":
                """[f'Code type 0x8 通过指定按键决定某条件单元是否被触发。']"""
        },
        "code_type_0x9":
        {
            "pattern": "r'^ *9[1248][\d][abcdef\d][abcdef\d][01][abcdef\d]0 *( * [abcdef\d]{8}){0,2} *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0x9: 算术运算',
            "details":
                """[f'Code type 0x9 在寄存器上进行算术运算。']"""
        },
        "code_type_0xA":
        {
            "pattern": "r'^ *A[1248][abcdef\d]{2}[01][012345][abcdef\d]{2} *( * [abcdef\d]{8}){0,1} *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0xA: 将寄存器数据写入内存',
            "details":
                """[f'Code type 0xA 将寄存器数据写入指定的内存地址。']"""
        },
        "code_type_0xC0":
        {
            "pattern": "r'^ *C0[1248][123456][abcdef\d][012345][abcdef\d]{2} *( * [abcdef\d]{8}){0,2} *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0xC0: 寄存器条件开始标志',
            "details":
                """[f'Code type 0xC0 将寄存器数据与其他数据进行比较。'
                    '如果条件不满足，则跳过本指令至条件结束标志之间的所有指令。']"""
        },
        "code_type_0xC1":
        {
            "pattern": "r'^ *C10[abcdef\d]0[abcdef\d][0123]0 *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0xC1: 保存/恢复寄存器数据',
            "details":
                """[f'Code type 0xC1 保存或恢复寄存器数据。']"""
        },
        "code_type_0xC2":
        {
            "pattern": "r'^ *C2[0123]0[abcdef\d]{4} *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0xC2: 保存/恢复寄存器数据（含掩码）',
            "details":
                """[f'Code type 0xC2 使用位掩码同时保存或恢复多个寄存器数据。']"""
        },
        "code_type_0xC3":
        {
            "pattern": "r'^ *C3000[078F][0F][abcdef\d] *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0xC3: 读/写静态寄存器',
            "details":
                """[f'Code type 0xC3 将指定寄存器数据写入某静态寄存器，或读取某静态寄存器数据并存入指定寄存器。']"""
        },
        "code_type_0xF0":
        {
            "pattern": "r'^ *F0[abcdef\d]{6} *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0xF0: 双倍拓宽指令',
            "details":
                """[f'Code type 0xF0 向虚拟机发送信号处理第一个双字节上的三个半字节，用于代替上面的半字节。']"""
        },
        "code_type_0xFF0":
        {
            "pattern": "r'^ *FF0[abcdef\d]{5} *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0xFF0: 暂停运行进程',
            "details":
                """[f'Code type 0xFF0 暂停运行当前的进程。']"""
        },
        "code_type_0xFF1":
        {
            "pattern": "r'^ *FF1[abcdef\d]{5} *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0xFF1: 继续运行进程',
            "details":
                """[f'Code type 0xFF1 继续运行当前的进程。']"""
        },
        "code_type_0xFFF":
        {
            "pattern": "r'^ *FFF[1248][abcdef\d]{4} *( * [abcdef\d]{8}){0,1} *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0xFFF: 调试日志',
            "details":
                """[f'Code type 0xFFF 调试日志写入文件。']"""
        },
        "code_type_padding":
        {
            "pattern": "r'^ *00000000.*$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type Padding: 填充字符',
            "details":
                """[f'Code type padding 没有实际意义，只是为了占位。']"""
        },
        "code_type_unknown":
        {
            "pattern": "r'^NEVER MATCH$'",
            "generate_type": 'force_discard',
            "description": 'Code Type Unknown: 未知代码类型',
            "details":
                """[f'未知的金手指代码类型，无法处理。']"""
        }
    }
}

localization = {
    "loc_EN":
    {
        "title": "Code Updater for Nintendo Switch ver 1.0.2",
        "msgbox_title_map":
        {
            "Info": "Info",
            "Warning": "Warning",
            "Error": "Error",
        },
        "hints_map":
        {
            "Old Main File:": "Old Main File:",
            "New Main File:": "New Main File:",
            "ARM64": "Force ARM64",
            "Input Old Codes:": "Input Old Codes:",
            "Input Old Codes and BID:": """[f'<{self.old_main_file.ModuleId.upper()}> Input Old Codes:']""",
            "Current Processing Codes:": "Current Processing Codes:",
            "Wing Length:": "Wing Length:",
            "Logs:": "Logs:",
            "New Codes Output:": "New Codes Output:",
            "New Codes Output and BID:": """[f'<{self.new_main_file.ModuleId.upper()}> New Codes Output:']""",
            "Load Old Main NSO File": "Load Old Main NSO File",
            "Load New Main NSO File": "Load New Main NSO File",
            "Save New Codes": "Save New Codes",
            "Save New NSO": "Save New NSO",
            "Old Assembly Codes:": "Old Assembly Codes:",
            "New Assembly Codes:": "New Assembly Codes:",
            "Extra Wing Length:": "Extra Length:",
            "Branch": "Switch to Branch"
        },
        "btn_map":
        {
            "Load Old": "Load",
            "Load New": "Load",
            "Regenerate": "Regenerate",
            "Start": "Start",
            "Generate": "Generate",
            "Skip": "Skip",
            "Undo": "Undo",
            "Restart": "Restart",
            "SaveCHT": "Save Code",
            "SaveNSO": "Save NSO",
            "GitHub": "Github",
            "Update": "Update",
            "Prev": "Prev Addr",
            "Next": "Next Addr",
            "Force Exit": "Force Quit",

            "select all": "select all",
            "copy": "copy",
            "paste": "paste",
            "cut": "cut",
        },
        "msg_map":
        {
            "request keys": """['No "keys.txt" found in the root of this app, cannot extract game packages.']""",
            "required title key version": """[f'Required "titlekek_{hex(masterKeyRev-1)[2:].zfill(2)}" not found in "keys.txt"!']""",
            "required master key version": """[f'Required "master_key_{hex(masterKeyRev-1)[2:].zfill(2)}" not found in "keys.txt"!']""",
            ".nso extraction failed": """['Extracting "main" from game package failed']""",
            "Unpack Warning": """[f'Unpack "{Path(file_path).suffix}" takes time, please be patient.']""",
            "Extract NCA": """['Extracting NCA from game package...']""",
            "Extract ticket": """['Extracting ticket content from .tik...']""",
            "Extract main": """['Extracting main file from .nca...']""",
            "processing": """['Processing, please wait...']""",
            "old cheats text ready": """['Old codes normalization process is complete. you can now start the generation process.']""",
            "code processing complete": """['All code processing is complete']""",

            "NOT File": """['File reading failed, please check the file path and permissions.']""",
            "NOT NSO File": """['The "main" file parsing failed, it may not be a valid NSO file.']""",
            "NSO file decompression failed": """['The "main" file decompression failed.']""",
            "NSO file decompressed": """['The "main" file decompressed.']""",
            "NSO file compression failed": """['The "main" file compression failed.']""",
            "NSO file compressed": """['The "main" file compressed.']""",
            "Old BID message": """[f'BID of the old codes should be "{self.old_main_file.ModuleId.upper()}".']""",
            "New BID message": """[f'BID of the new codes is "{self.new_main_file.ModuleId.upper()}".']""",
            "Pre-process message 0x08": """['080X0000 codes have been splited into 04 atom codes.']""",

            "Wing length check message": """['Wing length must be int or list, eg. "5", "[4,5]". Setting to default value.']""",
            "Extra wing length check message": """['Extra wing length must be int or list, eg. "6", "[5,6]". Setting to default value.']""",
            "Change wing length message": """[f'The number of found addresses exceeds the limit ({self.max_hit_num}), making it impossible to display all of them.',
                                            'It is recommended to adjust the wingspan width and regenerate.']""",

            "code_title": """['This is code title.']""",
            "master_code_title": """['This is master code title.']""",
            "asm_code": """[f'This is {asm_type} assembly code.',
                            'Code Type 0x0: Store Static Value to Memory.']""",

            "none_addr_located":  """[f'{addr_type}: None address located.']""",
            "single_addr_located":  """[f'{addr_type}: Single address "{addr_str}" located.']""",
            "multi_addr_located":  """[f'{addr_type}: Multiple address "{addr_str}" located.']""",

            "flat_generate": """['--- Press "Generate" to export or "Skip" to discard ---']""",
            "force_generate": """['--- Both "Generate" or "Skip" will export ---']""",
            "force_discard": """['--- Both "Generate" or "Skip" will discard ---']""",

            "discard_or_regen": """['--- Both "Generate" or "Skip" will discard, "Regenerate" to research ---']""",
            "choose_or_regen": """['--- Press "Generate" to export the highlighted match from the Assembly Code Window, "Skip" to discard or "Regenerate" ---']""",

            "wing_length_warn": """['*** Wing Length = [Branch Address Search Area, Branch Target Search Area] for NOW ***']""",
            "value_warn": """['*** This ASM type code section ONLY has values. Please generate with caution. ***']""",
        },
        "str_map":
        {
            "addr_type_b": "Branch to ",
            "asm_type_r": "regular",
            "asm_type_b": "branch",

            "Cheat Code": "Cheat Code",
            "Cheat Code Saved": "Cheat Code Saved",
            "Saved": "Saved",
            "OK": "OK",
            "Cancel": "Cancel",
            "NSO File": "NSO File",
            "NSO File Saved": "NSO File Saved",
            "File save failed": "File save failed",
        }
    },
    "loc_CN":
    {
        "title": "金手指自动更新器 ver 1.0.2c",
        "msgbox_title_map":
        {
            "Info": "信息",
            "Warning": "警告",
            "Error": "错误",
        },
        "hints_map":
        {
            "Old Main File:": "金手指对应Main：",
            "New Main File:": "目标版本Main：",
            "ARM64": "强制ARM64",
            "Input Old Codes:": "旧金手指输入：",
            "Input Old Codes and BID:": """[f'<{self.old_main_file.ModuleId.upper()}> 旧金手指输入：']""",
            "Current Processing Codes:": "当前处理金手指：",
            "Wing Length:": "翼展宽度：",
            "Logs:": "提示：",
            "New Codes Output:": "新金手指输出：",
            "New Codes Output and BID:": """[f'<{self.new_main_file.ModuleId.upper()}> 新金手指输出：']""",
            "Load Old Main NSO File": "载入金手指对应Main文件",
            "Load New Main NSO File": "载入目标Main文件",
            "Save New Codes": "保存新金手指",
            "Save New NSO": "保存新NSO",
            "Old Assembly Codes:": "旧版ASM源码：",
            "New Assembly Codes:": "新版ASM源码：",
            "Extra Wing Length:": "额外翼展宽度：",
            "Branch": "切换至跳转目标代码"
        },
        "btn_map":
        {
            "Load Old": "读取",
            "Load New": "读取",
            "Regenerate": "重新生成",
            "Start": "开始",
            "Generate": "生成",
            "Skip": "跳过",
            "Undo": "撤销",
            "Restart": "重置",
            "SaveCHT": "保存金手指",
            "SaveNSO": "保存NSO",
            "GitHub": "Github",
            "Update": "更新",
            "Prev": "上个地址",
            "Next": "下个地址",
            "Force Exit": "强制退出",

            "select all": "全选",
            "copy": "复制",
            "paste": "粘贴",
            "cut": "剪切",
        },
        "msg_map":
        {
            "request keys": """['本程序根目录下未找到 "keys.txt" 文件，无法自动解包游戏。']""",
            "required title key version": """[f'"keys.txt"中未找到"titlekek_{hex(masterKeyRev-1)[2:].zfill(2)}"!']""",
            "required master key version": """[f'"keys.txt"中未找到"master_key_{hex(masterKeyRev-1)[2:].zfill(2)}"!']""",
            ".nso extraction failed": """['从游戏包中提取 "main" 文件失败']""",
            "Unpack Warning": """[f'解包 "{Path(file_path).suffix}" 文件需要一段时间，请耐心等待']""",
            "Extract NCA": """['从游戏包提取NCA文件中...']""",
            "Extract ticket": """['从.tik获取相关信息中...']""",
            "Extract main": """['从.nca提取main文件中...']""",
            "processing": """['正在处理，请稍等...']""",
            "old cheats text ready": """['已完成旧金手指规范化处理，可以开始生成操作']""",
            "code processing complete": """['金手指全部处理完毕']""",

            "NOT File": """['文件读取失败，请检查文件路径和权限']""",
            "NOT NSO File": """['"main"文件解析出错，它可能不是一个正常的NSO文件']""",
            "NSO file decompression failed": """['"main"文件解压失败']""",
            "NSO file decompressed": """['"main"文件解压完成']""",
            "NSO file compression failed": """['"main"文件压缩失败']""",
            "NSO file compressed": """['"main"文件压缩完成']""",
            "Old BID message": """[f'旧金手指文件名（BID）必须为 "{self.old_main_file.ModuleId.upper()}"']""",
            "New BID message": """[f'新金手指文件名（BID）为 "{self.new_main_file.ModuleId.upper()}"']""",
            "Pre-process message 0x08": """['080X0000金手指代码已自动缩减为04原子代码']""",

            "Wing length check message": """['翼展宽度必须为整数，如："5"，"[4,5]"']""",
            "Extra wing length check message": """['额外翼展宽度必须为整数，如："6"，"[5,6]"']""",
            "Change wing length message": """[f'找到的地址的数量超过上限（{self.max_hit_num}），无法全部显示。',
                                            '建议调整翼展宽度后重新生成。']""",

            "code_title": """['这是普通码标题。']""",
            "master_code_title": """['这是大师码标题。']""",
            "asm_code": """[f'这是{asm_type}汇编码。',
                            'Code Type 0x0: 向内存地址写入数据。']""",

            "none_addr_located":  """[f'{addr_type}：未找到地址。']""",
            "single_addr_located":  """[f'{addr_type}：地址 "{addr_str}" 已定位。']""",
            "multi_addr_located":  """[f'{addr_type}: 多地址 "{addr_str}" 已定位。']""",

            "flat_generate": """['--- “生成”按钮生成，“跳过”按钮跳过此金手指 ---']""",
            "force_generate": """['--- “生成”与“跳过”按钮均会生成此金手指 ---']""",
            "force_discard": """['--- “生成”与“跳过”按钮均会跳过此金手指 ---']""",

            "discard_or_regen": """['--- “生成”与“跳过”按钮均会跳过此金手指，或使用“重新生成”按钮重新定位 ---']""",
            "choose_or_regen": """['--- “生成”按钮使用“新版ASM源码窗口”高亮地址生成，“跳过”按钮跳过此金手指，或使用“重新生成”按钮重新定位 ---']""",

            "wing_length_warn": """['*** 此处翼展宽度 = [金手指代码地址搜索区域，跳转目标地址搜索区域] ***']""",
            "value_warn": """['*** 这部分汇编码仅包含数值部分，请谨慎“生成”。 ***']""",
        },
        "str_map":
        {
            "addr_type_b": "跳转至",
            "asm_type_r": "普通",
            "asm_type_b": "branch跳转",

            "Cheat Code": "金手指",
            "Cheat Code Saved": "金手指已保存",
            "Saved": "已保存",
            "OK": "确定",
            "Cancel": "取消",
            "NSO File": "NSO文件",
            "NSO File Saved": "NSO文件已保存",
            "File save failed": "文件保存失败",
        }
    }
}