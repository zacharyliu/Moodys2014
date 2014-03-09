import math
import random
import numpy as np
import scipy.optimize
import csv

class Model2:
    params_common = {
        'maxRepeats': 2,
        'P_A': 0.0445,
        'P_B': 0.00513,
        'P_C': -0.018,
        'price': 7
    }

    params_K_5 = {
        'USDA_fruits': 2.5,
        'USDA_vegetables': 3.75,
        'USDA_proteins': 8,
        'USDA_proteins_max': 10,
        'USDA_grains': 8,
        'USDA_grains_max': 9,
        'USDA_dairy': 5,
        'USDA_sodium': 640*5,
    }

    params_6_8 = {
        'USDA_fruits': 2.5,
        'USDA_vegetables': 3.75,
        'USDA_proteins': 9,
        'USDA_proteins_max': 10,
        'USDA_grains': 8,
        'USDA_grains_max': 10,
        'USDA_dairy': 5,
        'USDA_sodium': 710*5,
    }

    params_9_12 = {
        'USDA_fruits': 5,
        'USDA_vegetables': 5,
        'USDA_proteins': 10,
        'USDA_proteins_max': 12,
        'USDA_grains': 10,
        'USDA_grains_max': 12,
        'USDA_dairy': 5,
        'USDA_sodium': 740*5,
    }

    params = dict(params_9_12.items() + params_common.items())

    def __init__(self, params):
        newParams = {}
        for key in self.params.keys():
            if key in params:
                newParams[key] = params[key]
            else:
                newParams[key] = self.params[key]

        self.params = newParams

        self.maxRepeats = newParams['maxRepeats']
        self.P_A, self.P_B, self.P_C = newParams['P_A'], newParams['P_B'], newParams['P_C']
        self.usda = {'fruits': newParams['USDA_fruits'], 'vegetables': newParams['USDA_vegetables'], 'proteins': newParams['USDA_proteins'], 'grains': newParams['USDA_grains'], 'dairy': newParams['USDA_dairy'], 'sodium': newParams['USDA_sodium']}
        self.price = newParams['price']

        with open('realPrices2.csv', 'rb') as csvfile:
            reader = csv.reader(csvfile)
            self.columns = reader.next()[1:]
            self.columnsLookup = {self.columns[i]: i for i in xrange(len(self.columns))}
            self.dishes = list(reader)
            self.dishesValues = np.array([dish[1:] for dish in self.dishes])
            self.dishesValues = self.dishesValues.astype(float)

    def scale(self, x):
        return [np.multiply(x[i], self.dishesValues[i]) for i in xrange(len(x))]

    def getAttr(self, x, attr):
        return [dish[int(self.columnsLookup[attr])] for dish in self.scale(x)]

    def constrainAttr(self, x, attr, value, isMaximum):
        constraint = np.sum(self.getAttr(x, attr)) - value
        if isMaximum:
            constraint *= -1
        return constraint

    def solve(self):
        result = scipy.optimize.minimize(fun = lambda x: -self.actualCalories(x),
                                         # x0 = [1.0/len(dishes)]*len(dishes),
                                         x0 = [0 for i in xrange(len(self.dishes))],
                                         # args = ['calories', 0, True],
                                         method='SLSQP',
                                         bounds = [(0, self.maxRepeats)]*len(self.dishes),
                                         constraints = [
                                             {'type': 'ineq', 'fun': self.constrainAttr, 'args': ['price', self.price, True]},
                                             {'type': 'ineq', 'fun': self.constrainAttr, 'args': ['fruits', self.usda['fruits'], False]},
                                             {'type': 'ineq', 'fun': self.constrainAttr, 'args': ['vegetables', self.usda['vegetables'], False]},
                                             {'type': 'ineq', 'fun': self.constrainAttr, 'args': ['proteins', self.usda['proteins'], False]},
                                             {'type': 'ineq', 'fun': self.constrainAttr, 'args': ['proteins', self.params['USDA_proteins_max'], True]},
                                             {'type': 'ineq', 'fun': self.constrainAttr, 'args': ['grains', self.usda['grains'], False]},
                                             {'type': 'ineq', 'fun': self.constrainAttr, 'args': ['grains', self.params['USDA_proteins_max'], True]},
                                             {'type': 'ineq', 'fun': self.constrainAttr, 'args': ['dairy', self.usda['dairy'], False]},
                                             {'type': 'ineq', 'fun': self.constrainAttr, 'args': ['sodium', self.usda['sodium'], True]},
                                         ],
                                         options = {
                                             'disp': True,
                                         })

        output = np.sum(self.scale(result.x), axis=0)
        print
        print 'Output'
        for i in xrange(len(output)):
            print self.columns[i], ':', output[i]

        print
        print 'Number of each dish:'
        for i in xrange(len(result.x)):
            print self.dishes[i][0], np.round(result.x[i], 1)

        print
        actual_calories = self.actualCalories(result.x)
        print 'Actual calorie consumption:', actual_calories
        print '=', actual_calories/5.0, 'per day'

        return actual_calories/5.0

    def weightedP(self, dishValues):
        p = [0.569, 0.403, 0.736, 0.736, 0.539]

        if np.sum(dishValues[:5]) == 0:
            return 1
        else:
            return np.sum(np.multiply(p, dishValues[:5])) / np.sum(dishValues[:5])

    def modeledP(self, dishValues):
        sugar = dishValues[int(self.columnsLookup['sugar'])]
        sodium = dishValues[int(self.columnsLookup['sodium'])]
        calcium = dishValues[int(self.columnsLookup['calcium'])]

        P = 1-math.e**-(self.P_A*sugar + self.P_B*sodium + self.P_C*calcium)
        # if P<0: print sugar, sodium, calcium, P
        return P

    def actualCalories(self, x):
        return np.sum([self.dishesValues[i][int(self.columnsLookup['calories'])] * self.modeledP(self.dishesValues[i]) * x[i] for i in xrange(len(self.dishesValues))])

if __name__ == '__main__':
    model = Model2({})
    model.solve()
