import os, re
from pathlib import Path
# from nsz.NszDecompressor import decompress as NszDecompress  # Hints: works fine on python but not on .exe compilation due to "bar"
from utilities.NszDecompressor import decompress as NszDecompress  # Hints: plz use this for .exe compilation
from nsz.Fs import factory
from struct import unpack
from os import listdir
from utilities.aes128 import AESECB,AESXTS,AESCTR

import tkinter
import tkinter.ttk

class Game_Package:
    def __init__(self, keys, loc) -> None:
        self.keys = keys
        self.loc_msg = loc

        self.xcz_type = ['.XCZ', '.xcz']
        self.nsz_type = ['.NSZ', '.nsz']
        self.xci_type = ['.XCI', '.xci']
        self.nsp_type = ['.NSP', '.nsp']

    def find_largest_file(self, path) -> str:
        largest_file = {'name': None, 'size': 0}
        for root, dirs, files in os.walk(path):
            if 'decompressed_nca' not in root:
                for file in files:
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    if file_size > largest_file['size']:
                        largest_file['name'] = file_path
                        largest_file['size'] = file_size
        return largest_file['name']
    
    def extract_ticket(self, tik_path):  # Refer to Eiffel2018 getMain.py
        with open(tik_path, 'rb') as f:
            signatureType = int.from_bytes(f.read(0x4), 'little')
            signSize = (0x200,0x100,0x3C)[(signatureType&0xFF)%3]
            signPadding = (0x3C,0x3C,0x40)[(signatureType&0xFF)%3]
            f.seek(signSize + signPadding + 0x40, 1)
            titleKey = f.read(0x100)
            f.seek(0x1, 1)
            if ord(f.read(0x1)) == 0:
                titleKey = titleKey[:16]            
            f.seek(0x3, 1)
            X, Y = ord(f.read(0x1)), ord(f.read(0x1))
            masterKeyRev = X if X > 0 else Y
            try:
                title_kek = AESECB(self.keys['titlekek_%02x'%max(masterKeyRev-1, 0)]).decrypt(titleKey)
            except:
                print('\n'.join(eval(self.loc_msg['required key version'])))
                return [None, None]
            f.seek(0x1A, 1)
            title_id = '%016X'%int.from_bytes(f.read(0x8), 'big')
            f.close()
            return [title_kek, title_id]

    def extract_main_file_from_nca(self, nca_path, tik_path, game_path) -> str:  # Refer to Eiffel2018 getMain.py
        if tik_path is not None:
            print('\n'.join(eval(self.loc_msg['Extract ticket'])))
            [title_kek, title_id] = self.extract_ticket(tik_path)
        else:
            title_kek = None
            title_id = None
        
        try:
            with open(nca_path, 'rb') as f:
                print('\n'.join(eval(self.loc_msg['Extract main'])))
                header = AESXTS(self.keys['header_key']).decrypt(f.read(0xC00))
                if header[0x200:0x204] != b'NCA3':
                    raise ValueError('Invalid NCA3 magic')
                ncaType = ('Program','Meta','Control','Manual','Data','PublicData')[header[0x205]]
                # print('Type: %s'%ncaType)
                if ncaType == 'Program':
                    main_path = None
                    build_id = None
                    if title_id is None or title_id == 'Unknown':
                        title_id = '%016X'%int.from_bytes(header[0x210:0x218], 'little')
                    rights_id = '%016X'%int.from_bytes(header[0x230:0x240], 'little')
                    if rights_id == '0000000000000000' or title_kek is None:
                        keyGeneration = max(header[0x206],header[0x220])
                        keyAreaEncryptionKeyIndex = ('application','ocean','system')[header[0x207]]
                        keyIndex = header[0x207] if header[0x220] < 3 else header[0x207] + header[0x206]
                        keyBlock = header[0x300+keyIndex*0x10: 0x300+(keyIndex+1)*0x10]
                        cryptoKey = AESECB(self.keys['key_area_key_%s_%02x'%(keyAreaEncryptionKeyIndex, max(keyGeneration-1,0))]).decrypt(keyBlock)
                        # print('key_area_key_%s_%02x'%(keyAreaEncryptionKeyIndex,max(keyGeneration-1,0)))
                    else:
                        cryptoKey = title_kek
                    # print('%016X'%int.from_bytes(cryptoKey, 'big'))
                    for sectionID in range(4):
                        startOffset, endOffset = unpack('<II',header[0x240+0x10*sectionID: 0x248+0x10*sectionID])
                        if startOffset == 0 and endOffset == 0:
                            continue
                        startOffset = startOffset*0x200 + 0x4000
                        endOffset = endOffset*0x200 + 0x4000
                        fsHeader = header[0x400+sectionID*0x200: 0x400+sectionID*0x200+0x200]
                        fsType = ('RomFS','PartitionFS')[fsHeader[2]]
                        encryptionType = ('Auto','None','AesXts','AesCtr','AesCtrEx','AesCtrSkipLayerHash','AesCtrExSkipLayerHash')[fsHeader[4]]
                        nonce = fsHeader[0x147: 0x13F: -1]
                        if fsType == 'PartitionFS' and (encryptionType == 'AesCtr' or encryptionType == 'AesCtrEx'):
                            mainOffset = 0
                            while mainOffset < 0x30000:
                                f.seek(startOffset + mainOffset)
                                exefsHeader = AESCTR(cryptoKey, nonce, startOffset+mainOffset).decrypt(f.read(0xC00))
                                if exefsHeader[:0x4] == b'PFS0':
                                    break
                                mainOffset += 0x4000
                            if exefsHeader[:0x4] != b'PFS0':
                                raise IOError('PFS0 header error'%exefsHeader[:4])
                            fileCount, stringTableSize = unpack('<II',exefsHeader[0x4:0xC])
                            dataStart = 0x10 + fileCount*0x18 + stringTableSize
                            filenames = exefsHeader[0x10+0x18*fileCount: 0x10+0x18*fileCount+stringTableSize]
                            for i in range(fileCount):
                                offset, size, stringOffset = unpack('<QQI',exefsHeader[0x10+i*0x18:0x24+i*0x18])
                                filename = filenames[stringOffset:].decode('utf-8').split('\x00',1)[0].strip(' \t\r\n\0')
                                # print('\t%i\t%08X\t%s\t%08X'%(i,offset,filename,size))
                                if filename == 'main': 
                                    mainStart = mainOffset + startOffset + dataStart + offset
                                    crypto = AESCTR(cryptoKey, nonce, (mainStart//16)*16)
                                    f.seek((mainStart//16)*16)
                                    NSO = crypto.decrypt(f.read((size//16)*16+16))[mainStart%16:size+(mainStart%16)]
                                    if NSO[:4] == b'NSO0':
                                        build_id = '%016X'%int.from_bytes(NSO[0x40:0x48], 'big')
                                        main_path = os.path.join(os.path.dirname(game_path), f'main_{build_id}')
                                        self.generate_main_file(main_path, NSO)
                                        return main_path  # Warning: skip sdk extraction
                                    else:
                                        raise IOError('main NSO0 header error! %s'%NSO[:4])
                                elif filename == 'sdk': 
                                    sdkStart = mainOffset + startOffset + dataStart + offset
                                    crypto = AESCTR(cryptoKey, nonce, (sdkStart//16)*16)
                                    f.seek((sdkStart//16)*16)
                                    NSO = crypto.decrypt(f.read((size//16)*16+16))[sdkStart%16: size+(sdkStart%16)]
                                    if NSO[:4] == b'NSO0':
                                        sdk_title = f'sdk_{build_id}' if build_id is not None else 'sdk_unknown'
                                        main_path = os.path.join(os.path.dirname(game_path), sdk_title)
                                        self.generate_main_file(main_path, NSO)
                                    else:
                                        raise IOError('sdk NSO0 header error! %s'%NSO[:4])
            f.close()
        except:
            print('\n'.join(eval(self.loc_msg['.nso extraction failed'])))
    
    def generate_main_file(self, main_path, bin):
        fo = open(main_path, 'bw')
        fo.write(bin)
        fo.close()

    def expandFiles(self, path):
        files = []
        path = path.resolve()

        if path.is_file():
            files.append(path)
        else:
            for f_str in listdir(path):
                f = Path(f_str)
                f = path.joinpath(f)
                files.append(f)
        return files

    def check_ticket(self, extract_path):
        for path in self.expandFiles(extract_path):
            if path.suffix == '.tik':
                return str(path)
        return None

    def get_main_file(self, game_path) -> str:
        game_path = Path(game_path).resolve()
        nca_path = None
        tik_path = None
        if game_path.is_file():
            game_path_str = str(game_path)
            out_folder = game_path.parent.absolute().joinpath(game_path.stem)
            container = factory(game_path)
            container.open(game_path_str, 'rb')
            print('\n'.join(eval(self.loc_msg['Extract NCA'])))
            if game_path.suffix in self.xcz_type:
                out_folder = Path(str(out_folder) + '_xcz')
                for hfs0 in container.hfs0:
                    secureIn = hfs0
                    secureIn.unpack(out_folder.joinpath(hfs0._path), "^.*\.(ncz|tik)$")
                tik_path = self.check_ticket(out_folder.joinpath(hfs0._path))
                main_nsz_path = Path(self.find_largest_file(str(out_folder.joinpath('secure'))))
                if not out_folder.joinpath('decompressed_nca').exists():
                    os.makedirs(out_folder.joinpath('decompressed_nca'))
                NszDecompress(main_nsz_path,
                    out_folder.joinpath('decompressed_nca'), None)
                nca_path = str(out_folder.joinpath('decompressed_nca', main_nsz_path.name))[:-1] + 'a'
            elif game_path.suffix in self.nsz_type:
                out_folder = Path(str(out_folder) + '_nsz')
                container.unpack(out_folder, "^.*\.(ncz|tik)$")
                tik_path = self.check_ticket(out_folder)
                main_nsz_path = Path(self.find_largest_file(str(out_folder)))
                if not out_folder.joinpath('decompressed_nca').exists():
                    os.makedirs(out_folder.joinpath('decompressed_nca'))
                NszDecompress(main_nsz_path,
                    out_folder.joinpath('decompressed_nca'), None)
                nca_path = str(out_folder.joinpath('decompressed_nca', main_nsz_path.name))[:-1] + 'a'
            elif game_path.suffix in self.xci_type:
                out_folder = Path(str(out_folder) + '_xci')
                for hfs0 in container.hfs0:
                    secureIn = hfs0
                    secureIn.unpack(out_folder.joinpath(hfs0._path), "^.*\.(nca|tik)$")
                tik_path = self.check_ticket(out_folder.joinpath(hfs0._path))
                nca_path = self.find_largest_file(str(out_folder.joinpath('secure')))
            elif game_path.suffix in self.nsp_type:
                out_folder = Path(str(out_folder) + '_nsp')
                container.unpack(out_folder, "^.*\.(nca|tik)$")
                tik_path = self.check_ticket(out_folder)
                nca_path = self.find_largest_file(str(out_folder))
            container.close()
        else:
            pass
        
        if nca_path is not None:
            main_path = self.extract_main_file_from_nca(nca_path, tik_path, str(game_path))
            return main_path
        else:
            return None