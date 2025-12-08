from ncclient import manager
import xml.dom.minidom

# 设备连接参数
device_info = {
    "host": "192.168.1.111",
    "port": 830,
    "username": "netconftest",
    "password": "Zzy@123456",
    "hostkey_verify": False,
    "device_params": {"name": "huawei"},
    "allow_agent": False,
    "look_for_keys": False,
}

try:
    # 建立NETCONF连接
    with manager.connect(**device_info) as m:
        interface_filter = """
            <filter type="subtree">
                <sshs xmlns="http://www.huawei.com/netconf/vrp" format-version="1.0" content-version="1.0">
                </sshs>
            </filter>
            """
        reply = m.get_config(source="running", filter=interface_filter)

        # 格式化输出
        pretty_xml = xml.dom.minidom.parseString(reply.data_xml).toprettyxml()
        print(reply)

        # 保存到文件
        with open("interface_config.xml", "w", encoding="utf-8") as f:
            f.write(pretty_xml)

except Exception as e:
    print(f"操作失败: {e}")
