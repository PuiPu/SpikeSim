import numpy as np

class MemoryConfig:
    """Memory configuration管理类"""
    
    # 基础阻值配置 (Ω)
    BASE_R_CONFIGS = {
        'RRAM_LOW':  19.139e3,  # RRAM 低阻值配置
        'RRAM_HIGH': 200e3,     # RRAM 高阻值配置  
        'SRAM':      120e3,     # SRAM 配置
        'CUSTOM':    6.25e3,    # 自定义低阻值
    }
    
    # 能耗配置 (pJ) - 来自 ela_spikesim.py (xbar_ar)
    ENERGY_CONFIGS = {
        'rram': 1.76423,
        'sram': 671.089,
    }
    
    # 面积配置 (µm²) - 来自 ela_spikesim.py $ (xbar_size**2)*(53*(40*10e-3)**2)*(k**2)  $
    AREA_CONFIGS = {
        'rram': 26.2144,
        'sram': 671.089,
    }
    
    # 其他硬件参数
    HARDWARE_PARAMS = {
        'ADC': 2.03084,           # ADC 能耗 (pJ)
        'MUX': 0.094245,          # MUX 能耗 (pJ)  
        'Tile_buff': 397,         # Tile buffer 能耗 (pJ)
        'Temp_Buff': 0.2,         # 临时buffer 能耗 (pJ)
        'Sub': 1.15E-6,           # 基片能耗 (pJ)
        'Htree': 19.64 * 8,       # H-tree 能耗 (pJ)
        'mem_fetch': 4.64,        # 内存读取能耗 (pJ)
        'neuron': 1.274 * 4.0,    # 神经元能耗 (pJ)
    }
    
    def __init__(self, memory_type='RRAM_LOW'):
        """
        初始化memory配置
        
        Args:
            memory_type: 'RRAM_LOW', 'RRAM_HIGH', 'SRAM', 'CUSTOM'
        """
        self.memory_type = memory_type
        self.base_r = self.BASE_R_CONFIGS[memory_type]
        
        # 设置对应的能耗和面积参数
        if 'RRAM' in memory_type:
            self.device_type = 'rram'
        else:
            self.device_type = 'sram'
            
        self.energy_factor = self.ENERGY_CONFIGS[self.device_type]
        self.area_factor = self.AREA_CONFIGS[self.device_type]
    
    def get_config_summary(self):
        """返回当前配置的摘要"""
        return {
            'memory_type': self.memory_type,
            'base_resistance': f"{self.base_r/1000:.3f} kΩ",
            'conductance': f"{1/self.base_r*1e6:.3f} µS",
            'device_type': self.device_type,
            'energy_factor': self.energy_factor,
            'area_factor': self.area_factor,
            'energy_ratio_vs_rram': self.energy_factor / self.ENERGY_CONFIGS['rram'],
            'area_ratio_vs_rram': self.area_factor / self.AREA_CONFIGS['rram'],
        }
    
    def print_config(self):
        """打印当前配置"""
        config = self.get_config_summary()
        print(f"{'='*50}")
        print(f"Memory Configuration: {config['memory_type']}")
        print(f"{'='*50}")
        print(f"基础阻值: {config['base_resistance']}")
        print(f"电导值: {config['conductance']}")  
        print(f"设备类型: {config['device_type'].upper()}")
        print(f"能耗因子: {config['energy_factor']:.3f} pJ")
        print(f"面积因子: {config['area_factor']:.3f} µm²")
        print(f"相对RRAM能耗比: {config['energy_ratio_vs_rram']:.1f}x")
        print(f"相对RRAM面积比: {config['area_ratio_vs_rram']:.1f}x")
        print(f"{'='*50}")
    
    def get_resistance_mapping(self, weight_value, n_bits=4):
        """
        计算权重值对应的有效电阻
        
        Args:
            weight_value: 权重值 (0 到 2^n_bits-1)
            n_bits: 量化位数
            
        Returns:
            effective_resistance: 有效电阻值 (Ω)
        """
        if weight_value == 0:
            return float('inf')  # 无穷大电阻
        else:
            return self.base_r / weight_value
    
    def compare_configs(self):
        """比较所有配置"""
        print(f"{'='*80}")
        print(f"所有 Memory Configuration 比较")
        print(f"{'='*80}")
        print(f"{'配置类型':<15} {'阻值(kΩ)':<12} {'电导(µS)':<12} {'能耗(pJ)':<12} {'面积(µm²)':<12}")
        print(f"{'-'*80}")
        
        for mem_type in self.BASE_R_CONFIGS:
            temp_config = MemoryConfig(mem_type)
            resistance = temp_config.base_r / 1000
            conductance = 1/temp_config.base_r * 1e6
            energy = temp_config.energy_factor
            area = temp_config.area_factor
            
            print(f"{mem_type:<15} {resistance:<12.3f} {conductance:<12.3f} {energy:<12.3f} {area:<12.3f}")
        
        print(f"{'='*80}")

# 使用示例
if __name__ == "__main__":
    # 创建不同的配置
    configs = ['RRAM_LOW', 'RRAM_HIGH', 'SRAM']
    
    for config_type in configs:
        config = MemoryConfig(config_type)
        config.print_config()
        print()
    
    # 比较所有配置
    MemoryConfig().compare_configs()
    
    # 权重映射示例
    print("\n权重到电阻映射示例 (4-bit):")
    rram_config = MemoryConfig('RRAM_LOW')
    sram_config = MemoryConfig('SRAM')
    
    print(f"{'权重值':<8} {'RRAM阻值(kΩ)':<15} {'SRAM阻值(kΩ)':<15}")
    print("-" * 40)
    for weight in [1, 5, 10, 15]:
        rram_r = rram_config.get_resistance_mapping(weight) / 1000
        sram_r = sram_config.get_resistance_mapping(weight) / 1000
        print(f"{weight:<8} {rram_r:<15.3f} {sram_r:<15.3f}")
