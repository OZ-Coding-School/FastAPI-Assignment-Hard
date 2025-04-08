from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `users` ADD `profile_image_url` VARCHAR(255);
        ALTER TABLE `movies` ADD `poster_image_url` VARCHAR(255);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `users` DROP COLUMN `profile_image_url`;
        ALTER TABLE `movies` DROP COLUMN `poster_image_url`;"""
