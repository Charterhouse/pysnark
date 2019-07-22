# (C) Meilof Veeningen, 2019

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
    