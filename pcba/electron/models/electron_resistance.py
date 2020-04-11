# -*- coding: utf-8 -*-

from odoo import models, fields, api
from electron_base import Electron_base_item
from electron_semi_conductor import Electon_semi_conductor

'''-------------电阻器 Begin-----------------'''
class Electron_resistance(models.Model):
    _name = 'electron.resistance'

    resi_val = fields.Char(string="Resistance Value")               #电阻值
    TCR = fields.Char(string="TCR")                                 #温度系数
    temperature = fields.Char(string="Woking Temperature")          #工作温度
    power = fields.Char(string="power(W)")                          #功率
    ingredient = fields.Char(string="Ingredient")                   #成分
    coating = fields.Char(string="Coating, Shell Type")             #涂层，外壳类型
    install_features = fields.Char(string="Installation Features")  #安装特性
    inst_type = fields.Char(string="Install Type")                  #安装类型
    height = fields.Char(string="Height-Installation")              #高度-安装（最大值）
    lead_form = fields.Char(string="Lead Form")                     #引线形式
    supplier_enca = fields.Char(string="Supplier Encapsulation")    #供应商器件封装
    rated_current = fields.Char(string="Rated Current")             #端子数
    fault_rate = fields.Char(string="Fault Rate")                   #故障率
    ancillary_use = fields.Char(string="Ancillary Use")             #配套使用产品/相关产品

    #@api.model
    #def add_record(self, vals):
        #if self.env['electron.content'].search([('pcb_number', '=', vals['pcb_number'])]):
            #return self.write(vals)
        #return self.create(vals)

"""-------------电阻器 End-----------------"""

"""-------------电容器 Begin--------------"""
class Electron_capacitor(models.Model):
    _name = 'electron.capacitor'

    #p_type = fields.Many2one('electron.electronic', string="Type")
    capacitance = fields.Char(string="Capacitance")             #电容
    voltage_rating = fields.Char(string="Nominal Voltage")      #电压-额定
    dielectrics = fields.Char(string="Dielectric Material")     #介电材料
    temperature = fields.Char(string="Woking Temperature")      #工作温度
    interval = fields.Char(string="Lead Spacing")               #引线间距
    termination = fields.Char(string="Termination")             #端接/端子类型
    height = fields.Char(string="Height-Installation")          #高度-安装（最大值）

#class Electron_content_capacitor(Electron_base_item):
    #_name = 'electron.content_capacitor'
    #_inherits = {
                #'electron.capacitor':'capacitor_id',
                #'electron.base':'base_id',
                #"electron.atta":"atta_id"
                #}
    #capacitor_id = fields.Many2one("electron.capacitor", required=True, ondelete='cascade')

"""-------------电容器 End--------------"""


"""------------电感器 Begin--------------"""
class Electron_inductor(models.Model):
    _name = 'electron.inductor'

    #p_type = fields.Many2one('electron.electronic', string="Type")
    inductance = fields.Char(string="inductance")                #电感
    Q_value = fields.Char(string="Q at different frequencies")   #不同频率时的 Q 值
    voltage_rating = fields.Char(string="Nominal Voltage")       #电压-额定
    dielectrics = fields.Char(string="Dielectric Material")      #介电材料
    temperature = fields.Char(string="Woking Temperature")       #工作温度
    interval = fields.Char(string="Lead Spacing")                #引线间距
    height = fields.Char(string="Height-Installation")           #高度-安装（最大值）


#class Electron_content_inductor(Electron_base_item):
    #_name = 'electron.content_inductor'
    #_inherits = {
                #'electron.inductor':'inductor_id',
                #'electron.base':'base_id',
                #"electron.atta":"atta_id"
                #}
    #inductor_id = fields.Many2one("electron.inductor", required=True, ondelete='cascade')

"""------------电感器 End--------------"""

"""------------电位计-可变电阻 Begin--------------"""
class Electron_potentiometer(models.Model):
    _name = 'electron.potentiometer'

    #p_type = fields.Many2one('electron.electronic', string="Type")
    resi_val = fields.Char(string="Resistance Value")            #电阻值
    shaft_size = fields.Char(string="Shaft Size")                #轴尺寸
    TCR = fields.Char(string="TCR")                              #温度系数
    cycles = fields.Char(string="Cycles")                        #圈数
    knob  = fields.Char(string="Knob")                           #调节类型
    diameter = fields.Char(string="Diameter")                    #直径
    po_length = fields.Char(string="Length")                     #长度
    ingredient = fields.Char(string="Ingredient")                #成分/电阻材料
    rotation_angle = fields.Char(string="Rotation Angle")        #旋转角度
    termination = fields.Char(string="Termination")              #端接/端子类型


#class Electron_content_potentiometer(Electron_base_item):
    #_name = 'electron.content_potentiometer'
    #_inherits = {
                #'electron.potentiometer':'potentiometer_id',
                #'electron.base':'base_id',
                #"electron.atta":"atta_id"
                #}
    #potentiometer_id = fields.Many2one("electron.potentiometer", required=True, ondelete='cascade')

"""------------电位计-可变电阻 End--------------"""

"""------------滤波器 Begin--------------"""
class Electron_filters(models.Model):
    _name = 'electron.filters'

    #p_type = fields.Many2one('electron.electronic', string="Type")
    filters_type = fields.Char(string="Filters Type")            #滤波器类型
    number_lines = fields.Char(string="Number Of Lines")         #线路数
    impedance = fields.Char(string="Impedance")                  #不同频率时的阻抗
    rated_current = fields.Char(string="Rated Current(Max)")     #额定电流（最大）
    dc_resistance = fields.Char(string="Dc Resistance(DCR)")     #直流电阻（DCR）（最大）
    rv_DC = fields.Char(string="Rated Voltage(DC)")              #额定电压(交流)
    rv_AC = fields.Char(string="Rated Voltage(AC)")              #额定电压(直流)
    temperature = fields.Char(string="Woking Temperature")       #工作温度
    grade = fields.Char(string="Grade")                          #等级
    authentication = fields.Char(string="Authentication")        #认可/认证（UR，VDE）
    height = fields.Char(string="Height-Installation")           #高度-安装（最大值）

#class Electron_content_filters(Electron_base_item):
    #_name = 'electron.content_filters'
    #_inherits = {
                #'electron.filters':'filters_id',
                #'electron.base':'base_id',
                #"electron.atta":"atta_id"
                #}
    #filters_id = fields.Many2one("electron.filters", required=True)

"""------------滤波器 Begin--------------"""



class Electron_content(Electron_base_item):
    _name = 'electron.content'
    _inherits = {
                'electron.base':'base_id',
                "electron.atta":"atta_id",
                'electron.resistance':'resistance_id',         #电阻
                'electron.capacitor':'capacitor_id',           #电容
                'electron.inductor':'inductor_id',             #电感
                'electron.potentiometer':'potentiometer_id',   #电位计
                'electron.filters':'filters_id',               #滤波器
                'electron.semi_conductor':'semi_conductor_id',         #集成电路（IC）
                }
    
    resistance_id = fields.Many2one("electron.resistance", required=True, ondelete='cascade')
    capacitor_id = fields.Many2one("electron.capacitor", required=True, ondelete='cascade')
    inductor_id = fields.Many2one("electron.inductor", required=True, ondelete='cascade')
    potentiometer_id = fields.Many2one("electron.potentiometer", required=True, ondelete='cascade')
    filters_id = fields.Many2one("electron.filters", required=True)
    


