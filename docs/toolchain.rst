The PySNARK toolchain
=====================

We discuss the usage of the PySNARK toolchain based on running one of the provided examples acting as each
of the different types of parties in a verifiable computation: trusted party, prover, or verifier.

As trusted party
----------------

To try out running PySNARK as trusted party performing key generation, do the following: ::

  cd examples
  python cube.py 3

If PySNARK has been correctly installed, this will perform a verifiable computation that will compute the cube of the input value, ``3``.
At the same time, it will generate all key material needed to verifiably perform the computation in the script.
(Performing an example computation is the only way to generate this key material.)
PySNARK produces the following files:

* Files that should be kept secret by the trusted party generating the key material:
    * ``pysnark_mastersk``: zk-SNARK master secret key
* Files that the trusted party should distribute to provers along with the Python script (i.e., `cube.py` in this case):
    * ``pysnark_schedule``: schedule of functions called in the computation
    * ``pysnark_masterek``: master evaluation key
    * ``pysnark_ek_main``: zk-SNARK evaluation key for the main function of the computation
    * ``pysnark_eqs_main``: equations for the main function of the computation
* Files that the trusted party should distribute to verifiers:
    * ``pysnark_schedule``: schedule of functions called in the computation
    * ``pysnark_masterpk``: master public key
    * ``pysnark_vk_main``: verificaiton key for the main function
* Files that the prover should distribute to verifiers:
    * ``pysnark_proof``: proof that the particular computation was performed correctly
    * ``pysnark_values``: input/output values of the computation
* Files that are not needed anymore after the execution:
    * ``pysnark_eqs``: equations for the zk-SNARK
    * ``pysnark_wires``: wire values of the computation
    
Note that the PySNARK master evaluation key (``pysnark_mastersk``) and master public key (``pysnark_masterpk``) grow as required. As a consequence, if a small computation is executed after a large computation, these files are larger than needed for the small computation.
PySNARK will indicate this with a warning such as the following::

  ** Evaluation/public keys larger than needed for function: 128>8 or 2>2.
  ** To re-create, remove pysnark_masterek and pysnark_masterpk and run again.

To obtain smaller keys that are sufficient for distribution to provers that only need to execute the small computation, remove the master evaluation and public key (but not the master secret key).
The master evaluation and public key will be re-generated and will now have the minimum size needed to succesfully execute the small computation.

    
As prover
---------

To try out running PySNARK as a prover, put the files discussed above (i.e.,  ``pysnark_schedule``, ``pysnark_masterek``, ``pysnark_ek_main``, and ``pysnark_eqs_main``) together with ``cube.py`` in a directory and run the same command: ::

  cd examples
  python cube.py 3

This will perform a verifiable computation based on the previously generated key material.

As verifier
-----------

To try out running PySNARK as a verifier, put the files discussed above (i.e.,  ``pysnark_schedule``, ``pysnark_masterpk`` and ``pysnark_vk_main`` received from the trusted party, and ``pysnark_proof`` and ``pysnark_values`` received from the prover) in a folder and run: ::

  PYTHONPATH=../.. python -m pysnark.qaptools.runqapver

This will verify the computation proof with respect to the input/output values from the ``pysnark_values`` file, e.g,: ::

  # PySNARK i/o
  main/o_in: 21
  main/o_out: 9261

In this case, we have verifiably computed the fact that the cube of 21 is 9261. See also the other provided examples.

Environment variables
---------------------

Operation of the PySNARK toolchain can be configured by means of the following environment variables:

* ``PYSNARK_ENABLED`` -- if set to another value than ``1``, this will disable the PySNARK runtime: no ``pysnark_*`` files will be written (except for :py:func:`pysnark.runtime.exportcomm`, which will still write a wire file but no commitment; this will also not disable function calls outside of :py:mod:`pysnark.runtime` such as :py:func:`pysnark.qaptools.runqapinput.gencomm`)
* ``PYSNARK_REBUILD`` -- if set to another value than ``0``, no key material will be (re)generated (normally, key material is generated either if a master secret key is present, or there is no PySNARK key material at all) but proofs will stilbe produced
* ``PYSNARK_KEYDIR`` -- if set, all PySNARK key material will be written to and read from the given directory
* ``PYSNARK_PROOFDIR`` -- if set, all PySNARK proofs, wires, and other material relating to the present computation will be written to and read from the given directory
* ``QAPTOOLS_BIN`` -- if set, the ``qaptools`` binaries from the given directory will be used

Using commitments
-----------------

PySNARK allows proofs to refer to committed data using `Geppetri <https://eprint.iacr.org/2017/013>`_.
This has three applications:

* it allows proofs to refer to external private inputs from parties other than the trusted third party;
* it allows different verifiable computations to share secret data with each other; and
* it allows to divide a verifiable computation into multiple subcomputations, each with their own evaluation and verification keys (but all based on the same master secret key)
 
See ``examples/testcomm.py`` for examples.
 
External secret inputs
^^^^^^^^^^^^^^^^^^^^^^
 
To commit to data, use :py:mod:`pysnark.qaptools.runqapinput`, e.g., to commit to values 1, 2, and 3 using a commitment named ``test``, use: ::

   python -m pysnark.qaptools.runqapinput test 1 2 3

Share ``pysnark_wires_test`` with any prover who wants to perform a computation with respect to this committed data, and ``pysnark_comm_test`` to any verifier. 
Alternatively, use :py:func:`pysnark.qaptools.runqapinput.gencomm` from a Python script.

Import this data into the verifiable computation with: :: 

  [one,two,three] = pysnark.runtime.importcomm("test")

Sharing data between verifiable computations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In the first computation, do: ::

  pysnark.runtime.exportcomm([Var(1),Var(2),Var(3)], "test")

and share ``pysnark_wires_test`` and ``pysnark_comm_test`` with the other prover and the verifier, respectively.

In the second verifiable computation, do: ::

  [one,two,three] = pysnark.runtime.importcomm("test")

Sharing data between different parts of a verifiable computation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is implicitly used whenever a function is called that is decorated with ``@pysnark.runtime.subqap``.
When a particular functon is used multiple times in a verifiable computation, using ``@pysnark.runtime.subqap`` prevents the circuit for the function to be replicated, resulting in smaller key material (but slower verification). 

