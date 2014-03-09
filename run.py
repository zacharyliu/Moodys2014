from model2 import Model2

factor = 0.2

params = {
    'maxRepeats': 2,
    'P_vegetables': 0.569,
    'P_fruits': 0.403,
    'P_proteins': 0.736,
    'P_grains': 0.736,
    'USDA_fruits': 2.5,
    'USDA_vegetables': 3.75,
    'USDA_proteins': 9.5,
    'USDA_grains': 9
}

outputs = {}

for key in params.keys():
    original = params[key]
    outputs[key] = {}

    # Increase by factor
    params[key] = original*(1+factor)
    model = Model2(**params)
    outputs[key]['increased'] = model.solve()

    # Decrease by factor
    params[key] = original*(1-factor)
    model = Model2(**params)
    outputs[key]['decreased'] = model.solve()

    # Original value
    params[key] = original
    model = Model2(**params)
    outputs[key]['original'] = model.solve()

print outputs