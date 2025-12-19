from ncclient import manager

# 设备连接参数
device_params = {
    "host": "192.168.56.101",
    "port": 830,
    "username": "zzy",
    "password": "123456qwer",
    "hostkey_verify": False,
    "device_params": {"name": "h3c"},
    'allow_agent': False,
    'look_for_keys': False
}

# 连接设备并获取设备支持的 YANG 模块列表
with manager.connect(**device_params) as m:
    with open("Output/get-server_capabilities/server_capabilities.txt","w+") as f:
        for cap in m.server_capabilities:
            f.write(cap+"\n")