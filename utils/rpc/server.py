# # xmlrpc服务端
#
# from xmlrpc.server import SimpleXMLRPCServer
#
#
# s = SimpleXMLRPCServer(('localhost', 5200))
#
#
# # def f(x):
# #     return x**2
# #
# #
# # s.register_function(f)
# # print('服务启动...')
# # s.serve_forever()
#
#
# class Love:
#     # def _dispatch(self, method, param):
#     #     print(method)
#     #     func = getattr(self, method)
#     #     return func(*param)
#
#     def jsp(self, x):
#         return 4 * x
#
#     def hyf(self, y):
#         return 2 * y
#
#
# s.register_instance(Love())
# print('服务启动...')
# s.serve_forever()


# 服务端

from rpyc import Service
from rpyc.utils.server import ThreadedServer


class TestService(Service):
    # 对于服务端来说， 只有以"exposed_"打头的方法才能被客户端调用，所以要提供给客户端的方法都得加"exposed_"
    def exposed_test(self, num):
        return num ** 2


s = ThreadedServer(TestService, hostname='localhost', port=9999, auto_register=False)
print('服务启动...')
s.start()
