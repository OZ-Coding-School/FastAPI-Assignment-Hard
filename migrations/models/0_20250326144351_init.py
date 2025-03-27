from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `users` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `username` VARCHAR(50) NOT NULL UNIQUE,
    `hashed_password` VARCHAR(128) NOT NULL,
    `age` INT NOT NULL,
    `gender` VARCHAR(6) NOT NULL  COMMENT 'MALE: male\nFEMALE: female',
    `last_login` DATETIME(6),
    KEY `idx_users_usernam_266d85` (`username`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `movies` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `title` VARCHAR(255) NOT NULL,
    `plot` LONGTEXT NOT NULL,
    `cast` JSON NOT NULL,
    `playtime` INT NOT NULL,
    `genre` VARCHAR(9) NOT NULL  COMMENT 'SF: SF\nADVENTURE: Adventure\nROMANCE: Romance\nCOMIC: Comic\nFANTASY: Fantasy\nSCIENCE: Science\nMYSTERY: Mystery\nACTION: Action\nHORROR: Horror'
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
