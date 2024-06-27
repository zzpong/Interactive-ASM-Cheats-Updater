import re, struct
from copy import deepcopy
from capstone import *
from keystone import *

from config.config import configuration


widen_hit_num = int(configuration['widen_hit_num'])
max_hit_num = int(configuration['max_hit_num'])

def arm_4bytes_to_bits(byte_data) -> bytearray:
    if len(byte_data) == 0:
        return bytearray()

    if isinstance(byte_data, bytes):
        byte_data = bytearray(byte_data)

    padding_needed = 4 - (len(byte_data) % 4) if len(byte_data) % 4 != 0 else 0
    byte_data += b'\x00' * padding_needed

    bit_data = bytearray()
    num_ints = len(byte_data) // 4
    for i in range(num_ints):
        packed_value = struct.unpack_from('<I', byte_data, i * 4)[0]
        binary_string = format(packed_value, '032b')
        bit_data += bytearray(binary_string.encode())
        bit_data += b' '
    return bit_data

def bitsarray_findall(bits_file: bytes, bits_feature, mode = 'widen') -> list:
    hit_addr = []
    hit_num = 0
    # if not isinstance(bits_file, bytes):
        # bits_file = bytes(bits_file)
    if not isinstance(bits_feature, bytes):
        bits_feature = bytes(bits_feature)

    for match in re.finditer(bits_feature, bits_file, re.DOTALL):
        get_addr = (match.start() // 33) * 4
        hit_addr.append(get_addr)
        hit_num += 1
        if mode == 'hit':
            break
        elif mode == 'widen' and hit_num > widen_hit_num:
            break
        elif mode == 'max' and hit_num > max_hit_num:
            break

    return hit_addr

def bytesarray_findall(bytes_file, bytes_feature) -> list:
    hit_addr = []
    for match in re.finditer(bytes_feature, bytes_file, re.DOTALL):
        hit_addr.append(match.start())

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

def get_bits_feature(bytes_file, address, wing_length, asm_type = 'ARM64', isLoose = False):
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
    
    bits_feature = bytearray()
    adrp_flag = False
    for index in range(len(padding_dict)):
        if padding_dict[str(index)]['is_removed']:
            bits_feature += arm_4bytes_to_bits(padding_dict[str(index)]['bytearray'])
        else:
            for i in Disassembler.disasm(padding_dict[str(index)]['bytearray'], padding_dict[str(index)]['start_address']):
                original_bytes = i.bytes
                original_bits = arm_4bytes_to_bits(original_bytes)
                bit_cache = bytearray(0)
                
                if len(original_bytes) != 4:  # Hints: <Arm A-profile A64 Instruction Set Architecture> from https://developer.arm.com/documentation
                    pass
                elif asm_type == 'ARM64':
                    if isLoose and adrp_flag and (i.mnemonic != 'add' or i.mnemonic != 'ldr'):
                        adrp_flag = False
                    
                    if i.mnemonic == 'bl' or i.mnemonic == 'b':
                        original_bits[6:32] = b'.' * 26
                    elif 'b.' in i.mnemonic or i.mnemonic == 'cbz' or i.mnemonic == 'cbnz':
                        original_bits[8:27] = b'.' * 19
                    elif i.mnemonic == 'tbz' or i.mnemonic == 'tbnz':
                        original_bits[13:27] = b'.' * 14
                    # elif i.mnemonic == 'blr' or i.mnemonic == 'br':  # Hints: do not process
                        # pass
                    elif isLoose and (i.mnemonic == 'str' or i.mnemonic == 'strb' or i.mnemonic == 'strh'):
                        if original_bits[7] == ord('1'):  # Hints: STR? <Xt>, [<Xn|SP>{, #<pimm>}]
                            original_bits[10:22] = b'.' * 12
                        elif original_bits[10] == ord('0'):  # Hints: STR? <Xt>, [<Xn|SP>], #<simm> or STR? <Xt>, [<Xn|SP>, #<simm>]!
                            original_bits[11:20] = b'.' * 9
                    elif isLoose and (i.mnemonic == 'ldr' or i.mnemonic == 'ldrb' or i.mnemonic == 'ldrh' or i.mnemonic == 'ldrsb' or i.mnemonic == 'ldrsh' or i.mnemonic == 'ldrsw'):
                        if original_bits[2] == ord('0'):  # Hints: LDR?? (literal): LDR?? <Xt>, <label>
                            original_bits[8:27] = b'.' * 19
                        elif original_bits[7] == ord('1'):  # Hints: LDR?? <Xt>, [<Xn|SP>{, #<pimm>}]
                            original_bits[10:22] = b'.' * 12
                        elif original_bits[10] == ord('0'):  # Hints: LDR?? <Xt>, [<Xn|SP>], #<simm> or LDR?? <Xt>, [<Xn|SP>, #<simm>]!
                            original_bits[11:20] = b'.' * 9
                    elif isLoose and (i.mnemonic == 'adr' or i.mnemonic == 'adrp'):
                        original_bits[1:3] = b'.' * 2
                        original_bits[8:27] = b'.' * 19
                        if i.mnemonic == 'adrp':
                            adrp_flag = True
                    elif isLoose and (adrp_flag and i.mnemonic == 'add'):
                        if original_bits[4] == ord('0'):  # Hints: ADD (immediate): ADD <Xd|SP>, <Xn|SP>, #<imm>{, <shift>}
                            original_bits[10:22] = b'.' * 12
                        adrp_flag = False
                elif asm_type == 'ARM32':  # Hints: <Arm A-profile A32&T32 Instruction Set Architecture> from https://developer.arm.com/documentation
                    # Hints: These may be incomplete.
                    if i.mnemonic == 'bl' or i.mnemonic == 'b' or ('b.' in i.mnemonic):
                        original_bits[8:32] = b'.' * 24
                    elif i.mnemonic == 'blx':
                        if original_bits[4] == ord('1'):
                            original_bits[8:32] = b'.' * 24
                
                bit_cache += original_bits
                bits_feature += bit_cache

    return [bits_feature, [start_address, end_address], real_addr_offset, feature_size]

def get_bits_feature_lite(bytes_file, address, asm_type = 'ARM64', isLoose = False):
    bits_feature_pack = get_bits_feature(bytes_file, address, [0, 0], asm_type, isLoose)
    return bits_feature_pack[0]

def get_bytes_from_file(bytes_file, loc):
    if loc[0] < 0:
        loc[0] = 0
    if loc[1] > len(bytes_file) - 1:
        loc[1] = len(bytes_file) - 1
    return bytes_file[loc[0]:loc[1]]

def find_single_bits_feature_addr(main_file_bundle, main_file_bits_bundle, bits_feature, old_feature_loc, hit_start_addr, hit_end_addr, wing_length, asm_type = 'ARM64', isLoose = False):
    [old_main_file, new_main_file] = main_file_bundle
    wing_step = 1  # Hints: recovery rate
    left_side_available = True
    right_side_available = True
    current_feature_loc = deepcopy(old_feature_loc)

    while (left_side_available or right_side_available):
        if left_side_available:
            hit_start_addr_next = []
            hit_end_addr_next = []
            bits_feature_next = ''
            wing_length_next = deepcopy(wing_length)
            wing_length_next[0] += wing_step

            current_feature_loc[0] -= wing_step*4
            if current_feature_loc[0] < 0:
                left_side_available = False
                continue
            bits_feature_next = get_bits_feature_lite(old_main_file, [current_feature_loc[0], old_feature_loc[0]], asm_type, isLoose) + bits_feature

            for index in range(len(hit_start_addr)):
                bytes_file = get_bytes_from_file(new_main_file, [hit_start_addr[index]-wing_step*4, hit_end_addr[index]])
                bits_file = arm_4bytes_to_bits(bytes_file)
                
                if len(bitsarray_findall(bits_file, bits_feature_next, mode = 'hit')) != 0:
                    hit_start_addr_next.append(hit_start_addr[index]-wing_step*4)
                    hit_end_addr_next.append(hit_end_addr[index])

            if len(hit_start_addr_next) != 0:
                hit_start_addr = deepcopy(hit_start_addr_next)
                hit_end_addr = deepcopy(hit_end_addr_next)
                wing_length = deepcopy(wing_length_next)
                bits_feature = deepcopy(bits_feature_next)
                old_feature_loc = deepcopy(current_feature_loc)
                if len(hit_start_addr_next) == 1:
                    return (hit_start_addr, wing_length)
            else:
                left_side_available = False

        if right_side_available:
            hit_start_addr_next = []
            hit_end_addr_next = []
            bits_feature_next = ''
            wing_length_next = deepcopy(wing_length)
            wing_length_next[1] += wing_step

            current_feature_loc[1] += wing_step*4
            if current_feature_loc[1] > len(old_main_file) - 1:
                right_side_available = False
                continue
            bits_feature_next = bits_feature + get_bits_feature_lite(old_main_file, [old_feature_loc[1], current_feature_loc[1]], asm_type, isLoose)

            for index in range(len(hit_start_addr)):
                bytes_file = get_bytes_from_file(new_main_file, [hit_start_addr[index], hit_end_addr[index]+wing_step*4])
                bits_file = arm_4bytes_to_bits(bytes_file)

                if len(bitsarray_findall(bits_file, bits_feature_next, mode = 'hit')) != 0:
                    hit_start_addr_next.append(hit_start_addr[index])
                    hit_end_addr_next.append(hit_end_addr[index]+wing_step*4)

            if len(hit_start_addr_next) != 0:
                hit_start_addr = deepcopy(hit_start_addr_next)
                hit_end_addr = deepcopy(hit_end_addr_next)
                wing_length = deepcopy(wing_length_next)
                bits_feature = deepcopy(bits_feature_next)
                old_feature_loc = deepcopy(current_feature_loc)
                if len(hit_start_addr_next) == 1:
                    return (hit_start_addr, wing_length)
            else:
                right_side_available = False
        
    return (hit_start_addr, wing_length)

def find_bits_feature_addr(main_file_bundle, main_file_bits_bundle, addr_range, wing_length, asm_type = 'ARM64'):
    [old_main_file, new_main_file] = main_file_bundle
    [old_main_bits_file, new_main_bits_file] = main_file_bits_bundle
    wing_length_org = deepcopy(wing_length)
    real_addr_offset_org = 0

    # Hints: Execute in strict mode first, which means isLoose = False.
    hit_once = False
    for i in range(10):
        [bits_feature, feature_loc, real_addr_offset, feature_size] = get_bits_feature(old_main_file, addr_range, wing_length, asm_type, isLoose = False)
        if not hit_once:
            real_addr_offset_org = real_addr_offset
        hit_start_addr = bitsarray_findall(new_main_bits_file, bits_feature)
        if len(hit_start_addr) <= widen_hit_num:
            break
        wing_length[0] += 1
        wing_length[1] += 1
        hit_once = True
    
    if len(hit_start_addr) == 0 and hit_once:
        wing_length[0] -= 1
        wing_length[1] -= 1
        [bits_feature, feature_loc, real_addr_offset, feature_size] = get_bits_feature(old_main_file, addr_range, wing_length, asm_type, isLoose = False)
        hit_start_addr = bitsarray_findall(new_main_bits_file, bits_feature, mode = 'max')

    if len(hit_start_addr) != 0:  # Hints: refine wing_length
        if len(hit_start_addr) > max_hit_num:
            print(f'========== hit_num > max_hit_num({max_hit_num}) ==========')
        hit_end_addr = list(map(lambda x:x+feature_size, hit_start_addr))
        real_addr_offset -= wing_length[0] * 4
        [hit_start_addr, wing_length] = find_single_bits_feature_addr(main_file_bundle, main_file_bits_bundle, bits_feature, feature_loc, hit_start_addr, hit_end_addr, wing_length, asm_type, isLoose = False)
        real_addr_offset += wing_length[0] * 4  # Hints: adjust real_addr_offset
        return [hit_start_addr, wing_length, real_addr_offset]

    # Hints: Then execute in loose mode, which means isLoose = True.
    hit_once = False
    for i in range(16):
        [bits_feature, feature_loc, real_addr_offset, feature_size] = get_bits_feature(old_main_file, addr_range, wing_length, asm_type, isLoose = True)
        hit_start_addr = bitsarray_findall(new_main_bits_file, bits_feature)
        if len(hit_start_addr) <= widen_hit_num:
            break
        wing_length[0] += 1
        wing_length[1] += 1
        hit_once = True
    
    if len(hit_start_addr) == 0 and hit_once:
        wing_length[0] -= 1
        wing_length[1] -= 1
        [bits_feature, feature_loc, real_addr_offset, feature_size] = get_bits_feature(old_main_file, addr_range, wing_length, asm_type, isLoose = True)
        hit_start_addr = bitsarray_findall(new_main_bits_file, bits_feature, mode = 'max')

    if len(hit_start_addr) != 0:  # Hints: refine wing_length
        if len(hit_start_addr) > max_hit_num:
            print(f'======== hit_num > max_hit_num({max_hit_num}) ========')
        hit_end_addr = list(map(lambda x:x+feature_size, hit_start_addr))
        real_addr_offset -= wing_length[0] * 4
        [hit_start_addr, wing_length] = find_single_bits_feature_addr(main_file_bundle, main_file_bits_bundle, bits_feature, feature_loc, hit_start_addr, hit_end_addr, wing_length, asm_type, isLoose = True)
        real_addr_offset += wing_length[0] * 4  # Hints: adjust real_addr_offset
        return [hit_start_addr, wing_length, real_addr_offset]
    
    # Hints: reforge wing_length
    wing_length_l = [3, 0]
    [bits_feature_l, feature_loc_l, real_addr_offset_l, feature_size_l] = get_bits_feature(old_main_file, addr_range, wing_length_l, asm_type, isLoose = True)
    hit_start_addr_l = bitsarray_findall(new_main_bits_file, bits_feature_l)
    hit_end_addr_l = list(map(lambda x:x+feature_size_l, hit_start_addr_l))
    real_addr_offset_l -= wing_length_l[0] * 4
    [hit_start_addr_l, wing_length_l] = find_single_bits_feature_addr(main_file_bundle, main_file_bits_bundle, bits_feature_l, feature_loc_l, hit_start_addr_l, hit_end_addr_l, wing_length_l, asm_type, isLoose = True)
    real_addr_offset_l += wing_length_l[0] * 4

    if len(hit_start_addr_l) == 1:
        return [hit_start_addr_l, wing_length_l, real_addr_offset_l]
    
    wing_length_r = [0, 3]
    [bits_feature_r, feature_loc_r, real_addr_offset_r, feature_size_r] = get_bits_feature(old_main_file, addr_range, wing_length_r, asm_type, isLoose = True)
    hit_start_addr_r = bitsarray_findall(new_main_bits_file, bits_feature_r)
    hit_end_addr_r = list(map(lambda x:x+feature_size_r, hit_start_addr_r))
    real_addr_offset_r -= wing_length_r[0] * 4
    [hit_start_addr_r, wing_length_r] = find_single_bits_feature_addr(main_file_bundle, main_file_bits_bundle, bits_feature_r, feature_loc_r, hit_start_addr_r, hit_end_addr_r, wing_length_r, asm_type, isLoose = True)
    real_addr_offset_r += wing_length_r[0] * 4

    if len(hit_start_addr_r) == 1:
        return [hit_start_addr_r, wing_length_r, real_addr_offset_r]
    
    if len(hit_start_addr_l) == 0 and len(hit_start_addr_r) == 0:
        return [[], wing_length_org, real_addr_offset_org]
    
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