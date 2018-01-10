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

"""
Executes a binary circuit, given as a text file, on two given inputs. If an
input is not given, zeros are assumed. Inputs are right-padded with zeros.

The binary circuit should be given in the format described
`here <https://www.cs.bris.ac.uk/Research/CryptographySecurity/MPC/>`_.

For instance, to execute Nigel Smart's addition circuit, download
``adder_32bit.txt`` and run the script, e.g. as follows: ::

  python gc.py adder_32bit.txt 010001 00111

(Note that the inputs Nigel Smart's circuits for arithmetic circuits are given
in inverse binary representation, e.g., 010001 is 100010_2=34 and 00111 is
11100_2=28 so this computation returns 62=111110_2, i.e., 0111110000....)
"""

import sys

from pysnark.lib.base import input_bit_array, output_bit_array

import pysnark.prove

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print >>sys.stderr, "*** Usage:", sys.argv[0], "<circuitfile> [<in1> [<in2>]]"
        sys.exit(2)

    circuit = open(sys.argv[1])
    ngates, nwires = map(int, circuit.next().split())
    nin1, nin2, nout = map(int, circuit.next().split())
    circuit.next()

    wires = dict()

    in1 = sys.argv[2] if len(sys.argv) > 2 else ""
    if len(in1) > nin1:
        print >>sys.stderr, "*** First input too long: is", len(in1), "and should be at most", nin1
        sys.exit(2)
    in1 = in1+("0"*(nin1-len(in1)))
    in1v = input_bit_array(in1, "in1")

    in2 = sys.argv[3] if len(sys.argv) > 3 else ""
    if len(in2) > nin2:
        print >>sys.stderr, "*** Second input too long: is", len(in2), "and should be at most", nin2
        sys.exit(2)
    in2 = in2+("0"*(nin2-len(in2)))
    in2v = input_bit_array(in2, "in2")

    for i in xrange(nin1): wires[i] = in1v[i]
    for i in xrange(nin2): wires[i+nin1] = in2v[i]

    i=0

    for ln in circuit:
        i=i+1
        if i%1000==0: sys.stderr.write(".")

        ln = ln.strip()
        if ln=="": continue
        lns = ln.split(" ")

        tp = lns[2+int(lns[0])+int(lns[1])]
        if tp=="XOR":
            in1 = wires[int(lns[2])]
            in2 = wires[int(lns[3])]
            wires[int(lns[4])] = in1+in2-2*in1*in2
            #print "xor out", in1, in2, wires[int(lns[4])]
        elif tp=="AND":
            in1 = wires[int(lns[2])]
            in2 = wires[int(lns[3])]
            wires[int(lns[4])] = in1*in2
            #print "and out", in1, in2, wires[int(lns[4])]
        elif tp=="INV":
            wires[int(lns[3])] = 1 - wires[int(lns[2])]
            #print "inv out", wires[int(lns[2])], wires[int(lns[3])]
        else:
            print >>sys.stderr, "*** Unrecognized wire type", tp

    if i>=1000: print >>sys.stderr

    print output_bit_array([wires[ngates+nin1+nin2-nout+i] for i in xrange(nout)], "out")
