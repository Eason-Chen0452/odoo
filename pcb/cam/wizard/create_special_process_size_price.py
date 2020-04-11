# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, SUPERUSER_ID
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


class create_special_process_size_price(models.TransientModel):
    """ Create Special Process Size Price"""
    _name = "create.special.process.size.price"
    _description = "Create Size Fee of Special Process" 

    special_process_id = fields.Many2one('cam.special.process', string='Target Special Process')
    
    source_special_process_id = fields.Many2one('cam.special.process', string='Source Special Process')

    min_fee_type = fields.Selection(AVAILABLE_PRICE_TYPE, string='Min Size Fee Type', required=True, default=AVAILABLE_PRICE_TYPE[0][0])
    min_fee = fields.Float('Min Size Fee', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    min_fee_compute = fields.Selection([('+', '+'), ('-', '-')], string='Min Size Fee Compute', default=0.0)
    min_change_fee = fields.Float('Min Size Fee Change Rate', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    min_fee_class = fields.Selection([('l', 'L'), ('%', '%')], string='Min Size Fee Class', default='l')
    
    limit_size = fields.Float('Limit Size', required=True, digits=dp.get_precision('size'), default=0.0)
    
    max_fee_type = fields.Selection(AVAILABLE_PRICE_TYPE, string='Max Size Fee Type', required=True, default=AVAILABLE_PRICE_TYPE[0][0])
    max_fee = fields.Float('Max Size Fee', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    max_fee_compute = fields.Selection([('+', '+'), ('-', '-')], string='Max Size Fee Compute', default='+')
    max_change_fee = fields.Float('Max Size Fee Change Rate', required=True, digits= dp.get_precision('Product Price'), default=0.0)
    max_fee_class = fields.Selection([('l', 'L'), ('%', '%')], string='Max Size Fee Class', default='l')
    

    #def default_get(self, cr, uid, fields, form=None, reference=None, context=None):
        #if not context:
            #context = {}       
        
        #res = super(create_special_process_size_price, self).default_get(cr, uid, fields, context=context)
        
        #return res   

    def view_init(self):
        """
        Check some preconditions before the wizard executes.
        """
        if context is None:
            context = {}
        
        layer_number_ids = self.pool.get('cam.special.process').search(cr, uid, [('active', '=', True)], context=context)
        
        if not layer_number_ids:
            raise osv.except_osv(_("Warning!"), _("No Special Process can be use to copy to current Special Process."))
        return False    
    
    def create_special_process_size(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        
        context= self._context            
        w = self
        special_process_id = context and context.get('active_id', False) or False
        
        if not(w is None):
            destination_special_process_id = special_process_id
            source_special_process_id = w.source_special_process_id.id
            
            min_fee_type = w.min_fee_type
            min_fee = w.min_fee 
            min_fee_type = w.min_fee_type
            min_fee_compute = w.min_fee_compute
            min_change_fee = w.min_change_fee
            min_fee_class = w.min_fee_class
            
            limit_size = w.limit_size

            max_fee_type = w.max_fee_type
            max_fee = w.max_fee 
            max_fee_type = w.max_fee_type
            max_fee_compute = w.max_fee_compute
            max_change_fee = w.max_change_fee
            max_fee_class = w.max_fee_class
            
            
            special_process_obj = self.env['cam.special.process']
            special_process_size_obj = self.env['cam.special.process.line']
            source_special_process_items = special_process_obj.browse(source_special_process_id)
            
            for special_process_item in source_special_process_items.line_ids:
                special_process_size_exist_id = special_process_size_obj.search([('special_process_id.id', '=',destination_special_process_id), ('max_size', '=', float(special_process_item.max_size))])
                
                max_size = special_process_item.max_size
                if limit_size ==0 or max_size <= limit_size:
                    price = min_fee
                    price_type = min_fee_type
                else:
                    price = max_fee
                    price_type = max_fee_type                
                    
                if special_process_size_exist_id is None or len(special_process_size_exist_id) == 0:
                    value = {
                        'surface_process_id': destination_special_process_id,
                        'max_size': special_process_item.max_size,
                        'price_type': price_type,
                        'price': price,
                    }
                    
                    special_process_size_id = special_process_size_obj.create(value)


                if limit_size ==0 or max_size <= limit_size:
                    if min_fee_class == "l":
                        change_min_fee = min_change_fee
                    else:
                        change_min_fee = min_fee * (min_change_fee/100)

                    if min_fee_compute == '+':
                        min_fee = min_fee + change_min_fee
                    else:
                        min_fee = min_fee - change_min_fee  
                else:
                    if max_fee_class == "l":
                        change_max_fee = max_change_fee
                    else:
                        change_max_fee = max_fee * (max_change_fee/100)

                    if max_fee_compute == '+':
                        max_fee = max_fee + change_max_fee
                    else:
                        max_fee = max_fee - change_max_fee                  
                            
        return {} 

