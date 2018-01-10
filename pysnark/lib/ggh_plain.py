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

import os

coeffile = open(os.path.join(os.path.dirname(__file__), 'gghkey.txt'))
coeffile.read(17)
coeffs = [int(coeffile.read(5), 16) for _ in xrange(64*7296)]

def ggh_hash(plain):
    out = []
    
    for outix in xrange(64):
        outval = sum([x*y for (x,y) in zip(coeffs[7296*outix:7296*outix+7296],plain)])
        for i in xrange(19):
            out.append(1 if outval&(1<<(18-i)) else 0)
      
    return out


def toint(vals):
    return sum([val * (1 << (len(vals) - ix - 1)) for (ix, val) in enumerate(vals)])

def fromint(val, len):
    return [1 if val&(1<<(len-ix-1)) else 0 for ix in xrange(len)]

def packout(vals):
    return [toint(vals[0:244]),
            toint(vals[244:488]),
            toint(vals[488:732]),
            toint(vals[732:976]),
            toint(vals[976:])]

def packin(vals):
    return packout(vals[0:1216]) + packout(vals[1216:2432]) + packout(vals[2432:3648]) + \
           packout(vals[3648:4864]) + packout(vals[4864:6080]) + packout(vals[6080:])

def unpackout(vals):
    return fromint(vals[0],244)+fromint(vals[1],244)+fromint(vals[2],244)+fromint(vals[3],244)+fromint(vals[4],240)

def unpackin(vals):
    return unpackout(vals[0:5]) + unpackout(vals[5:10]) + unpackout(vals[10:15]) + \
           unpackout(vals[15:20]) + unpackout(vals[20:25]) + unpackout(vals[25:30])
