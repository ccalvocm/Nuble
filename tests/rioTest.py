import pywr
from pywr.core import Model
from pywr.core import Model, Input, Output, Catchment
from pywr.parameters import MonthlyProfileParameter
from pywr.domains import river
from numpy.testing import assert_allclose
import pytest
from pywr.notebook import draw_graph

path="rioTest.json"
model = Model.load(path)

node = model.nodes["mrf"]
demand = model.nodes["demanda1"]

# test getting properties
assert isinstance(node.mrf, MonthlyProfileParameter)
assert_allclose(node.mrf_cost, -1000)
assert_allclose(node.cost, 0.0)

# test setting properties
node.mrf = 40
node.mrf_cost = -999
# assert_allclose(node.mrf, 40)
# assert_allclose(node.mrf_cost, -999)

# run the model and see if it works
model.run()
draw_graph(model, labels = True, attributes = True, width=900,height=900)
