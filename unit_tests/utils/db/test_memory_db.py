import pytest

from plasma_cash.utils.db.exceptions import BlockAlreadyExistsException
from plasma_cash.utils.db.memory_db import MemoryDb


class TestMemoryDb(object):
    @pytest.fixture(scope='function')
    def db(self):
        return MemoryDb()

    def test_block_normal_case(self, db):
        DUMMY_BLOCK = 'dummy block'
        DUMMY_BLK_NUM = 1
        db.save_block(DUMMY_BLOCK, DUMMY_BLK_NUM)
        assert db.get_block(DUMMY_BLK_NUM) == DUMMY_BLOCK

    def test_get_block_none(self, db):
        NON_EXIST_BLK_NUM = -1
        assert db.get_block(NON_EXIST_BLK_NUM) is None

    def test_save_block_already_exists(self, db):
        DUMMY_BLK_NUM = 1
        db.save_block('first block', DUMMY_BLK_NUM)
        with pytest.raises(BlockAlreadyExistsException):
            db.save_block('second block should fail', DUMMY_BLK_NUM)
