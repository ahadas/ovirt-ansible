#!/usr/bin/python

import os
import io
import tarfile
import sys
import time

BLOCKSIZE = 512
NUL = "\0"
buf = bytearray(4096)

fd = os.open(sys.argv[1], os.O_WRONLY | os.O_CREAT)
tar = io.FileIO(fd, "w")

print 'writing ovf'
ovf = sys.argv[2]
info = tarfile.TarInfo(name="ovf")
info.size = len(ovf.encode('utf-8'))
info.mtime = time.time()
tar.write(info.tobuf())
tar.write(ovf)
remainder = info.size % BLOCKSIZE
if remainder > 0:
    tar.write(NUL * (BLOCKSIZE - remainder))

for arg in sys.argv[3:]:
    idx = arg.index('::')
    path = arg[:idx]
    size = int(arg[idx+2:])
    print 'writing disk %s (%d)' % (path, size)
    fd = os.open(path, os.O_RDONLY)
    basename = os.path.basename(path)
    info = tarfile.TarInfo(name=basename)
    info.size = size
    info.mtime = time.time()
    tar.write(info.tobuf())
    file = io.FileIO(fd, "r+")
    while 1:
        if file.readinto(buf) == 0:
            break
        tar.write(buf)
    remainder = info.size % BLOCKSIZE
    if remainder > 0:
        tar.write(NUL * (BLOCKSIZE - remainder))

# writing two null blocks at the end of the file
empty = NUL * 512
tar.write(empty)
tar.write(empty)

tar.close()

