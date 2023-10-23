import re
from copy import deepcopy
from capstone import *
from keystone import *


def bytesarray_escape(bytes_array) -> bytearray:
    try:
        byte_cache = re.escape(bytes_array)
    except:
        byte_cache = bytes_array
    try:
        byte_cache = byte_cache.replace(b")", b"\\)")
        byte_cache = byte_cache.replace(b"(", b"\\(")
    except:
        pass
    if bytes_array == 0x29:
        byte_cache = b"\\)"
    elif bytes_array == 0x28:
        byte_cache = b"\\("
    return byte_cache

def bytesarray_findall(bytes_file, bytes_feature) -> list:
    hit_addr = []
    sliced_addr = 0
    bytes_file_len = len(bytes_file)
    while True:
        result = re.search(bytes_feature, bytes_file, re.DOTALL)
        if result is None:
            break
        hit_addr.append(result.span()[0] + sliced_addr)
        if result.span()[1] >= bytes_file_len:
            break
        bytes_file = bytes_file[(result.span()[1]):]
        sliced_addr += result.span()[1]
    return hit_addr

def bytes_padding(asm_binarray, start_address) -> dict:
    padding_index = bytesarray_findall(asm_binarray, b"\x00\x00\x00\x00")
    padding_prop = []
    padding_dict = {}

    for addr in range(0, len(asm_binarray), 4):
        if addr in padding_index:
            padding_prop.extend([0,0,0,0])
        else:
            padding_prop.extend([1,1,1,1])
    
    index = 0
    count = 0
    while True:
        if padding_prop[index] == 0:
            try:
                index_end = padding_prop.index(1, index)
                padding_dict.update({
                    f'{count}':
                    {
                        'is_removed': True,
                        'bytearray': asm_binarray[index : index_end],
                        'start_address': start_address + index
                    }
                })
                count += 1
                index = index_end  
            except:
                padding_dict.update({
                    f'{count}':
                    {
                        'is_removed': True,
                        'bytearray': asm_binarray[index:],
                        'start_address': start_address + index
                    }
                })
                count += 1
                break
        else:
            try:
                index_end = padding_prop.index(0, index)
                padding_dict.update({
                    f'{count}':
                    {
                        'is_removed': False,
                        'bytearray': asm_binarray[index : index_end],
                        'start_address': start_address + index
                    }
                })
                count += 1
                index = index_end
            except:
                padding_dict.update({
                    f'{count}':
                    {
                        'is_removed': False,
                        'bytearray': asm_binarray[index:],
                        'start_address': start_address + index
                    }
                })
                count += 1
                break
    
    return padding_dict

def get_bytes_feature(bytes_file, address, wing_length, asm_type = 'ARM64'):
    start_address = address[0] - wing_length[0] * 4
    end_address = address[1] + wing_length[1] * 4
    real_addr_offset = wing_length[0] * 4
    if start_address < 0:
        start_address = 0
        real_addr_offset = address[0]
    if end_address > len(bytes_file) - 1:
        end_address = len(bytes_file) - 1
    feature_size = end_address - start_address
    asm_binarray = bytes_file[start_address : end_address]
    
    padding_dict = bytes_padding(asm_binarray, start_address)
    
    if asm_type == 'ARM64':
        Disassembler = Cs(CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN)
    elif asm_type == 'ARM32':
        Disassembler = Cs(CS_ARCH_ARM, CS_MODE_LITTLE_ENDIAN)
    
    bytes_feature = bytearray()
    adrp_flag = False
    for index in range(len(padding_dict)):
        if padding_dict[str(index)]['is_removed']:
            bytes_feature += padding_dict[str(index)]['bytearray']
        else:
            for i in Disassembler.disasm(padding_dict[str(index)]['bytearray'], padding_dict[str(index)]['start_address']):
                byte_cache = bytearray(0)
                if asm_type == 'ARM64':
                    if i.mnemonic == 'bl' or i.mnemonic == 'b' or ('b.' in i.mnemonic):
                        byte_cache = bytearray(b'(.{3})')
                        try:
                            byte_cache += bytesarray_escape(i.bytes[3])
                        except:
                            byte_cache.append(bytesarray_escape(i.bytes[3]))
                    elif i.mnemonic == 'blr' or i.mnemonic == 'br':
                        byte_cache = bytearray(b'(.{2})')
                        byte_cache += bytesarray_escape(i.bytes[2:4])
                    elif i.mnemonic == 'adrp':
                        byte_cache = bytearray(b'(.{4})')
                        adrp_flag = True
                    elif (i.mnemonic == 'ldr' or i.mnemonic == 'ldrb' or i.mnemonic == 'add') and adrp_flag:
                        try:
                            byte_cache += bytesarray_escape(i.bytes[0])
                        except:
                            byte_cache.append(bytesarray_escape(i.bytes[0]))
                        byte_cache += bytearray(b'(.{2})')
                        try:
                            byte_cache += bytesarray_escape(i.bytes[3])
                        except:
                            byte_cache.append(bytesarray_escape(i.bytes[3]))
                        adrp_flag = False
                    else:
                        byte_cache = re.escape(bytearray(i.bytes))
                        adrp_flag = False
                elif asm_type == 'ARM32':
                    if i.mnemonic == 'bl' or i.mnemonic == 'b' or ('b.' in i.mnemonic):
                        byte_cache = bytearray(b'(.{3})')
                        try:
                            byte_cache += bytesarray_escape(i.bytes[3])
                        except:
                            byte_cache.append(bytesarray_escape(i.bytes[3]))
                    elif i.mnemonic == 'blx' or i.mnemonic == 'bx':
                        byte_cache = bytearray(b'(.{1})')
                        byte_cache += bytesarray_escape(i.bytes[1:4])
                    else:
                        byte_cache = re.escape(bytearray(i.bytes))

                bytes_feature += byte_cache

    bytes_feature_hex = ''.join('{:02x}'.format(x) for x in bytes_feature)

    return [bytes_feature_hex, [start_address, end_address], real_addr_offset, feature_size]

def get_bytes_feature_lite(bytes_file, address, asm_type = 'ARM64'):
    bytes_feature_pack = get_bytes_feature(bytes_file, address, [0, 0], asm_type)
    return bytes_feature_pack[0]

def get_bytes_from_file(bytes_file, loc):
    if loc[0] < 0:
        loc[0] = 0
    if loc[1] > len(bytes_file) - 1:
        loc[1] = len(bytes_file) - 1
    return bytes_file[loc[0]:loc[1]]

def find_single_feature_addr(main_file_bundle, bytes_feature_hex, old_feature_loc, hit_start_addr, hit_end_addr, wing_length, asm_type = 'ARM64'):
    [old_main_file, new_main_file] = main_file_bundle
    wing_step = 1  # Hints: recovery rate
    left_side_available = True
    right_side_available = True
    current_feature_loc = deepcopy(old_feature_loc)

    while (left_side_available or right_side_available):
        if left_side_available:
            hit_start_addr_next = []
            hit_end_addr_next = []
            bytes_feature_hex_next = ''
            wing_length_next = deepcopy(wing_length)
            wing_length_next[0] += wing_step

            current_feature_loc[0] -= wing_step*4
            if current_feature_loc[0] < 0:
                left_side_available = False
                continue
            bytes_feature_hex_next = get_bytes_feature_lite(old_main_file, [current_feature_loc[0], old_feature_loc[0]], asm_type) + bytes_feature_hex

            for index in range(len(hit_start_addr)):
                bytes_file = get_bytes_from_file(new_main_file, [hit_start_addr[index]-wing_step*4, hit_end_addr[index]])
                
                if len(bytesarray_findall(bytes_file, bytes(bytearray.fromhex(bytes_feature_hex_next)))) != 0:
                    hit_start_addr_next.append(hit_start_addr[index]-wing_step*4)
                    hit_end_addr_next.append(hit_end_addr[index])

            if len(hit_start_addr_next) != 0:
                hit_start_addr = deepcopy(hit_start_addr_next)
                hit_end_addr = deepcopy(hit_end_addr_next)
                wing_length = deepcopy(wing_length_next)
                bytes_feature_hex = deepcopy(bytes_feature_hex_next)
                old_feature_loc = deepcopy(current_feature_loc)
                if len(hit_start_addr_next) == 1:
                    return (hit_start_addr, wing_length)
            else:
                left_side_available = False

        if right_side_available:
            hit_start_addr_next = []
            hit_end_addr_next = []
            bytes_feature_hex_next = ''
            wing_length_next = deepcopy(wing_length)
            wing_length_next[1] += wing_step

            current_feature_loc[1] += wing_step*4
            if current_feature_loc[1] > len(old_main_file) - 1:
                right_side_available = False
                continue
            bytes_feature_hex_next = bytes_feature_hex + get_bytes_feature_lite(old_main_file, [old_feature_loc[1], current_feature_loc[1]], asm_type)

            for index in range(len(hit_start_addr)):
                bytes_file = get_bytes_from_file(new_main_file, [hit_start_addr[index], hit_end_addr[index]+wing_step*4])

                if len(bytesarray_findall(bytes_file, bytes(bytearray.fromhex(bytes_feature_hex_next)))) != 0:
                    hit_start_addr_next.append(hit_start_addr[index])
                    hit_end_addr_next.append(hit_end_addr[index]+wing_step*4)

            if len(hit_start_addr_next) != 0:
                hit_start_addr = deepcopy(hit_start_addr_next)
                hit_end_addr = deepcopy(hit_end_addr_next)
                wing_length = deepcopy(wing_length_next)
                bytes_feature_hex = deepcopy(bytes_feature_hex_next)
                old_feature_loc = deepcopy(current_feature_loc)
                if len(hit_start_addr_next) == 1:
                    return (hit_start_addr, wing_length)
            else:
                right_side_available = False
        
    return (hit_start_addr, wing_length)

def find_feature_addr(main_file_bundle, addr_range, wing_length, asm_type = 'ARM64'):
    [old_main_file, new_main_file] = main_file_bundle

    [bytes_feature_hex, feature_loc, real_addr_offset, feature_size] = get_bytes_feature(old_main_file, addr_range, wing_length, asm_type)
    bytes_feature = bytes(bytearray.fromhex(bytes_feature_hex))
    hit_start_addr = bytesarray_findall(new_main_file, bytes_feature)
    hit_end_addr = list(map(lambda x:x+feature_size, hit_start_addr))

    if len(hit_start_addr) != 0:  # Hints: refine wing_length
        real_addr_offset -= wing_length[0] * 4
        [hit_start_addr, wing_length] = find_single_feature_addr(main_file_bundle, bytes_feature_hex, feature_loc, hit_start_addr, hit_end_addr, wing_length, asm_type)
        real_addr_offset += wing_length[0] * 4  # Hints: adjust real_addr_offset
        return [hit_start_addr, wing_length, real_addr_offset]
    
    # Hints: reforge wing_length
    wing_length_l = [1, 0]
    [bytes_feature_hex_l, feature_loc_l, real_addr_offset_l, feature_size_l] = get_bytes_feature(old_main_file, addr_range, wing_length_l, asm_type)
    bytes_feature_l = bytes(bytearray.fromhex(bytes_feature_hex_l))
    hit_start_addr_l = bytesarray_findall(new_main_file, bytes_feature_l)
    hit_end_addr_l = list(map(lambda x:x+feature_size_l, hit_start_addr_l))
    real_addr_offset_l -= wing_length_l[0] * 4
    [hit_start_addr_l, wing_length_l] = find_single_feature_addr(main_file_bundle, bytes_feature_hex_l, feature_loc_l, hit_start_addr_l, hit_end_addr_l, wing_length_l, asm_type)
    real_addr_offset_l += wing_length_l[0] * 4

    if len(hit_start_addr_l) == 1:
        return [hit_start_addr_l, wing_length_l, real_addr_offset_l]
    
    wing_length_r = [0, 1]
    [bytes_feature_hex_r, feature_loc_r, real_addr_offset_r, feature_size_r] = get_bytes_feature(old_main_file, addr_range, wing_length_r, asm_type)
    bytes_feature_r = bytes(bytearray.fromhex(bytes_feature_hex_r))
    hit_start_addr_r = bytesarray_findall(new_main_file, bytes_feature_r)
    hit_end_addr_r = list(map(lambda x:x+feature_size_r, hit_start_addr_r))
    real_addr_offset_r -= wing_length_r[0] * 4
    [hit_start_addr_r, wing_length_r] = find_single_feature_addr(main_file_bundle, bytes_feature_hex_r, feature_loc_r, hit_start_addr_r, hit_end_addr_r, wing_length_r, asm_type)
    real_addr_offset_r += wing_length_r[0] * 4

    if len(hit_start_addr_r) == 1:
        return [hit_start_addr_r, wing_length_r, real_addr_offset_r]
    
    if (len(hit_start_addr_l) != 0 and len(hit_start_addr_r) != 0
            and len(hit_start_addr_l) > len(hit_start_addr_r)):
        return [hit_start_addr_r, wing_length_r, real_addr_offset_r]
    
    return [hit_start_addr_l, wing_length_l, real_addr_offset_l]

def generate_ASM_code(bytes_file, addr_range, asm_type = 'ARM64'):
    [start_address, end_address] = addr_range
    asm_binarray = bytes_file[start_address : end_address]

    if len(asm_binarray) == 0:
        return None

    padding_dict = bytes_padding(asm_binarray, start_address)

    if asm_type == 'ARM64':
        Disassembler = Cs(CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN)
    elif asm_type == 'ARM32':
        Disassembler = Cs(CS_ARCH_ARM, CS_MODE_LITTLE_ENDIAN)
    
    msg = []
    gap_length = 0

    for index in range(len(padding_dict)):
        if padding_dict[str(index)]['is_removed']:
            if index == range(len(padding_dict))[-1]:
                gap_length = int((end_address - padding_dict[str(index)]['start_address'])/4)
            else:
                gap_length = int((padding_dict[str(index+1)]['start_address'] - padding_dict[str(index)]['start_address'])/4)
            _start_addr = padding_dict[str(index)]['start_address']
            for i in range(gap_length):
                msg.append("0x%s:\t%s" %((hex(_start_addr)[2:]).zfill(8).upper(), 'Zero Padding'))
                _start_addr += 4
        else:
            for i in Disassembler.disasm(padding_dict[str(index)]['bytearray'], padding_dict[str(index)]['start_address']):
                asm_code_disam = ("0X%s:\t%s\t%s" %((hex(i.address)[2:]).zfill(8).upper(), i.mnemonic.upper(), i.op_str.upper()))
                asm_code_disam = asm_code_disam.replace('0X', '0x')
                msg.append(asm_code_disam)

    return msg

def get_branch_code_body(code_str: str, branch_addr: int, ASM_type = 'ARM64'):
    if ASM_type == 'ARM64':
        Assembler = Ks(KS_ARCH_ARM64, KS_MODE_LITTLE_ENDIAN)
        encoding_dock, _ = Assembler.asm(code_str, branch_addr)
    elif ASM_type == 'ARM32':
        Assembler = Ks(KS_ARCH_ARM, KS_MODE_ARM | KS_MODE_LITTLE_ENDIAN)
        encoding_dock, _ = Assembler.asm(code_str, branch_addr)
    return ''.join('{:02x}'.format(x).upper() for x in reversed(encoding_dock))

### ADR fix for keystone ###
#   31	30	29	28	27	26	25	24	23	22	21	20	19	18	17	16	15	14	13	12	11	10	9	8	7	6	5	4	3	2	1	0
#   0	immlo	1	0	0	0	0	immhi	                                                                Rd
########## Details #########
# Issue: https://github.com/keystone-engine/keystone/issues/290
# LDR would load 64 bits memory into register, plz use ADR instead 
####### Now support ########
# small base_addr + small offset (keystone original)
# large base_addr + small offset (added):
# remove last 3 bytes of base_addr as 'pages' cost, then offset - base_addr and fill [immhi, immlo]. base_addr smaller than 3 bytes share the same code.
# large base_addr + large offset, but (offset - base_addr) small (added):
# offset - base_addr then fill [immhi, immlo].
# small base_addr + large offset (large offset cannot be saved in just 21 bits, branch to any part of the offset as the user's choice)
def keystone_long_adr_fix(b_op, base_addr, offset, ASM_type = 'ARM64'):
    code_str = b_op + ' #' + hex(0)
    if ASM_type == 'ARM64':
        Assembler = Ks(KS_ARCH_ARM64, KS_MODE_LITTLE_ENDIAN)
        encoding_dock, _ = Assembler.asm(code_str, 0)
    elif ASM_type == 'ARM32':
        Assembler = Ks(KS_ARCH_ARM, KS_MODE_ARM | KS_MODE_LITTLE_ENDIAN)
        encoding_dock, _ = Assembler.asm(code_str, 0)
    
    base_code_body = ''.join('{:02x}'.format(x).upper() for x in reversed(encoding_dock))
    base_code_body = list(bin(int(base_code_body,16))[2:].zfill(32))
    [immlo, immhi] = get_relative_addr(base_addr, offset)
    base_code_body[1:3] = immlo
    base_code_body[8:27] = immhi
    code_body = hex(int(''.join(base_code_body), 2))[2:].zfill(8).upper()
    return code_body

def get_relative_addr(base_addr: int, offset: int):
    if abs(offset - base_addr) >= 4096:  # Hints: remove last 3 bytes as 'pages' cost if larger addr shift
        base_addr = int(hex(base_addr)[:-3], 16) if abs(base_addr) >= 4096 else 0
    relative_addr = offset - base_addr
    bin_relative_addr = get_complement(relative_addr)
    return (list(bin_relative_addr[19:21]), list(bin_relative_addr[0:19]))

def get_complement(num: int):
    if num >= 0:
        return bin(num)[2:].zfill(21)
    
    bin_num = (abs(num) ^ 2097151) + 1  # Hints: '0b 1 1111 1111 1111 1111 1111'
    return bin(bin_num)[2:].zfill(21)