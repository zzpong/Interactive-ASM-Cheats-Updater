localization = {
    "loc_EN":
        {
            "title": "Interactive ASM Cheats Updater ver 0.1",
            "wing_length_default": "[1, 1]",
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
                "Load New Main NSO File": "Load New Main NSO File",
                "Save new cheats": "Save new cheats"
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
                "cut": "cut"
            },
            "msg_map":
            {
                "NOT NSO File": """['NOT NSO File.']""",
                "DIR already exists": """['DIR already exists.']""",
                "NSO file decompressed": """['NSO file decompressed.']""",
                "BID message": """[f'BID of cheat code should be "{self.main_old_file.ModuleId.upper()}".']""",
                "Pre-process message": """['080X0000 cheat codes have been splited into 04.']""",
                "Wing length check message": """['Wing length must be int or list, eg. "20", "[15,10]". Setting to default value.']""",
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
                        '--- Press "generate" to export the FIRST match, "skip" to discard or "regenerate" ---']""",
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
                        '--- Press "generate" to export the FIRST match, "skip" to discard or "regenerate" ---']""",
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
                        '--- Press "generate" to export the FIRST match, "skip" to discard or "regenerate", branch link unchanged ---',
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
                        '--- Press "generate" to export the FIRST match, "skip" to discard or "regenerate" ---',
                        '*** wing length = [search area for Address, search area for Branch link] for NOW ***']""",
                "asm_bl_single_to_multi":
                    """['This part is asm bl code.',
                        f'Address [{hit_start_addr_str}] located.',
                        f'Multiple branch link [{bl_target_hit_start_addr_str}] located.',
                        '--- Press "generate" to export, "skip" to discard or "regenerate", FIRST match branch link selected ---'
                        '*** wing length = [search area for Address, search area for Branch link] for NOW ***']""",
                "asm_bl_multi_to_single":
                    """['This part is asm bl code.',
                        f'Multiple address [{hit_start_addr_str}] located.',
                        f'Branch link [{bl_target_hit_start_addr_str}] located.',
                        '--- Press "generate" to export the FIRST match, "skip" to discard or "regenerate" ---',
                        '*** wing length = [search area for Address, search area for Branch link] for NOW ***']""",
                "asm_bl_single_to_single":
                    """['This part is asm bl code.',
                        f'Address [{hit_start_addr_str}] located.',
                        f'Branch link [{bl_target_hit_start_addr_str}] located.',
                        '--- Press "generate" to export or "skip" to discard ---',
                        '*** wing length = [search area for Address, search area for Branch link] for NOW ***']""",
                "asm_bl_multi_to_exist":
                    """[f'This part is asm bl code. Multiple address [{hit_start_addr_str}] located.',
                        '--- Press "generate" to export the FIRST match, "skip" to discard or "regenerate" ---']""",
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
        }
}