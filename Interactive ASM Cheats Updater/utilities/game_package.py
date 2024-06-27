import os, re
from pathlib import Path
from tkinter import messagebox
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from utilities.NszDecompressor import decompress as NszDecompress  # Hints: modified progress bar for tkinter
from nsz.Fs import factory
from struct import unpack
from os import listdir
from utilities.aes128 import AESECB,AESXTS,AESCTR
from utilities.exception import GamePackageError


generate_msg = lambda x:'\n'.join(eval(x))  # just for static characters


class GamePackage:
    def __init__(self, globalInfo):
        self.key_path = globalInfo.root_path
        self.logger = globalInfo.logger
        self.msg_map = globalInfo.msg_map
        self.str_map = globalInfo.str_map
        self.msgbox_title_map = globalInfo.msgbox_title_map
        self.keys = self.get_keys()

    def get_keys(self):
        keys = {}
        key_file = Path(os.path.join(self.key_path, 'keys.txt'))
        if not key_file.is_file():
            key_file = Path.home().joinpath('.switch', 'prod.keys')
        if not key_file.is_file():
            messagebox.showwarning(title=self.msgbox_title_map['Warning'], message=generate_msg(self.msg_map['request keys']))
            raise GamePackageError('Keys not found!')
        with open(key_file, encoding="utf8") as f:
            for line in f.readlines():
                pattern = re.match('\s*([a-z0-9_]+)\s*=\s*([A-F0-9]+)\s*', line, re.I)
                if pattern:
                    keys[pattern.group(1)] = bytes.fromhex(pattern.group(2))
        return keys

    def find_largest_file(self, path) -> str:
        largest_file = {'name': None, 'size': 0}
        for root, dirs, files in os.walk(path):
            if 'decompressed_nca' in root:
                continue
            for file in files:
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                if file_size > largest_file['size']:
                    largest_file['name'] = file_path
                    largest_file['size'] = file_size
        return largest_file['name']
    
    def decrypt_aes_abc(self, data, key):
    # Author: RiggZh
    # data: titlekek_source  key: master_key_0x
    # https://pycryptodome.readthedocs.io/en/latest/src/cipher/classic.html#ecb-mode
    # https://stackoverflow.com/questions/52964138/how-can-i-decrypt-message-from-user-input-in-python-using-cryptography
        decryptor = Cipher(
            algorithms.AES(key),
            modes.ECB(),
            backend=default_backend()
        ).decryptor()
        return decryptor.update(data) + decryptor.finalize()

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
                if 'titlekek_%02x'%max(masterKeyRev-1, 0) not in self.keys:
                    if 'master_key_%02x'%max(masterKeyRev-1, 0) not in self.keys:
                        self.logger.warning('\n'.join(eval(self.msg_map['required master key version'])))
                        messagebox.showwarning(title=self.msgbox_title_map['Warning'], message='\n'.join(eval(self.msg_map['required master key version'])))
                        return [None, None]
                    else:
                        title_kek_0x = self.decrypt_aes_abc(self.keys['titlekek_source'], self.keys['master_key_%02x'%max(masterKeyRev-1, 0)])
                        title_kek = AESECB(title_kek_0x).decrypt(titleKey)
                else:
                    title_kek = AESECB(self.keys['titlekek_%02x'%max(masterKeyRev-1, 0)]).decrypt(titleKey)
            except:
                self.logger.warning('\n'.join(eval(self.msg_map['required title key version'])))
                messagebox.showwarning(title=self.msgbox_title_map['Warning'], message='\n'.join(eval(self.msg_map['required title key version'])))
                return [None, None]
            f.seek(0x1A, 1)
            title_id = '%016X'%int.from_bytes(f.read(0x8), 'big')
            f.close()
            return [title_kek, title_id]

    def extract_main_file_from_nca(self, nca_path, tik_path, game_path) -> str:  # Refer to Eiffel2018 getMain.py
        if tik_path is not None:
            print(generate_msg(self.msg_map['Extract ticket']))
            self.logger.info(generate_msg(self.msg_map['Extract ticket']))
            [title_kek, title_id] = self.extract_ticket(tik_path)
        else:
            title_kek = None
            title_id = None
        
        try:
            with open(nca_path, 'rb') as f:
                print(generate_msg(self.msg_map['Extract main']))
                self.logger.info(generate_msg(self.msg_map['Extract main']))
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
                                raise GamePackageError('PFS0 header error'%exefsHeader[:4])
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
                                        main_path = os.path.join(os.path.dirname(game_path), f'BID_{build_id}')
                                        self.generate_main_file(main_path, NSO)
                                        return main_path  # Warning: skip sdk extraction
                                    else:
                                        raise GamePackageError('main NSO0 header error! %s'%NSO[:4])
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
                                        raise GamePackageError('sdk NSO0 header error! %s'%NSO[:4])
            f.close()
        except:
            messagebox.showerror(title=self.msgbox_title_map['Error'], message=generate_msg(self.msg_map['.nso extraction failed']))
            raise GamePackageError(generate_msg(self.msg_map['.nso extraction failed']))
    
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

    def get_nca_from_xcx(self, container, out_folder, file_type):
        out_folder = Path(str(out_folder) + '_' + file_type)
        for hfs0 in container.hfs0:
            secureIn = hfs0
            if file_type == 'xci':
                secureIn.unpack(out_folder.joinpath(hfs0._path), "^.*\.(nca|tik)$")
            elif file_type == 'xcz':
                secureIn.unpack(out_folder.joinpath(hfs0._path), "^.*\.(ncz|tik)$")

        tik_path = self.check_ticket(out_folder.joinpath(hfs0._path))
        if file_type == 'xci':
            nca_path = self.find_largest_file(str(out_folder.joinpath('secure')))
        elif file_type == 'xcz':
            main_nsz_path = Path(self.find_largest_file(str(out_folder.joinpath('secure'))))
            if not out_folder.joinpath('decompressed_nca').exists():
                os.makedirs(out_folder.joinpath('decompressed_nca'))
            NszDecompress(main_nsz_path,
                out_folder.joinpath('decompressed_nca'), None)
            nca_path = str(out_folder.joinpath('decompressed_nca', main_nsz_path.name))[:-1] + 'a'
        
        return (tik_path, nca_path)
    
    def get_nca_from_nsx(self, container, out_folder, file_type):
        out_folder = Path(str(out_folder) + '_' + file_type)
        if file_type == 'nsp':
            container.unpack(out_folder, "^.*\.(nca|tik)$")
        elif file_type == 'nsz':
            container.unpack(out_folder, "^.*\.(ncz|tik)$")

        tik_path = self.check_ticket(out_folder)
        if file_type == 'nsp':
            nca_path = self.find_largest_file(str(out_folder))
        elif file_type == 'nsz':
            main_nsz_path = Path(self.find_largest_file(str(out_folder)))
            if not out_folder.joinpath('decompressed_nca').exists():
                os.makedirs(out_folder.joinpath('decompressed_nca'))
            NszDecompress(main_nsz_path,
                out_folder.joinpath('decompressed_nca'), None)
            nca_path = str(out_folder.joinpath('decompressed_nca', main_nsz_path.name))[:-1] + 'a'

        return (tik_path, nca_path)

    def get_main_file(self, game_path) -> str:
        game_path = Path(game_path).resolve()
        nca_path = None
        tik_path = None
        if not game_path.is_file():
            return None
        
        game_path_str = str(game_path)
        out_folder = game_path.parent.absolute().joinpath(game_path.stem)
        container = factory(game_path)
        container.open(game_path_str, 'rb')
        print(generate_msg(self.msg_map['Extract NCA']))
        self.logger.info(generate_msg(self.msg_map['Extract NCA']))
        if game_path.suffix.lower() == '.xcz':
            (tik_path, nca_path) = self.get_nca_from_xcx(container, out_folder, file_type = 'xcz')
        elif game_path.suffix.lower() == '.nsz':
            (tik_path, nca_path) = self.get_nca_from_nsx(container, out_folder, file_type = 'nsz')
        elif game_path.suffix.lower() == '.xci':
            (tik_path, nca_path) = self.get_nca_from_xcx(container, out_folder, file_type = 'xci')
        elif game_path.suffix.lower() == '.nsp':
            (tik_path, nca_path) = self.get_nca_from_nsx(container, out_folder, file_type = 'nsp')
        container.close()
        
        if nca_path is None:
            return None
            
        main_path = self.extract_main_file_from_nca(nca_path, tik_path, str(game_path))
        return main_path