import os, json, shutil, time, subprocess, chardet, struct, io
from copy import deepcopy
from tkinter import messagebox
from typing import Optional
from asyncio.subprocess import PIPE, STDOUT

from utilities.exception import MainNSOError
from utilities.nsnsotool import NSOfile


def bytearray_slice(bytearray, loc, byteorderbig = False):
    byte_4 = bytearray[4*loc : 4+4*loc]
    if byteorderbig:
        byte_4.reverse()
    return byte_4

def bytes_to_int(bytearray):
    return int.from_bytes(bytearray, byteorder='big', signed=False)

def arm_4bytes_to_bits(byte_data: bytearray) -> bytes:
    if not byte_data:
        return b''

    padding_needed = 4 - (len(byte_data) % 4) if len(byte_data) % 4 else 0
    byte_data += b'\x00' * padding_needed

    output = io.BytesIO()
    num_ints = len(byte_data) // 4
    for i in range(num_ints):
        packed_value = struct.unpack_from('<I', byte_data, i * 4)[0]
        binary_string = format(packed_value, '032b')
        output.write(binary_string.encode() + b' ')

    return output.getvalue()

def get_pages_size(code_size):
    return ((code_size & 0xFFFFF000) + 0x1000)

generate_msg = lambda x:'\n'.join(eval(x))  # just for static characters


class MainNSOStruct:
    def __init__(self, file_path: str, globalInfo) -> None:
        self.file_path = file_path
        self.globalInfo = globalInfo
        self.logger = globalInfo.logger
        self.msg_map = globalInfo.msg_map
        self.str_map = globalInfo.str_map
        self.msgbox_title_map = globalInfo.msgbox_title_map

        self.Magic = ''
        self.Flags = bytearray(4)
        self.textFileOffset = bytearray(4)  # text base address in main file
        self.textMemoryOffset = bytearray(4)  # text base address in console memory
        self.textDecompSize = bytearray(4)
        self.ModuleNameOffset = bytearray(4)  # only text_addr in ModuleName needed
        self.rodataFileOffset = bytearray(4)  # rodata base address in main file
        self.rodataMemoryOffset = bytearray(4)  # rodata base address in console memory
        self.rodataDecompSize = bytearray(4)
        self.ModuleSize = bytearray(4)
        self.rwdataFileOffset = bytearray(4)  # rwdata base address in main file
        self.rwdataMemoryOffset = bytearray(4)  # rwdata base address in console memory
        self.rwdataDecompSize = bytearray(4)
        self.bssSize = bytearray(4)
        self.ModuleId = ''  # build_id

        self.textFileEnd = bytearray(4)
        self.codeCaveStart = bytearray(4)
        self.codeCaveEnd = bytearray(4)
        self.bssMemoryOffset = bytearray(4)  # bss base address in console memory

        self.rodataStart = 0x0
        self.rodataEnd = 0x0
        self.rwdataStart = 0x0
        self.rwdataEnd = 0x0
        self.bssStart = 0x0
        self.bssEnd = 0x0
        self.multimediaStart = 0x0

        self.NSORaw = None
        self.NSORaw4Mod = bytearray()
        self.mainFuncFile = bytearray()
        self.mainFuncFile_bits = b''

    def process_file(self):
        if not self.is_NSO_file():
            messagebox.showerror(title=self.msgbox_title_map['Error'], message=generate_msg(self.msg_map['NOT NSO File']))
            raise MainNSOError(generate_msg(self.msg_map['NOT NSO File']))
        else:
            if self.is_Compressed():
                self.decompress()
            self.get_struct_from_file()
            self.get_mainfunc_file()
            if len(self.Flags) == 0 or (int.from_bytes(self.Flags, 'little') & 0b111):
                messagebox.showerror(title=self.msgbox_title_map['Error'], message=generate_msg(self.msg_map['NSO file decompression failed']))
                raise MainNSOError(generate_msg(self.msg_map['NSO file decompression failed']))
            return True

    def decompress(self):
        try:
            org_file = NSOfile(self.file_path, self.globalInfo)
            org_file.process_file()
            if org_file.is_Compressed():
                dec_file_path = org_file.generate_dec_path(self.file_path)
                org_file.self_decompress()
        except Exception as e:
            messagebox.showerror(title=self.msgbox_title_map['Error'], message=generate_msg(self.msg_map['NSO file decompression failed']))
            raise MainNSOError(generate_msg(self.msg_map['NSO file decompression failed']))

        self.logger.info(generate_msg(self.msg_map['NSO file decompressed']))

    def decode_outs_from_system(self, outs):
        encode_type = chardet.detect(outs)['encoding']
        try:
            contents = [z.strip() for z in outs.decode(encode_type).split('\n') if z]
        except:
            try:
                contents = [z.strip() for z in outs.decode('latin-1').split('\n') if z]
            except:
                try:
                    contents = [z.strip() for z in outs.decode('latin-1', 'ignore').split('\n') if z]
                except:
                    contents = None

        return contents

    def get_struct_from_file(self):
        self.NSORaw = bytearray(os.path.getsize(self.file_path))
        with open(self.file_path, 'rb') as fp:
            fp.readinto(self.NSORaw)

        self.Magic = bytearray_slice(self.NSORaw, 0, byteorderbig = False).decode('unicode_escape')
        self.Flags = bytearray_slice(self.NSORaw, 3, byteorderbig = False)
        self.textFileOffset = bytearray_slice(self.NSORaw, 4, byteorderbig = True)
        self.textMemoryOffset = bytearray_slice(self.NSORaw, 5, byteorderbig = True)
        self.textDecompSize = bytearray_slice(self.NSORaw, 6, byteorderbig = True)
        self.ModuleNameOffset = bytearray_slice(self.NSORaw, 7, byteorderbig = True)
        self.rodataFileOffset = bytearray_slice(self.NSORaw, 8, byteorderbig = True)
        self.rodataMemoryOffset = bytearray_slice(self.NSORaw, 9, byteorderbig = True)
        self.rodataDecompSize = bytearray_slice(self.NSORaw, 10, byteorderbig = True)
        self.ModuleSize = bytearray_slice(self.NSORaw, 11, byteorderbig = True)
        self.rwdataFileOffset = bytearray_slice(self.NSORaw, 12, byteorderbig = True)
        self.rwdataMemoryOffset = bytearray_slice(self.NSORaw, 13, byteorderbig = True)
        self.rwdataDecompSize = bytearray_slice(self.NSORaw, 14, byteorderbig = True)
        self.bssSize = bytearray_slice(self.NSORaw, 15, byteorderbig = True)

        offset = 16 
        self.ModuleId = ''.join('{:02x}'.format(x) for x in self.NSORaw[4*offset : 8+4*offset])
        self.textFileEnd = (bytes_to_int(self.textFileOffset) +
                        bytes_to_int(self.textDecompSize)).to_bytes(4, byteorder='big', signed=False)
        
        if self.has_code_cave():
            self.codeCaveStart = (bytes_to_int(self.textMemoryOffset) +
                    bytes_to_int(self.textDecompSize)).to_bytes(4, byteorder='big', signed=False)
            self.codeCaveEnd = self.rodataMemoryOffset
        else:
            self.codeCaveStart = bytearray.fromhex('00000000')
            self.codeCaveEnd = bytearray.fromhex('00000000')

        self.rodataStart = bytes_to_int(self.rodataMemoryOffset)
        self.rodataEnd = self.rodataStart + bytes_to_int(self.rodataDecompSize)
        self.rwdataStart = bytes_to_int(self.rwdataMemoryOffset)
        self.rwdataEnd = self.rwdataStart + bytes_to_int(self.rwdataDecompSize)
        self.bssStart = get_pages_size(self.rwdataEnd)
        self.bssEnd = self.bssStart + bytes_to_int(self.bssSize)
        self.multimediaStart = get_pages_size(self.bssEnd)

        self.bssMemoryOffset = self.bssStart.to_bytes(4, byteorder='big', signed=False)

    def get_mainfunc_file(self):
        if self.is_NSO_file():
            self.mainFuncFile = self.NSORaw[bytes_to_int(self.textFileOffset) : bytes_to_int(self.textFileEnd)]

    def get_mainfunc_bits_file(self):
        self.mainFuncFile_bits = arm_4bytes_to_bits(self.mainFuncFile)

    def get_NSORaw4Mod_file(self):
        self.NSORaw4Mod = deepcopy(self.NSORaw)

    def is_NSO_file(self):
        file_size = os.path.getsize(self.file_path)
        if file_size < 0x100:
            return False
        buf = bytearray(4)
        with open(self.file_path, 'rb') as fp:
            fp.readinto(buf)
        self.Magic = bytearray_slice(buf, 0, byteorderbig = False).decode('unicode_escape')
        return self.Magic == 'NSO0'

    def is_Compressed(self):
        with open(self.file_path, 'rb') as fp:
            fp.seek(12)
            flags_byte = fp.read(4)
            flags = int.from_bytes(flags_byte, byteorder='little')
        return (flags & 0b111)  # Nso Header from https://github.com/Atmosphere-NX/Atmosphere/blob/35d93a7c4188cda103957aa757fd31f9fe7d18cb/libraries/libstratosphere/include/stratosphere/ldr/ldr_types.hpp#L84

    def is_main_addr(self, addr):
        return addr in range(bytes_to_int(self.textFileOffset), bytes_to_int(self.textFileEnd))

    def is_rodata_addr(self, addr):
        return addr in range(self.rodataStart, self.rodataEnd)

    def is_rwdata_addr(self, addr):
        return addr in range(self.rwdataStart, self.rwdataEnd)

    def has_code_cave(self):
        return (bytes_to_int(self.rodataMemoryOffset) -
                (bytes_to_int(self.textDecompSize) +
                  bytes_to_int(self.textMemoryOffset)) ) > 0
    
    def modify(self, addr, bytes_content, in_code_cave = False):
        if in_code_cave and not self.has_code_cave():
            return

        self.NSORaw4Mod[bytes_to_int(self.textFileOffset) + addr :
                        bytes_to_int(self.textFileOffset) + addr + len(bytes_content)] = bytes_content
            
    def to_Json(self, file_path: Optional[str] = None):
        code_cave = {
                        "start": self.codeCaveStart.hex(),
                        "end": self.codeCaveEnd.hex()
                    } if self.has_code_cave() else None
        json_data = {
                        "Magic": self.Magic,
                        "Flags": self.Flags.hex(),
                        "textFileOffset": self.textFileOffset.hex(),
                        "textMemoryOffset": self.textMemoryOffset.hex(),
                        "textDecompSize": self.textDecompSize.hex(),
                        "ModuleNameOffset": self.ModuleNameOffset.hex(),
                        "rodataFileOffset": self.rodataFileOffset.hex(),
                        "rodataMemoryOffset": self.rodataMemoryOffset.hex(),
                        "rodataDecompSize": self.rodataDecompSize.hex(),
                        "ModuleSize": self.ModuleSize.hex(),
                        "rwdataFileOffset": self.rwdataFileOffset.hex(),
                        "rwdataMemoryOffset": self.rwdataMemoryOffset.hex(),
                        "rwdataDecompSize": self.rwdataDecompSize.hex(),
                        "bssMemoryOffset": self.bssMemoryOffset.hex(),
                        "bssSize": self.bssSize.hex(),
                        "ModuleId": self.ModuleId,
                        "textFileEnd": self.textFileEnd.hex(),
                        "codeCave":code_cave
                    }
        if file_path is not None:
            with open(f'{file_path}.json', 'w') as result_file:
                json.dump(json_data, result_file, indent=1)
        return json_data