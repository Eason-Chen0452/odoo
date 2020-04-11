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


class create_layer_size_price(models.TransientModel):
    """ Create Layer Size Price"""
    _name = "create.layer.size.price"
    _description = "Create PCB Price of Size for Every Layer" 

    layer_id = fields.Many2one('cam.layer.number', string='Target PCB Layer Number')
    source_layer_id = fields.Many2one('cam.layer.number', string='Source PCB Layer Number')
    material_min_fee_type = fields.Selection(AVAILABLE_PRICE_TYPE, string='Min Size Material Fee Type', required=True, default=AVAILABLE_PRICE_TYPE[0][0])
    material_min_fee = fields.Float('Min Size Material Fee', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    material_min_fee_compute = fields.Selection([('+', '+'), ('-', '-')], string='Min Size Material Fee Compute', default='+')
    material_min_change_fee = fields.Float('Min Size Fee Change Rate', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    material_min_fee_class = fields.Selection([('l', 'L'), ('%', '%')], string='Min Size Material Fee Class', default='l')
    material_limit_size = fields.Float('Mateiral Limit Size', required=True, digits=dp.get_precision('size'), default=0.0)
    material_max_fee_type = fields.Selection(AVAILABLE_PRICE_TYPE, string='Max Size Material Fee Type', required=True, default=AVAILABLE_PRICE_TYPE[0][0])
    material_max_fee = fields.Float('Max Size Material Unit Price', required=True, digits=dp.get_precision('Product Price'), default= 0.0)
    material_max_fee_compute = fields.Selection([('+', '+'), ('-', '-')], string='Max Size Material Fee Compute', default='+')
    material_max_change_fee = fields.Float('Max Size Fee Change Rate', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    material_max_fee_class = fields.Selection([('l', 'L'), ('%', '%')], 'Max Size Material Fee Class', default='l')
    
    engineering_min_fee_type = fields.Selection(AVAILABLE_PRICE_TYPE, string='Min Size Engineering Fee Type', required=True, default=AVAILABLE_PRICE_TYPE[0][0])
    engineering_min_fee = fields.Float('Min Size Engineering Fee', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    engineering_min_fee_compute = fields.Selection([('+', '+'), ('-', '-')], string='Min Size Engineering Fee Compute', default='+')
    engineering_min_change_fee = fields.Float('Min Size Fee Change Rate', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    engineering_min_fee_class = fields.Selection([('l', 'L'), ('%', '%')], string='Min Size Engineering Fee Class', default='l')
    
    engineering_limit_size = fields.Float('Engineering Limit Size', required=True, digits=dp.get_precision('size'), default=0.0)

    engineering_max_fee_type = fields.Selection(AVAILABLE_PRICE_TYPE, string='Max Size Engineering Fee Type', required=True, default=AVAILABLE_PRICE_TYPE[0][0])
    engineering_max_fee = fields.Float('Max Size Engineering Fee', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    engineering_max_fee_compute = fields.Selection([('+', '+'), ('-', '-')], string='Max Size Engineering Fee Compute', default='+')
    engineering_max_change_fee = fields.Float('Max Size Fee Change Rate', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    engineering_max_fee_class = fields.Selection([('l', 'L'), ('%', '%')], string='Max Size Engineering Fee Class', default='l')
    
    etest_min_fee_type = fields.Selection(AVAILABLE_PRICE_TYPE, string='Min Size ETest Fee Type', required=True, default=AVAILABLE_PRICE_TYPE[0][0])
    etest_min_fee = fields.Float('Min Size ETest Fee', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    etest_min_fee_compute = fields.Selection([('+', '+'), ('-', '-')], string='Min Size Etest Fee Compute', default='+')
    etest_min_change_fee = fields.Float('Min Size Fee Change Rate', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    etest_min_fee_class = fields.Selection([('l', 'L'), ('%', '%')], string='Min Size ETest Fee Class', default='l')
    
    etest_limit_size = fields.Float('Etest Limit Size', required=True, digits=dp.get_precision('size'), default=0.0)

    etest_max_fee_type = fields.Selection(AVAILABLE_PRICE_TYPE, string='Max Size ETest Fee Type', required=True, default=AVAILABLE_PRICE_TYPE[0][0])
    etest_max_fee = fields.Float('Max Size ETest Fee', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    etest_max_fee_compute = fields.Selection([('+', '+'), ('-', '-')], string='Max Size Etest Fee Compute', default='+')
    etest_max_change_fee = fields.Float('Max Size Fee Change Rate', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    etest_max_fee_class = fields.Selection([('l', 'L'), ('%', '%')], string='Max Size ETest Fee Class', default='l')
    
    film_min_fee_type = fields.Selection(AVAILABLE_PRICE_TYPE, string='Min Size Film Fee Type', required=True, default=AVAILABLE_PRICE_TYPE[0][0])    
    film_min_fee = fields.Float('Min Size Film Fee', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    film_min_fee_compute = fields.Selection([('+', '+'), ('-', '-')], string='Min Size Etest Fee Compute', default='l')
    film_min_change_fee = fields.Float('Min Size Fee Change Rate', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    film_min_fee_class = fields.Selection([('l', 'L'), ('%', '%')], string='Min Size Film Fee Class', default='l')

    film_limit_size = fields.Float('Film Limit Size', required=True, digits=dp.get_precision('size'), default=0.0)

    film_max_fee_type = fields.Selection(AVAILABLE_PRICE_TYPE, string='Max Size Film Fee Type', required=True, default=AVAILABLE_PRICE_TYPE[0][0])
    film_max_fee = fields.Float('Max Size Film Fee', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    film_max_fee_compute = fields.Selection([('+', '+'), ('-', '-')], string='Max Size Etest Fee Compute', default='+')
    film_max_change_fee = fields.Float('Max Size Fee Change Rate', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    film_max_fee_class = fields.Selection([('l', 'L'), ('%', '%')], string='Max Size Film Fee Class', default='l')
    
    min_delay_hours = fields.Integer('Min Delay Hours', required=True, default=24, help="This is the min delay in days between the sales order confirmation and the  reception of goods for this PCB and for the customer. It is used by the scheduler to order requests based on reordering delays.")
    min_delay_hours_compute = fields.Selection([('+', '+'), ('-', '-')], string='Min Delay Hours Compute', default='+')
    min_delay_change_hours = fields.Float('Change Min Delay Hours', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    min_delay_change_class = fields.Selection([('l', 'L'), ('%', '%')], string='Min Delay Hours Change Class', default='l')
    max_delay_hours = fields.Integer('Max Delay Hours', required=True, default=0.0, help="This is the max delay in days between the sales order confirmation and the  reception of goods for this PCB and for the customer. It is used by the scheduler to order requests based on reordering delays.")
    max_delay_hours_compute = fields.Selection([('+', '+'), ('-', '-')], string='Max Delay Hours Compute', default='+')
    max_delay_change_hours = fields.Float('Change Max Delay Hours', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    max_delay_change_class = fields.Selection([('l', 'L'), ('%', '%')], string='Max Delay Hours Change Class', default='l')
    quick_time = fields.Integer('Quick Time(H)', required=True, default=0.0)
    quick_time_compute = fields.Selection([('+', '+'), ('-', '-')], string='Quick Time Compute', default='+')
    quick_change_time = fields.Float('Change Quick Time', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    quick_time_change_class = fields.Selection([('l', 'L'), ('%', '%')], string='Quick Time Change Class', default='l') 
    quick_fee = fields.Integer('Quick Fee(%)', required=True, default=0.0)
    quick_fee_compute = fields.Selection([('+', '+'), ('-', '-')], string='Quick Fee Compute', default='+')
    quick_change_fee = fields.Float('Change Quick Fee', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    quick_fee_change_class = fields.Selection([('l', 'L'), ('%', '%')], string='Quick Fee Change Class', default='l')
    auto_create_copper_base = fields.Boolean('Auto Create Copper base Price List', default=False)
    

    #def default_get(self, cr, uid, fields, form=None, reference=None, context=None):
        #if not context:
            #context = {}       
        
        #res = super(create_layer_size_price, self).default_get(cr, uid, fields, context=context)
        
        #return res   

    def view_init(self):
        """
        Check some preconditions before the wizard executes.
        """
        layer_number_ids = self.env['cam.layer.number'].search([('active', '=', True)])
        
        if not layer_number_ids:
            raise UserError(_("No Layer Number can be use to copy to current layer number."))
        return False    
    
    def create_layer_size(self):
        if context is None:
            context = {}
        context = self._context            
        w = self
        layer_id = context and context.get('active_id', False) or False
        
        if not(w is None):
            destination_layer_number_id = layer_id
            source_layer_number_id = w.source_layer_id.id
            auto_create_copper_base = w.auto_create_copper_base
            
            material_min_fee_type = w.material_min_fee_type
            material_min_fee = w.material_min_fee 
            material_min_fee_type = w.material_min_fee_type
            material_min_fee_compute = w.material_min_fee_compute
            material_min_change_fee = w.material_min_change_fee
            material_min_fee_class = w.material_min_fee_class
            
            material_limit_size = w.material_limit_size

            material_max_fee_type = w.material_max_fee_type
            material_max_fee = w.material_max_fee 
            material_max_fee_type = w.material_max_fee_type
            material_max_fee_compute = w.material_max_fee_compute
            material_max_change_fee = w.material_max_change_fee
            material_max_fee_class = w.material_max_fee_class
            
            engineering_min_fee = w.engineering_min_fee
            engineering_min_fee_type = w.engineering_min_fee_type
            engineering_min_fee_compute = w.engineering_min_fee_compute
            engineering_min_change_fee = w.engineering_min_change_fee
            engineering_min_fee_class = w.engineering_min_fee_class
 
            engineering_limit_size = w.engineering_limit_size
 
            engineering_max_fee = w.engineering_max_fee
            engineering_max_fee_type = w.engineering_max_fee_type
            engineering_max_fee_compute = w.engineering_max_fee_compute
            engineering_max_change_fee = w.engineering_max_change_fee
            engineering_max_fee_class = w.engineering_max_fee_class
            
            etest_min_fee = w.etest_min_fee
            etest_min_fee_type = w.etest_min_fee_type
            etest_min_fee_compute = w.etest_min_fee_compute
            etest_min_change_fee = w.etest_min_change_fee
            etest_min_fee_class = w.etest_min_fee_class
            
            etest_limit_size = w.etest_limit_size
            

            etest_max_fee = w.etest_max_fee
            etest_max_fee_type = w.etest_max_fee_type
            etest_max_fee_compute = w.etest_max_fee_compute
            etest_max_change_fee = w.etest_max_change_fee
            etest_max_fee_class = w.etest_max_fee_class
            
            film_min_fee = w.film_min_fee
            film_min_fee_type = w.film_min_fee_type
            film_min_fee_compute = w.film_min_fee_compute
            film_min_change_fee = w.film_min_change_fee
            film_min_fee_class = w.film_min_fee_class            

            film_limit_size = w.film_limit_size

            film_max_fee = w.film_max_fee
            film_max_fee_type = w.film_max_fee_type
            film_max_fee_compute = w.film_max_fee_compute
            film_max_change_fee = w.film_max_change_fee
            film_max_fee_class = w.film_max_fee_class            
            
            min_delay_hours = w.min_delay_hours
            min_delay_hours_compute = w.min_delay_hours_compute
            min_delay_change_hours = w.min_delay_change_hours
            min_delay_change_class = w.min_delay_change_class
            
            max_delay_hours = w.max_delay_hours
            max_delay_hours_compute = w.max_delay_hours_compute
            max_delay_change_hours = w.max_delay_change_hours
            max_delay_change_class = w.max_delay_change_class
            
            
            quick_time = w.quick_time
            quick_time_compute = w.quick_time_compute
            quick_change_time = w.quick_change_time
            quick_time_change_class = w.quick_time_change_class
            
            quick_fee = w.quick_fee           
            quick_fee_compute = w.quick_fee_compute
            quick_change_fee = w.quick_change_fee
            quick_fee_change_class = w.quick_fee_change_class
            
            
            layer_number_obj = self.env['cam.layer.number']
            layer_size_obj = self.env['cam.layer.number.size']
            source_layer_number_item = layer_number_obj.browse(source_layer_number_id)
            
            for layer_item in source_layer_number_item.size_ids:
                layer_size_exist_id = layer_size_obj.search([('layer_id.id', '=',destination_layer_number_id), ('max_size', '=', float(layer_item.max_size))])
                
                max_size = layer_item.max_size
                if material_limit_size ==0 or max_size <= material_limit_size:
                    material_fee = material_min_fee
                    material_fee_type = material_min_fee_type
                else:
                    material_fee = material_max_fee
                    material_fee_type = material_max_fee_type
                
                if engineering_limit_size ==0 or max_size <= engineering_limit_size:
                    engineering_fee = engineering_min_fee
                    engineering_fee_type = engineering_min_fee_type
                else:
                    engineering_fee = engineering_max_fee
                    engineering_fee_type = engineering_max_fee_type

                if etest_limit_size ==0 or max_size <= etest_limit_size:
                    etest_fee = etest_min_fee
                    etest_fee_type = etest_min_fee_type
                else:
                    etest_fee = etest_max_fee
                    etest_fee_type = etest_max_fee_type

                if film_limit_size ==0 or max_size <= film_limit_size:
                    film_fee = film_min_fee
                    film_fee_type = film_min_fee_type
                else:
                    film_fee = film_max_fee
                    film_fee_type = film_max_fee_type
                    
                if layer_size_exist_id is None or len(layer_size_exist_id) == 0:
                    value = {
                        'layer_id': destination_layer_number_id,
                        'max_size': layer_item.max_size,
                        'volume_type': layer_item.volume_type,
                        'material_fee_type': material_fee_type,
                        'material_fee': material_fee,
                        'engineering_fee_type': engineering_fee_type,
                        'engineering_fee': engineering_fee,
                        'etest_fee_type': etest_fee_type,
                        'etest_fee': etest_fee,
                        'film_fee_type': film_fee_type,
                        'film_fee': film_fee,
                        'min_delay_hours': min_delay_hours,
                        'max_delay_hours': max_delay_hours,
                        'quick_time': quick_time,
                        'quick_fee': quick_fee,                    
                    }
                    layer_size_id = layer_size_obj.create(value)
                    if auto_create_copper_base:
                        layer_size_obj.act_auto_create([layer_size_id,])
                
                if material_limit_size ==0 or max_size <= material_limit_size:
                    if material_min_fee_class == "l":
                        change_min_material_fee = material_min_change_fee
                    else:
                        change_min_material_fee = material_min_fee * (material_min_change_fee/100)
                    if material_min_fee_compute == '+':
                        material_min_fee = material_min_fee + change_min_material_fee
                    else:
                        material_min_fee = material_min_fee - change_min_material_fee  
                else:
                    if material_max_fee_class == "l":
                        change_max_material_fee = material_max_change_fee
                    else:
                        change_max_material_fee = material_max_fee * (material_max_change_fee/100)
                    if material_max_fee_compute == '+':
                        material_max_fee = material_max_fee + change_max_material_fee
                    else:
                        material_max_fee = material_max_fee - change_max_material_fee  

                if engineering_limit_size ==0 or max_size <= engineering_limit_size:
                    if engineering_min_fee_class == "l":
                        change_min_engineering_fee = engineering_min_change_fee
                    else:
                        change_min_engineering_fee = engineering_min_fee * (engineering_min_change_fee/100)
                    if engineering_min_fee_compute == '+':
                        engineering_min_fee = engineering_min_fee + change_min_engineering_fee
                    else:
                        engineering_min_fee = engineering_min_fee - change_min_engineering_fee                    
                else:
                    if engineering_max_fee_class == "l":
                        change_max_engineering_fee = engineering_max_change_fee
                    else:
                        change_max_engineering_fee = engineering_max_fee * (engineering_max_change_fee/100)
                    if engineering_max_fee_compute == '+':
                        engineering_max_fee = engineering_max_fee + change_max_engineering_fee
                    else:
                        engineering_max_fee = engineering_max_fee - change_max_engineering_fee                    
                    
                if etest_limit_size ==0 or max_size <= etest_limit_size:
                    if etest_min_fee_class == "l":
                        change_min_etest_fee = etest_min_change_fee
                    else:
                        change_min_etest_fee = etest_min_fee * (etest_min_change_fee/100)
                    if etest_min_fee_compute == '+':
                        etest_min_fee = etest_min_fee + change_min_etest_fee
                    else:
                        etest_min_fee = etest_min_fee - change_min_etest_fee
                else:
                    if etest_max_fee_class == "l":
                        change_max_etest_fee = etest_max_change_fee
                    else:
                        change_max_etest_fee = etest_max_fee * (etest_max_change_fee/100)
                    if etest_max_fee_compute == '+':
                        etest_max_fee = etest_max_fee + change_max_etest_fee
                    else:
                        etest_max_fee = etest_max_fee - change_max_etest_fee
                    
                if film_limit_size ==0 or max_size <= film_limit_size:
                    if film_min_fee_class == "l":
                        change_min_film_fee = film_min_change_fee
                    else:
                        change_min_film_fee = film_min_fee * (film_min_change_fee/100)
                    if film_min_fee_compute == '+':
                        film_min_fee = film_min_fee + change_min_film_fee
                    else:
                        film_min_fee = film_min_fee - change_min_film_fee
                else:
                    if film_max_fee_class == "l":
                        change_max_film_fee = film_max_change_fee
                    else:
                        change_max_film_fee = film_max_fee * (film_max_change_fee/100)
                    if film_max_fee_compute == '+':
                        film_max_fee = film_max_fee + change_max_film_fee
                    else:
                        film_max_fee = film_max_fee - change_max_film_fee                    
                    
                if min_delay_change_class == "l":
                    change_min_delay_hours = min_delay_change_hours
                else:
                    change_min_delay_hours = min_delay_hours * (min_delay_change_hours/100)
                if min_delay_hours_compute == '+':
                    min_delay_hours = min_delay_hours + change_min_delay_hours
                else:
                    min_delay_hours = min_delay_hours - change_min_delay_hours

                if max_delay_change_class == "l":
                    change_max_delay_hours = max_delay_change_hours
                else:
                    change_max_delay_hours = max_delay_hours * (max_delay_change_hours/100)
                if max_delay_hours_compute == '+':
                    max_delay_hours = max_delay_hours + change_max_delay_hours
                else:
                    max_delay_hours = max_delay_hours - change_max_delay_hours

                if quick_time_change_class == "l":
                    change_quick_time = quick_change_time
                else:
                    change_quick_time = quick_time * (quick_change_time/100)
                if quick_time_compute == '+':
                    quick_time = quick_time + change_quick_time
                else:
                    quick_time = quick_time - change_quick_time

                if quick_fee_change_class == "l":
                    change_quick_fee = quick_change_fee
                else:
                    change_quick_fee = quick_fee * (quick_change_fee/100)
                if quick_fee_compute == '+':
                    quick_time = quick_time + change_quick_fee
                else:
                    quick_time = quick_time - change_quick_fee
        
        return {} 

