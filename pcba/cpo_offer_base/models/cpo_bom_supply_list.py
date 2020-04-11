# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo import _
import xlrd
import xlwt
import base64
import re
from .cpo_inherit_sale_order import CPO_BOM_SUPPLY_SELECT

BOM_HEAD_SELECTION = [('cpo_item', 'Item'),
                    ('cpo_qty', 'Quantity'),
                    ('cpo_p_n', 'P/N'),
                    ('cpo_description','Bom Description'),
                    #('cpo_type', 'Type'),
                    #('cpo_title', 'Title'),
                    #('cpo_detail', 'Detail'),
                    #('cpo_reference', 'Reference(m)'),
                    #('cpo_vendor', 'Vendor'),
                    ('cpo_vendor_p_n', 'Vendor P/N'),
                    #('cpo_vendor_desc', 'VendorDesc'),
                    ('cpo_mfr', 'Manufacturer'),
                    ('cpo_mfr_p_n', 'Manufacturer P/N'),
                    ('cpo_remark', 'Remark'),
                    ('cpo_package', 'Packaging')]
class cpo_bom_supply_list(models.Model):
    _name = 'cpo_bom_supply.list'

    mfr = fields.Char(string="Manufacturer P/N", required=True)
    supply = fields.Selection(CPO_BOM_SUPPLY_SELECT, string="Supply Style", required=True)
    order_id = fields.Many2one("sale.order", "Order ID", required=True, ondelete='cascade', index=True, copy=False)

    @api.constrains('order_id')
    def _check_order_id(self):
        if not self.order_id:
            return False
        res = self.search([('order_id', '=', self.order_id.id), ('mfr', '=', self.mfr)])
        if len(res) > 1:
            raise ValidationError("update cpo_bom_supply_list check field:order_id, fond repeat.")

    @api.constrains('mfr')
    def _check_mfr(self):
        if not self.mfr:
            return False
        res = self.search([('order_id', '=', self.order_id.id), ('mfr', '=', self.mfr)])
        if len(res) > 1:
            raise ValidationError("update cpo_bom_supply_list check field:mfr, fond repeat.")

    @api.model
    def to_create_ref(self, vals):
        has_row = self.search([('order_id', '=', vals.get('order_id')), ('mfr', '=', vals.get('mfr'))])
        if has_row:
            has_row.unlink()
        return self.create(vals)

    @api.model
    def del_old_data(self, order_id):
        assert int(order_id), 'Bom Supply Line Del Old data error,order_id not is int.'
        self.search([('order_id', '=', order_id)]).unlink()
        return True

class cpo_bom_fields_line(models.Model):
    _name = 'cpo_bom_fields.line'

    src_title = fields.Char(string="Src Title", required=True)
    cpo_title = fields.Selection(BOM_HEAD_SELECTION, string="CPO Title", required=True)
    order_id = fields.Many2one("sale.order", "Order ID", required=True, ondelete='cascade', index=True, copy=False)

    @api.constrains('order_id')
    def _check_order_id(self):
        if not self.order_id:
            return False
        res = self.search([('order_id', '=', self.order_id.id), ('src_title', '=', self.src_title)])
        if len(res) > 1:
            raise ValidationError("update cpo_bom_fields.line check field:src_title, fond repeat.")

    @api.constrains('src_title')
    def _check_mfr(self):
        if not self.src_title:
            return False
        res = self.search([('order_id', '=', self.order_id.id), ('src_title', '=', self.src_title)])
        if len(res) > 1:
            raise ValidationError("update cpo_bom_fields.line check field:src_title, fond repeat.")

    @api.model
    def to_create_fields_ref(self, vals):
        has_row = self.search([('order_id', '=', vals.get('order_id')), ('src_title', '=', vals.get('src_title'))])
        if has_row:
            has_row.unlink()
        return self.create(vals)

    @api.model
    def del_old_data(self, order_id):
        assert int(order_id), 'Bom Fields Line Del Old data error,order_id not is int.'
        self.search([('order_id', '=', order_id)]).unlink()
        return True


class cpo_bom_data_line(models.Model):
    _name = 'cpo_bom_data.line'

    p_type = fields.Selection([
        ('smt_component_qty', 'Smt Component QTY'),
        ('pin_hole_qty', 'Pin Hole QTY'),
        ], 'Type')
    original_bom_qty = fields.Char(string="BOM Original File Quantity")
    client_input_qty = fields.Char(string="Client Input Quantity")
    order_id = fields.Many2one("sale.order", "Order ID", required=True, ondelete='cascade', index=True, copy=False)

    #@api.constrains('order_id')
    #def _check_order_id(self):
        #if not self.order_id:
            #return False
        #res = self.search([('order_id', '=', self.order_id.id), ('client_input_qty', '=', self.client_input_qty)])
        #if len(res) > 1:
            #raise ValidationError("update cpo_bom_fields.line check field:client_input_qty, fond repeat.")

    #@api.multi
    #def check_material_qty(self, bom):
        #cpo_bom = self.env['cpo_offer_bom.bom']
        #cpo_bom_id = cpo_bom.search([('order_ids', '=', bom.order_ids.id)])

        #order_line = self.env['sale.order.line']
        #order_line_id = order_line.search([('bom_rootfile', '=', bom.id)])

        #if order_line_id.smt_component_qty != len(cpo_bom_id) :
            #if self.judge_state == 'false_f' :
                #self.judge_state = 'true_t'
                #self.create({'client_input_qty' : order_line_id.smt_component_qty,
                             #'original_bom_qty' : len(cpo_bom_id),
                             #'order_id' : order_line_id.order_id.id})
                #order_line_id.smt_component_qty = len(cpo_bom_id)
        #return True
