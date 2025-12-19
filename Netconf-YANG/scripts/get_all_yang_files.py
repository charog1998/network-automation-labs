# 结合get_yang_file.py中的get_yang_schema方法和get_netcong_state.py脚本获取到的yang文件列表，实现批量获取设备上所有YANG文件并保存到本地

from ncclient import manager
from lxml import etree
import re
import os

def get_yang_schema(
    host: str,
    username: str,
    password: str,
    identifier: str,
    version: str,
    port: int = 830,
    format_type: str = "yang",
    **kwargs
):
    """
    获取设备上指定YANG文件的内容
    :param host: 设备IP地址
    :param username: 登录用户名
    :param password: 登录密码
    :param identifier: YANG文件标识（如H3C-acl-data）
    :param version: YANG文件版本（如2019-12-20）
    :param port: NETCONF端口（默认830）
    :param format_type: 获取格式（默认yang，可选yang-library）
    :return: 字典，包含执行状态和YANG文件内容/错误信息
    """
    # 定义关键命名空间
    schema_ns = "urn:ietf:params:xml:ns:yang:ietf-netconf-monitoring"  # get-schema和data节点的命名空间
    rpc_base_ns = "urn:ietf:params:xml:ns:netconf:base:1.0"  # rpc-reply节点的命名空间

    # 构建get-schema RPC请求
    get_schema_ele = etree.Element(f"{{{schema_ns}}}get-schema")
    etree.SubElement(get_schema_ele, f"{{{schema_ns}}}identifier").text = identifier
    etree.SubElement(get_schema_ele, f"{{{schema_ns}}}version").text = version
    etree.SubElement(get_schema_ele, f"{{{schema_ns}}}format").text = format_type

    # 转换为XML字符串
    rpc_request = etree.tostring(
        get_schema_ele,
        encoding="utf-8",
        pretty_print=True,
        xml_declaration=False
    ).decode("utf-8")

    try:
        with manager.connect(
            host=host,
            port=port,
            username=username,
            password=password,
            hostkey_verify=False,
            allow_agent=False,
            look_for_keys=False,
            timeout=120,
            device_params={"name": "h3c"}  # 强制适配H3C设备
        ) as m:
            if not m.connected:
                return {"success": False, "error": "NETCONF连接建立失败"}

            # 发送RPC请求
            response = m.dispatch(etree.fromstring(rpc_request))

            if response is None or response.xml is None:
                return {"success": False, "error": "设备返回空响应"}

            # 解析响应XML
            xml_tree = etree.fromstring(response.xml.encode("utf-8"))

            # 检查是否有RPC错误
            rpc_error_ele = xml_tree.find(f"{{{rpc_base_ns}}}rpc-error")
            if rpc_error_ele:
                error_msg = etree.tostring(rpc_error_ele, encoding="utf-8", pretty_print=True).decode("utf-8")
                return {"success": False, "error": f"RPC错误: {error_msg}"}

            # 查找YANG内容所在的data节点（关键修复！）
            # 匹配带有schema_ns命名空间的data节点（设备响应的实际结构）
            data_ele = xml_tree.find(f".//{{{schema_ns}}}data")
            
            if data_ele is None:
                return {"success": False, "error": "响应中未找到带有正确命名空间的data节点"}

            # 提取并清理YANG内容（保留原始格式）
            # 使用method="text"提取纯文本，避免XML标签干扰
            yang_content = etree.tostring(data_ele, encoding="utf-8", method="text").decode("utf-8")
            # 清理多余空行，保留YANG文件的规范格式
            yang_content = re.sub(r'\n\s*\n+', '\n\n', yang_content.strip())

            if not yang_content:
                return {"success": False, "error": "data节点中未提取到YANG内容"}

            return {
                "success": True,
                "yang_filename": f"{identifier}@{version}.yang",
                "yang_content": yang_content
            }

    except Exception as e:
        error_detail = f"异常类型：{type(e).__name__}，详情：{str(e)}"
        return {"success": False, "error": error_detail}

if __name__ == "__main__":
    DEVICE_CONFIG = {
        "host": "192.168.56.101",
        "port": 830,
        "username": "zzy",
        "password": "123456qwer",
        "hostkey_verify": False,
        "device_params": {"name": "h3c"},
        'allow_agent': False,
        'look_for_keys': False
    }
    import xml.etree.ElementTree as ET

    # 解析XML文件
    tree = ET.parse('Output/netconf_response.xml')
    root = tree.getroot()

    # 定义命名空间映射（因为XML中使用了命名空间）
    namespaces = {
        'nc': 'urn:ietf:params:xml:ns:netconf:base:1.0',
        'monitoring': 'urn:ietf:params:xml:ns:yang:ietf-netconf-monitoring'
    }

    # 存储结果的列表
    schema_list = []

    # 查找所有schema元素并提取数据
    for schema in root.findall('.//monitoring:schema', namespaces):
        identifier = schema.find('monitoring:identifier', namespaces).text
        version = schema.find('monitoring:version', namespaces).text
        schema_list.append({
            'identifier': identifier,
            'version': version
        })

    for item in schema_list:
        YANG_CONFIG = item
        print(f"\n🔍 正在获取YANG文件：{item['identifier']}@{item['version']}")
        result = get_yang_schema(**DEVICE_CONFIG, **YANG_CONFIG)
        if result["success"]:
            print(f"\n✅ 成功获取YANG文件：{result['yang_filename']}")
            print("-" * 50)
            # 保存到本地文件
            if item['identifier'].split('-')[-1].lower() in ["data","action","config"]:
                dir_name = item['identifier'].split('-')[-1].lower()
            else:
                dir_name = "other"
            with open(os.path.join("Netconf-YANG/YANG-models/vendors/h3c", dir_name, result["yang_filename"]), "w", encoding="utf-8") as f:
                f.write(result["yang_content"])
            print(f"\n📁 完整YANG文件已保存到本地：{result['yang_filename']}")
        else:
            print(f"\n❌ 获取失败：{result['error']}")