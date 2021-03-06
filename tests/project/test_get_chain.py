import pytest

from populus.project import (
    Project,
)

from populus.utils.geth import (
    get_geth_ipc_path,
    get_data_dir as get_local_chain_datadir,
)
from populus.utils.networking import (
    get_open_port,
)


TESTNET_BLOCK_1_HASH = '0xad47413137a753b2061ad9b484bf7b0fc061f654b951b562218e9f66505be6ce'
MAINNET_BLOCK_1_HASH = '0x88e96d4537bea4d9c05d12549907b32561d3bf31f45aae734cdc119f13406cb6'


@pytest.mark.slow
def test_project_tester_chain(project_dir):
    project = Project()

    chain = project.get_chain('tester')

    with chain as running_tester_chain:
        web3 = running_tester_chain.web3
        assert web3.version.node.startswith('TestRPC')


@pytest.mark.slow
def test_project_testrpc_chain(project_dir):
    project = Project()

    chain = project.get_chain('testrpc')

    with chain as running_tester_chain:
        web3 = running_tester_chain.web3
        assert web3.version.node.startswith('TestRPC')


@pytest.mark.slow
def test_project_temp_chain(project_dir):
    project = Project()

    chain = project.get_chain('temp')

    with chain as running_temp_chain:
        web3 = running_temp_chain.web3
        assert hasattr(running_temp_chain, 'geth')
        assert web3.version.node.startswith('Geth')


@pytest.mark.skip("Morden no longer exists")
@pytest.mark.slow
def test_project_morden_chain(project_dir):
    project = Project()

    chain = project.get_chain('morden')

    with chain as running_morden_chain:
        web3 = running_morden_chain.web3
        assert web3.version.node.startswith('Geth')

        running_morden_chain.wait.for_block(block_number=1, timeout=180)

        block_1 = web3.eth.getBlock(1)
        assert block_1['hash'] == TESTNET_BLOCK_1_HASH


@pytest.mark.slow
def test_project_local_chain_ipc(project_dir):
    project = Project()

    project.config['chains.local.chain.class'] = 'populus.chain.LocalGethChain'
    project.config['chains.local.web3.provider.class'] = 'web3.providers.ipc.IPCProvider'
    project.write_config()

    chain = project.get_chain('local')

    with chain as running_local_chain:
        web3 = running_local_chain.web3
        assert web3.version.node.startswith('Geth')

        running_local_chain.wait.for_block(block_number=1, timeout=180)

        block_1 = web3.eth.getBlock(1)
        assert block_1['hash'] != MAINNET_BLOCK_1_HASH
        assert block_1['hash'] != TESTNET_BLOCK_1_HASH
        assert block_1['miner'] == web3.eth.coinbase


@pytest.mark.slow
def test_project_local_chain_rpc(project_dir):
    project = Project()
    rpc_port = str(get_open_port())
    project.config['chains.local.chain.class'] = 'populus.chain.LocalGethChain'
    project.config['chains.local.chain.settings.rpc_port'] = rpc_port
    project.config['chains.local.web3.provider.class'] = 'web3.providers.rpc.HTTPProvider'
    project.config['chains.local.web3.provider.settings.endpoint_uri'] = "http://127.0.0.1:{0}".format(rpc_port)
    project.write_config()

    chain = project.get_chain('local')

    with chain as running_local_chain:
        web3 = running_local_chain.web3
        assert web3.version.node.startswith('Geth')

        running_local_chain.wait.for_block(block_number=1, timeout=180)

        block_1 = web3.eth.getBlock(1)
        assert block_1['hash'] != MAINNET_BLOCK_1_HASH
        assert block_1['hash'] != TESTNET_BLOCK_1_HASH
        assert block_1['miner'] == web3.eth.coinbase
