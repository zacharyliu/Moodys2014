from model2 import Model2

factor = 0.2

params = Model2.params

outputs = {}

for key in params.keys():
    original = params[key]
    outputs[key] = {}

    # Increase by factor
    params[key] = original*(1+factor)
    model = Model2(params)
    outputs[key]['increased'] = model.solve()

    # Decrease by factor
    params[key] = original*(1-factor)
    model = Model2(params)
    outputs[key]['decreased'] = model.solve()

    # Original value
    params[key] = original
    model = Model2(params)
    outputs[key]['original'] = model.solve()

print outputs