PySNARK & smart contracts
=========================

PySNARK supports the automatic generation of smart contracts that verify the correctness of the given zk-SNARK.
These smart contracts are written in Solidity and require support for the recent zkSNARK verification opcodes (`EIP 196 <https://github.com/ethereum/EIPs/blob/master/EIPS/eip-196.md>`_, `EIP 197 <https://github.com/ethereum/EIPs/blob/master/EIPS/eip-197.md>`_).
To test them out, install a development version of Truffle using `these instructions <https://github.com/trufflesuite/truffle/blob/develop/CONTRIBUTING.md>`_.

Continuing the above example, as verifier first run: ::

  truffle init

to initialise Truffle (to just see the Solidity code without installing truffle, create two empty directories ``contracts`` and ``test``).

Next, run: ::

  python -m pysnark.contract

to generate smart contract ``contracts/Pysnark.sol`` to verify computations of the ``cube.py`` script (using library ``contracts/Pairing.sol`` that is also copied into the directory), and test script ``test/TestPysnark.sol`` that gives a test case for the contract based on the current I/O and proof.
Finally, run: ::

  truffle test

to run the test script and check that the given proof can indeed be verified in Solidity.

Note that ``test/TestPysnark.sol`` indeed contains the I/O from the computation: ::

  pragma solidity ^0.4.2;

  import "truffle/Assert.sol";
  import "../contracts/Pysnark.sol";
  
  contract TestPysnark {
      function testVerifies() public {
          Pysnark ps = new Pysnark();
          uint[] memory proof = new uint[](22);
          uint[] memory io = new uint[](2);
          proof[0] = ...;
          ...
          proof[21] = ...;
          io[0] = 21; // main/o_in
          io[1] = 9261; // main/o_out
          Assert.equal(ps.verify(proof, io), true, "Proof should verify");
      }
  }
  
Commitments in smart contracts
------------------------------

Smart contracts can also refer to commitments, e.g., as imported with the :py:func:`pysnark.runtime.importcomm` API call. 
In this case, the commitment becomes an argument to the verification function (a six-valued integer array), and the test case shows how the commitment used in the present computation should be used as value for that argument, e.g.: ::

  pragma solidity ^0.4.2;
  
  import "truffle/Assert.sol";
  import "../contracts/Pysnark.sol";
  
  contract TestPysnark {
      function testVerifies() public {
          Pysnark ps = new Pysnark(); 
          uint[] memory pysnark_comm_test = new uint[](6);
          pysnark_comm_test[0] = ...;
          ...
          Assert.equal(ps.verify(proof, io, pysnark_comm_test), true, "Proof should verify");
      }
  }

Running out of gas
------------------

Wen testing PySNARK smart contracts using Truffle (especially when using commitments or large amounts of I/O), one may get the message that Truffle runs out of gas.
In this case, it is possible to increase Truffle's gas limit by editing the ``deployer.deploy`` line in ``migrations/1_initial_migration.js``, e.g.::

  deployer.deploy(Migrations, {gas: 6700000});
