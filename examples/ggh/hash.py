# Copyright (c) 2016-2018 Koninklijke Philips N.V. All rights reserved. A
# copyright license for redistribution and use in source and binary forms,
# with or without modification, is hereby granted for non-commercial,
# experimental and research purposes, provided that the following conditions
# are met:
# - Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimers.
# - Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimers in the
#   documentation and/or other materials provided with the distribution. If
#   you wish to use this software commercially, kindly contact
#   info.licensing@philips.com to obtain a commercial license.
#
# This license extends only to copyright and does not include or grant any
# patent license or other license whatsoever.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import sys

from pysnark.lib.ggh_plain import ggh_hash

def readhexbits(fl):
    while True:
        ch = fl.read(1)
        if ch=='': return
        if ch==' ' or ch=='\n' or ch=='\r': continue
        val = (ord(ch)-ord('A')+10 if ord(ch)>=ord('A') else ord(ch)-ord('0'))
        yield 1 if val&8!=0 else 0
        yield 1 if val&4!=0 else 0
        yield 1 if val&2!=0 else 0
        yield 1 if val&1!=0 else 0

def bitstohex(str):
    try:
        while True:
            bit1 = str.next()
            bit2 = str.next()
            bit3 = str.next()
            bit4 = str.next()
            val = bit1*8 + bit2*4 + bit3*2 + bit4
            yield chr(val-10+ord('A') if val >= 10 else val+ord('0'))
    except StopIteration:
        pass

bits = readhexbits(sys.stdin)

hexin = []
try:
    while True:
        hexin = []
        for _ in xrange(7296): hexin.append(bits.next())
        sys.stdout.write("".join(list(bitstohex(iter(ggh_hash(hexin))))))
except StopIteration:
    if len(hexin)>0: sys.stdout.write("".join(list(bitstohex(iter(ggh_hash(hexin))))))

print
