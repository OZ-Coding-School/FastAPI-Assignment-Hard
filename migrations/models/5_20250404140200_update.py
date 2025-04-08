from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `movie_genres`;
        CREATE TABLE `movies_genres` (
    `genre_id` BIGINT NOT NULL REFERENCES `genres` (`id`) ON DELETE CASCADE,
    `movies_id` BIGINT NOT NULL REFERENCES `movies` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `movies_genres`;"""
