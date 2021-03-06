import re
from copy import deepcopy
from capstone import *
from keystone import *

def bytesarray_findall(bytes_file, bytes_feature) -> list:
    index = 0
    index_arr = []
    while True:
        id = bytes_file.find(bytes_feature, index)
        if id == -1:
            break
        else:
            index_arr.append(id)
            index = id + 1
    return index_arr

def bytesarray_refindall(bytes_file, bytes_feature) -> list:
    hit_start_addr = []
    sliced_start_addr = 0
    sliced_max_addr = len(bytes_file)
    while True:
        result = re.search(bytes_feature, bytes_file, re.DOTALL)
        if result is not None:
            hit_start_addr.append(result.span()[0]+sliced_start_addr)
            if (result.span()[1]+1) <= sliced_max_addr:
                bytes_file = bytes_file[(result.span()[1]+1):]
                sliced_start_addr += result.span()[1]+1
            else:
                break
        else:
            break
    return hit_start_addr

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

def find_bytes_feature(bytes_file, address, wing_length):
    if isinstance(address, list):
        pre_address = address[0]
        post_address = address[1]
    else:
        pre_address = address
        post_address = address
    if isinstance(wing_length, int):
        start_address = pre_address - wing_length * 4
        end_address = post_address + wing_length * 4
    elif isinstance(wing_length, list):
        start_address = pre_address - wing_length[0] * 4
        end_address = post_address + wing_length[1] * 4
    asm_binarray = bytes_file[start_address : end_address]

    align_index = bytesarray_findall(asm_binarray, b"\x00\x00\x00\x00")
    align_prop = []
    for addr in range(0, len(asm_binarray), 4):
        if addr in align_index:
            align_prop.extend([0,0,0,0])
        else:
            align_prop.extend([1,1,1,1])
    asm_json = {}
    index = 0
    count = 0
    while True:
        if align_prop[index] == 0:
            try:
                index_end = align_prop.index(1, index)
                asm_json.update({
                    f'{count}':
                    {
                        'is_removed': True,
                        'bytearray': deepcopy(asm_binarray[index:index_end]),
                        'start_address': start_address + index
                    }
                })
                count += 1
                index = index_end  
            except:
                asm_json.update({
                    f'{count}':
                    {
                        'is_removed': True,
                        'bytearray': deepcopy(asm_binarray[index:]),
                        'start_address': start_address + index
                    }
                })
                count += 1
                break
        else:
            try:
                index_end = align_prop.index(0, index)
                asm_json.update({
                    f'{count}':
                    {
                        'is_removed': False,
                        'bytearray': deepcopy(asm_binarray[index:index_end]),
                        'start_address': start_address + index
                    }
                })
                count += 1
                index = index_end
            except:
                asm_json.update({
                    f'{count}':
                    {
                        'is_removed': False,
                        'bytearray': deepcopy(asm_binarray[index:]),
                        'start_address': start_address + index
                    }
                })
                count += 1
                break

    json_bytes_feature = {
        "start_address": hex(start_address),
        "end_address": hex(end_address),
        "taget_start_offset": hex(pre_address - start_address),
        "taget_end_offset": hex(post_address - start_address),
        "bytes_feature": "",
        "original_codes": {}
    }
    Disassembler = Cs(CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN)
    bytes_feature = bytearray()
    print(bytes_feature)
    adrp_flag = False

    for index in range(len(asm_json)):
        if asm_json[str(index)]['is_removed']:
            bytes_feature += asm_json[str(index)]['bytearray']
        else:
            for i in Disassembler.disasm(asm_json[str(index)]['bytearray'], asm_json[str(index)]['start_address']):
                print("0x%x:\t%s\t%s\t%s" %(i.address, i.mnemonic, i.op_str, i.bytes))
                json_bytes_feature["original_codes"].update({f"{hex(i.address)}": [f"{i.mnemonic}  {i.op_str}", ''.join('{:02x}'.format(x) for x in i.bytes)]})
                byte_cache = bytearray(0)
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
                bytes_feature += byte_cache

    json_bytes_feature["bytes_feature"] = ''.join('{:02x}'.format(x) for x in bytes_feature)

    return json_bytes_feature

def create_bl_links(code_with_bl: dict) -> str:
    new_code_line = ''
    Assembler = Ks(KS_ARCH_ARM64, KS_MODE_LITTLE_ENDIAN)
    print(code_with_bl)
    for key in code_with_bl:
        if code_with_bl[key]['contents']['is_shown']:
            if code_with_bl[key]['code_type'] != 'Normal':
                code_1st = code_with_bl[key]['contents']['code_head']
                code_2nd = code_with_bl[key]['contents']['code_addr']
                if code_with_bl[key]['contents']['is_bl']:
                    if code_with_bl[key]['contents']['bl_line'] is None:
                        bl_address = code_with_bl[key]['contents']['bl_addr']
                    else:
                        bl_address = (code_with_bl[str(code_with_bl[key]['contents']['bl_line'])]['contents']['base_addr'] 
                        + 4*code_with_bl[str(code_with_bl[key]['contents']['bl_line'])]['contents']['bl_shift'])
                    code_address = code_with_bl[key]['contents']['base_addr']
                    b_op = code_with_bl[key]['contents']['bl_type']
                    code_str = b_op + ' #' + hex(bl_address)
                    encoding_dock, _ = Assembler.asm(code_str, code_address)
                    code_3rd = []
                    _code_3rd = ''.join('{:02x}'.format(x) for x in reversed(encoding_dock))
                    _code_3rd = _code_3rd.upper()
                    code_3rd.append(_code_3rd)
                else:
                    code_3rd = code_with_bl[key]['contents']['code_main']
                for index in range(len(code_1st)):
                    new_code_line += f'{code_1st[index].upper()} {code_2nd[index].upper()} {code_3rd[index].upper()}' + '\n'
            else:
                new_code_line += code_with_bl[key]['contents']['code_raw'].upper() + '\n'
    return new_code_line + '\n'