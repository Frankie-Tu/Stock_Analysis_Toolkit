from collections import OrderedDict
import pdb

od = OrderedDict()

od["one"] = [1]
od["two"] = [2]

od["one"].append(3)
print(od)