# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo import _

class cpo_smt_price(models.Model):
    _name = 'cpo_smt_price.smt'

    TYPE_SELECTION = [('pcb', 'PCB'),
                      ('smt_make', "SMT Make"),
                      ('plug_in', 'Plug-in'),
                      ('backhand_welding', 'Backhand Welding'),
                      ('packge', 'Packge'),
                      ('stencil', 'Stencil'),
                      ('furnace_tool', 'Pass stove tool'),
                      ('paste_tool', 'Jointed board tool'),
                      ('binder_plate_tool', 'Binder plate tool'),
                      ('test_tool', 'Test tool'),
                      ('jig_tool', 'Jig tool'),
                      ('bom_service', 'Bom Service'),
                      ('add_smt_make', 'Add Smt Make'),
                      ('discount', 'Discount')
                      ]
    layer_pcb = fields.Integer(string="Layer")
    qty = fields.Integer(string="Quantity")
    pin_qty = fields.Integer(string="Pin Quantity")
    pcb_length = fields.Float(string="PCB Length")
    pcb_width = fields.Float(string="PCB Width")
    price = fields.Float(string="Price")
    type_selection = fields.Selection(TYPE_SELECTION, string="Type")

    # @api.multi
    def get_pcba_make_fee_no_bom(self, layer_pcb, pcs_number, smt_component_qty, pin_qty, pcb_length, pcb_width, pcb_special='No', backhand_weld_qty=0):
        # smt_price=self.env['cpo_smt_price.smt']
        # 读取计价规则
        fee_type = '001'
        su_self = self.sudo()
        smt_make_price_rule = su_self.search([('type_selection', '=', 'smt_make')])
        plug_in_rule = su_self.search([('type_selection', '=', 'plug_in')])
        backhand_welding_rule = su_self.search([('type_selection', '=', 'backhand_welding')])
        packge_rule = su_self.search([('type_selection', '=', 'packge')])
        stencil_rule = su_self.search([('type_selection', '=', 'stencil')])
        furnace_tool_rule = su_self.search([('type_selection', '=', 'furnace_tool')])
        paste_tool_rule = su_self.search([('type_selection', '=', 'paste_tool')])
        binder_plate_tool_rule = su_self.search([('type_selection', '=', 'binder_plate_tool')])
        test_tool_rule = su_self.search([('type_selection', '=', 'test_tool')])
        jig_tool_rule = su_self.search([('type_selection', '=', 'jig_tool')])
        add_smt_make_price_rule = su_self.search([('type_selection', '=', 'add_smt_make')], limit=1)
        smt_make_fee = 0.0
        pin_fee = 0.0
        backhand_welding_fee = 0.0
        packge_fee = 0.0
        stencil_fee = 0.0
        furnace_tool_fee = 0.0
        paste_tool_fee = 0.0
        binder_plate_tool_fee = 0.0
        test_tool_fee = 0.0
        jig_tool_fee = 0.0
        # if product_uom_qty > 50 :
        # 超过50片
        # return False
        # 计算贴片价格
        if smt_component_qty < 400:
            # smt_make_price_rule = smt_make_price_rule.search([('id', 'in', smt_make_price_rule.mapped("id")),('layer_pcb', '=', layer_pcb),('qty', '>=', smt_component_qty)]).sorted(key=lambda r: r.qty)
            smt_make_price_rule = smt_make_price_rule.search([
                ('id', 'in', smt_make_price_rule.mapped("id")),
                ('layer_pcb', '=', layer_pcb),
                ('qty', '>=', smt_component_qty),
            ]).sorted(key=lambda r: r.qty)
            if smt_make_price_rule :
                smt_make_fee = smt_make_price_rule[0].price
                # if pcs_number > 50:
                #    smt_make_fee += smt_component_qty * 3 * 0.015 * (pcs_number - 50)
        else:
            # smt_make_fee = smt_component_qty * 3 * 0.015 * pcs_number
            smt_make_fee = smt_component_qty * 10 * pcs_number
        if pcs_number > 20:
                smt_make_fee += smt_component_qty * 4 * 0.015 * (pcs_number - 20)
        # 计算插件价格
        if pin_qty:
            # pin_fee = pin_qty * 0.07 * pcs_number
            pin_fee = pin_qty * 10 if pin_qty < 20 else 800
            if pcs_number > 20:
                pin_fee += pin_qty * 0.07 * (pcs_number - 20)
            # pin_price_rule_min = plug_in_rule.search([('id', 'in', plug_in_rule.mapped("id")),('qty', '>=', pin_qty)]).sorted(key=lambda r: r.qty)
            # if pin_price_rule_min :
            #    pin_fee = pin_price_rule_min[0].price
            # else :
            #    pin_fee += pin_qty * 0.07
        # 计算后焊费用
        # if backhand_weld_qty:
        #     backhand_welding_rule = backhand_welding_rule.search([('id', 'in', backhand_welding_rule.mapped("id")),('qty', '>=', backhand_weld_qty)]).sorted(key=lambda r: r.qty)
        #     if backhand_welding_rule :
        #         backhand_welding_fee = backhand_welding_rule[0].price
        #     else:
        #         backhand_welding_fee = backhand_weld_qty * 0.015
        # 计算钢网费用
        cu_size = pcb_length * pcb_width
        stencil_list = []
        for stencil in stencil_rule:
            if stencil.pcb_length * stencil.pcb_width >= cu_size :
                stencil_list.append(stencil.price)
        if stencil_rule:
            stencil_fee = min(stencil_list) if stencil_list else max(stencil_rule.sorted(lambda x:x.price).mapped("price"))
        # 计算过炉治具
        # if furnace_tool_rule :
        #    furnace_tool_fee = furnace_tool_rule[0].price
        # 计算拼板治具
        # if paste_tool_rule :
        #    paste_tool_fee = paste_tool_rule[0].price
        # 计算压板治具
        # if binder_plate_tool_rule :
        # binder_plate_tool_fee = binder_plate_tool_rule[0].price
        # 计算测试治具
        if pcb_special != 'No' and test_tool_rule :
            test_tool_fee = test_tool_rule[0].price
        # 计算夹板治具
        jig_gen_size = 50 * 50
        if (pcb_length*pcb_width) < jig_gen_size and jig_tool_rule:
            jig_tool_fee = jig_tool_rule[0].price
        rate = 6.6
        if self.env.user.company_id.currency_id.rate_ids:
            rate = self.env.user.company_id.currency_id.rate_ids[0].rate
        round_num = self.env.user.company_id.currency_id.decimal_places
        if fee_type == '001':
            if add_smt_make_price_rule:
                smt_make_fee += smt_make_fee * add_smt_make_price_rule.price
            else:
                smt_make_fee += smt_make_fee * 0.5
            test_tool_fee = 0
            if jig_tool_fee > 0:
                jig_tool_fee = 200 * rate
            stencil_fee = 100 * rate
        # process_price = pin_fee + backhand_welding_fee + stencil_fee +
        # furnace_tool_fee + paste_tool_fee + binder_plate_tool_fee + test_tool_fee
        process_price = pin_fee + furnace_tool_fee + paste_tool_fee + binder_plate_tool_fee + test_tool_fee
        smt_assembly_fee = smt_make_fee + pin_fee
        return {
            'smt_assembly_fee': round(smt_assembly_fee / rate, round_num),
            'stencil_fee': round(stencil_fee / rate, round_num),
            'test_tool_fee': round(test_tool_fee / rate, round_num),
            'jig_tool_fee': round(jig_tool_fee / rate, round_num),
            'total': round((smt_assembly_fee + stencil_fee + test_tool_fee + jig_tool_fee) / rate, round_num)
            # 'process_price': round(process_price/ rate, round_num),
            # 'smt_make_fee': round(smt_make_fee / rate, round_num),
            # 'total': round((smt_make_fee + process_price + stencil_fee) / rate, round_num)
        }

    @api.multi
    def pbca_and_pcb_price_integration(self, args):
        cpo_select_pcb, pcba, x_fee, x_value, freight_fee = args['cpo_select_pcb'], args['pcba_value'], {}, {}, 0
        pcba_value = self.get_pcba_make_fee_no_bom(
            float(pcba['cpo_side']), float(pcba['cpo_quantity']), float(pcba['cpo_smt_qty']), float(pcba['cpo_dip_qty']),
            float(pcba['cpo_length']), float(pcba['cpo_width']), pcba['cpo_select_value']
        )
        if cpo_select_pcb:
            pcb = args['pcb_value']
            pcb_special = pcb['pcb_special_requirements']
            pcb_value = self.env['sale.quotation'].get_pcb_price({'pcb_value': pcb,
                                                                  'pcb_special_requirements': pcb_special,
                                                                  'cpo_country': args.get('cpo_country')})
            if pcb_value.get('warning'):
                return pcb_value.get('warning')
            for x_dict in pcb_value.get('value'):
                if 'Cost' in x_dict:
                    if x_dict not in ['Special Process Cost', 'Special Material Cost', 'Gold Finger Cost', 'Other Cost',
                                      'Core&PP Cost', 'Surface Cost', 'Solder Mask Color Cost', 'Text Color Cost',
                                      'Copper Cost', 'Thickness Cost', 'Benchmark Cost']:
                        x_fee.update({x_dict: pcb_value.get('value')[x_dict]})
                else:
                    x_value.update({x_dict: pcb_value.get('value')[x_dict]})
            freight_fee = round(pcb_value['Shipping Cost'] * 1.5, 0)
        return {
            'pcba_fee': {
                'smt_assembly_fee': pcba_value['smt_assembly_fee'],
                'stencil_fee': pcba_value['stencil_fee'],
                'test_tool_fee': pcba_value['test_tool_fee'],
                'jig_tool_fee': pcba_value['jig_tool_fee'],
                'total': pcba_value['total'],
            },
            'pcb_fee': {
                'x_fee': x_fee,
                'x_value': x_value,
            },
            'Shipping Cost': freight_fee,
            'Total Cost': (pcba_value['total'] + (0 if not x_fee else x_fee['Total Cost']) + freight_fee)
        }

    # 独立调用
    @api.multi
    def get_routine_smt_price(self, order_id):
        value = self.GetRoutinePricePCBA(order_id)
        value = {
            'cpo_quantity': int(value.get('qty')),
            'price': value.get('price'),
            'cpo_side': value.get('side'),
            'cpo_smt_qty': value.get('smt'),
            'cpo_dip_qty': value.get('dip'),
            'cpo_length': value.get('length'),
            'cpo_width': value.get('width'),
            'pcb_thickness': value.get('thick'),
            'cpo_select_value': value.get('select'),
        }
        return value

    def GetRoutinePricePCBA(self, order_id):
        line_id = self.env['sale.order.line'].search([('order_id', '=', int(order_id))])
        value = {
            'side': line_id.layer_pcb,
            'width': line_id.pcb_width,
            'length': line_id.pcb_length,
            'dip': line_id.smt_plug_qty,
            'smt': line_id.smt_component_qty,
            'qty': line_id.product_uom_qty,
            'thick': line_id.pcb_thickness,
            'select': line_id.pcb_special,
        }
        price = self.get_pcba_make_fee_no_bom(
            float(value['side']), float(value['qty']), float(value['smt']), float(value['dip']), float(value['length']),
            float(value['width']), value['select']
        )
        value.update({'price': price})
        return value

