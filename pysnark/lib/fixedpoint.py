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

from pysnark.options import vc_p
from pysnark.runtime import Var

"""
Support for fixed-point computations
"""

class VarFxp(Var):
    """
    Variable representing a fixed-point number. Number x is represented as integer
    :math:`x * 2^r`, where r is the resolution :py:data:`VarFxp.res`
    """

    res = 20     #: Resulution for fixed-point numbers
    maxden = 40  #: Maximal length of denominiators for :py:func:`__div__`, including resolution

    def __init__(self, val, sig=None):
        """
        Constructor, see :py:func:`Var.__init__`

        :param val: Value for the variable; accepts floats or ints (interpr
        :param sig: See :py:func:`Var.__init__`
        """
        if isinstance(val,float): val = int(val*(1<<VarFxp.res)+0.5)
        Var.__init__(self, val, sig)

    @classmethod
    def fromvar_noconv(cls, var):
        return VarFxp(var.value, var.sig)

    @classmethod
    def fromvar(cls, var):
        """
        Convers a non-fixed-point variable to fixed point

        :param var: A non-fixed-point variable
        :return: A new fixed-point variable representing the same value
        """
        assert not isinstance(var, VarFxp)

        return VarFxp.fromvar_noconv(var*(1<<VarFxp.res))

    def floatval(self):
        """
        Returns floating-point value represented by this variable.

        :return: value
        """
        val = self.value if self.value < vc_p / 2 else self.value - vc_p
        valf = float(val) / (1 << VarFxp.res)
        return valf

    def __repr__(self):
        return Var.__repr__+ "e-" + str(VarFxp.res)

    def __str__(self):
        return "{"+str(self.floatval())+"}"

    def val(self, nm=None):
        Var.val(self)
        return self.floatval()

    def __add__(self, other):
        if isinstance(other, VarFxp):
            return VarFxp.fromvar_noconv(Var.__add__(self, other))
        else:
            return VarFxp.fromvar_noconv(Var.__add__(self, other*(1<<VarFxp.res)))

    def __sub__(self, other):
        return self + (-other)

    def __rsub__(self, other):
        return (-self) + other

    def __neg__(self):
        return VarFxp.fromvar_noconv(Var.__neg__(self))

    def __div__(self, other):
        """
        Fixed-point division. This is an expensive operation: it costs approximately :py:func:`maxden` equations
        :param other: Other fixed-point number
        :return: Result of division
        """
        if isinstance(other, VarFxp):
            assert other.value.bit_length() <= VarFxp.maxden

            reti = int(float(self.value)*(1<<VarFxp.res)/float(other.value)+0.5)
            ret = VarFxp(reti,True)

            df=Var.__mul__(self, 1<<VarFxp.res)-Var.__mul__(ret,other)    # division error: should be in [-other,other]
            Var.__add__(other, -df).assert_positive(VarFxp.maxden)
            Var.__add__(other, df).assert_positive(VarFxp.maxden+1)

            return ret
        else:
            return NotImplemented

    def __mul__(self, other):
        if isinstance(other, VarFxp):
            i1 = self.value if self.value < vc_p/2 else self.value - vc_p
            i2 = other.value if other.value < vc_p / 2 else other.value - vc_p
            reti = (i1*i2+(1<<(VarFxp.res-1)))>>VarFxp.res
            ret = VarFxp(reti, True)

            diff = Var.__add__((1<<VarFxp.res)*ret, -Var.__mul__(self, other))  # mul error: should be in [-2^f,2^f]
            (diff + (1<<VarFxp.res)).assert_positive(VarFxp.res+1)
            ((1<<VarFxp.res) - diff).assert_positive(VarFxp.res+1)

            return ret
        elif isinstance(other, Var) or isinstance(other, int) or isinstance(other, long):
            return VarFxp.fromvar_noconv(Var.__mul__(self, other))
        else:
            return NotImplemented


