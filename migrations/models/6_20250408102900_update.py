from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `movies` MODIFY COLUMN `release_date` DATE NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `movies` MODIFY COLUMN `release_date` DATETIME(6) NOT NULL;"""
