from copy import deepcopy
import os, json
from typing import Optional


class Main_File:  # parse header
    def __init__(self, file_name) -> None:
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
        self.saveFile = bytearray()
        self.NSORaw = bytearray()
        self.mainFuncFile = bytearray()
        self.fileName = file_name

    def get_struct_from_file(self):
        buf = bytearray(os.path.getsize(self.fileName))
        with open(self.fileName, 'rb') as fp:
            fp.readinto(buf)
        self.saveFile = buf
        self.NSORaw = deepcopy(self.saveFile)
        offset = 0
        self.Magic = buf[4*offset : 4+4*offset].decode('unicode_escape')
        offset = 3
        self.Flags = buf[4*offset : 4+4*offset]
        offset = 4
        cache = buf[4*offset : 4+4*offset]
        cache.reverse()
        self.textFileOffset = cache
        offset = 5
        cache = buf[4*offset : 4+4*offset]
        cache.reverse()
        self.textMemoryOffset = cache
        offset = 6
        cache = buf[4*offset : 4+4*offset]
        cache.reverse()
        self.textDecompSize = cache
        offset = 7
        cache = buf[4*offset : 4+4*offset]
        cache.reverse()
        self.ModuleNameOffset = cache
        offset = 8
        cache = buf[4*offset : 4+4*offset]
        cache.reverse()
        self.rodataFileOffset = cache
        offset = 9
        cache = buf[4*offset : 4+4*offset]
        cache.reverse()
        self.rodataMemoryOffset = cache
        offset = 10
        cache = buf[4*offset : 4+4*offset]
        cache.reverse()
        self.rodataDecompSize = cache
        offset = 16 
        self.ModuleId = ''.join('{:02x}'.format(x) for x in buf[4*offset : 8+4*offset])
        self.textFileEnd = (int.from_bytes(self.textFileOffset, byteorder='big', signed=False) +
                        int.from_bytes(self.textDecompSize, byteorder='big', signed=False)).to_bytes(4, byteorder='big', signed=False)
        if self.has_code_cave():
            self.codeCaveStart = (int.from_bytes(self.textMemoryOffset, byteorder='big', signed=False) +
                    int.from_bytes(self.textDecompSize, byteorder='big', signed=False)).to_bytes(4, byteorder='big', signed=False)
            self.codeCaveEnd = self.rodataMemoryOffset
        else:
            self.codeCaveStart = bytearray.fromhex('00000000')
            self.codeCaveEnd = bytearray.fromhex('00000000')

    def is_NSO_file(self):
        buf = bytearray(os.path.getsize(self.fileName))
        with open(self.fileName, 'rb') as fp:
            fp.readinto(buf)
        offset = 0
        self.Magic = buf[4*offset : 4+4*offset].decode('unicode_escape')
        if self.Magic == 'NSO0':
            return True
        else:
            return False

    def is_Compressed(self):
        buf = bytearray(os.path.getsize(self.fileName))
        with open(self.fileName, 'rb') as fp:
            fp.readinto(buf)
        offset = 3
        self.Flags = buf[4*offset : 4+4*offset]
        if sum(self.Flags) != 0:
            return True
        else:
            return False
    
    def is_main_addr(self, addr):
        return addr in range(int.from_bytes(self.textFileOffset, byteorder='big', signed=False), int.from_bytes(self.textFileEnd, byteorder='big', signed=False))

    def has_code_cave(self):
        if (int.from_bytes(self.rodataMemoryOffset, byteorder='big', signed=False) -
            (int.from_bytes(self.textDecompSize, byteorder='big', signed=False) +
            int.from_bytes(self.textMemoryOffset, byteorder='big', signed=False)) ) > 0:
            return True
        else:
            return False
    
    def modify(self, code_type, relative_addr, contents):
        if code_type == 'asm_main':
            self.NSORaw[int.from_bytes(self.textFileOffset, byteorder='big', signed=False)+relative_addr :
                         int.from_bytes(self.textFileOffset, byteorder='big', signed=False)+relative_addr+len(contents)] = contents
        elif code_type == 'asm_cave':
            if self.has_code_cave():
                self.NSORaw[int.from_bytes(self.codeCaveStart, byteorder='big', signed=False)+relative_addr :
                            int.from_bytes(self.codeCaveStart, byteorder='big', signed=False)+relative_addr+len(contents)] = contents
        return
            
    def to_Json(self, file_name: Optional[str] = None):
        if self.has_code_cave():
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
                        "codeCave":
                        {
                            "start": self.codeCaveStart.hex(),
                            "end": self.codeCaveEnd.hex()
                        }
                    }
        else:
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
                        "textFileEnd": self.textFileEnd.hex()
                    }
        if file_name is not None:
            with open(f'{file_name}.json', 'w') as result_file:
                json.dump(json_data, result_file, indent=1)
        return json_data
    
    def get_mainfunc_file(self):
        if self.is_NSO_file():
            self.mainFuncFile = self.saveFile[int.from_bytes(self.textFileOffset, byteorder='big', signed=False) : int.from_bytes(self.textFileEnd, byteorder='big', signed=False)]
            return True
        else:
            return False