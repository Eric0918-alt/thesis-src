-- MySQL 8.x 初始化脚本（执行后在 backend/.env 中将 DB_ENGINE 设为 mysql 并运行 python manage.py migrate）
CREATE DATABASE IF NOT EXISTS `thesis_reflection_db`
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;
