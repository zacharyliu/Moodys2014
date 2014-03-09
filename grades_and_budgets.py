from model2 import Model2

outputs = []
for params in [Model2.params_K_5, Model2.params_6_8, Model2.params_9_12]:
    output = []
    for price in [7, 6]:
        params['price'] = price
        model = Model2(params)
        output.append(model.solve())
    outputs.append(output)

print outputs