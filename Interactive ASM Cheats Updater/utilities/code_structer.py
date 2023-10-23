import re
from tkinter import messagebox
from capstone import *
from keystone import *

    
def create_one_msg(msg: str):
    return msg + '\n'

def remove_redudent_linebreak(msg: str):
    msg = remove_redudent_pre_linebreak(msg)
    msg = remove_redudent_post_linebreak(msg)
    return msg

def remove_redudent_pre_linebreak(msg: str):
    while msg != '' and msg[0] == '\n':
        msg = msg[1:]
    return msg

def remove_redudent_post_linebreak(msg: str):
    while msg != '' and msg[-1] == '\n':
        msg = msg[:-1]
    return msg

def is_code(msg: str):
    try:
        code = re.split(' ', msg)
        int(code[0], 16)
        return True
    except:
        return False

def is_title(msg: str):
    return '[' in msg or '{' in msg

def remove_inner_code_linebreak(code_list: list):
    purified_code_list = []
    linebreak_cache = []
    has_linebreak = False

    for index in range(len(code_list)):
        if code_list[index] != '\n':
            if is_title(code_list[index]) and has_linebreak:
                purified_code_list.extend(linebreak_cache)
            purified_code_list.append(code_list[index])
            linebreak_cache = []
            has_linebreak = False
            continue

        if index - 1 < 0:
            purified_code_list.append(code_list[index])
            continue

        if has_linebreak:
            linebreak_cache.append(code_list[index])
            continue

        if is_code(code_list[index-1][:-1]) or is_title(code_list[index-1]):
            linebreak_cache.append(code_list[index])
            has_linebreak = True
    
    return purified_code_list

def bytes_to_int(bytearray):
    return int.from_bytes(bytearray, byteorder='big', signed=False)


class PseudoStack:
    def __init__(self) -> None:
        self.body = []
    
    def push(self, elem):
        self.body.append(elem)
    
    def pop(self):
        if len(self.body) == 0:
            return None
        else:
            elem = self.body[-1]
            del self.body[-1]
            return elem
    
    def clear(self):
        self.body = []
    
    def get(self):
        if len(self.body) == 0:
            return None
        else:
            return self.body[-1]
            
class CodeStruct:
    def __init__(self, raw_text: str, globalInfo, file_bundle, force_ASM64 = False) -> None:
        self.logger = globalInfo.logger
        self.msg_map = globalInfo.msg_map
        self.code_pattern = globalInfo.code_pattern
        self.old_main_file = file_bundle[0]
        self.new_main_file = file_bundle[1]

        self.code_text = self.normalize_code(raw_text)
        if not force_ASM64:  # Hints: Any static value writing to memory can be disassembled as ASM32 code
            self.ASM_type = self.check_ASM_type()
        else:
            self.ASM_type = 'ARM64'
        self.generate_code_struct()
    
    def normalize_code(self, raw_text: str):
        pattern_code_title = re.compile(r'^ *(\[.*\]) *$')
        pattern_master_code_title = re.compile(r'^ *(\{.*\}) *$')
        # pattern_code = re.compile(r'^ *([abcdef\d]{8}) *( * [abcdef\d]{8}){0,3} *$', re.I)
        pattern_code = re.compile(r'^ *([abcdef\d]{8}) *([abcdef\d]{8})? *([abcdef\d]{8})? *([abcdef\d]{8})? *$', re.I)
        pattern_long_asm_code = re.compile(r'^ *080([abcdef\d])0000 *([abcdef\d]{8}) *([abcdef\d]{8}) *([abcdef\d]{8}) *$', re.I)

        code_list_raw = re.split('\n{2,}', remove_redudent_linebreak(raw_text))
        self.code_list = []
        code_text = ''
        is_splited = False
        has_content = False
        has_unknown = False

        for code in code_list_raw:
            code_chunk_list = re.split('\n', code)
            for code_chunk in code_chunk_list:
                if (pattern_code_title.match(code_chunk) is not None
                        or pattern_master_code_title.match(code_chunk) is not None):
                    self.code_list.append(create_one_msg(code_chunk))
                    has_content = True
                    continue

                pattern = pattern_long_asm_code.match(code_chunk)
                if pattern is not None:
                    self.code_list.append(create_one_msg(f'040{pattern.group(1).upper()}0000 {pattern.group(2).upper()} {pattern.group(4).upper()}'))
                    next_addr = hex(int(pattern.group(2), 16) + 4)[2:].zfill(8).upper()
                    self.code_list.append(create_one_msg(f'040{pattern.group(1).upper()}0000 {next_addr} {pattern.group(3).upper()}'))
                    is_splited = True
                    has_content = True
                    continue
                
                pattern = pattern_code.match(code_chunk)
                if pattern_code.match(code_chunk) is not None:
                    self.code_list.append(create_one_msg(' '.join(pattern.group(i).upper() for i in range(1, len(pattern.groups())) if pattern.group(i) is not None)))
                    has_content = True
                    continue
                
                if has_content:  # Hints: code + \n + unknown + (\n) + code
                    if not has_unknown:
                        self.code_list.append('\n')
                        has_unknown = True

            if has_content and not has_unknown:  # Hints: code + unknown + \n + code
                self.code_list.append('\n')
            has_content = False
            has_unknown = False

        self.code_list = remove_inner_code_linebreak(self.code_list)  # Hints: title/code_part + \n + code_part

        if is_splited:
            messagebox.showinfo(title='Info', message='\n'.join(eval(self.msg_map['Pre-process message'])))

        for code in self.code_list:
            code_text += code

        return remove_redudent_linebreak(code_text)

    def check_ASM_type(self):  # Hints: ASM Type should be consistent in one single main.elf
        pattern_asm_code = re.compile(r'^ *(040[abcdef\d]0000) *([abcdef\d]{8}) *([abcdef\d]{8}) *$', re.I)  # Hints: main only, no heap
        Disassembler_64 = Cs(CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN)
        Disassembler_32 = Cs(CS_ARCH_ARM, CS_MODE_LITTLE_ENDIAN)
        asm64_count = 0
        asm32_count = 0

        for code in self.code_list:
            pattern = pattern_asm_code.match(code[:-1])  # Hints: Remove '\n'
            if pattern is None:
                continue
            if pattern.group(3)[0:4] == '0000':  # Hints: Store value to memory could be misleaded to ASM32 code
                continue
            
            code_addr = int(pattern.group(2), 16)
            code_bytes = bytearray.fromhex(pattern.group(3))
            code_bytes.reverse()

            for _ in Disassembler_64.disasm(code_bytes, code_addr):
                asm64_count += 1
            for _ in Disassembler_32.disasm(code_bytes, code_addr):
                asm32_count += 1

        if asm64_count + asm32_count == 0:
            return 'ARM64'
        if asm64_count >= asm32_count:
            return 'ARM64'
        else:
            return 'ARM32'

    def is_title(self, msg: str):
        return (msg == 'code_title' or msg == 'master_code_title')
    
    def is_code(self, msg: str):
        return not is_title(msg)
    
    def get_code_struct_by_pos(self, code_dict: dict, position: list):
        return code_dict[str(position[0])][str(position[1])]
    
    def get_code_struct_type_by_pos(self, code_dict: dict, position: list):
        return code_dict[str(position[0])][str(position[1])]['type']

    def is_neighbor(self, addr_main, addr_extend: int):
        if not isinstance(addr_main, int):
            addr = addr_main[-1]
        return (abs(addr - addr_extend) == 4)

    def is_asm_code_mergable(self, asm_dict_main: dict, asm_dict_extend: dict):  # Hints: Branch cannot merge with anything, pure value merge with neighbor asm
        in_same_cave = asm_dict_main['contents']['in_code_cave'] and asm_dict_extend['contents']['in_code_cave']
        in_same_multi = asm_dict_main['contents']['multimedia_offset'] is not None and asm_dict_extend['contents']['multimedia_offset'] is not None
        in_same_main = (not asm_dict_main['contents']['in_code_cave'] and not asm_dict_extend['contents']['in_code_cave']
                            and asm_dict_main['contents']['multimedia_offset'] is None and asm_dict_extend['contents']['multimedia_offset'] is None)
        if (self.is_neighbor(asm_dict_main['contents']['addr'], asm_dict_extend['contents']['addr'])
                and (in_same_main or in_same_cave or in_same_multi)):
            if not (not asm_dict_main['contents']['is_value'][-1] and asm_dict_main['contents']['detail']['is_branch']):
                if not (not asm_dict_extend['contents']['is_value'] and asm_dict_extend['contents']['detail']['is_branch']):
                    return True

        return False

    def check_comb(self, code_chunk: dict, force_new_code = False):
        if sum(self.position) == 0 and not self.struct_initialized:
            self.struct_initialized = True
            return ('new_code', self.position)
        
        if force_new_code:
            return ('new_code', [self.position[0]+1, 0, 0])
        
        if self.get_code_struct_type_by_pos(self.code_struct, self.position) != code_chunk['type']:
            if self.is_code(code_chunk['type']):
                return ('new_chunk', [self.position[0], self.position[1]+1, 0])
            else:
                return ('new_code', [self.position[0]+1, 0, 0])

        if (self.get_code_struct_type_by_pos(self.code_struct, self.position) == code_chunk['type']
                and code_chunk['type'] != 'code_type_asm'):
                return ('merge_chunk', [self.position[0], self.position[1], self.position[2]+1])
            
        if self.is_asm_code_mergable(self.get_code_struct_by_pos(self.code_struct, self.position), code_chunk):
            return ('merge_chunk', [self.position[0], self.position[1], self.position[2]+1])
        else:
            return ('new_chunk', [self.position[0], self.position[1]+1, 0])

    def process_code_chunk_lite(self, code_chunk: dict, procedure: str, new_position: list):
        if procedure == 'new_code':
            self.code_struct.update(
                {
                    str(new_position[0]):
                    {
                        str(new_position[1]):
                        {
                            'type': code_chunk['type'],
                            'contents':
                                {
                                    'raw': [code_chunk['contents']['raw']]
                                }
                        }
                    }
                }
            )
        elif procedure == 'new_chunk':
            self.code_struct[str(new_position[0])].update(
                    {
                        str(new_position[1]):
                        {
                            'type': code_chunk['type'],
                            'contents':
                                {
                                    'raw': [code_chunk['contents']['raw']]
                                }
                        }
                    }
            )
        elif procedure == 'merge_chunk':
            self.get_code_struct_by_pos(self.code_struct, new_position)['contents']['raw'].append(
                code_chunk['contents']['raw'])

    def process_code_chunk_asm(self, code_chunk: dict, procedure: str, new_position: list):
        if procedure == 'new_chunk':
            if not code_chunk['contents']['is_value']:
                code_branch_detail = code_chunk['contents']['detail']['branch_detail']
                branch_detail = {
                            'branch_type': code_branch_detail['branch_type'],
                            'branch_addr': code_branch_detail['branch_addr'],
                            'branch_to_cave': code_branch_detail['branch_to_cave'],
                            'branch_to_multi': code_branch_detail['branch_to_multi'],
                            'branch_multi_offset': code_branch_detail['branch_multi_offset'],
                    } if code_chunk['contents']['detail']['is_branch'] else None
            
            detail = {
                        'disam': [code_chunk['contents']['detail']['disam']],
                        'is_branch': code_chunk['contents']['detail']['is_branch'],
                        'branch_detail': branch_detail
            } if not code_chunk['contents']['is_value'] else None

            self.code_struct[str(new_position[0])].update(
                    {
                        str(new_position[1]):
                        {
                            'type': code_chunk['type'],
                            'contents':
                                {
                                    'raw': [code_chunk['contents']['raw']],
                                    'head': [code_chunk['contents']['head']],
                                    'addr': [code_chunk['contents']['addr']],
                                    'body': [code_chunk['contents']['body']],
                                    'is_value': [code_chunk['contents']['is_value']],
                                    'in_code_cave': code_chunk['contents']['in_code_cave'],
                                    'multimedia_offset': code_chunk['contents']['multimedia_offset'],
                                    'detail': detail
                                }
                        }
                    }
            )

        elif procedure == 'merge_chunk':
            if not code_chunk['contents']['is_value']:
                if self.get_code_struct_by_pos(self.code_struct, new_position)['contents']['detail'] is not None:
                    self.get_code_struct_by_pos(self.code_struct, new_position)['contents']['detail']['disam'].append(
                        code_chunk['contents']['detail']['disam']
                    )
                else:
                    self.get_code_struct_by_pos(self.code_struct, new_position)['contents']['detail'] = {
                        'disam': [code_chunk['contents']['detail']['disam']],
                        'is_branch': False,
                        'branch_detail': None
                    }
            
            self.get_code_struct_by_pos(self.code_struct, new_position)['contents']['raw'].append(
                code_chunk['contents']['raw']
            )
            self.get_code_struct_by_pos(self.code_struct, new_position)['contents']['head'].append(
                code_chunk['contents']['head']
            )
            self.get_code_struct_by_pos(self.code_struct, new_position)['contents']['addr'].append(
                code_chunk['contents']['addr']
            )
            self.get_code_struct_by_pos(self.code_struct, new_position)['contents']['body'].append(
                code_chunk['contents']['body']
            )
            self.get_code_struct_by_pos(self.code_struct, new_position)['contents']['is_value'].append(
                code_chunk['contents']['is_value']
            )

    def generate_booklet(self, addr_dict: dict):
        addr_booklet = {}
        for key in addr_dict:
            if key not in addr_booklet:
                addr_booklet.update({
                    key: addr_dict[key]
                })
            else:
                addr_booklet[key].append(addr_dict[key])
        return addr_booklet

    def is_full_of_value(self, is_value_list: list):
        result = True
        for is_value in is_value_list:
            result = result and is_value
        return result

    def get_available_position(self, code_num: int, addr_list: list):
        position = []
        for addr in addr_list:
            if code_num == addr[0]:
                position.append(addr)
        return position if position != [] else None

    def link_branch_addr(self, code_branch_detail: dict, code_num: str, is_master_code: bool):
        addr = code_branch_detail['branch_addr']
        if str(addr) not in self.addr_dict:
            position = None
        elif is_master_code:
            position = self.addr_dict[str(addr)]   
        else:
            position = self.get_available_position(int(code_num), self.addr_dict[str(addr)])

        code_branch_detail.update({'branch_link': position})
        return position

    def add_broadcast_pointer(self, broadcast_position: list, target_position: list):
        contents = self.get_code_struct_by_pos(self.code_struct, broadcast_position)['contents']
        if 'broadcast' in contents:
            contents['broadcast'].append(target_position)
        else:
            contents.update({'broadcast': [target_position]})

    def link_pointer(self):
        for code_num in self.code_struct:
            is_master_code = False
            is_value_only = True

            for chunk_num in self.code_struct[code_num]:
                code_chunk = self.code_struct[code_num][chunk_num]
                if code_chunk['type'] == 'master_code_title':
                    is_master_code = True
                    continue

                if code_chunk['type'] == 'code_type_asm':
                    if not self.is_full_of_value(code_chunk['contents']['is_value']):
                        is_value_only = False
                    if code_chunk['contents']['detail'] is not None and code_chunk['contents']['detail']['is_branch']:
                        positions = self.link_branch_addr(code_chunk['contents']['detail']['branch_detail'], code_num, is_master_code)
                        if positions is not None:
                            for position in positions:
                                self.add_broadcast_pointer(position, [int(code_num), int(chunk_num), 0])

            self.code_struct[code_num].update(
                {
                    'info':
                    {
                        'is_master_code': is_master_code,
                        'is_value_only': is_value_only
                    }
                }
            )

    def process_code_chunk(self, code_chunk: dict, procedure: str, new_position: list):    
        if code_chunk['type'] != 'code_type_asm':
            self.process_code_chunk_lite(code_chunk, procedure, new_position)
        else:
            self.process_code_chunk_asm(code_chunk, procedure, new_position)
            if str(code_chunk['contents']['addr']) in self.addr_dict:
                self.addr_dict[str(code_chunk['contents']['addr'])].append(new_position)
            else:
                self.addr_dict.update({str(code_chunk['contents']['addr']): [new_position]})

    def generate_code_struct(self):
        self.code_struct = {}
        self.addr_dict = {}
        self.position = [0, 0, 0]  # Hints: code_index, chunk_index, offset = 0, 0, 0
        is_legal_code_body = False
        force_new_code = False
        self.struct_initialized = False

        for code in self.code_list:
            if code == '\n':
                force_new_code = True  # Hints: title or comments is another variant of code title, split title here
                continue
            code_info = self.analyse_single_code(code[:-1])  # Hints: remove '\n'

            if not is_legal_code_body:  # Hints: _start_ code + \n + title + \n + code
                is_legal_code_body = self.is_title(code_info['type'])
                if not is_legal_code_body:
                    continue
            
            (procedure, new_position) = self.check_comb(code_info, force_new_code)
            self.process_code_chunk(code_info, procedure, new_position)
            self.position = new_position
            force_new_code = False
        
        self.addr_booklet = self.generate_booklet(self.addr_dict)
        self.link_pointer()
        self.addr_dict = {}
        self.struct_initialized = False
    
    def analyse_single_code(self, code: str):  # Warning: prefer normalize code before use
        pattern_code_title = re.compile(r'^ *(\[.*\]) *$')
        pattern_master_code_title = re.compile(r'^ *(\{.*\}) *$')

        is_code_title = pattern_code_title.match(code)  # Warning: ":=" only for python > 3.8
        if is_code_title is not None:
            return {
                'type': 'code_title',
                'contents':
                    {
                        'raw': code
                    }
            }

        is_master_code_title = pattern_master_code_title.match(code)
        if is_master_code_title is not None:
            return {
                'type': 'master_code_title',
                'contents':
                    {
                        'raw': code
                    }
            }

        pattern_asm_code = re.compile(r'^ *(040[abcdef\d]0000) *([abcdef\d]{8}) *([abcdef\d]{8}) *$', re.I)
        is_pattern_asm_code = pattern_asm_code.match(code)
        if is_pattern_asm_code is not None:
            if self.ASM_type == 'ARM64':
                Disassembler = Cs(CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN)
            elif self.ASM_type == 'ARM32':
                Disassembler = Cs(CS_ARCH_ARM, CS_MODE_LITTLE_ENDIAN)

            can_be_disassembled = False
            in_code_cave = False
            multimedia_offset = None
            is_branch = False
            code_addr = int(is_pattern_asm_code.group(2), 16)
            code_bytes = bytearray.fromhex(is_pattern_asm_code.group(3))
            code_bytes.reverse()

            if (code_addr >= bytes_to_int(self.old_main_file.codeCaveStart)
                and code_addr < bytes_to_int(self.old_main_file.codeCaveEnd)):
                in_code_cave = True
            if code_addr >= bytes_to_int(self.old_main_file.rodataMemoryOffset):
                multimedia_offset = code_addr - bytes_to_int(self.old_main_file.rodataMemoryOffset)
            for i in Disassembler.disasm(code_bytes, code_addr):
                can_be_disassembled = True

                if i.mnemonic == 'bl' or i.mnemonic == 'b' or ('b.' in i.mnemonic) or (i.mnemonic == 'adr' and '#' in i.op_str):
                    is_branch = True
                    branch_to_cave = False
                    branch_to_multi = False
                    branch_multi_offset = None
                    branch_type = i.mnemonic
                    if branch_type == 'adr' and '#' in i.op_str:  # Hints: Add extra branch type here
                        [extra_op, branch_addr] = i.op_str.split('#')
                        branch_addr = int(branch_addr, 16)
                        branch_type += ' ' + extra_op
                    else:
                        branch_addr = int(i.op_str[1:], 16)
                    if (branch_addr >= bytes_to_int(self.old_main_file.codeCaveStart)
                            and branch_addr < bytes_to_int(self.old_main_file.codeCaveEnd)):
                        branch_to_cave = True
                    if branch_addr >= bytes_to_int(self.old_main_file.rodataMemoryOffset):
                        branch_to_multi = True
                        branch_multi_offset = branch_addr - bytes_to_int(self.old_main_file.textMemoryOffset)
                    
                asm_code_disam = ("0X%s:\t%s\t%s" %(hex(i.address)[2:].upper(), i.mnemonic.upper(), i.op_str.upper()))
                asm_code_disam = asm_code_disam.replace('0X', '0x')

            branch_detail = {
                                    'branch_type': branch_type,
                                    'branch_addr': branch_addr,
                                    'branch_to_cave': branch_to_cave,
                                    'branch_to_multi': branch_to_multi,
                                    'branch_multi_offset': branch_multi_offset,
                            } if is_branch else None
            detail = {
                                    'disam': asm_code_disam,
                                    'is_branch': is_branch,
                                    'branch_detail': branch_detail
                        } if can_be_disassembled else None
            return {
                'type': 'code_type_asm',
                'contents':
                    {
                        'raw': code,
                        'head': is_pattern_asm_code.group(1),
                        'addr': code_addr,
                        'body': is_pattern_asm_code.group(3),
                        'is_value': not can_be_disassembled,  # Hints: assuming type 0x0[12]xxxxxx need alignment and not an asm value
                        'in_code_cave': in_code_cave,
                        'multimedia_offset': multimedia_offset,
                        'detail': detail
                    }
            }

        for key in self.code_pattern:
            pattern = re.compile(eval(self.code_pattern[key]["pattern"]), re.I)
            if pattern.match(code) is not None:
                return {
                    'type': key,
                    'contents':
                        {
                            'raw': code
                        }
                }

        return  {
            'type': 'code_type_unknown',
            'contents':
                {
                    'raw': code
                }
        }

    def get_normalized_code(self):
        return self.code_text