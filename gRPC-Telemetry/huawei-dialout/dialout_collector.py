from concurrent import futures
import time
import importlib
import grpc
import huawei_grpc_dialout_pb2_grpc
import huawei_telemetry_pb2

_ONE_DAY_IN_SECONDS = 60*60*24

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    huawei_grpc_dialout_pb2_grpc.add_gRPCDataserviceServicer_to_server(Telemetry_CPU_Info(),server)

    server.add_insecure_port('192.168.1.5:20000')

    server.start()

    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)

class Telemetry_CPU_Info(huawei_grpc_dialout_pb2_grpc.gRPCDataserviceServicer):
    def __init__(self):
        return
    
    def dataPublish(self, request_iterator, context):
        for i in request_iterator:
            print('################ start ##################\n')
            telemetry_data = huawei_telemetry_pb2.Telemetry.FromString(i.data)
            print(telemetry_data)

            for row_data in telemetry_data.data_gpb.row:
                print("------")
                print(telemetry_data.proto_path)
                print("------")
                module_name = telemetry_data.proto_path.split(".")[0]
                root_class = telemetry_data.proto_path.split(".")[1]

                decode_module = importlib.import_module( module_name+"_pb2" )
                print(decode_module)

                decode_func = getattr(decode_module,root_class).FromString

                print("--------- content is ---------\n")
                print(decode_func(row_data.content))
                print("------------ done ------------")

if __name__ == "__main__":
    serve()