"""让 Django 的 MySQL 后端使用纯 Python 的 PyMySQL 驱动。

必须在 Django 建立数据库连接之前执行，因此放在项目包的 __init__ 中。
"""
import pymysql

pymysql.install_as_MySQLdb()
