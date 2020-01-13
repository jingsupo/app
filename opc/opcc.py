from opcua import Client, ua


def brower_child(root):
    """
    递归调用遍历，格式化不好做，有深度问题
    """
    name = root.get_node_class().name
    # print(name)
    if name == "Object":
        brower_obj(root)
        for c in root.get_children():
            print("  ", end='')
            brower_child(c)
    elif name == 'Variable':
        brower_var(root)
    else:
        brower_method(root)


class CurState():
    def __init__(self, parent=None, p=None, d=0):
        self.parent = parent  # unused
        self.p = p
        self.d = d


def brower_child2(root, max_d=-1, ignore=[]):
    """
    栈+循环遍历，非常好用
    """
    stack = [CurState(None, root, 0)]
    while len(stack):
        cur = stack.pop()
        name = cur.p.get_node_class().name

        print(''.join(['  ' for i in range(cur.d)]), end="")

        if cur.p.get_browse_name().Name in ignore:
            continue

        if name == "Object":
            brower_obj(cur.p)
            if max_d > 0 and cur.d >= max_d:
                continue
            for c in cur.p.get_children():
                stack.append(CurState(cur.p, c, cur.d+1))

        elif name == 'Variable':
            brower_var(cur.p)
        else:
            brower_method(cur.p)


def brower_obj(v):
    # print(v.get_browse_name())
    rw = 'R '
    bname = v.get_browse_name()
    print("*%2d:%-30s (%-2s, %-23s)" %
          (bname.NamespaceIndex, bname.Name, rw, "Object"))


def brower_var(v):
    # print(v.get_browse_name())
    rw = 'R '
    if ua.AccessLevel.CurrentWrite in v.get_access_level():
        rw = "RW"
    bname = v.get_browse_name()
    tv = v.get_data_value().Value
    v_show = tv.Value
    if len(str(v_show)) > 1024:
        v_show = str(v_show[:56]) + "..."
    print("-%2d:%-30s (%-2s, %-23s) =>" %
          (bname.NamespaceIndex, bname.Name, rw, tv.VariantType), v_show)


def brower_method(v):
    # print(v.get_description())
    rw = 'C '
    bname = v.get_browse_name()
    # args = []
    # for a in v.get_properties():
    #     dt = a.get_data_type().NodeIdType.name
    #     args.append(dt)
    print("@%2d:%-30s (%-2s, %-23s)" %
          (bname.NamespaceIndex, bname.Name, rw, "Method"))


def main_c():
    url = "opc.tcp://127.0.0.1:4840/freeopcua/server/"
    #url = "opc.tcp://localhost:49320"
    c = Client(url)
    try:
        c.connect()
        root = c.get_root_node()
        print("\r\nBrower:")
        brower_child2(root.get_child(["0:Objects"]), -1, ["Server"])
    except Exception as e:
        print("Client Exception:", e)
    finally:
        c.disconnect()


if __name__ == "__main__":
    main_c()
