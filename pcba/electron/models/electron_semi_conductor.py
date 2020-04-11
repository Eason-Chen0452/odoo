# -*- coding: utf-8 -*-

from odoo import models, fields, api
from electron_base import Electron_base_item

class Electon_semi_conductor(models.Model):
    _name = 'electron.semi_conductor'

    #semi_conductor_id = fields.Many2one("electron.semi_conductor", ondelete='cascade')


    """存储器 专用IC"""
    IC_type = fields.Char(string="IC Type")                          #类型
    applications = fields.Char(string="Applications")                #应用
    supplier_enca = fields.Char(string="Supplier Device Package")    #供应商器件封装
    ddr_sdram = fields.Char(string="DDR SDRAM")                      #储存器类型
    memory_format = fields.Char(string="Memory Format")              #存储器格式
    technology = fields.Char(string="Technology")                    #技术
    memory_capacity = fields.Char(string="Memory Capacity")          #存储容量
    clock_rate = fields.Char(string="Clock Rate")                    #时钟频率
    write_cycle = fields.Char(string="Write cycle time-word,page")   #写周期时间 - 字，页
    access_time = fields.Char(string="Access Time")                  #访问时间
    memory_interface = fields.Char(string="Memory Interface")        #存储器接口
    voltage_power = fields.Char(string="Voltage-power Supply")       #电压-电源
    programmable_type = fields.Char(string="Programmable Type")      #可编程类型
    controller_type = fields.Char(string="Controller Type")          #控制器类型

    """嵌入式"""
    applications = fields.Char(string="Applications")                #应用
    core_processor = fields.Char(string="Core Processor")            #核心处理器
    program_c_type = fields.Char(string="Program Memory Type")       #程序存储器类型
    controller_series = fields.Char(string="Controller Series")      #控制器系列
    RAM_capacity = fields.Char(string="RAM Capacity")                #RAM 容量
    interface = fields.Char(string="Interface")                      #接口
    IO_count = fields.Char(string="I/O Count")                       #I/O 数
    voltage_power = fields.Char(string="Voltage-power Supply")       #电压-电源
    kernel_type = fields.Char(string="Kernel Type")                  #内核类型
    speed = fields.Char(string="Speed")                              #速度
    program_bytes = fields.Char(string="Program SRAM Bytes")         #程序 SRAM 字节
    fpge_SRAM = fields.Char(string="FPGA SRAM")                      #FPGA SRAM
    eeprom_capacity = fields.Char(string="EEPROM Capacity")          #EEPROM 容量
    data_bytes = fields.Char(string="Data SRAM Bytes")               #数据 SRAM 字节
    kernel_unit = fields.Char(string="FPGA Kernel Unit")             #FPGA 内核单元
    grid = fields.Char(string="FPGA Grid Electrode")                 #FPGA 栅极
    fpga_bfm = fields.Char(string="FPGA BFM")                        #FPGA 寄存器
    kernel = fields.Char(string="Kernel/Bus Width")                  #核数/总线宽度
    coprocessor = fields.Char(string="Coprocessor DSP")              #协处理器/DSP
    ram_controller = fields.Char(string="RAM Controller")            #RAM 控制器
    realview = fields.Char(string="RealView")                        #图形加速
    display_interface = fields.Char(string="Display With Interface Controller")#显示与接口控制器
    ethernet = fields.Char(string="Ethernet")                        #以太网
    sata = fields.Char(string="SATA")                                #SATA
    usb = fields.Char(string="USB")                                  #USB
    voltage = fields.Char(string="Voltage-I/O")                      #电压-I/O
    security_feat = fields.Char(string="Security Feature")           #安全特性
    core_dimensions = fields.Char(string="Core Dimensions")          #核心尺寸
    peripheral = fields.Char(string="Peripheral")                    #外设
    oscillator_type = fields.Char(string="Oscillator Type")          #振荡器类型
    data_converter = fields.Char(string="Data Converter")



    mb_type = fields.Char(string="Module/Board Type")                #模块/板类型
    connectivity = fields.Char(string="Connectivity")                #连接性
    peripherals = fields.Char(string="Peripherals")                  #外设
    storage_capacity =fields.Char(string="Program Storage Capacity") #程序储存容量
    data_converter = fields.Char(string="Data Converter")            #数据转换器
    voltage_io = fields.Char(string="Voltage I/O")                   #电压-I/O
    framework = fields.Char(string="Framework")                      #架构
    """#将主要属性”放入描述中"""

    macro_number = fields.Char(string="The macro unit number")       #宏单元数
    serializer = fields.Char(string="Serializer")                    #串行器
    data_rate = fields.Char(string="Data Rate")                      #数据速率
    input_type = fields.Char(string="Input Type")                    #输入类型/输入
    output_type = fields.Char(string="Output Type")                  #输出类型/输出
    #voltage_power = fields.Char(string="Voltage-Power")              #电压-电源
    #current_supply = fields.Char(string="Current Supply")            #电流-电源
    #capacitance = fields.Char(string="Capacitance")                  #电容
    conduction_r = fields.Char(string="Conduction resistance (maximum)")#导通电阻（最大值）`
    signal_conditioning = fields.Char(string="Signal Conditioning")  #信号调节
    channels = fields.Char(string="Channels")                        #通道数
    standard = fields.Char(string="Standard")                        #标准
    functionality = fields.Char(string="Functionality")              #功能
    onoff_circuit = fields.Char(string="On-off Circuit")             #开关电路




