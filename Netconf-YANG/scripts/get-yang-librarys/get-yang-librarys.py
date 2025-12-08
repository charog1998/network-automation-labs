from ncclient import manager
import xml.dom.minidom

# 设备连接参数
device_params = {
    "host": "192.168.1.111",
    "port": 830,
    "username": "netconftest",
    "password": "Zzy@123456",
    "hostkey_verify": False,
    "device_params": {"name": "huawei"},
    'allow_agent': False,
    'look_for_keys': False
}

# 连接设备并获取设备支持的 YANG 模块列表
with manager.connect(**device_params) as m:
    with open("Netconf-YANG/scripts/get-yang-librarys/all-yang-modules.txt","w+") as f:
        for cap in m.server_capabilities:
            if 'module=' in cap:
                module_info = cap.split('module=')[1]
                module_name = module_info.split('&')[0] if '&' in module_info else module_info
                f.write(f"- {module_name}"+"\n")