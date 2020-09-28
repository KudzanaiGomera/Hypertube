import math
import hashlib
import time
from bcoding import bencode, bdecode
import logging
import os
import sys

a1 = sys.argv
class Torrent(object):
    def __init__(self):

        self.torrent_file2 = a1[1]
        self.torrent_file = {}
        self.total_length: int = 0
        self.piece_length: int = 0
        self.pieces: int = 0
        self.info_hash: str = ''
        self.peer_id: str = ''
        self.announce_list = ''
        self.file_names = []
        self.number_of_pieces: int = 0

    # def load_from_path(self, path):
    #     with open(path, 'rb') as file:
    #         contents = bdecode(file)
    def open_from_file(self, movie):
        with open(a1[1], 'r+b') as file2:
            contents2 =bdecode(file2)

        self.torrent_file2 = contents2
        self.piece_length = self.torrent_file2['info']['piece length']
        self.pieces = self.torrent_file2['info']['pieces']
        raw_info_hash = bencode(self.torrent_file2['info'])
        self.info_hash = hashlib.sha1(raw_info_hash).digest()
        self.peer_id = self.generate_peer_id()
        self.announce_list = self.get_trakers()
        self.init_files()
        self.number_of_pieces = math.ceil(self.total_length / self.piece_length)
        logging.debug(self.announce_list)
        logging.debug(self.file_names)

        assert(self.total_length > 0)
        assert(len(self.file_names) > 0)

        return self

    def init_files(self):
        root = self.torrent_file2['info']['name']

        if 'files' in self.torrent_file2['info']:
            if not os.path.exists(root):
                os.mkdir(root, 0o0766 )

            for file in self.torrent_file2['info']['files']:
                path_file = os.path.join(root, *file["path"])

                if not os.path.exists(os.path.dirname(path_file)):
                    os.makedirs(os.path.dirname(path_file))

                self.file_names.append({"path": path_file , "length": file["length"]})
                self.total_length += file["length"]

        else:
            self.file_names.append({"path": root , "length": self.torrent_file['info']['length']})
            self.total_length = self.torrent_file2['info']['length']

    def get_trakers(self):
        if 'announce-list' in self.torrent_file2:
            return self.torrent_file2['announce-list']
        else:
            return [[self.torrent_file2['announce']]]

    def generate_peer_id(self):
        seed = str(time.time())
        return hashlib.sha1(seed.encode('utf-8')).digest()
