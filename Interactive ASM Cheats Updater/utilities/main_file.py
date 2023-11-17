import os, json, shutil, time, subprocess, chardet
from copy import deepcopy
from tkinter import messagebox
from typing import Optional
from asyncio.subprocess import PIPE, STDOUT

from utilities.exception import MainNSOError


def bytearray_slice(bytearray, loc, byteorderbig = False):
    byte_4 = bytearray[4*loc : 4+4*loc]
    if byteorderbig:
        byte_4.reverse()
    return byte_4

def bytes_to_int(bytearray):
    return int.from_bytes(bytearray, byteorder='big', signed=False)

generate_msg = lambda x:'\n'.join(eval(x))


class MainNSOStruct:
    def __init__(self, file_path: str, globalInfo) -> None:
        self.file_path = file_path
        self.logger = globalInfo.logger
        self.msg_map = globalInfo.msg_map
        self.back_path = globalInfo.back_path
        self.tool_path = globalInfo.tool_path

        self.Magic = ''
        self.Flags = bytearray(4)
        self.textFileOffset = bytearray(4)  # text base address in main file
        self.textMemoryOffset = bytearray(4)  # text base address in console memory
        self.textDecompSize = bytearray(4)
        self.ModuleNameOffset = bytearray(4)  # only text_addr in ModuleName needed
        self.rodataFileOffset = bytearray(4)  # rodata base address in main file
        self.rodataMemoryOffset = bytearray(4)  # rodata base address in console memory
        self.rodataDecompSize = bytearray(4)
        self.ModuleId = ''  # build_id
        self.textFileEnd = bytearray(4)
        self.codeCaveStart = bytearray(4)
        self.codeCaveEnd = bytearray(4)

        self.NSORaw = bytearray()
        self.NSORaw4Mod = bytearray()
        self.mainFuncFile = bytearray()

    def process_file(self):
        if not self.is_NSO_file():
            raise MainNSOError(generate_msg(self.msg_map['NOT NSO File']))
        else:
            if self.is_Compressed():
                self.decompress()
            self.get_struct_from_file()
            self.get_mainfunc_file()
            return True

    def decompress(self):
        file_name = os.path.basename(self.file_path)
        if not os.path.exists(self.back_path):
            os.makedirs(self.back_path)
       
        back_file_path = os.path.join(self.back_path, f'{file_name}_❀{int(time.time())}.bak')
        shutil.copyfile(self.file_path, back_file_path)
        if not os.path.exists(os.path.join(self.tool_path, 'nsnsotool.exe')):
            messagebox.showerror(title='Error', message=generate_msg(self.msg_map['nsnsotool missing']))
            raise MainNSOError(MainNSOError(generate_msg(self.msg_map['nsnsotool missing'])))

        try:
            process = subprocess.Popen(["cmd"], shell=False, close_fds=True, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
            commands = ('cd tools\n'
                        f'nsnsotool "{self.file_path}"\n'
                    )
            outs, errs = process.communicate(commands.encode('utf-8'))
            content = self.decode_outs_from_system(outs)
            if content is not None:
                print(*content, sep="\n")
        except Exception as e:
            messagebox.showerror(title='Error', message=generate_msg(self.msg_map['nsnsotool warning']))
            raise MainNSOError(MainNSOError(generate_msg(self.msg_map['nsnsotool warning'])))
        
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
        buf = bytearray(os.path.getsize(self.file_path))
        with open(self.file_path, 'rb') as fp:
            fp.readinto(buf)
        self.NSORaw = buf
        self.NSORaw4Mod = deepcopy(self.NSORaw)

        self.Magic = bytearray_slice(buf, 0, byteorderbig = False).decode('unicode_escape')
        self.Flags = bytearray_slice(buf, 3, byteorderbig = False)
        self.textFileOffset = bytearray_slice(buf, 4, byteorderbig = True)
        self.textMemoryOffset = bytearray_slice(buf, 5, byteorderbig = True)
        self.textDecompSize = bytearray_slice(buf, 6, byteorderbig = True)
        self.ModuleNameOffset = bytearray_slice(buf, 7, byteorderbig = True)
        self.rodataFileOffset = bytearray_slice(buf, 8, byteorderbig = True)
        self.rodataMemoryOffset = bytearray_slice(buf, 9, byteorderbig = True)
        self.rodataDecompSize = bytearray_slice(buf, 10, byteorderbig = True)

        offset = 16 
        self.ModuleId = ''.join('{:02x}'.format(x) for x in buf[4*offset : 8+4*offset])
        self.textFileEnd = (bytes_to_int(self.textFileOffset) +
                        bytes_to_int(self.textDecompSize)).to_bytes(4, byteorder='big', signed=False)
        
        if self.has_code_cave():
            self.codeCaveStart = (bytes_to_int(self.textMemoryOffset) +
                    bytes_to_int(self.textDecompSize)).to_bytes(4, byteorder='big', signed=False)
            self.codeCaveEnd = self.rodataMemoryOffset
        else:
            self.codeCaveStart = bytearray.fromhex('00000000')
            self.codeCaveEnd = bytearray.fromhex('00000000')
    
    def get_mainfunc_file(self):
        if self.is_NSO_file():
            self.mainFuncFile = self.NSORaw[bytes_to_int(self.textFileOffset) : bytes_to_int(self.textFileEnd)]

    def is_NSO_file(self):
        buf = bytearray(os.path.getsize(self.file_path))
        with open(self.file_path, 'rb') as fp:
            fp.readinto(buf)
        self.Magic = bytearray_slice(buf, 0, byteorderbig = False).decode('unicode_escape')
        return self.Magic == 'NSO0'

    def is_Compressed(self):
        buf = bytearray(os.path.getsize(self.file_path))
        with open(self.file_path, 'rb') as fp:
            fp.readinto(buf)
        self.Flags = bytearray_slice(buf, 3, byteorderbig = False)
        return sum(self.Flags) != 0
    
    def is_main_addr(self, addr):
        return addr in range(bytes_to_int(self.textFileOffset), bytes_to_int(self.textFileEnd))

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
                        "ModuleId": self.ModuleId,
                        "textFileEnd": self.textFileEnd.hex(),
                        "codeCave":code_cave
                    }
        if file_path is not None:
            with open(f'{file_path}.json', 'w') as result_file:
                json.dump(json_data, result_file, indent=1)
        return json_data