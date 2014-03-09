from model2 import Model2

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

model = Model2(**params)
model.solve()
