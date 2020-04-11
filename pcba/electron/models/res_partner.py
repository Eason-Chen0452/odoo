# -*- coding: utf-8 -*-

from odoo import models, fields, api

class res_partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    supplier_description = fields.Text("Supplier Description")

    @api.model
    def electrion_create_supplier(self, vals):
        '''
        供应商字段信息：
            名字: name
            logo: image
            描述：supplier_description
            网站:website
        '''
        assert vals.get('name'), 'create supplier error,not find name'
        vals.update({
            'supplier': True,
            'company_type': 'company',
        })
        return self.create(vals)
