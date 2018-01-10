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

import os.path
import subprocess
import sys

from pysnark.runtime import Var, subqap, enterfn
from pysnark.lib.array import Array
from pysnark.lib.ggh import ggh_hash, ggh_hash_packed
from pysnark.lib.ggh_plain import packin, packout, unpackin, unpackout

import pysnark.prove

if __name__ == '__main__':
    if len(sys.argv)<2:
        print "*** Usage: ", sys.argv[0], "file [pos]"
        sys.exit(2)

    # lib
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


    def hextobits(str):
        for ch in str:
            if ch=='\n' or ch=='\r' or ch==' ': continue
            val = (ord(ch) - ord('A') + 10 if ord(ch) >= ord('A') else ord(ch) - ord('0'))
            yield 1 if val & 8 != 0 else 0
            yield 1 if val & 4 != 0 else 0
            yield 1 if val & 2 != 0 else 0
            yield 1 if val & 1 != 0 else 0


    def bitstohex(str):
        try:
            while True:
                bit1 = str.next()
                bit2 = str.next()
                bit3 = str.next()
                bit4 = str.next()
                val = bit1 * 8 + bit2 * 4 + bit3 * 2 + bit4
                yield chr(val - 10 + ord('A') if val >= 10 else val + ord('0'))
        except StopIteration:
            pass

    def printashex(bits):
        for z in bitstohex(iter(bits)):
            sys.stdout.write(z)
        print

    def printpackedin(vals):
        unpk = unpackin([val.value for val in vals])
        printashex(unpk)

    def printpackedout(vals):
        unpk = unpackout([val.value for val in vals])
        printashex(unpk)

    # convert file into hash tree

    fname = sys.argv[1]

    if not os.path.isfile(fname+".l0"):
        print >>sys.stderr, "*** Writing level 0 hash", fname+".l0"
        l0out = open(fname+".l0", "w")
        fin = open(fname, "rb")
        while True:
            ch = fin.read(1)
            if ch=='': break
            l0out.write(chr(ord(ch)/16-10+ord('A') if ord(ch)/16 >= 10 else ord(ch)/16+ord('0')))
            l0out.write(chr(ord(ch)%16-10+ord('A') if ord(ch)%16 >= 10 else ord(ch)%16+ord('0')))
        l0out.close()
        fin.close()

    fsz = os.path.getsize(fname)
    fbits = fsz*8

    hashexe = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hash.exe" if os.name=="nt" else "hash")

    level = 0

    while fbits>1216:
        fin = fname+".l"+str(level)
        fout = fname+".l"+str(level+1)

        if not os.path.exists(fout):
            print >>sys.stderr, "*** Hashing", fin, "to", fout
            inf = open(fin)
            outf = open(fout, "w")

            if not os.path.isfile(hashexe):
                print >>sys.stderr, "*** Hashing executable", hashexe, "not found; compile it first"
                sys.exit(2)

            subprocess.call(hashexe, stdin=inf, stdout=outf)

        fbits = fbits/6
        level = level+1

    tophash = list(readhexbits(open(fname+".l"+str(level))))
    print "Level", level-1, "hash:", packout(tophash)

    if len(sys.argv)==2: sys.exit(0)

    # hash tree authentication

    if len(sys.argv)==4 and sys.argv[3]=="--single":
        enterfn("hashtree_" + str(level) + "_single")
    elif len(sys.argv)==4:
        print "*** Usage:", sys.argv[2], "<file> <pos> [--single]"
        sys.exit(2)
    else:
        ggh_hash_packed = subqap("ggh")(ggh_hash_packed)
        enterfn("hashtree_" + str(level))

    posi = int(sys.argv[2])
    pos = Var(posi, "pos")
    pos.assert_smaller(fsz)

    # read level 0

    quo,rem= pos.divmod(912, posi.bit_length()-9)

    l0file = open(fname+".l0")
    l0file.seek(2*(quo.value*912))
    bits = map(lambda x: Var(x, True), list(hextobits(l0file.read(2*912))))
    bits = bits+[Var(0,True) for _ in xrange(7296-len(bits))]
    for bit in bits: bit.assert_bit() # TODO: ggh_hash_packed also assert bits, but this does not ensure that packin's input are bits!
    l0file.close()

    tobytes = [bits[i]*128+bits[i+1]*64+bits[i+2]*32+bits[i+3]*16+
               bits[i+4]*8+bits[i+5]*4+bits[i+6]*2+bits[i+7] for i in xrange(0,len(bits),8)]

    res = (Array(tobytes)[rem]).val("char")
    print "Character at location", posi, ":", res, chr(res)

    hin = packin(bits)
    #printpackedin(hin)
    hout = ggh_hash_packed(hin)
    #printpackedout(hout)

    for i in xrange(1,level):
        print >>sys.stderr, "At level", i, "of", level-1
        quo,rem = quo.divmod(6, posi.bit_length()-7-2*i) # could be slightly tighter
        hashfl = open(fname+".l"+str(i))
        hashfl.seek(1824*quo.value)
        hin = Array([Array([Var(val, True) for val in packout(list(hextobits(hashfl.read(304))))]) for _ in xrange(6)])
        hashfl.close()
        hin[rem].assert_equals(Array(hout))
        hout = ggh_hash_packed(hin.joined())
        #printpackedout(hout)

    print "Level", level-1,  "hash (from VC): ", Var.vals(hout, "tophash")