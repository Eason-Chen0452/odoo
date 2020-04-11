# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from RedisCommunicate import CpoRedisBase


class RedisClient(models.Model):
    _name = 'redis.client'
    _description = 'Redis Client'

    host = fields.Char('Host')
    port = fields.Integer('Port')
    db = fields.Integer('DB')

    def test_redis(self):
        pool = CpoRedisBase(self.host, self.port, self.db)
        redis = pool._connection()
        if not redis:
            raise ValidationError(_('...'))
        print(redis.connection_pool.pid)

