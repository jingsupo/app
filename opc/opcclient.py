from opcua import Client


if __name__ == "__main__":

    client = Client("opc.tcp://localhost:49320")

    try:
        client.connect()

        # Client has a few methods to get proxy to UA nodes that should always be in address space such as Root or Objects
        root = client.get_root_node()
        print("Objects node is: ", root)

        # Node objects have methods to read and write node attributes as well as browse or populate address space
        print("Children of root are: ", root.get_children())

        myvar = root.get_child(["0:Objects", "2:模拟器示例", "2:函数", "2:Random1"]).get_value()

        print("myvar is: ", myvar)

        # Stacked myvar access
        print("myvar is: ", client.get_node("ns=2;s=通道 1.设备 1.标记 1").get_value())

    finally:
        client.disconnect()