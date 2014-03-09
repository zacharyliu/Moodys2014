import math
import random
import numpy as np
import scipy.optimize
import csv

maxRepeats = 2
p = [0.569, 0.403, 0.736, 0.736]

with open('test2.csv', 'rb') as csvfile:
    reader = csv.reader(csvfile)
    columns = reader.next()[1:]
    columnsLookup = {columns[i]: i for i in xrange(len(columns))}
    dishes = list(reader)
    dishesValues = np.array([dish[1:] for dish in dishes])
    dishesValues = dishesValues.astype(float)

def scale(x):
    return [np.multiply(x[i], dishesValues[i]) for i in xrange(len(x))]

def getAttr(x, attr):
    return [dish[int(columnsLookup[attr])] for dish in scale(x)]

usda = {'fruits': 2.5, 'vegetables': 3.75, 'proteins': 9.5, 'grains': 9}

def constrainAttr(x, attr, value, isMaximum):
    constraint = np.sum(getAttr(x, attr)) - value
    if isMaximum:
        constraint *= -1
    return constraint

result = scipy.optimize.minimize(fun = constrainAttr,
                                 # x0 = [1.0/len(dishes)]*len(dishes),
                                 x0 = [random.random() * maxRepeats for i in xrange(len(dishes))],
                                 args = ['calories', 0, True],
                                 method='SLSQP',
                                 bounds = [(0, maxRepeats)]*len(dishes),
                                 constraints = [
                                     {'type': 'ineq', 'fun': constrainAttr, 'args': ['price', 6, True]},
                                     {'type': 'ineq', 'fun': constrainAttr, 'args': ['fruits', usda['fruits'], False]},
                                     {'type': 'ineq', 'fun': constrainAttr, 'args': ['vegetables', usda['vegetables'], False]},
                                     {'type': 'ineq', 'fun': constrainAttr, 'args': ['proteins', usda['proteins'], False]},
                                     {'type': 'ineq', 'fun': constrainAttr, 'args': ['grains', usda['grains'], False]},
                                 ],
                                 options = {
                                     'disp': True,
                                 })

output = np.sum(scale(result.x), axis=0)
print
print 'Output'
for i in xrange(len(output)):
    print columns[i], ':', output[i]

print
print 'Number of each dish:'
for i in xrange(len(result.x)):
    print dishes[i][0], np.round(result.x[i], 1)

def modeledP(dishValues):
    sugar = dishValues[int(columnsLookup['sugar'])]
    sodium = dishValues[int(columnsLookup['sodium'])]
    calcium = dishValues[int(columnsLookup['calcium'])]
    A = 0.0445
    B = 0.00513
    C = -0.018

    P = 1-math.e**-(A*sugar + B*sodium + C*calcium)
    return P

def actualCalories(x):
    return np.sum([dishesValues[i][int(columnsLookup['calories'])] * modeledP(dishesValues[i]) * x[i] for i in xrange(len(dishesValues))])

print
actual_calories = actualCalories(result.x)
print 'Actual calorie consumption:', actual_calories
print '=', actual_calories/5.0, 'per day'