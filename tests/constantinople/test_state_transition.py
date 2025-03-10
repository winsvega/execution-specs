from functools import partial
from typing import Dict

import pytest

from ethereum import rlp
from ethereum.base_types import U256, Bytes, Bytes8, Bytes32, Uint
from ethereum.crypto.hash import Hash32
from ethereum.exceptions import InvalidBlock
from tests.helpers import TEST_FIXTURES
from tests.helpers.load_state_tests import (
    Load,
    fetch_state_test_files,
    idfn,
    run_blockchain_st_test,
)

fetch_constantinople_tests = partial(
    fetch_state_test_files, network="ConstantinopleFix"
)

FIXTURES_LOADER = Load("ConstantinopleFix", "constantinople")

run_constantinople_blockchain_st_tests = partial(
    run_blockchain_st_test, load=FIXTURES_LOADER
)

ETHEREUM_TESTS_PATH = TEST_FIXTURES["ethereum_tests"]["fixture_path"]

# Run legacy state tests
test_dir = f"{ETHEREUM_TESTS_PATH}/LegacyTests/Constantinople/BlockchainTests/"


# These are tests that are considered to be incorrect,
# Please provide an explanation when adding entries
LEGACY_IGNORE_LIST = (
    # The test considers a scenario that cannot be reached by following the
    # rules of consensus. For more details, read:
    # https://github.com/ethereum/py-evm/pull/1224#issuecomment-418775512
    "stRevertTest/RevertInCreateInInit_d0g0v0.json",
    # The test considers a scenario that cannot be reached by following the
    # rules of consensus.
    "stCreate2/RevertInCreateInInitCreate2_d0g0v0.json",
    # The test considers a scenario that cannot be reached by following the
    # rules of consensus.
    "stSStoreTest/InitCollision_d0g0v0.json",
    # The test considers a scenario that cannot be reached by following the
    # rules of consensus.
    "stSStoreTest/InitCollision_d1g0v0.json",
    # The test considers a scenario that cannot be reached by following the
    # rules of consensus.
    "stSStoreTest/InitCollision_d2g0v0.json",
    # The test considers a scenario that cannot be reached by following the
    # rules of consensus.
    "stSStoreTest/InitCollision_d3g0v0.json",
    # ValidBlockTest
    "bcForkStressTest/ForkStressTest.json",
    "bcGasPricerTest/RPC_API_Test.json",
    "bcMultiChainTest",
    "bcTotalDifficultyTest",
    # InvalidBlockTest
    "bcForgedTest",
    "bcMultiChainTest",
    "GasLimitHigherThan2p63m1_ConstantinopleFix",
)

# All tests that recursively create a large number of frames (50000)
LEGACY_BIG_MEMORY_TESTS = (
    # GeneralStateTests
    "50000_",
    "/stQuadraticComplexityTest/",
    "/stRandom2/",
    "/stRandom/",
    "/stSpecialTest/",
    "stTimeConsuming/",
    # ValidBlockTest
    "randomStatetest94_",
)

LEGACY_SLOW_TESTS = (
    # GeneralStateTests
    "stRandom/randomStatetest177.json",
    "stCreateTest/CreateOOGafterMaxCodesize.json",
    # ValidBlockTest
    "bcExploitTest/DelegateCallSpam.json",
    # InvalidBlockTest
    "bcUncleHeaderValidity/nonceWrong.json",
    "bcUncleHeaderValidity/wrongMixHash.json",
)

fetch_legacy_state_tests = partial(
    fetch_constantinople_tests,
    test_dir,
    ignore_list=LEGACY_IGNORE_LIST,
    slow_list=LEGACY_SLOW_TESTS,
    big_memory_list=LEGACY_BIG_MEMORY_TESTS,
)


@pytest.mark.parametrize(
    "test_case",
    fetch_legacy_state_tests(),
    ids=idfn,
)
def test_legacy_state_tests(test_case: Dict) -> None:
    run_constantinople_blockchain_st_tests(test_case)


# Run Non-Legacy state tests
test_dir = f"{ETHEREUM_TESTS_PATH}/BlockchainTests/GeneralStateTests/"

non_legacy_only_in = (
    "stCreateTest/CREATE_HighNonce.json",
    "stCreateTest/CREATE_HighNonceMinus1.json",
)


@pytest.mark.parametrize(
    "test_case",
    fetch_constantinople_tests(test_dir, only_in=non_legacy_only_in),
    ids=idfn,
)
def test_non_legacy_state_tests(test_case: Dict) -> None:
    run_constantinople_blockchain_st_tests(test_case)


def test_transaction_with_insufficient_balance_for_value() -> None:
    genesis_header = FIXTURES_LOADER.Header(
        parent_hash=Hash32([0] * 32),
        ommers_hash=Hash32.fromhex(
            "1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347"
        ),
        coinbase=FIXTURES_LOADER.hex_to_address(
            "8888f1f195afa192cfee860698584c030f4c9db1"
        ),
        state_root=FIXTURES_LOADER.hex_to_root(
            "d84598d90e2a72125c111171717f5508fd40ed0d0cd067ceb4e734d4da3a810a"
        ),
        transactions_root=FIXTURES_LOADER.hex_to_root(
            "56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421"
        ),
        receipt_root=FIXTURES_LOADER.hex_to_root(
            "56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421"
        ),
        bloom=FIXTURES_LOADER.Bloom([0] * 256),
        difficulty=Uint(0x020000),
        number=Uint(0x00),
        gas_limit=Uint(0x2FEFD8),
        gas_used=Uint(0x00),
        timestamp=U256(0x54C98C81),
        extra_data=Bytes([0x42]),
        mix_digest=Bytes32([0] * 32),
        nonce=Bytes8([0] * 8),
    )

    genesis_header_hash = bytes.fromhex(
        "0b22b0d49035cb4f8a969d584f36126e0ac6996b9db7264ac5a192b8698177eb"
    )

    assert rlp.rlp_hash(genesis_header) == genesis_header_hash

    genesis_block = FIXTURES_LOADER.Block(
        genesis_header,
        (),
        (),
    )

    state = FIXTURES_LOADER.State()

    address = FIXTURES_LOADER.hex_to_address(
        "a94f5374fce5edbc8e2a8697c15331677e6ebf0b"
    )

    account = FIXTURES_LOADER.Account(
        nonce=Uint(0),
        balance=U256(0x056BC75E2D63100000),
        code=Bytes(),
    )

    FIXTURES_LOADER.set_account(state, address, account)

    tx = FIXTURES_LOADER.LegacyTransaction(
        nonce=U256(0x00),
        gas_price=U256(1000),
        gas=U256(150000),
        to=FIXTURES_LOADER.hex_to_address(
            "c94f5374fce5edbc8e2a8697c15331677e6ebf0b"
        ),
        value=U256(1000000000000000000000),
        data=Bytes(),
        v=U256(0),
        r=U256(0),
        s=U256(0),
    )

    env = FIXTURES_LOADER.Environment(
        caller=address,
        origin=address,
        block_hashes=[genesis_header_hash],
        coinbase=genesis_block.header.coinbase,
        number=genesis_block.header.number + 1,
        gas_limit=genesis_block.header.gas_limit,
        gas_price=tx.gas_price,
        time=genesis_block.header.timestamp,
        difficulty=genesis_block.header.difficulty,
        state=state,
    )

    with pytest.raises(InvalidBlock):
        FIXTURES_LOADER.process_transaction(env, tx)
