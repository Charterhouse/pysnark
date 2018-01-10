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
import os.path
import subprocess
import sys

import options
import qapsplit
import qaptools.runqapgen
import qaptools.runqapgenf
import qaptools.runqapinput
import qaptools.runqapprove
import qaptools.runqapver
import schedule
from atexitmaybe import maybe


def prove():
    if options.do_rebuild():
        qaplens,blklen,extlen,sigs = qapsplit.qapsplit()
        sz = 1<<((max([max(qaplens.values()),blklen,extlen])-1).bit_length())
        pubsz = 1<<((extlen-1).bit_length()) if extlen is not None else 0
        print "qaplen:", max(qaplens.values()), "blklen:", blklen, "extlen:", extlen, "sz", sz, "pubsz", pubsz

        cursz, curpubsz = qaptools.runqapgen.ensure_mkey(sz, pubsz)

        for nm in sigs.keys():
            qaptools.runqapgenf.ensure_ek(nm, sigs[nm], 1<<((qaplens[nm]-1).bit_length()))

    qaptools.runqapprove.run()

    allfs = list(schedule.oftype("function"))
    (eqs,eks,vks) = map(set,zip(*[(fn[1], fn[2], fn[3]) for fn in allfs])) if allfs!=[] else (set(),set(), set())
    alles = list(schedule.oftype("external"))
    (wrs,cms) = map(set,zip(*[(fn[2], fn[3]) for fn in alles])) if alles!=[] else (set(),set())

    if os.path.isfile(options.get_mpkey_file()) and all([os.path.isfile(vk) for vk in vks]):
        vercom = qaptools.runqapver.run()
        print >>sys.stderr, "Verification succeeded"
    else:
        vercom = qaptools.runqapver.getcommand()
        print >>sys.stderr, "Verification keys missing, skipping verification"

    print >>sys.stderr, "  prover keys/eqs: ", options.get_mkey_file(), " ".join(eks), " ".join(eqs), options.get_schedule_file()
    print >>sys.stderr, "  prover data:     ", " ".join(wrs)
    print >>sys.stderr, "  verifier keys:   ", options.get_mpkey_file(), " ".join(vks), options.get_schedule_file()
    print >>sys.stderr, "  verifier data:   ", " ".join(cms), options.get_proof_file(), options.get_io_file()
    print >>sys.stderr, "  verifier cmd:    ", vercom
    if options.do_rebuild() and (cursz>sz or curpubsz>pubsz):
        print >>sys.stderr, "** Evaluation/public keys larger than needed for function: " +\
                            str(cursz)+">"+str(sz) + " or " + str(curpubsz)+">"+str(pubsz)+ "."
        print >>sys.stderr, "** To re-create, remove " + options.get_mkey_file() + " and " +\
                            options.get_mpkey_file() + " and run again."

    #print >>sys.stderr, "  key material + proof material:"
    #print >>sys.stderr, " ", options.get_mpkey_file(), vks,\
    #                    options.get_schedule_file(), , bcs

if __name__ == "__main__":
    prove()
else:
    if 'sphinx' not in sys.modules and options.do_pysnark() and options.do_proof():
        import atexit
        atexit.register(maybe(prove))
