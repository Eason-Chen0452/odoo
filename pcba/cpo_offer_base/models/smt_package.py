# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


# smt打包价使用的价格表
class SMTPackagePrice(models.Model):
    _name = 'smt.package.price'
    _description = 'SMT Package Price'
    _order = 'smt_type'

    smt_type = fields.Selection([('Material', 'Material'), ('No Material', 'No Material')], required=True, string='Price Type')
    smt_qty = fields.Integer('Limit PCS Number')
    smt_length = fields.Float('Limit Size Length/mm', digits=(16, 2))
    smt_width = fields.Float('Limit Size Width/mm', digits=(16, 2))
    smt_dip = fields.Integer('Limit Material Type')
    dip_unit_fee = fields.Float('Single General Class Charge', digits=(16, 2))
    smt_number = fields.Integer('Limit SMT Parts Quantity')
    smt_unit_fee = fields.Float('Smt Single Material Charge', digits=(16, 2))
    smt_price = fields.Float('Price', digits=(16, 2))


# 此为专门处理STM打包价的 不做其他事情
class SMTPackageSaleOrder(models.Model):
    _inherit = 'sale.order'

    # 前端接口 SMT打包价报价接口
    def get_smt_package(self, args, package=False):
        return self.SMTPackgeCost(args, package)

    # 返回价格
    def SMTPackgeCost(self, args, package):
        package_dict = args.get('package_form')
        package_dict = self.GetPackageField(package_dict)
        price_id = self.env['smt.package.price']
        if package_dict.get('included') == 'yes':
            price_id = price_id.search([('smt_type', '=', 'Material')])
        elif package_dict.get('included') == 'no':
            price_id = price_id.search([('smt_type', '=', 'No Material')])
        package_dict.update({"price_id": price_id})
        package_dict = self.GetErrorMessage(package_dict)
        if package_dict.get('warning'):
            return package_dict
        package_dict = self.CalculatePrice(package_dict)
        return package_dict

    # 整理数据
    def GetPackageField(self, args):
        args = {
            'dip': args.get('pcba_material_type') or args.get('pcba_package_dip'),
            'length': args.get('pcba_package_length'),
            'qty': args.get('pcba_package_qty'),
            'smt': args.get('pcba_package_smt'),
            'side': args.get('pcba_package_smt_side'),
            'surface': args.get('pcba_package_surface'),
            'thick': args.get('pcba_package_thick'),
            'width': args.get('pcba_package_width'),
            'included': args.get('pcba_package_included'),
        }
        return args

    # 整理错误
    def GetErrorMessage(self, args):
        error, price_id = {}, args.get('price_id')
        if args.get('included') == 'yes':
            if int(args.get('qty')) > price_id.smt_qty:
                error.update({'Production Quantity': 'The number cannot exceed 5pcs'})
            elif float(args.get('length')) > price_id.smt_length or float(args.get('width')) > price_id.smt_width:
                error.update({'PCB/PCB panel size': 'Dimensions, length and width should not exceed 100mm'})
            elif int(args.get('smt')) > price_id.smt_number:
                error.update({'SMT parts quantity': 'The total number of SMT cannot exceed 50'})
            elif int(args.get('dip')) > price_id.smt_dip:
                error.update({'DIP through hole quantity': "DIP through hole quantity can't be bigger than 0"})
        elif args.get('included') == 'no':
            if int(args.get('qty')) > price_id.smt_qty:
                error.update({'Production Quantity': 'The number cannot exceed 20pcs'})
            elif float(args.get('length')) > price_id.smt_length or float(args.get('width')) > price_id.smt_width:
                error.update({'PCB/PCB panel size': 'Dimensions, length and width should not exceed 100mm'})
            elif int(args.get('dip')) + int(args.get('smt')) > price_id.smt_dip + price_id.smt_dip:
                error.update({'DIP and SMT': 'The total number of DIP and SMT cannot exceed 50'})
        if error:
            return {'warning': error}
        return args

    # 计算价格
    def CalculatePrice(self, args):
        price_id, qty, smt, dip = args.get('price_id'), int(args.get('qty')), int(args.get('smt')), int(args.get('dip'))
        price = qty * (smt * price_id.smt_unit_fee) * (dip * price_id.dip_unit_fee) + price_id.smt_price
        return {'Total Price': price}

    # 创建订单
    def create_smt_package(self, args, partner_id=False):
        return self.GetCreateSTMPackage(args, partner_id=partner_id)

    def GetCreateSTMPackage(self, args, partner_id=False):
        args = self.GetPackageField(args)
        price_id = self.env['smt.package.price']
        if args.get('included') == 'yes':
            price_id = price_id.search([('smt_type', '=', 'Material')])
        elif args.get('included') == 'no':
            price_id = price_id.search([('smt_type', '=', 'No Material')])
        args.update({"price_id": price_id})
        price = self.CalculatePrice(args)
        if partner_id:
            partner = self.env['res.partner'].browse(int(partner_id))
        else:
            partner = self.env.ref("base.public_partner")
        addr = partner.address_get(['delivery', 'invoice'])
        product_id = self.env['product.product'].search([('name', '=', 'PCBA')])
        # 用户后面传过来
        x_field = 'smt_plug_qty' if args.get('included') == 'no' else 'bom_material_type'
        surface_id = self.env['cam.surface.process'].search([('english_name', '=', args.get('surface'))]).id
        order_id = self.create({
            'partner_id': partner.id,  # 客户
            'partner_invoice_id': addr['invoice'],  # 发票地址
            'partner_shipping_id': addr['delivery'],  # 送货地址
            'currency_id': self.env.ref('base.USD').id,  # 货币 现在暂时写死
            'product_type': product_id.name,
            'order_line': [(0, 0, {
                'product_id': product_id.id,
                'product_uom_qty': int(args.get('qty')),
                'layer_pcb': int(args.get('side')),
                'pcb_width': float(args.get('width')),
                'pcb_length': float(args.get('length')),
                'smt_component_qty': int(args.get('smt')),
                x_field: int(args.get('dip')),
                'pcb_thickness': float(args.get('thick')),
                'smt_assembly_fee': price.get('Total Price'),
                'surface_id': surface_id,
                'package_type': 'Material' if args.get('included') == 'yes' else 'No Material'
            })]
        })
        return order_id.id

    # PCBA 订单修改 前端调用方法
    def GetPCBAUpdate(self, args, package=False):
        return self.pcba_order_update(args, package=package)

    def arrange_pcba_data(self, args, package=False):
        value = {
            'product_uom_qty': args.get('cpo_quantity') or args.get('pcba_package_qty'),
            'smt_component_qty': args.get('cpo_smt_qty') or args.get('pcba_package_smt'),
            'smt_plug_qty': args.get('cpo_dip_qty') or args.get('pcba_material_type') or args.get('pcba_package_dip'),
            'layer_pcb': args.get('cpo_side') or args.get('pcba_package_smt_side'),
            'pcb_length': args.get('cpo_length') or args.get('pcba_package_length'),
            'pcb_width': args.get('cpo_width') or args.get('pcba_package_width'),
            'pcb_thickness': args.get('pcb_thickness') or args.get('pcba_package_thick'),
            'copper_foil': args.get('pcb_copper'),
            'cpo_note': args.get('text_val'),
            'pcb_special': args.get('cpo_select_value'),
        }
        if package:
            pass
        return value

    def pcba_order_update(self, args, package=False):
        order_id = int(args.get('edit_id'))
        args = self.arrange_pcba_data(args, package=package)
        self.browse(order_id).order_line.write(args)
        return order_id


# SMT打包价中需要增加表面处理此项 当没有值时进行,进行隐藏
class SMTPackageSaleOrderLine(models.Model):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'

    surface_id = fields.Many2one('cam.surface.process', 'Surface Treatment', default=False)
    package_type = fields.Selection([('Material', 'Material'), ('No Material', 'No Material')], string='Package Type', default=False)
