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
This module provides efficient hashes using the "Ajtai-GGH" hash function
due to Ajtai and Goldreich/Goldwasser/Halevi (Goldreich, Goldwasser, Halevi,
"Collision-Free Hashing from Lattice Problems").

This implementation uses parameters N=64, Q=524288, M=7296 and translates a
7296-bit input into a 1216-bit output (i.e., it has a compression ratio of 6).
These parameters are as suggested by Chris Peikert and used in Pepper,
see `here <https://github.com/pepper-project/pequin/blob/master/compiler/Gocode/src/vericomp/hash/ggh/ggh.go>`_.

The coefficients of the hash function have been generated using a PRF.
"""

import os

from pysnark.runtime import Var
from pysnark.lib.base import lin_comb_pub
from pysnark.lib.ggh_plain import coeffs, unpackin, packout as packoutplain, packin as packinplain

# also work on Vars
packout = packoutplain
packin = packinplain

def ggh_hash(plain):
    """
    Computes a GGH hash of the given input bits. This function does not ensure
    that the inputs are actually bits, but it guarantees that the outputs are bits

    :param plain: Plaintext: array of 7296 bits
    :return: Hash: array of 1216 bits
    """
    out = []
    
    for outix in xrange(64):
        outval = lin_comb_pub(coeffs[7296*outix:7296*outix+7296], plain)
        outvalb = outval.bit_decompose(32)                       # 912*8 19-bit values can be at most 32 bits long        
        out = out + outvalb[18::-1]                              # last 19 bits, most to least significant

    return out

def ggh_hash_packed(plain_packed):
    bits = [Var(bit,True) for bit in unpackin([pl.value for pl in plain_packed])]
    for bit in bits: bit.assert_bit()
    out = ggh_hash(bits)
    return packout(out)