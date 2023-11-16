code_pattern = {
    "loc_EN":
    {
        "code_type_0x0":
        {
            "pattern": "r'^ *0[12][abcdef\d]{6} *( * [abcdef\d]{8}){2,3} *$'",
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
        "code_type_unknown":
        {
            "pattern": "r'^NEVER MATCH$'",
            "generate_type": 'force_discard',
            "description": 'Code Type Unknown: They Live Innocent and Pure',
            "details":
                    """[f'No unknowns were harmed in the making on this code.']"""
        }
    },
    "loc_CN":
        {
        "code_type_0x0":
        {
            "pattern": "r'^ 0[12][abcdef\d]{6} *( * [abcdef\d]{8}){0,3} *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0x0: 向指定内存地址存入数据',
            "details":
                    """[f'Code type 0x0 会向指定内存地址存入数据。']"""
        },
        "code_type_0x1":
        {
            "pattern": "r'^ *1[1248][0123][123456]00[abcdef\d]{2} *( * [abcdef\d]{8}){2,3} *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0x1: 开始循环标志',
            "details":
                """[f'Code type 0x1 将特定内存地址数据与某常量比较。',
                    '如果条件不满足，则跳过此指令至Code type 0x2之间的所有指令。']"""
        },
        "code_type_0x2":
        {
            "pattern": "r'^ *2[01]000000 *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0x2: 结束循环标志',
            "details":
                """[f'Code type 0x2 为循环结束标志 (循环始于 Code Type 0x1 或 Code Type 0x8)。',
                    '在使用else指令时，此结束标志前的所有代码都将被跳过。']"""
        },
        "code_type_0x3":
        {
            "pattern": "r'^ *3[01]0[abcdef\d]0000 *( * [abcdef\d]{8}){0,1} *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0x3: 开始/结束循环',
            "details":
                """[f'Code type 0x3 将执行本指令所指定次数的循环体。']"""
        },
        "code_type_0x4":
        {
            "pattern": "r'^ *400[abcdef\d]0000 *( * [abcdef\d]{8}){2} *$'",
            "generate_type": 'force_generate',
            "description": 'Code Type 0x4: 为寄存器载入某常量',
            "details":
                """[f'Code type 0x4 将会为指定寄存器加载某常量。']"""
        },
        "code_type_0x5":
        {
            "pattern": "r'^ *5[1248][0123][abcdef\d][01]0[abcdef\d]{2} * [abcdef\d]{8} *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0x5: 为寄存器载入某内存',
            "details":
                """[f'Code type 0x5 将会为指定寄存器加载某内存数据。']"""
        },
        "code_type_0x6":
        {
            "pattern": "r'^ *6[1248]0[abcdef\d][01][01][abcdef\d]0 *( * [abcdef\d]{8}){2} *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0x6: 将常量写入某内存',
            "details":
                """[f'Code type 0x6 将会为指定内存写入某寄存器常量数据。']"""
        },
        "code_type_0x7":
        {
            "pattern": "r'^ *7[1248]0[abcdef\d][01234]000 * [abcdef\d]{8} *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0x7: 算术运算（旧版）',
            "details":
                """[f'Code type 0x7 为算术运算指令。',
                    '但此指令已被更新的 Code type 0x9 替代，此处仅为保证后向兼容。']"""
        },
        "code_type_0x8":
        {
            "pattern": "r'^ *(8)[abcdef\d]{7} *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0x8: 按键触发标志',
            "details":
                    """[f'Code type 0x8 通过指定按键决定某条件单元是否被触发。']"""
        },
        "code_type_0x9":
        {
            "pattern": "r'^ *9[1248][\d][abcdef\d][abcdef\d][01][abcdef\d]0 *( * [abcdef\d]{8}){0,2} *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0x9: 算术运算',
            "details":
                """[f'Code type 0x9 允许用户在寄存器上进行算术运算。']"""
        },
        "code_type_0xA":
        {
            "pattern": "r'^ *A[1248][abcdef\d]{2}[01][012345][abcdef\d]{2} *( * [abcdef\d]{8}){0,1} *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0xA: 将寄存器数据写入内存',
            "details":
                """[f'Code type 0xA 允许将寄存器数据写入内存。']"""
        },
        "code_type_0xC0":
        {
            "pattern": "r'^ *C0[1248][123456][abcdef\d][012345][abcdef\d]{2} *( * [abcdef\d]{8}){0,2} *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0xC0: 寄存器开始循环标志',
            "details":
                """[f'Code type 0xC0 将寄存器值与另一值比较。'
                    '如果不满足，则跳过之后循环体。']"""
        },
        "code_type_0xC1":
        {
            "pattern": "r'^ *C10[abcdef\d]0[abcdef\d][0123]0 *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0xC1: 写入寄存器',
            "details":
                """[f'Code type 0xC1 提供写入寄存器功能。']"""
        },
        "code_type_0xC2":
        {
            "pattern": "r'^ *C2[0123]0[abcdef\d]{4} *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0xC2: 写入寄存器（含掩码）',
            "details":
                """[f'Code type 0xC2 提供通过掩码同时写入多个寄存器的功能。']"""
        },
        "code_type_0xC3":
        {
            "pattern": "r'^ *C3000[078F][0F][abcdef\d] *$'",
            "generate_type": 'flat_generate',
            "description": 'Code Type 0xC3: 读/写静态寄存器',
            "details":
                """[f'Code type 0xC3 将读/写某静态寄存器至指定寄存器。']"""
        },
        "code_type_unknown":
        {
            "pattern": "r'^NEVER MATCH$'",
            "generate_type": 'force_discard',
            "description": 'Code Type Unknown: 你瞅啥？',
            "details":
                    """[f'这搭哪滴了它？']"""
        }
    }
}

localization = {
    "loc_EN":
        {
            "title": "Code Updater for Nintendo Switch ver 1.0.2",
            "wing_length_default": "[1, 1]",
            "extra_wing_length_default": "[2, 2]",
            "hints_map":
            {
                "Old Main File:": "Old Main File:",
                "New Main File:": "New Main File:",
                "ARM64": "Force ARM64",
                "Input Old Codes:": "Input Old Codes:",
                "Current Processing Codes:": "Current Processing Codes:",
                "Wing Length:": "Wing Length:",
                "Logs:": "Logs:",
                "New Codes Output:": "New Codes Output:",
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
                "Generate": "Generate",
                "Skip": "Skip",
                "Undo": "Undo",
                "Restart": "Restart",
                "SaveCHT": "SaveCHT",
                "SaveNSO": "SaveNSO",
                "GitHub": "Github",
                "Update": "Update",
                "Prev": "Prev Addr",
                "Next": "Next Addr",
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
                "Extract NCA": """['Extracting NCA from game package ......']""",
                "Extract ticket": """['Extracting ticket content from .tik ......']""",
                "Extract main": """['Extracting main file from .nca ......']""",

                "NOT NSO File": """['NOT NSO File.']""",
                "NSO file decompressed": """['NSO file decompressed.']""",
                "BID message": """[f'BID of the old codes should be "{self.old_main_file.ModuleId.upper()}".']""",
                "Pre-process message": """['080X0000 codes have been splited into 04 atom codes.']""",

                "nsnsotool warning": """['nsnsotool failed working']""",
                "nsnsotool missing": """['tools/nsnsotool.exe missing']""",

                "Wing length check message": """['Wing length must be int or list, eg. "20", "[15,10]". Setting to default value.']""",
                "Extra wing length check message": """['Extra wing length must be int or list, eg. "20", "[15,10]". Setting to default value.']""",

                "code_title": """['This is code title.']""",
                "master_code_title": """['This is master code title.']""",
                "asm_code": """[f'This is{asm_type} assembly code.']""",

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

                "Cheat Code": """['Cheat Code']""",
                "Saved": """['Saved']""",
                "OK": """['OK']""",
                "Cancel": """['Cancel']""",
                "NSO File": """['NSO File']""",
            }
        },
 "loc_CN":
         {
            "title": "金手指自动更新器 ver 1.0.1c",
            "wing_length_default": "[1, 1]",
            "extra_wing_length_default": "[2, 2]",
            "hints_map":
            {
                "Old Main File:": "金手指对应Main：",
                "New Main File:": "目标版本Main：",
                "ARM64": "强制ARM64",
                "Input Old Codes:": "旧金手指输入：",
                "Current Processing Codes:": "当前处理金手指：",
                "Wing Length:": "翼展宽度：",
                "Logs:": "提示：",
                "New Codes Output:": "新金手指输出：",
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
                "Generate": "生成",
                "Skip": "跳过",
                "Undo": "撤销",
                "Restart": "重置",
                "SaveCHT": "保存CHT",
                "SaveNSO": "保存NSO",
                "GitHub": "Github",
                "Update": "更新",
                "Prev": "上个地址",
                "Next": "下个地址",
                "copy": "复制",
                "paste": "粘贴",
                "cut": "剪切",
            },
            "msg_map":
            {
                "request keys": """['本程序根目录下未找到 "keys.txt" 文件，无法自动解包游戏。']""",
                "required title key version": """[f'"keys.txt"中未找到"titlekek_{hex(masterKeyRev-1)[2:].zfill(2)}"!']""",
                "required master key version": """[f'"keys.txt"中未找到"master_key_{hex(masterKeyRev-1)[2:].zfill(2)}"!']""",
                ".nso extraction failed": """['从游戏中提取 "main" 文件失败']""",
                "Unpack Warning": """[f'解包 "{Path(file_path).suffix}" 文件需要一段时间，请耐心等待']""",
                "Extract NCA": """['从游戏包提取NCA文件中......']""",
                "Extract ticket": """['从.tik获取相关信息中......']""",
                "Extract main": """['从.nca提取main文件中......']""",

                "NOT NSO File": """['文件不合法']""",
                "NSO file decompressed": """['已自动解压main文件']""",
                "BID message": """[f'金手指文件名（BID）必须为 "{self.old_main_file.ModuleId.upper()}"']""",
                "Pre-process message": """['080X0000金手指代码已自动缩减为04原子代码']""",

                "nsnsotool warning": """['nsnsotool未正常工作']""",
                "nsnsotool missing": """['tools/nsnsotool.exe文件丢失']""",

                "Wing length check message": """['翼展宽度必须为整数，如："20"，"[15,10]"']""",
                "Extra wing length check message": """['额外翼展宽度必须为整数，如："20"，"[15,10]"']""",

                "code_title": """['这是普通码标题。']""",
                "master_code_title": """['这是大师码标题。']""",
                "asm_code": """[f'这是{asm_type} 汇编码。']""",

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

                "Cheat Code": """['Cheat Code']""",
                "Saved": """['Saved']""",
                "OK": """['OK']""",
                "Cancel": """['Cancel']""",
                "NSO File": """['NSO File']""",
            }
        }
}