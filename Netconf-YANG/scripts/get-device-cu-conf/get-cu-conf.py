from ncclient import manager

# 设备连接参数
device_info = {
    "host": "192.168.1.111",
    "port": 830,
    "username": "netconftest",
    "password": "Zzy@123456",
    "hostkey_verify": False,
    "device_params": {"name": "huawei"},
    'allow_agent': False,
    'look_for_keys': False
}

try:
    # 建立NETCONF连接
    with manager.connect(**device_info) as m:
        print("连接成功，正在获取配置...")
        
        # 核心方法：获取running配置数据库的全量配置
        # 返回的是包含XML的RPC回复对象
        config_reply = m.get_config(source='running')
        
        # 获取XML格式的配置数据
        full_config_xml = config_reply.data_xml
        with open("Netconf-YANG/scripts/get-device-cu-conf/cu-conf.xml","w") as f:
            f.write(full_config_xml)
        
except Exception as e:
    print(f"操作失败: {e}")