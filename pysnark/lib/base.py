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

from pysnark.runtime import Var
import pysnark.runtime

def input_bit_array(bits, nm=None):
    """
    Imports bitstring as a single input of the program. This checks that all provided values are actually bits.

    :param bits: String consisting of (at most 253) 0s and 1s (starting with most significant)
    :param nm: Name of input variable (None for automatic)
    :return: Array of bits
    """

    assert len(bits)<=253

    bvals = [Var(int(bit),True) for bit in bits]
    for bit in bvals: bit.assert_bit()
    io = Var(sum([(1<<(len(bits)-ix-1))*v.value for (ix,v) in enumerate(bvals)]), nm)
    (io-sum([(1<<(len(bits)-ix-1))*v for (ix,v) in enumerate(bvals)])).assert_zero()

    return bvals


def output_bit_array(bits, nm=None):
    """
    Exports bitstring as a single output of the QAP. This does not check that all provided values are actually bits;
    use :py:func:`pysnark.runtime.Var.assert_bit` for that.

    :param bits: Array of Vars representing bits
    :param nm: Name of output variable (None for automatic)
    :return: Bitstring representing the value
    """

    Var(sum([(1<<(len(bits)-ix-1))*v.value for (ix,v) in enumerate(bits)]), nm)
    return "".join([str(bit.value) for bit in bits])


def lin_comb_pub(cofs, vals):
    """
    Returns linear combination of given values with given coefficients. This
    can be executed more efficiently than computing the sum by hand but
    introduces an additional equation to the program.

    :param cofs: Array of integer coefficients
    :param vals: Array of values
    :return: Variable representing the linear combination
    """
    
    global qape
    
    intval = sum([c*v for (c,v) in zip(cofs,vals) if isinstance(v,int)], 0)
    ret = Var(sum([c*v.value for (c, v) in zip(cofs, vals) if not isinstance(v,int)])+intval, True)

    if pysnark.runtime.qape != None:
        intstr = " "+Var.constant(intval).strsig() if intval!=0 else ""
        print >> pysnark.runtime.qape, "*  ="+intstr, " ".join([(c * v).strsig() for (c, v) in zip(cofs, vals) if not isinstance(v,int)]), (-1 * ret).strsig()

    return ret

def lin_comb(cofs, vals):
    """
    Returns linear combination of given values with given coefficients
    :param cofs: Array of variable coefficients
    :param vals: Array of variable values
    :return: Variable representing the linear combination
    """

    return sum([c*v for (c,v) in zip(cofs, vals)])

def if_then_else(cond, trueval, falseval):
    """
    Returns one of two values depending on choice bit
    :param cond: Choice bit (function does not ensure that this is a bit)
    :param trueval: Value if choice bit is 1
    :param falseval: Value if choice bit is 0
    :return: Value given by choice bit
    """

    return falseval+cond*(trueval-falseval)
