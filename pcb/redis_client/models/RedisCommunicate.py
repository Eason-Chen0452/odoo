# -*- coding: utf-8 -*-

import redis


class CpoRedisBase(object):

    # 初始化
    def __init__(self, host, port, db=0, password=None):
        self._host = str(host)
        self._port = port
        self._db = db
        self._password = password

    # 连接
    def _connection(self):
        value = {
            'host': self._host,
            'port': self._port,
            'db': self._db,
        }
        pool = redis.ConnectionPool(**value)
        pool = redis.Redis(connection_pool=pool)
        try:
            ping = pool.ping()
            if ping:
                return pool
        except Exception:
            return False

