# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, SUPERUSER_ID
from odoo.tools.translate import _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, AccessError

from datetime import datetime, timedelta
import time
from dateutil.relativedelta import relativedelta

AVAILABLE_PRICE_TYPE = [
    ('item', 'Item'),
    ('csize', 'Size(cm²)'),
    ('msize', 'Size(㎡)'),
    ('pcs', 'PCS'),
    ('set', 'SET'),
]

class create_ink_size_price(models.TransientModel):
    """ Create Ink Color Size Price"""
    _name = "create.ink.size.price"
    _description = "Create Size Fee of Ink Color" 

    ink_color_id = fields.Many2one('cam.ink.color', string='Target Ink Color')
    source_ink_color_id = fields.Many2one('cam.ink.color', string='Source Ink Color')
    text_min_fee_type = fields.Selection(AVAILABLE_PRICE_TYPE, string='Text Color Min Size Fee Type', required=True, default=AVAILABLE_PRICE_TYPE[0][0])
    text_min_fee = fields.Float('Text Color Min Size Fee', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    text_min_fee_compute = fields.Selection([('+', '+'), ('-', '-')], string='Text Color Min Size Fee Compute', default='+')
    text_min_change_fee = fields.Float('Min Size Fee Change Rate', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    text_min_fee_class = fields.Selection([('l', 'L'), ('%', '%')], string='Text Color Min Size Fee Class', default='l')
    text_limit_size = fields.Float('Text Color Limit Size', required=True, digits=dp.get_precision('size'), default=0.0)
    text_max_fee_type = fields.Selection(AVAILABLE_PRICE_TYPE, string='Text Color Max Size Fee Type', required=True, default=AVAILABLE_PRICE_TYPE[0][0])
    text_max_fee = fields.Float('Text Color Max Size Fee', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    text_max_fee_compute = fields.Selection([('+', '+'), ('-', '-')], string='Text Color Max Size Fee Compute', default='+')
    text_max_change_fee = fields.Float('Max Size Fee Change Rate', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    text_max_fee_class = fields.Selection([('l', 'L'), ('%', '%')], string='Text Color Max Size Fee Class', default='l')
    silk_screen_min_fee_type = fields.Selection(AVAILABLE_PRICE_TYPE, string='Silk Screen Min Size Fee Type', required=True, default=AVAILABLE_PRICE_TYPE[0][0])
    silk_screen_min_fee = fields.Float('Silk Screen Min Size Fee', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    silk_screen_min_fee_compute = fields.Selection([('+', '+'), ('-', '-')], string='Silk Screen Min Size Fee Compute', default='l')
    silk_screen_min_change_fee = fields.Float('Min Size Fee Change Rate', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    silk_screen_min_fee_class = fields.Selection([('l', 'L'), ('%', '%')], string='Silk Screen Min Size Fee Class', default='l')  
    silk_screen_limit_size = fields.Float('Silk Screen Limit Size', required=True, digits=dp.get_precision('size'), default=0.0)
    silk_screen_max_fee_type = fields.Selection(AVAILABLE_PRICE_TYPE, string='Silk Screen Max Size Fee Type', required=True, default=AVAILABLE_PRICE_TYPE[0][0])
    silk_screen_max_fee = fields.Float('Silk Screen Max Size Fee', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    silk_screen_max_fee_compute = fields.Selection([('+', '+'), ('-', '-')], string='Silk Screen Max Size Fee Compute', default='+')
    silk_screen_max_change_fee = fields.Float('Max Size Fee Change Rate', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    silk_screen_max_fee_class = fields.Selection([('l', 'L'), ('%', '%')], string='Silk Screen Max Size Fee Class', default='l')


    def view_init(self, fields):
        """
        Check some preconditions before the wizard executes.
        """
        ink_color_obj = self.env['cam.ink.color']
        layer_number_ids = ink_color_obj.search([('active', '=', True)])
        
        if not layer_number_ids:
            raise UserError("No Ink Color can be use to copy to current Ink Color.")
        return False    
    
    def create_ink_color_size(self):
        context = self._context
        ink_color_id = context and context.get('active_id', False) or False
        w = self
        if not(w is None):
            destination_ink_color_id = ink_color_id
            source_ink_color_id = w.source_ink_color_id.id
            
            text_min_fee_type = w.text_min_fee_type
            text_min_fee = w.text_min_fee 
            text_min_fee_type = w.text_min_fee_type
            text_min_fee_compute = w.text_min_fee_compute
            text_min_change_fee = w.text_min_change_fee
            text_min_fee_class = w.text_min_fee_class
            
            text_limit_size = w.text_limit_size

            text_max_fee_type = w.text_max_fee_type
            text_max_fee = w.text_max_fee 
            text_max_fee_type = w.text_max_fee_type
            text_max_fee_compute = w.text_max_fee_compute
            text_max_change_fee = w.text_max_change_fee
            text_max_fee_class = w.text_max_fee_class
            
            silk_screen_min_fee = w.silk_screen_min_fee
            silk_screen_min_fee_type = w.silk_screen_min_fee_type
            silk_screen_min_fee_compute = w.silk_screen_min_fee_compute
            silk_screen_min_change_fee = w.silk_screen_min_change_fee
            silk_screen_min_fee_class = w.silk_screen_min_fee_class
 
            silk_screen_limit_size = w.silk_screen_limit_size
 
            silk_screen_max_fee = w.silk_screen_max_fee
            silk_screen_max_fee_type = w.silk_screen_max_fee_type
            silk_screen_max_fee_compute = w.silk_screen_max_fee_compute
            silk_screen_max_change_fee = w.silk_screen_max_change_fee
            silk_screen_max_fee_class = w.silk_screen_max_fee_class
            
            
            ink_color_obj = self.env['cam.ink.color']
            ink_color_size_obj = self.env['cam.ink.color.line']
            source_ink_color_items = ink_color_obj.browse(source_ink_color_id)
            
            for ink_color_item in source_ink_color_items.line_ids:
                ink_color_size_exist_id = ink_color_size_obj.search([('ink_color_id.id', '=',destination_ink_color_id), ('ink_type', '=', ink_color_item.ink_type), ('max_size', '=', float(ink_color_item.max_size))])
                
                max_size = ink_color_item.max_size
                if text_limit_size ==0 or max_size <= text_limit_size:
                    text_fee = text_min_fee
                    text_fee_type = text_min_fee_type
                else:
                    text_fee = text_max_fee
                    text_fee_type = text_max_fee_type
                
                if silk_screen_limit_size ==0 or max_size <= silk_screen_limit_size:
                    silk_screen_fee = silk_screen_min_fee
                    silk_screen_fee_type = silk_screen_min_fee_type
                else:
                    silk_screen_fee = silk_screen_max_fee
                    silk_screen_fee_type = silk_screen_max_fee_type

                if ink_color_item.ink_type == 'text':
                    price_type = text_fee_type
                    price = text_fee
                else:
                    price_type = silk_screen_fee_type
                    price = silk_screen_fee
                    
                if ink_color_size_exist_id is None or len(ink_color_size_exist_id) == 0:
                    value = {
                        'ink_color_id': destination_ink_color_id,
                        'ink_type': ink_color_item.ink_type,
                        'max_size': ink_color_item.max_size,
                        'price_type': price_type,
                        'price': price,
                    }
                    ink_color_size_id = ink_color_size_obj.create(value)
                
                if  ink_color_item.ink_type == 'text':
                    if text_limit_size ==0 or max_size <= text_limit_size:
                        if text_min_fee_class == "l":
                            change_min_text_fee = text_min_change_fee
                        else:
                            change_min_text_fee = text_min_fee * (text_min_change_fee/100)
    
                        if text_min_fee_compute == '+':
                            text_min_fee = text_min_fee + change_min_text_fee
                        else:
                            text_min_fee = text_min_fee - change_min_text_fee  
                    else:
                        if text_max_fee_class == "l":
                            change_max_text_fee = text_max_change_fee
                        else:
                            change_max_text_fee = text_max_fee * (text_max_change_fee/100)
    
                        if text_max_fee_compute == '+':
                            text_max_fee = text_max_fee + change_max_text_fee
                        else:
                            text_max_fee = text_max_fee - change_max_text_fee  
                else:
                    if silk_screen_limit_size ==0 or max_size <= silk_screen_limit_size:
                        if silk_screen_min_fee_class == "l":
                            change_min_silk_screen_fee = silk_screen_min_change_fee
                        else:
                            change_min_silk_screen_fee = silk_screen_min_fee * (silk_screen_min_change_fee/100)
                        
                        if silk_screen_min_fee_compute == '+':
                            silk_screen_min_fee = silk_screen_min_fee + change_min_silk_screen_fee
                        else:
                            silk_screen_min_fee = silk_screen_min_fee - change_min_silk_screen_fee                    
                    else:
                        if silk_screen_max_fee_class == "l":
                            change_max_silk_screen_fee = silk_screen_max_change_fee
                        else:
                            change_max_silk_screen_fee = silk_screen_max_fee * (silk_screen_max_change_fee/100)
                        if silk_screen_max_fee_compute == '+':
                            silk_screen_max_fee = silk_screen_max_fee + change_max_silk_screen_fee
                        else:
                            silk_screen_max_fee = silk_screen_max_fee - change_max_silk_screen_fee                    
                            
        return {} 

