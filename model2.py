import math
import random
import numpy as np
import scipy.optimize
import csv

class Model2:
    def __init__(self,
                 maxRepeats=2,
                 P_vegetables=0.569,
                 P_fruits=0.403,
                 P_proteins=0.736,
                 P_grains=0.736,
                 USDA_fruits=2.5,
                 USDA_vegetables=3.75,
                 USDA_proteins=9.5,
                 USDA_grains=9):
        self.maxRepeats = maxRepeats
        self.P = [P_vegetables, P_fruits, P_proteins, P_grains]
        self.usda = {'fruits': USDA_fruits, 'vegetables': USDA_vegetables, 'proteins': USDA_proteins, 'grains': USDA_grains}

        with open('test2.csv', 'rb') as csvfile:
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
        result = scipy.optimize.minimize(fun = self.constrainAttr,
                                         # x0 = [1.0/len(dishes)]*len(dishes),
                                         x0 = [random.random() * self.maxRepeats for i in xrange(len(self.dishes))],
                                         args = ['calories', 0, True],
                                         method='SLSQP',
                                         bounds = [(0, self.maxRepeats)]*len(self.dishes),
                                         constraints = [
                                             {'type': 'ineq', 'fun': self.constrainAttr, 'args': ['price', 6, True]},
                                             {'type': 'ineq', 'fun': self.constrainAttr, 'args': ['fruits', self.usda['fruits'], False]},
                                             {'type': 'ineq', 'fun': self.constrainAttr, 'args': ['vegetables', self.usda['vegetables'], False]},
                                             {'type': 'ineq', 'fun': self.constrainAttr, 'args': ['proteins', self.usda['proteins'], False]},
                                             {'type': 'ineq', 'fun': self.constrainAttr, 'args': ['grains', self.usda['grains'], False]},
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

        def modeledP(dishValues):
            sugar = dishValues[int(self.columnsLookup['sugar'])]
            sodium = dishValues[int(self.columnsLookup['sodium'])]
            calcium = dishValues[int(self.columnsLookup['calcium'])]
            A = 0.0445
            B = 0.00513
            C = -0.018

            P = 1-math.e**-(A*sugar + B*sodium + C*calcium)
            return P

        def actualCalories(x):
            return np.sum([self.dishesValues[i][int(self.columnsLookup['calories'])] * modeledP(self.dishesValues[i]) * x[i] for i in xrange(len(self.dishesValues))])

        print
        actual_calories = actualCalories(result.x)
        print 'Actual calorie consumption:', actual_calories
        print '=', actual_calories/5.0, 'per day'