# -*- coding: utf-8 -*-
from odoo import models, fields, api
import datetime
import logging
_logger = logging.getLogger(__name__)

class ModuleVersionSetting(models.Model):
    """
    创建网页访问设置。当模块数据表更新时，页面直接访问，涉及数据存储会报错；创建记录，用了设置是否调用接口
    """

    _name = 'module_version_management.module_version_setting'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    _sql_constraints = [
        ('cpo_type_unique', 'unique(cpo_type)', u'The current type of record already exists!')
    ]

    SELECTION_TYPE = [
        ('url', 'Website access record'),
        ('quote', 'Website quotation record')
    ]

    @api.model
    def _cpo_set_time(self):
        now_time = datetime.datetime.now()
        return now_time

    cpo_description = fields.Text(string="Record description")
    cpo_version = fields.Float(string="Module Version")
    cpo_active = fields.Boolean(string="Activate", track_visibility='always')
    cpo_type = fields.Selection(SELECTION_TYPE, default="url", string="Function type")
    cpo_time = fields.Datetime(string="Date Time", default=_cpo_set_time)

    @api.multi
    def cpo_view_data_changes(self, type):
        version = 1.0
        cpo_flag = False
        try:
            record_data = self.sudo().search([
                ('cpo_version', '>=', version),
                ('cpo_type', '=', type),
                ('cpo_active', '=', True)
            ])
            if record_data:
                cpo_flag = True
            return cpo_flag
        except Exception, e:
            _logger.error("Abnormal capture: %s (empty or not writable)" % e)
        return cpo_flag

