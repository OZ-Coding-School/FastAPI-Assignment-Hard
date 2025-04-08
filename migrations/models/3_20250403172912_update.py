from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `genres` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `external_id` INT NOT NULL UNIQUE,
    `name` VARCHAR(255) NOT NULL
) CHARACTER SET utf8mb4;
        ALTER TABLE `movies` ADD `release_date` DATETIME(6) NOT NULL;
        ALTER TABLE `movies` RENAME COLUMN `plot` TO `overview`;
        ALTER TABLE `movies` RENAME COLUMN `playtime` TO `runtime`;
        ALTER TABLE `movies` ADD `external_id` INT NOT NULL UNIQUE;
        ALTER TABLE `movies` DROP COLUMN `genre`;
        ALTER TABLE `movies` MODIFY COLUMN `cast` VARCHAR(255) NOT NULL;
        CREATE TABLE IF NOT EXISTS `movie_genres` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `genre_id` BIGINT NOT NULL,
    `movie_id` BIGINT NOT NULL,
    CONSTRAINT `fk_movie_ge_genres_c7d0356e` FOREIGN KEY (`genre_id`) REFERENCES `genres` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_movie_ge_movies_014c0d12` FOREIGN KEY (`movie_id`) REFERENCES `movies` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `movies` ADD `genre` VARCHAR(9) NOT NULL COMMENT 'SF: SF\nADVENTURE: Adventure\nROMANCE: Romance\nCOMIC: Comic\nFANTASY: Fantasy\nSCIENCE: Science\nMYSTERY: Mystery\nACTION: Action\nHORROR: Horror';
        ALTER TABLE `movies` RENAME COLUMN `runtime` TO `playtime`;
        ALTER TABLE `movies` RENAME COLUMN `overview` TO `plot`;
        ALTER TABLE `movies` DROP COLUMN `release_date`;
        ALTER TABLE `movies` DROP COLUMN `external_id`;
        ALTER TABLE `movies` MODIFY COLUMN `cast` JSON NOT NULL;
        DROP TABLE IF EXISTS `movie_genres`;
        DROP TABLE IF EXISTS `genres`;"""
