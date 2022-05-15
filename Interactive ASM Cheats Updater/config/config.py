localization = {
    "loc_EN":
        {
            "title": "Interactive ASM Cheats Updater ver 0.3",
            "wing_length_default": "[1, 1]",
            "loc_extra_wing_length_default": "[2, 2]",
            "hints_map":
            {
                "Old Main File:": "Old Main File:",
                "New Main File:": "New Main File:",
                "Debug": "Debug",
                "Copy old cheats here:": "Copy old cheats here:",
                "Current processing cheat:": "Current processing cheat:",
                "Wing Length:": "Wing Length:",
                "Logs:": "Logs:",
                "New cheats will be here:": "New cheats will be here:",
                "Load Old Main NSO File": "Load Old Main NSO File",
                "Load New Main NSO File": "Load New Main NSO File",
                "Save new cheats": "Save new cheats",
                "Old Main ASM:": "Old Main ASM:",
                "New Main ASM:": "New Main ASM:",
                "Extra Wing Length:": "Extra Length:",
                # "Branch": "Switch to Branch Target ASM Code"
                "Branch": "Switch to BL Target"
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
                "copy": "copy",
                "paste": "paste",
                "cut": "cut",
                "Update": "Update",
                "Prev": "Prev Addr",
                "Next": "Next Addr"
            },
            "msg_map":
            {
                "NOT NSO File": """['NOT NSO File.']""",
                "DIR already exists": """['DIR already exists.']""",
                "NSO file decompressed": """['NSO file decompressed.']""",
                "BID message": """[f'BID of cheat code should be "{self.main_old_file.ModuleId.upper()}".']""",
                "Pre-process message": """['080X0000 cheat codes have been splited into 04.']""",
                "Wing length check message": """['Wing length must be int or list, eg. "20", "[15,10]". Setting to default value.']""",
                "Extra wing length check message": """['Extra wing length must be int or list, eg. "20", "[15,10]". Setting to default value.']""",
                "Unknown cheat format": """[f'Unknown cheat format removed: {i}']""",
                "Cheat Code": """['Cheat Code']""",
                "Saved": """['Saved']""",
                "OK": """['OK']""",
                "Cancel": """['Cancel']""",
                "nsnsotool warning": """['nsnsotool failed working']""",
                "nsnsotool missing": """['tools/nsnsotool.exe missing']""",
                "asm_normal_asm_no_addr": 
                    """[f'This part is normal asm code. No address located, please change wing length and regenerate.',
                        '--- Both "generate" or "skip" will discard, "regenerate" to research ---']""",
                "asm_normal_asm_multi_addr": 
                    """[f'This part is normal asm code. Multiple address [{hit_start_addr_str}] located.',
                        '--- Press "generate" to export the match that highlighted in New Main ASM window, "skip" to discard or "regenerate" ---']""",
                "asm_normal_asm_single_addr":
                    """[f'This part is normal asm code. Address [{hit_start_addr_str}] located.',
                        '--- Press "generate" to export or "skip" to discard ---']""",
                "asm_bl_cave_no_cave":
                    """['This part is asm bl code in code cave. However, there is NO SPACE in the new game version.',
                        '--- Both "generate" or "skip" will discard ---']""",
                "asm_bl_cave_no_space":
                    """['This part is asm bl code in code cave. Space of code cave in new game is critical now, you can skip other code cave to save this one.',
                        '--- Both "generate" or "skip" will discard ---']""",
                "asm_bl_cave_has_space":
                    """[f'This part is asm bl code in code cave. New code cave {code_cave_addr} find.',
                        '--- Press "generate" to export or "skip" to discard ---']""",
                "asm_bl_cave_to_outer":
                    """['This part is asm bl code in code cave, but it points to .datasegment.',
                        f'New code cave {code_cave_addr} find.',
                        '--- Both "generate" or "skip" will discard ---']""",
                "asm_bl_cave_to_cave":
                    """['This part is asm bl code in code cave, but it points to code cave address which is not an asm code.',
                        f'New code cave {code_cave_addr} find.',
                        f'--- Both "generate" or "skip" will discard ---']""",
                "asm_bl_cave_no_addr":
                    """['This part is asm bl code in code cave.',
                        f'New code cave {code_cave_addr} find.',
                        'Branch link search failed.',
                        '--- Press "generate" to export original branch link address, "skip" to discard or "regenerate" ---']""",
                "asm_bl_cave_multi_addr":
                    """['This part is asm bl code in code cave.',
                        f'New code cave {code_cave_addr} find.',
                        f'Multiple branch link [{bl_target_hit_start_addr_str}] located.',
                        '--- Press "generate" to export the match that highlighted in New Main ASM window, "skip" to discard or "regenerate" ---']""",
                "asm_bl_cave_single_addr":
                    """['This part is asm bl code in code cave.',
                        f'New code cave {code_cave_addr} find.',
                        f'Branch link [{bl_target_hit_start_addr_str}] located.',
                        '--- Press "generate" to export or "skip" to discard ---']""",
                "asm_bl_no_addr":
                    """['This part is asm bl code. No address located, please change wing length and regenerate.',
                        '--- Both "generate" or "skip" will discard, "regenerate" to research ---']""",
                "asm_bl_to_outer":
                    """['This part is asm bl code which points to .datasegment, please check if any mistake happens.',
                        '--- Both "generate" or "skip" will discard ---']""",
                "asm_bl_to_cave":
                    """['This part is asm bl code, but it points to code cave address which is not an asm code.'
                        '--- Both "generate" or "skip" will discard ---']""",
                "asm_bl_multi_to_none":
                    """['This part is asm bl code.',
                        f'Multiple address [{hit_start_addr_str}] located.',
                        'Branch link search failed.',
                        '--- Press "generate" to export the match that highlighted in New Main ASM window, "skip" to discard or "regenerate", branch link unchanged ---',
                        '*** wing length = [search area for Address, search area for Branch link] for NOW ***']""",
                "asm_bl_single_to_none":
                    """['This part is asm bl code.',
                        f'Address [{hit_start_addr_str}] located.',
                        'Branch link search failed.',
                        '--- Press "generate" to export or "skip" to discard, branch link unchanged ---',
                        '*** wing length = [search area for Address, search area for Branch link] for NOW ***']""",
                "asm_bl_multi_to_multi":
                    """['This part is asm bl code.',
                        f'Multiple address [{hit_start_addr_str}] located.',
                        f'Multiple branch link [{bl_target_hit_start_addr_str}] located.',
                        '--- Press "generate" to export the match that highlighted in New Main ASM window, "skip" to discard or "regenerate" ---',
                        '*** wing length = [search area for Address, search area for Branch link] for NOW ***']""",
                "asm_bl_single_to_multi":
                    """['This part is asm bl code.',
                        f'Address [{hit_start_addr_str}] located.',
                        f'Multiple branch link [{bl_target_hit_start_addr_str}] located.',
                        '--- Press "generate" to export, "skip" to discard or "regenerate", the branch link match that highlighted in New Main ASM window selected ---'
                        '*** wing length = [search area for Address, search area for Branch link] for NOW ***']""",
                "asm_bl_multi_to_single":
                    """['This part is asm bl code.',
                        f'Multiple address [{hit_start_addr_str}] located.',
                        f'Branch link [{bl_target_hit_start_addr_str}] located.',
                        '--- Press "generate" to export the match that highlighted in New Main ASM window, "skip" to discard or "regenerate" ---',
                        '*** wing length = [search area for Address, search area for Branch link] for NOW ***']""",
                "asm_bl_single_to_single":
                    """['This part is asm bl code.',
                        f'Address [{hit_start_addr_str}] located.',
                        f'Branch link [{bl_target_hit_start_addr_str}] located.',
                        '--- Press "generate" to export or "skip" to discard ---',
                        '*** wing length = [search area for Address, search area for Branch link] for NOW ***']""",
                "asm_bl_multi_to_exist":
                    """[f'This part is asm bl code. Multiple address [{hit_start_addr_str}] located.',
                        '--- Press "generate" to export the match that highlighted in New Main ASM window, "skip" to discard or "regenerate" ---']""",
                "asm_bl_single_to_exist":
                    """[f'This part is asm bl code. Address [{hit_start_addr_str}] located.',
                        '--- Press "generate" to export or "skip" to discard ---']""",
                "no_code":
                    """['This part is cheat title or comments which has no effect on cheat functions.',
                        '--- Press "generate" to export or "skip" to discard ---']""",
                "code_but_no_asm":
                    """['This part is memory cheat which always changes with updates.',
                        '--- Press "generate" to export all or "skip" to export title only ---']""",
                "asm_title":
                    """['This part is title of asm code.',
                        '--- Both "generate" and "skip" will export the title ---']""",
                "asm_normal_code":
                    """['This part is normal code part of asm code, which always changes with updates.',
                        '--- Press "generate" to export or "skip" to discard ---']""",
                "asm_cave_code_no_cave":
                    """['This part is code cave of asm code. However, there is NO SPACE in the new game version.',
                        '--- Both "generate" or "skip" will discard ---']""",
                "asm_cave_code_no_space":
                    """['This part is code cave of asm code. Space of code cave in new game is critical now, you can skip other code cave to save this one.',
                        '--- Both "generate" or "skip" will discard ---']""",
                "asm_cave_code_has_space":
                    """[f'This part is code cave of asm bl code. New code cave {code_cave_addr} find.',
                        '--- Press "generate" to export or "skip" to discard ---']"""
            }
        },
 "loc_CN":
        {
            "title": "金手指自动更新器 ver 0.3c",
            "wing_length_default": "[1, 1]",
            "loc_extra_wing_length_default": "[2, 2]",
            "hints_map":
            {
                "Old Main File:": "金手指对应Main:",
                "New Main File:": "目标版本Main:",
                "Debug": "调试",
                "Copy old cheats here:": "旧版金手指输入:",
                "Current processing cheat:": "当前处理金手指:",
                "Wing Length:": "翼展宽度:",
                "Logs:": "提示:",
                "New cheats will be here:": "新版本金手指输出:",
                "Load Old Main NSO File": "载入旧版Main文件",
                "Load New Main NSO File": "载入新版Main文件",
                "Save new cheats": "保存新版金手指",
                "Old Main ASM:": "旧版ASM源码:",
                "New Main ASM:": "新版ASM源码:",
                "Extra Wing Length:": "额外宽度:",
                # "Branch": "切换至跳转目标区域ASM代码"
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
                "copy": "复制",
                "paste": "粘贴",
                "cut": "剪切",
                "Update": "更新",
                "Prev": "上个地址",
                "Next": "下个地址"
            },
            "msg_map":
            {
                "NOT NSO File": """['文件不合法']""",
                "DIR already exists": """['路径已存在']""",
                "NSO file decompressed": """['已自动解压Main文件']""",
                "BID message": """[f'金手指文件名（BID）必须为 "{self.main_old_file.ModuleId.upper()}"']""",
                "Pre-process message": """['080X0000金手指代码已自动缩减为04原子代码']""",
                "Wing length check message": """['翼展宽度必须为整数，如："20"，"[15,10]"']""",
                "Extra wing length check message": """['额外宽度必须为整数，如："20"，"[15,10]"']""",
                "Unknown cheat format": """[f'未知金手指代码已移除：{i}']""",
                "Cheat Code": """['金手指代码']""",
                "Saved": """['已保存']""",
                "OK": """['确定']""",
                "Cancel": """['取消']""",
                "nsnsotool warning": """['nsnsotool未正常工作']""",
                "nsnsotool missing": """['tools/nsnsotool.exe文件丢失']""",
                "asm_normal_asm_no_addr": 
                    """[f'这是普通ASM金手指代码，未找到新地址，请修改翼展宽度并点击重新生成按钮。',
                        '--- “生成”与“跳过”按钮均会跳过生成，或使用“重新生成”按钮重新搜索 ---']""",
                "asm_normal_asm_multi_addr": 
                    """[f'这是普通ASM金手指代码，多个新地址[{hit_start_addr_str}]已定位。',
                        '--- 使用“生成”按钮导出“新版ASM源码窗口”高亮地址，“跳过”按钮跳过生成，或点击“重新生成”按钮 ---']""",
                "asm_normal_asm_single_addr":
                    """[f'这是普通ASM金手指代码，单个新地址[{hit_start_addr_str}]已定位。',
                        '--- 使用“生成”按钮生成，或“跳过”按钮均跳过生成金手指 ---']""",
                "asm_bl_cave_no_cave":
                    """['这是在code cave中的ASM跳转代码，可惜新版本中并未找到code cave空间。',
                        '--- “生成”与“跳过”按钮均会跳过生成 ---']""",
                "asm_bl_cave_no_space":
                    """['这是在code cave中的ASM跳转代码。新版本code cave空间占用已满，请移除其他code cave代码后重试。',
                        '--- “生成”与“跳过”按钮均会跳过生成 ---']""",
                "asm_bl_cave_has_space":
                    """[f'这是在code cave中的ASM跳转代码。新code cave {code_cave_addr} 已定位。',
                        '--- 使用“生成”按钮生成，或“跳过”按钮均跳过生成金手指 ---']""",
                "asm_bl_cave_to_outer":
                    """['这是在code cave中的ASM跳转代码，但其指向无效空间.datasegment。',
                        f'新code cave {code_cave_addr} 已定位。',
                        '--- “生成”与“跳过”按钮均会跳过生成 ---']""",
                "asm_bl_cave_to_cave":
                    """['这是在code cave中的ASM跳转代码，但其指向非ASM代码。',
                        f'新code cave {code_cave_addr} 已定位。',
                        f'--- “生成”与“跳过”按钮均会跳过生成 ---']""",
                "asm_bl_cave_no_addr":
                    """['这是在code cave中的ASM跳转代码。',
                        f'新code cave {code_cave_addr} 已定位。',
                        '跳转地址定位失败。',
                        '--- 使用“生成”按钮导出原始跳转地址，“跳过”按钮跳过生成，或点击“重新生成”按钮 ---']""",
                "asm_bl_cave_multi_addr":
                    """['这是在code cave中的ASM跳转代码。',
                        f'新code cave {code_cave_addr} 已定位。',
                        f'多跳转地址 [{bl_target_hit_start_addr_str}] 已定位。',
                        '--- 使用“生成”按钮导出“新版ASM源码窗口”高亮地址，“跳过”按钮跳过生成，或点击“重新生成”按钮 ---']""",
                "asm_bl_cave_single_addr":
                    """['这是在code cave中的ASM跳转代码。',
                        f'新code cave {code_cave_addr} 已定位。',
                        f'单跳转地址 [{bl_target_hit_start_addr_str}] 已定位。',
                        '--- 使用“生成”按钮生成，或“跳过”按钮均跳过生成金手指 ---']""",
                "asm_bl_no_addr":
                    """['这是ASM跳转代码，未定位到地址，请修改翼展宽度后重新生成。',
                        '--- “生成”与“跳过”按钮均会跳过生成，或使用“重新生成”按钮重新搜索 ---']""",
                "asm_bl_to_outer":
                    """['这是ASM跳转代码，但指向.datasegment，请查看金手指代码是否有误。',
                        '--- “生成”与“跳过”按钮均会跳过生成 ---']""",
                "asm_bl_to_cave":
                    """['这是ASM跳转代码，但其指向非ASM代码。'
                        '--- “生成”与“跳过”按钮均会跳过生成 ---']""",
                "asm_bl_multi_to_none":
                    """['这是ASM跳转代码。',
                        f'多个新地址 [{hit_start_addr_str}] 已定位。',
                        '跳转地址定位失败。',
                        '--- 使用“生成”按钮导出“新版ASM源码窗口”高亮地址，“跳过”按钮跳过生成，或点击“重新生成”按钮。当前跳转地址未变更 ---',
                        '*** 此处翼展宽度 = [金手指代码地址搜索区域，跳转目标地址搜索区域] ***']""",
                "asm_bl_single_to_none":
                    """['这是ASM跳转代码。',
                        f'单个新地址 [{hit_start_addr_str}] 已定位。',
                        '跳转地址定位失败。',
                        '--- 使用“生成”按钮生成，或“跳过”按钮均跳过生成金手指。当前跳转地址未变更 ---',
                        '*** 此处翼展宽度 = [金手指代码地址搜索区域，跳转目标地址搜索区域] ***']""",
                "asm_bl_multi_to_multi":
                    """['这是ASM跳转代码。',
                        f'多个新地址 [{hit_start_addr_str}] 已定位。',
                        f'多跳转地址 [{bl_target_hit_start_addr_str}] 已定位。',
                        '--- 使用“生成”按钮导出“新版ASM源码窗口”高亮地址，“跳过”按钮跳过生成，或点击“重新生成”按钮 ---',
                        '*** 此处翼展宽度 = [金手指代码地址搜索区域，跳转目标地址搜索区域] ***']""",
                "asm_bl_single_to_multi":
                    """['这是ASM跳转代码。',
                        f'单个新地址 [{hit_start_addr_str}] 已定位。',
                        f'多跳转地址 [{bl_target_hit_start_addr_str}] 已定位。',
                        '--- 使用“生成”按钮导出“新版ASM源码窗口”高亮地址，“跳过”按钮跳过生成，或点击“重新生成”按钮 ---'
                        '*** 此处翼展宽度 = [金手指代码地址搜索区域，跳转目标地址搜索区域] ***']""",
                "asm_bl_multi_to_single":
                    """['这是ASM跳转代码。',
                        f'多个新地址 [{hit_start_addr_str}] 已定位。',
                        f'单跳转地址 [{bl_target_hit_start_addr_str}] 已定位。',
                        '--- 使用“生成”按钮导出“新版ASM源码窗口”高亮地址，“跳过”按钮跳过生成，或点击“重新生成”按钮 ---',
                        '*** 此处翼展宽度 = [金手指代码地址搜索区域，跳转目标地址搜索区域] ***']""",
                "asm_bl_single_to_single":
                    """['这是ASM跳转代码。',
                        f'单个新地址 [{hit_start_addr_str}] 已定位。',
                        f'单跳转地址 [{bl_target_hit_start_addr_str}] 已定位。',
                        '--- 使用“生成”按钮生成，或“跳过”按钮均跳过生成金手指 ---',
                        '*** 此处翼展宽度 = [金手指代码地址搜索区域，跳转目标地址搜索区域] ***']""",
                "asm_bl_multi_to_exist":
                    """[f'这是ASM跳转代码。 多个新地址 [{hit_start_addr_str}] 已定位。',
                        '--- 使用“生成”按钮导出“新版ASM源码窗口”高亮地址，“跳过”按钮跳过生成，或点击“重新生成”按钮 ---']""",
                "asm_bl_single_to_exist":
                    """[f'这是ASM跳转代码。 地址 [{hit_start_addr_str}] 已定位。',
                        '--- 使用“生成”按钮生成，或“跳过”按钮均跳过生成金手指 ---']""",
                "no_code":
                    """['这是不影响金手指功能的标题或注释文本。',
                        '--- 使用“生成”按钮生成，或“跳过”按钮均跳过生成金手指 ---']""",
                "code_but_no_asm":
                    """['这是金手指的内存代码部分，它基本每次都随游戏版本变化，无法自动更新。',
                        '--- 使用“生成”按钮导出全部内容，或“跳过”按钮仅导出标题 ---']""",
                "asm_title":
                    """['这是ASM代码的标题。',
                        '--- “生成”与“跳过”按钮均会仅导出标题 ---']""",
                "asm_normal_code":
                    """['这是ASM代码中的内存代码部分，它基本每次都随游戏版本变化，无法自动更新。',
                        '--- 使用“生成”按钮生成，或“跳过”按钮均跳过生成金手指 ---']""",
                "asm_cave_code_no_cave":
                    """['这是在code cave中的ASM代码，但新版本游戏中不存在code cave。',
                        '--- “生成”与“跳过”按钮均会跳过生成 ---']""",
                "asm_cave_code_no_space":
                    """['这是在code cave中的ASM代码，但新版本code cave空间占用已满，请移除其他code cave代码后重试。',
                        '--- “生成”与“跳过”按钮均会跳过生成 ---']""",
                "asm_cave_code_has_space":
                    """[f'这是在code cave中的ASM代码，新code cave {code_cave_addr} 已定位。',
                        '--- 使用“生成”按钮生成，或“跳过”按钮均跳过生成金手指 ---']"""
            }
        }
}