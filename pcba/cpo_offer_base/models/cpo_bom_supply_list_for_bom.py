# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo import _
import xlrd
import xlwt
import base64
import re
from .cpo_inherit_sale_order import CPO_BOM_SUPPLY_SELECT
from .cpo_bom_supply_list import BOM_HEAD_SELECTION

class cpo_bom_supply_list_for_bom(models.Model):
    _name = 'cpo_bom_supply.list_for_bom'

    mfr = fields.Char(string="Manufacturer P/N", required=True)
    supply = fields.Selection(CPO_BOM_SUPPLY_SELECT, string="Supply Style", required=True)
    bom_id = fields.Many2one("cpo_offer_bom.bom", "Bom ID", required=True, ondelete='cascade', index=True, copy=False)

    @api.constrains('bom_id')
    def _check_bom_id(self):
        if not self.bom_id:
            return False
        res = self.search([('bom_id', '=', self.bom_id.id), ('mfr', '=', self.mfr)])
        if len(res) > 1:
            raise ValidationError("update cpo_bom_supply_list check field:bom_id, fond repeat.")

    @api.constrains('mfr')
    def _check_mfr(self):
        if not self.mfr:
            return False
        res = self.search([('bom_id', '=', self.bom_id.id), ('mfr', '=', self.mfr)])
        if len(res) > 1:
            raise ValidationError("update cpo_bom_supply_list check field:mfr, fond repeat.")

    @api.model
    def to_create_ref(self, vals):
        has_row = self.search([('bom_id', '=', vals.get('bom_id')), ('mfr', '=', vals.get('mfr'))])
        if has_row:
            has_row.unlink()
        return self.create(vals)

    @api.model
    def del_old_data(self, bom_id):
        assert int(bom_id), 'Bom Supply Line Del Old data error,bom_id not is int.'
        self.search([('bom_id', '=', bom_id)]).unlink()
        return True

class cpo_bom_fields_line_for_bom(models.Model):
    _name = 'cpo_bom_fields.line_for_bom'

    src_title = fields.Char(string="Src Title", required=True)
    cpo_title = fields.Selection(BOM_HEAD_SELECTION, string="CPO Title", required=True)
    bom_id = fields.Many2one("cpo_offer_bom.bom", "Bom ID", required=True, ondelete='cascade', index=True, copy=False)

    @api.constrains('bom_id')
    def _check_bom_id(self):
        if not self.bom_id:
            return False
        res = self.search([('bom_id', '=', self.bom_id.id), ('src_title', '=', self.src_title)])
        if len(res) > 1:
            raise ValidationError("for bom :update cpo_bom_fields.line check field:src_title, fond repeat.")

    @api.constrains('src_title')
    def _check_mfr(self):
        if not self.src_title:
            return False
        res = self.search([('bom_id', '=', self.bom_id.id), ('src_title', '=', self.src_title)])
        if len(res) > 1:
            raise ValidationError("for bom :update cpo_bom_fields.line check field:src_title, fond repeat.")

    @api.model
    def to_create_fields_ref(self, vals):
        has_row = self.search([('bom_id', '=', vals.get('bom_id')), ('src_title', '=', vals.get('src_title'))])
        if has_row:
            has_row.unlink()
        return self.create(vals)

    @api.model
    def del_old_data(self, bom_id):
        assert int(bom_id), 'For Bom  :Bom Fields Line Del Old data error,bom_id not is int.'
        self.search([('bom_id', '=', bom_id)]).unlink()
        return True

class express_waybill_line_for_bom(models.Model):
    _name = 'express_waybill.line_for_bom'

    bom_id = fields.Many2one('cpo_offer_bom.bom', string="Bom ID", required=True, ondelete='cascade', index=True, copy=False)
    express_provider = fields.Char(string="Express Provider")
    express_number = fields.Char(string="Express Number")

    _sql_constraints = [
        ('express_number_unique',
         'UNIQUE(express_number)',
         "The express number must be unique"),
    ]
