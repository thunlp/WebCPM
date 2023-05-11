import platformctrl
op = platformctrl.Operator()
op.execute(platformctrl.Operation.START)
a = op.search("中国最高的山峰")
print(a[0])

x = op.load_page(1)
print(x)