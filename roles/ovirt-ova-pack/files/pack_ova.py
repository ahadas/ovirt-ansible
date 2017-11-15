#!/usr/bin/python

import io
import os
import sys
import tarfile
import time

BLOCKSIZE = 512
NUL = "\0"
buf = bytearray(4096)


def createTarInfo(name, size):
    info = tarfile.TarInfo(name)
    info.size = size
    info.mtime = time.time()
    return info


def padToBlockSize(file, size):
    remainder = size % BLOCKSIZE
    if remainder > 0:
        file.write(NUL * (BLOCKSIZE - remainder))

ova_path = sys.argv[1]
print "opening for write: %s" % ova_path
ova_fd = os.open(ova_path, os.O_WRONLY)
ova_file = io.FileIO(ova_fd, "w")

ovf = sys.argv[2]
print "writing ovf: %s" % ovf
ovf_size = len(ovf.encode('utf-8'))
tar_info = createTarInfo("ovf", ovf_size)
ova_file.write(tar_info.tobuf())
ova_file.write(ovf)
padToBlockSize(ova_file, ovf_size)

for disk_info in sys.argv[3:]:
    idx = disk_info.index('::')
    disk_path = disk_info[:idx]
    disk_size = int(disk_info[idx+2:])
    print 'writing disk: path=%s size=%d' % (disk_path, disk_size)
    disk_name = os.path.basename(disk_path)
    tar_info = createTarInfo(disk_name, disk_size)
    ova_file.write(tar_info.tobuf())
    disk_fd = os.open(disk_path, os.O_RDONLY)
    disk_file = io.FileIO(disk_fd, "r+")
    while 1:
        if disk_file.readinto(buf) == 0:
            break
        ova_file.write(buf)
    padToBlockSize(ova_file, disk_size)

# writing two null blocks at the end of the file
empty_block = NUL * 512
ova_file.write(empty_block)
ova_file.write(empty_block)

ova_file.close()
