# # xmlrpc客户端
#
# import xmlrpc.client
#
#
# s = xmlrpc.client.ServerProxy('http://localhost:5200')
# print(s.jsp(4))
# print(s.hyf(4))


# 客户端

import rpyc


c = rpyc.connect('localhost', 9999)
for i in range(100):
    res = c.root.test(i)
    print(res)
c.close()
