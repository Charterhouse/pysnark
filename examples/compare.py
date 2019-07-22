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

from pysnark.runtime import Var

import pysnark.prove

if __name__ == '__main__':
    val1 = Var(10, True)
	
    print val1.check_smaller(7, 4)    # false
    print val1.check_smaller(8, 4)    # false
    print val1.check_smaller(9, 4)    # false
    print val1.check_smaller(10, 4)   # false
    print val1.check_smaller(11, 4)   # true
    print val1.check_smaller(12, 4)   # true
    
    print val1.check_smaller(Var(7,True), 4)    # false
    print val1.check_smaller(Var(8,True), 4)    # false
    print val1.check_smaller(Var(9,True), 4)    # false
    print val1.check_smaller(Var(10,True), 4)   # false
    print val1.check_smaller(Var(11,True), 4)   # true
    print val1.check_smaller(Var(12,True), 4)   # true
    