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

from pysnark.lib.base import lin_comb, if_then_else
from pysnark.runtime import Var

class Array:
    def __init__(self, vals):
        self.arr = list(vals)

    def __repr__(self):
        return self.arr.__repr__()

    def __getitem__(self, item):
        if isinstance(item, tuple) and len(item) == 1: item = item[0]
        if isinstance(item, int):
            return self.arr[item]
        elif isinstance(item, Var):
            if item.value < 0 or item.value >= len(self.arr):
                raise IndexError(str(item.value)+"<0 or "+str(item.value)+">="+str(len(self.arr)))
            ixs = [(item-ix).iszero() for ix in range(len(self.arr))]
            sum(ixs).assert_equals(1)
            return lin_comb(ixs, self.arr)
        elif isinstance(item, tuple):
            return self[item[0]][item[1:]]
        else:
            raise TypeError

    def __setitem__(self, item, value):
        if isinstance(item, tuple) and len(item)==1: item = item[0]
        if isinstance(item, int):
            self.arr[item] = value
        elif isinstance(item, Var):
            if item.value < 0 or item.value >= len(self.arr):
                raise IndexError(str(item.value)+"<0 or "+str(item.value)+">="+str(len(self.arr)))
            ixs = [(item-ix).iszero() for ix in range(len(self.arr))]
            sum(ixs).assert_equals(1)
            for ix in range(len(self.arr)):
                self.arr[ix] = if_then_else(ixs[ix], value, self.arr[ix])
        elif isinstance(item, tuple):
            it = self[item[0]]
            it[item[1:]] = value
            self[item[0]] = it
        else:
            raise TypeError

    def __sub__(self, other):
        return Array([sv-ov for (sv,ov) in zip(self.arr, other.arr)])

    def __add__(self, other):
        if isinstance(other, int):
            return Array([sv+other for sv in self.arr])
        return Array([sv+ov for (sv,ov) in zip(self.arr, other.arr)])

    __radd__ = __add__

    def __rmul__(self, other):
        return Array([other*sv for sv in self.arr])

    def assert_equals(self, other):
        if len(self.arr)!=len(other.arr):
            raise ValueError("arrays not of the same length: " + str(len(self.arr)) + "!=" + str(len(other.arr)))

        for (l,r) in zip(self.arr, other.arr): l.assert_equals(r)

    def joined(self):
        return [val for ar in self.arr for val in ar.arr]
