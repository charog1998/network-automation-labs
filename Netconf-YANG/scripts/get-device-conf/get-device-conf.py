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
        # 同理，这里的ifm改成任意的yang模组应该都能查到对应的结果
        interface_filter = """
            <filter type="subtree">
                <ifm xmlns="http://www.huawei.com/netconf/vrp" format-version="1.0" content-version="1.0">
                    <interfaces>
                        <interface/>
                    </interfaces>
                </ifm>
            </filter>
            """
        reply = m.get_config(source="running", filter=interface_filter)

        # 格式化输出
        pretty_xml = xml.dom.minidom.parseString(reply.data_xml).toprettyxml()
        print(reply)

        # 保存到文件
        with open("Netconf-YANG/scripts/get-interface-conf/interface_config.xml", "w", encoding="utf-8") as f:
            f.write(pretty_xml)

except Exception as e:
    print(f"操作失败: {e}")
