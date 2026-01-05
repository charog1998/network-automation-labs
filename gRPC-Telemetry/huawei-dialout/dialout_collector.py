from concurrent import futures
import time
import importlib
import grpc
import huawei_grpc_dialout_pb2_grpc
import huawei_telemetry_pb2

_ONE_DAY_IN_SECONDS = 60*60*24

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    huawei_grpc_dialout_pb2_grpc.add_gRPCDataserviceServicer_to_server(TelemetryDataService(),server)
    server.add_insecure_port('192.168.1.5:20000')
    server.start()

    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)

class TelemetryDataService(huawei_grpc_dialout_pb2_grpc.gRPCDataserviceServicer):
    """
    一个通用的Telemetry数据处理服务。
    通过解析 'proto_path' 动态加载对应的 Protobuf 模块来解码数据。
    """
    def __init__(self):
        return
    
    def dataPublish(self, request_iterator, context):
        """
        处理来自 gRPC 客户端的流式数据。
        """
        for i in request_iterator:
            print('############ New Telemetry Packet ############\n')
            telemetry_data = huawei_telemetry_pb2.Telemetry.FromString(i.data)
            print(telemetry_data)

            for row_data in telemetry_data.data_gpb.row:
                print("------------------ Proto is ------------------")
                print(telemetry_data.proto_path)
                print("----------------------------------------------")
                module_name = telemetry_data.proto_path.split(".")[0]
                root_class = telemetry_data.proto_path.split(".")[1]

                decode_module = importlib.import_module( module_name+"_pb2" )
                print(decode_module)

                decode_func = getattr(decode_module,root_class).FromString

                print("----------------- Content is -----------------\n")
                print(decode_func(row_data.content))
                print("----------- Packet Processing Done -----------")

if __name__ == "__main__":
    serve()