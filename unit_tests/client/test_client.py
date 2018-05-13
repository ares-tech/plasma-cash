import pytest
from mockito import any, mock, verify, when

from plasma_cash.child_chain.block import Block
from plasma_cash.client.client import Client
from unit_tests.unstub_mixin import UnstubMixin


class TestClient(UnstubMixin):

    @pytest.fixture(scope='function')
    def root_chain(self):
        return mock()

    @pytest.fixture(scope='function')
    def child_chain(self):
        return mock()

    @pytest.fixture(scope='function')
    def client(self, root_chain, child_chain):
        return Client(root_chain, child_chain)

    def test_constructor(self):
        DUMMY_ROOT_CHAIN = 'root chain'
        DUMMY_CHILD_CHAIN = 'child chain'
        c = Client(DUMMY_ROOT_CHAIN, DUMMY_CHILD_CHAIN)
        assert c.root_chain == DUMMY_ROOT_CHAIN
        assert c.child_chain == DUMMY_CHILD_CHAIN

    def test_deposit(self, client, root_chain):
        MOCK_TRANSACT = mock()
        DUMMY_AMOUNT = 1
        DUMMY_DEPOSITOR = 'dummy depositor'
        DUMMY_CURRENCY = 'dummy currency'

        when(root_chain).transact({'from': DUMMY_DEPOSITOR}).thenReturn(MOCK_TRANSACT)

        client.deposit(DUMMY_AMOUNT, DUMMY_DEPOSITOR, DUMMY_CURRENCY)

        verify(MOCK_TRANSACT).deposit(DUMMY_CURRENCY, DUMMY_AMOUNT)

    def test_submit_block(self, client, child_chain):
        MOCK_HASH = 'mock hash'
        MOCK_BLOCK = mock({'hash': MOCK_HASH})
        MOCK_HEX = 'mock hex'
        MOCK_SIG = mock({'hex': lambda: MOCK_HEX})

        KEY = 'key to sign'

        when(client).get_current_block().thenReturn(MOCK_BLOCK)
        when('plasma_cash.client.client.utils').normalize_key(KEY).thenReturn(KEY)
        when('plasma_cash.client.client').sign(MOCK_HASH, KEY).thenReturn(MOCK_SIG)

        client.submit_block(KEY)

        verify(child_chain).submit_block(MOCK_HEX)

    def test_send_transaction(self, client, child_chain):
        DUMMY_PREV_BLOCK = 'dummy prev block'
        DUMMY_UID = 5566
        DUMMY_AMOUNT = 123
        DUMMY_NEW_OWNER = 'new owner'
        DUMMY_NEW_OWNER_ADDR = 'new owner address'
        DUMMY_KEY = 'key'
        DUMMY_NORMALIZED_KEY = 'normalized key'
        MOCK_TX = mock()
        DUMMY_TX_HEX = 'dummy tx hex'
        MOCK_ENCODED_TX = mock({'hex': lambda: DUMMY_TX_HEX})

        (when('plasma_cash.client.client.utils')
            .normalize_address(DUMMY_NEW_OWNER).thenReturn(DUMMY_NEW_OWNER_ADDR))
        (when('plasma_cash.client.client.utils')
            .normalize_key(DUMMY_KEY).thenReturn(DUMMY_NORMALIZED_KEY))
        (when('plasma_cash.client.client').Transaction(
            DUMMY_PREV_BLOCK, DUMMY_UID, DUMMY_AMOUNT, DUMMY_NEW_OWNER_ADDR
            ).thenReturn(MOCK_TX))

        # `Transaction` is mocked previously, so use `any` here as a work around
        (when('plasma_cash.client.client.rlp')
            .encode(MOCK_TX, any)
            .thenReturn(MOCK_ENCODED_TX))

        client.send_transaction(
            DUMMY_PREV_BLOCK,
            DUMMY_UID,
            DUMMY_AMOUNT,
            DUMMY_NEW_OWNER,
            DUMMY_KEY
        )
        verify(MOCK_TX).sign(DUMMY_NORMALIZED_KEY)
        verify(child_chain).send_transaction(DUMMY_TX_HEX)

    def test_get_current_block(self, child_chain, client):
        DUMMY_BLOCK = 'dummy block'
        DUMMY_BLOCK_HEX = 'dummy block hex'
        DUMMY_DECODED_BLOCK = 'decoded block'

        when(child_chain).get_current_block().thenReturn(DUMMY_BLOCK)
        (when('plasma_cash.client.client.utils')
            .decode_hex(DUMMY_BLOCK)
            .thenReturn(DUMMY_BLOCK_HEX))
        (when('plasma_cash.client.client.rlp')
            .decode(DUMMY_BLOCK_HEX, Block)
            .thenReturn(DUMMY_DECODED_BLOCK))

        assert client.get_current_block() == DUMMY_DECODED_BLOCK