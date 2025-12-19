# 根据新华三的文档，获取NETCONF状态信息的操作可通过发送<get><netconf-state/></get>报文实现，通用格式为：
# <?xml version="1.0" encoding="UTF-8"?>
# <rpc message-id="m-641" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
#   <get>
#     <filter type='subtree'>
#       <netconf-state xmlns='urn:ietf:params:xml:ns:yang:ietf-netconf-monitoring'>
#          <getType/>
#       </netconf-state>
#     </filter>
#   </get>
# </rpc>

# 其中，getType可以为capabilities、datastores、schemas、sessions或者statistics：
# 不指定getType时，该操作则获取NETCONF全部信息。
# 当指定getType时，该操作仅返回相应类型的应答数据。其中，getType取值为：
#     capabilities：  该操作用来获取设备能力集
#     datastores：    该操作用来获取设备中的数据库
#     schemas：       该操作用来获取设备中的YANG文件名称列表
#     sessions：      该操作用来获取设备中的会话信息
#     statistics：    该操作用来获取NETCONF的统计信息

# 设备收到NETCONF信息获取请求报文后，将相应属性的值通过如下报文反馈给客户端：
# <?xml version="1.0"?>
# <rpc-reply message-id="100" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
#   <data>
#      全部NETCONF全部相关信息
#   </data>
# </rpc-reply>
# 据此可编写脚本如下：
from ncclient import manager
import xml.dom.minidom

# NETCONF连接参数
host = '192.168.56.101'
port = 830  # 默认NETCONF端口
username = 'zzy'
password = '123456qwer'

# 建立连接并发送RPC
with manager.connect(
    host=host,
    port=port,
    username=username,
    password=password,
    hostkey_verify=False,  # 生产环境建议使用证书验证
    device_params={'name': 'default'}
) as m:
    
    filter_xml = """<netconf-state xmlns='urn:ietf:params:xml:ns:yang:ietf-netconf-monitoring'>
                     <schemas/>
                  </netconf-state>"""
    response = m.get(filter=('subtree', filter_xml))

    pretty_response = xml.dom.minidom.parseString(response.xml).toprettyxml()
    with open('Output/netconf_response.xml', 'w', encoding='utf-8') as f:
        f.write(pretty_response)