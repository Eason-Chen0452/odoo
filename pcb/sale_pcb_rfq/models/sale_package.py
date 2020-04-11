# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
import time


class Sale_Quotation_Package(models.Model):
    _inherit = 'sale.quotation'

    # 网页打包价 报价 - PCB
    def get_pcb_package(self, args):
        args = self.GetPackageField(args)
        args = self.GetPackageCost(args)
        return args

    def GetPackageCost(self, args):
        price_id = self.env['package.price.main'].search([('bale_general_bool', '=', True)])  # 打包价格表
        if not price_id:
            return {'warning': {'no': 'No general price list is available.'}}
        # 确定尺寸,面积,数量符不符合
        area_dict = {
            'length': args.get('length'),
            'width': args.get('width'),
            'qty': args.get('qty'),
            'price_id': price_id,
        }
        area_dict = self.get_area(area_dict)
        if area_dict.get('warning'):
            return {'warning': {'area_warning': area_dict.get('warning')}}
        # 层数 板材
        layer_dict = {
            'area_id': area_dict.get('area_id'),
            'layer': args.get('layer'),
            'base': args.get('base'),
            'length': args.get('length'),
            'width': args.get('width'),
        }
        layer_dict = self.get_layer_base(layer_dict)
        if layer_dict.get('warning'):
            return {'warning': {'layer_warning': layer_dict.get('warning')}}
        # 表面处理
        surface_dict = {
            'area_id': area_dict.get('area_id'),
            'surface': args.get('surface')
        }
        surface_dict = self.get_surface(surface_dict)
        # 板厚
        thick_dict = {
            'thick': args.get('thick'),
            'layer_id': layer_dict.get('layer_id'),
        }
        thick_dict = self.get_thickness(thick_dict)
        if thick_dict.get('warning'):
            return {'warning': {'thick_warning': thick_dict.get('warning')}}
        # 内外铜厚
        copper_dict = {
            'inner': args.get('inner'),
            'outer': args.get('outer'),
            'layer_id': layer_dict.get('layer_id')
        }
        copper_dict = self.get_copper(copper_dict)
        if copper_dict.get('warning'):
            return {'warning': {'copper_warning': copper_dict.get('warning')}}
        # 阻焊颜色 和 文字颜色
        text_dict = {
            'text': args.get('text'),
            'area_id': area_dict.get('area_id')
        }
        text_dict = self.get_text(text_dict)
        mask_dict = {
            'mask': args.get('solder'),
            'area_id': area_dict.get('area_id')
        }
        mask_dict = self.get_mask(mask_dict)
        # 线宽线距 孔径
        hole_line_dict = {
            'width': args.get('min_width'),
            'space': args.get('min_space'),
            'aperture': args.get('min_hole'),
            'area_id': area_dict.get('area_id')
        }
        hole_line_dict = self.get_hole_line(hole_line_dict)
        delivery = (layer_dict['delivery'] + thick_dict['add_delivery'] + copper_dict['add_delivery'] +
                    text_dict['add_delivery'] + mask_dict['add_delivery'] + surface_dict['add_delivery'])
        price = (layer_dict['price'] + thick_dict['price'] + copper_dict['price'] + text_dict['price'] + mask_dict['price'] +
                 hole_line_dict['aperture_price'] + hole_line_dict['line_price'] + surface_dict['price'])
        return {
            'value': {
                'PCB Area': round(area_dict.get('size'), 4),  # 要的
                'Delivery Period': str(delivery) + ' Day',  # 交期
                'Total Cost': round(price, 2),  # 总费用 包含运费
                'Package Cost': round(price, 2),  # 打包价费用
                'pcb_special': {
                    'Total_holes': round(layer_dict['total_hole'], 0),  # 总孔数
                    'Inner_hole_line': layer_dict['inner_line'],  # 内层孔到线
                    'Number_core': layer_dict['core'],  # 芯板张数
                    'PP_number': layer_dict['pp'],  # pp张数
                    'Blind_hole_structure': 0,  # 埋盲孔结构
                    'Blind_and_buried_hole': 0,  # 埋盲孔钻带数
                    'Min_line_width': hole_line_dict['width'],  # 线宽
                    'Min_line_space': hole_line_dict['space'],  # 线距
                    'Min_aperture': hole_line_dict['aperture'],  # 孔
                    'Copper_weight_wall': 20,  # 孔铜
                    'Countersunk_deep_holes': 0,  # 沉头/...
                    'Total_test_points': round(layer_dict['total_hole'], 0)  # 测试总点数
                }
            },
            'Shipping Cost': 0,  # 运费费用
        }

    # 整理数据字段
    def GetPackageField(self, args):
        x_dict, y_dict, line = {}, {}, None
        if type(args) is dict and 'pcb_value' in args.keys():
            x_dict = args.get('pcb_value')
            y_dict = x_dict.get('pcb_special_requirements')
        elif type(args) is not dict:
            line = args
            args = {}
        value = {
            'text': x_dict.get('pcb_silkscreen_color') or args.get('pcb_silkscreen_color'),
            'inner': x_dict.get('pcb_inner_copper') or args.get('pcb_inner_copper'),
            'outer': x_dict.get('pcb_outer_copper') or args.get('pcb_outer_copper'),
            'solder': x_dict.get('pcb_solder_mask') or args.get('pcb_solder_mask'),
            'thick': x_dict.get('pcb_thickness') or args.get('pcb_thickness'),
            'length': x_dict.get('pcb_length') or args.get('pcb_length'),
            'width': x_dict.get('pcb_breadth') or args.get('pcb_breadth'),
            'layer': x_dict.get('pcb_layer') or args.get('pcb_layer'),
            'base': x_dict.get('pcb_type') or args.get('pcb_type'),
            'qty': x_dict.get('cpo_quantity') or args.get('cpo_quantity'),
            'surface': x_dict.get('pcb_surfaces') or args.get('pcb_surfaces'),
            'min_width': y_dict.get('Min_line_width') or args.get('Min_line_width'),
            'min_space': y_dict.get('Min_line_space') or args.get('Min_line_space'),
            'min_hole': y_dict.get('Min_aperture') or args.get('Min_aperture'),
        }
        if value.get('surface'):
            x_dict = value.get('surface')
            x_dict['pcb_surface'] = x_dict.pop('surface_value') if 'surface_value' in x_dict.keys() else x_dict.get('pcb_surface')
        return value

    # 内外铜厚
    def get_copper(self, args):
        inner, outer, layer_id = args.get('inner'), args.get('outer'), args.get('layer_id')
        price, add_delivery = 0, 0
        if outer:
            outer_id = layer_id.outer_copper_id.search([('ln_id', '=', layer_id.id),
                                                        ('outer', '>=', outer)])
            if not outer_id:
                return {'warning': 'The outer copper thickness you choose is beyond the processing range of the package price.'}
            price += outer_id[0].price
            add_delivery = outer_id[0].add_delivery
        if inner and float(inner) != 0:
            inner_id = layer_id.inner_copper_id.search([('ln_id', '=', layer_id.id),
                                                        ('inner', '>=', inner)])
            if not inner_id:
                return {'warning': 'The inner copper thickness you choose is beyond the processing range of the package price.'}
            price += inner_id[0].price
            inner_delivery = inner_id[0].add_delivery
            add_delivery = add_delivery if inner_delivery < add_delivery else inner_delivery
        return {'price': price, 'add_delivery': add_delivery}

    # 板厚
    def get_thickness(self, args):
        thick, layer_id = args.get('thick'), args.get('layer_id')
        thick_id = layer_id.thickness_id.search([('ln_id', '=', layer_id.id),
                                                 ('min_thick', '<=', thick),
                                                 ('max_thick', '>=', thick)])
        if not thick_id:
            return {'warning': 'The input plate thickness is outside the package price range.'}
        price = thick_id.price
        add_delivery = thick_id.add_delivery
        return {'price': price, 'add_delivery': add_delivery}

    # 层数 板材
    def get_layer_base(self, args):
        layer, area_id, base = args.get('layer'), args.get('area_id'), args.get('base')
        length, width = args.get('length'), args.get('width')
        x_value = 'base_type' if type(base) is int else 'base_type.english_name'
        layer_id = area_id.layer_id.search([('area_id', '=', area_id.id), ('layer_number_id.layer_number', '=', layer)])
        if not layer_id:
            return {'warning': 'This layer is not in the package price'}
        base_id = layer_id.substrate_id.search([('ln_id', '=', layer_id.id), (x_value, '=', base)])
        total_hole = float(layer_id.density / 100 * float(length) * float(width))
        price = base_id.price
        delivery = layer_id.delivery
        core = max((float(layer) - 2) / 2, 1)
        return {'layer_id': layer_id, 'price': price, 'delivery': delivery, 'pp': core + 1, 'core': core,
                'total_hole': total_hole, 'inner_line': layer_id.inner_line}

    # 线宽线距 孔径
    def get_hole_line(self, args):
        width, space, aperture, area_id = args.get('width'), args.get('space'), args.get('aperture'), args.get('area_id')
        spacing_id = area_id.spacing_id.search([('area_id', '=', area_id.id), ('price', '=', 0)])[0]  # 取4mil
        aperture_id = area_id.aperture_id.search([('area_id', '=', area_id.id), ('price', '=', 0)])[0]  # 取10mil
        width = spacing_id.lws_min if float(width) == 0 else width
        space = spacing_id.lws_min if float(space) == 0 else space
        aperture = aperture_id.aperture_min if float(aperture) == 0 else aperture
        line_price = spacing_id.price
        aperture_price = aperture_id.price
        return {'line_price': line_price, 'aperture_price': aperture_price, 'width': width, 'space': space, 'aperture': aperture}

    # 阻焊颜色
    def get_mask(self, args):
        area_id, mask = args.get('area_id'), args.get('mask')
        x_value = 'ink_color_id' if type(mask) is int else 'ink_color_id.english_name'
        mask_id = area_id.solder_id.search([('area_id', '=', area_id.id), (x_value, '=', mask)])
        price = mask_id.price if mask_id.price else 0
        add_delivery = mask_id.add_delivery if mask_id.add_delivery else 0
        return {'price': price, 'add_delivery': add_delivery}

    # 文字颜色
    def get_text(self, args):
        area_id, text = args.get('area_id'), args.get('text')
        x_value = 'ink_color_id' if type(text) is int else 'ink_color_id.english_name'
        text_id = area_id.text_id.search([('area_id', '=', area_id.id), (x_value, '=', text)])
        price = text_id.price if text_id.price else 0
        add_delivery = text_id.add_delivery if text_id.add_delivery else 0
        return {'price': price, 'add_delivery': add_delivery}

    # 验证平米数 尺寸 数量
    def get_area(self, args):
        length, width, qty, price_id = args.get('length'), args.get('width'), args.get('qty'), args.get('price_id')
        size = (float(length) * float(width) * 0.01) * int(qty) / 10000
        area_id = price_id.bale_area_id.search([('area_min', '<', size), ('area_max', '>=', size)])
        # 超出平米数
        if not area_id:
            return {'warning': 'The number of square meters you have entered has exceeded the allowable range.'}
        # 超出PCB板厘米数
        elif area_id.area_size < float(length) * float(width) * 0.01:
            return {'warning': 'PCB board size is out of specification'}
        # 超出数量
        elif area_id.area_quantity < int(qty):
            return {'warning': 'PCB board exceeds the allowable number range'}
        elif (float(length) * float(width) * 0.01) < 9:
            return {'warning': 'PCB single board is too small'}
        return {'area_id': area_id, 'size': size}

    # 表面处理
    def get_surface(self, args):
        area_id, surface = args.get('area_id'), args.get('surface')
        nickel, coated, thick_gold = None, None, None
        if type(surface) is dict:
            nickel = surface.get('nickel_thickness')  # 沉金镍厚
            coated = surface.get('coated_area')  # 涂覆面积
            thick_gold = 0 if 'Immersion gold' not in surface['pcb_surface'] else surface['pcb_surface'][16:17]  # 沉金厚度
            surface = surface['pcb_surface'][:14] if 'Immersion gold' in surface['pcb_surface'] else surface['pcb_surface']
        elif type(surface) is int:
            thick_gold = args.get('gold_thickness') if args.get('gold_thickness') else 0  # 沉金厚度
            coated = args.get('pcb_coated_area')  # 涂覆面积
            nickel = args.get('pcb_nickel_thickness')  # 沉金镍厚
        x_value = 'surface_id' if type(surface) is int else 'surface_id.english_name'
        surface_id = area_id.surface_id.search([('area_id', '=', area_id.id),
                                                (x_value, '=', surface),
                                                ('thick_gold', '=', thick_gold)])
        price = surface_id.price
        add_delivery = surface_id.add_delivery
        if coated and nickel:
            coated_fee = max((float(coated) - 30), 0) / 30 * 70 / 100 + 1  # 临时这样写
            nickel_fee = 1 if nickel in ['120', '0'] else max((((float(nickel) / 50) - 2) * 0.1 + 1), 1)
            price = price * coated_fee * nickel_fee
        return {'price': price, 'add_delivery': add_delivery, 'coated': coated, 'nickel': nickel, 'thick_gold': thick_gold, 'surface': surface}

    def ArrangeQuotePackage(self, args):
        pcb = args if type(args) is dict else args[0]
        pcb_text_color = pcb['pcb_silkscreen_color']  # 字符颜色
        inner = pcb['pcb_inner_copper']  # 内铜厚
        outer = pcb['pcb_outer_copper']  # 外铜厚
        pcb_solder_mask = pcb['pcb_solder_mask']  # 阻焊
        pcb_thickness = pcb['pcb_thickness']  # 板厚
        pcb_length = pcb['pcb_length']  # 长度
        pcb_width = pcb['pcb_width']  # 宽度
        pcb_layer = pcb['pcb_layer']  # 层数
        pcb_test = False if pcb['pcb_test'] != 'E-test fixture' else True  # 测试
        pcb_type = pcb['pcb_type']  # 板材
        pcb_vias = pcb['pcb_vias']  # 过孔处理
        pcb_qty = pcb['cpo_quantity']  # 数量
        pcb_frame = pcb['cpo_pcb_frame']  # 钢网
        text_val = pcb['text_val']  # 备注
        pcb_surface = pcb['pcb_surfaces']  # 表面处理 - 是字典
        pcb_min_line_width = pcb['Min_line_width']  # 最小线宽
        pcb_min_line_space = pcb['Min_line_space']  # 最小线距
        pcb_min_aperture = pcb['Min_aperture']  # 最小孔径
        pcb_inner_line = pcb['Inner_hole_line']  # 内层孔到线
        pcb_total_holes = pcb['Total_holes']  # 总孔数
        pcb_copper_weight = pcb['Copper_weight_wall']  # 孔铜厚度
        pcb_number_core =pcb['Number_core']  # 芯板张数
        pcb_pp = pcb['PP_number']  # pp张数
        pcb_test_points = pcb['Total_test_points']  # 总测试点数
        pcb_acceptable = pcb['quality_standard']  # 验收标准
        price_id = self.env['package.price.main'].search([('bale_general_bool', '=', True)])
        area_dict = self.get_area({'length': pcb_length, 'width': pcb_width, 'qty': pcb_qty, 'price_id': price_id})
        layer_dict = self.get_layer_base({'area_id': area_dict.get('area_id'), 'layer': pcb_layer, 'base': pcb_type, 'length': pcb_length, 'width': pcb_width})
        surface_dict = self.get_surface({'area_id': area_dict.get('area_id'), 'surface': pcb_surface})
        vias_id = self.env['cam.via.process'].search([('english_name', '=', pcb_vias)]).id
        surface_id = self.env['cam.surface.process'].search([('english_name', '=', surface_dict['surface'])]).id
        layer_id = self.env['cam.layer.number'].search([('layer_number', '=', pcb_layer)]).id
        acceptance_id = self.env['cam.acceptance.criteria'].search([('cpo_level', '=', pcb_acceptable)]).id
        text_color_id = self.env['cam.ink.color'].search([('english_name', '=', pcb_text_color)]).id
        sold_mask_id = self.env['cam.ink.color'].search([('english_name', '=', pcb_solder_mask)]).id
        type_id = self.env['cam.base.type'].search([('english_name', '=', pcb_type)]).id  # 基材
        uom_id = self.env['product.uom'].search([('name', '=', 'SET')]).id
        line = {
            'delivery_hour': layer_dict['delivery'] * 24,  # 原始的时间
            'pcs_size': float(pcb_width) * float(pcb_length) * 0.01,  # 厘米面积
            'total_size': area_dict['size'],  # 平米面积
            'pcs_per_set': 1,  # pcs数
            'surface': surface_id,  # 表面处理
            'product_uom_qty': pcb_qty,  # 数量
            'product_uos_qty': pcb_qty,  # 数量
            'via_process': vias_id,  # 普通工艺的id号
            'gold_thickness': surface_dict['thick_gold'] if surface_dict['thick_gold'] else 0,  # 沉金数值
            'gold_size': surface_dict['coated'] if surface_dict['coated'] else 0,  # 沉金面积
            'cpo_nickel_thickness': surface_dict['nickel'] if surface_dict['nickel'] else '0',  # 沉金镍厚
            'outer_copper': outer,  # 外铜厚
            'inner_copper': inner if inner else 0,  # 内铜厚
            'volume_type': 'prototype',
            'layer_number': layer_id,  # 层数
            'cpo_standard': acceptance_id,  # 验收标准
            'silkscreen_color': sold_mask_id,  # 阻焊
            'text_color': text_color_id,  # 字符颜色
            'base_type': type_id,  # 基材
            'cpo_type_steel_mesh': pcb_frame,  # 钢网
            'package_bool': True,  # 确定是打包价
            'cpo_width': pcb_width,
            'thickness': pcb_thickness,
            'cpo_length': pcb_length,
            'product_uom': uom_id,  # 计量单位
            'product_uos': uom_id,  # 计量单位
            'tooling': False if pcb_test is False else True,  # 测试架
            'fly_probe': True if pcb_test is False else False,  # 飞针
            'test_points': int(float(pcb_test_points)),  # 测试总点数
            'min_hole': pcb_min_aperture,  # 最小孔
            'min_line_cpo_width': pcb_min_line_width,  # 线宽
            'min_line_distance': pcb_min_line_space,  # 线距
            'line_to_hole_distance': pcb_inner_line,  # 内层孔到线
            'total_holes': int(float(pcb_total_holes)),  # 总孔数
            'cpo_pp_number': pcb_pp,  # pp张数
            'cpo_core_number': pcb_number_core,  # 芯板张数
            'cpo_hole_copper': pcb_copper_weight,  # 孔铜
            'request': text_val,
        }
        return line

    # 创建生成订单 - 创建PCB打包价订单 - 暂时使用简单的方式得到价格
    def create_pcb_package(self, *args):
        pcb_partner_id = args[0]['pcb_partner_id']  # 客户
        if pcb_partner_id:
            partner = self.env['res.partner'].browse(pcb_partner_id)
        else:
            partner = self.env.ref("base.public_partner")
        addr = partner.address_get(['delivery', 'invoice'])
        # 用户后面传过来
        vals = {
            'partner_id': partner.id,  # 客户
            'partner_invoice_id': addr['invoice'],  # 发票地址
            'partner_shipping_id': addr['delivery'],  # 送货地址
            'currency_id': self.env.ref('base.USD').id,  # 货币
        }
        quotation_id = self.create(vals)
        line = self.ArrangeQuotePackage(args)
        random_name = partner.name + str(int(time.time()))[:7]
        line.update({
            'quotation_id': quotation_id.id,
            'product_no': random_name,  # 产品编号
        })
        quotation_id.quotation_line.create(line)
        cpo_sale_order = {}
        if quotation_id.amount_total != 0:
            cpo_sale_order = self.action_done(quotation_id)
            quotation_id.signal_workflow('action_done')
            quotation_id.update({'state': 'done'})
        return cpo_sale_order['res_id'] if cpo_sale_order['res_id'] else None




