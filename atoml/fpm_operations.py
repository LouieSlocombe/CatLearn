# -*- coding: utf-8 -*-
"""
Created on Tue Jan  3 12:01:30 2017

@author: mhangaard
"""
import numpy as np
from random import shuffle

from .fingerprint_setup import sure_independence_screening


def triangular(n):
    return sum(range(n+1))


def do_sis(X, y, l=None, size=None, increment=1):
    """ function to narrow down a list of descriptors based on sure
    independence screening.
    Input:
        X: n x m matrix
        y: length n vector
        l: length m list of strings (optional)
        size: integer (optional)
        increment: integeer (optional)

    Output:
        X: n x size matrix
        l: length size list of strings
    """
    shape = np.shape(X)
    assert shape[1] == len(l)
    if size is None:
        size = shape[0]
    while shape[1] > size:
        shape = np.shape(X)
        select = sure_independence_screening(y, X, size=shape[1]-increment)
        X = X[:, select['accepted']]
        if l is not None:
            l = l[select['accepted']]
    return X, l


class fpm_operations():
    def __init__(self, X=None, x=None):
        self.X = X
        self.x = x

    def get_order_2(self):
        A = self.X
        """Get all combinations x_ij = x_i * x_j, where x_i,j are features.
        The sorting order in dimension 0 is preserved.
        Input)
            A: nxm matrix, where n is the number of training examples and
            m is the number of features.
        Output)
            n x triangular(m) matrix
        """
        shapeA = np.shape(A)
        nfi = 0
        new_features = np.zeros([shapeA[0], triangular(shapeA[1])])
        for f1 in range(shapeA[1]):
            for f2 in range(f1, shapeA[1]):
                new_feature = A[:, f1]*A[:, f2]
                new_features[:, nfi] = new_feature
                nfi += 1
        return new_features

    def get_labels_order_2(self):
        """Get all combinations ij, where i,j are feature labels.
        Input)
            x: length m vector, where m is the number of features.
        Output)
            traingular(m) vector
        """
        L = len(self.x)
        # assert L == np.shape(self.X)[1]
        new_features = []
        for f1 in range(L):
            for f2 in range(f1, L):
                new_features.append(self.x[f1] + '_x_' + self.x[f2])
        return np.array(new_features)

    def get_order_2ab(self, a, b):
        A = self.X
        """Get all combinations x_ij = x_i*a * x_j*b, where x_i,j are features.
        The sorting order in dimension 0 is preserved.
        Input)
            A: nxm matrix, where n is the number of training examples and
            m is the number of features.

            a: float

            b: float
        Output)
            n x triangular(m) matrix
        """
        shapeA = np.shape(A)
        nfi = 0
        new_features = np.zeros([shapeA[0], triangular(shapeA[1])])
        for f1 in range(shapeA[1]):
            for f2 in range(f1, shapeA[1]):
                new_feature = A[:, f1]**a * A[:, f2]**b
                new_features[:, nfi] = new_feature
                nfi += 1
        return new_features

    def get_ablog(self, a, b):
        A = self.X
        """Get all combinations x_ij = a*log(x_i) + b*log(x_j),
        where x_i,j are features.
        The sorting order in dimension 0 is preserved.
        Input)
            A: nxm matrix, where n is the number of training examples and
            m is the number of features.

            a: float

            b: float
        Output)
            n x triangular(m) matrix
        """
        shapeA = np.shape(A)
        nfi = 0
        new_features = np.zeros([shapeA[0], triangular(shapeA[1])])
        for f1 in range(shapeA[1]):
            for f2 in range(f1, shapeA[1]):
                new_feature = a*np.log(A[:, f1]) + b*np.log(A[:, f2])
                new_features[:, nfi] = new_feature
                nfi += 1
        return new_features

    def fpmatrix_split(self, nsplit, fix_size=None, replacement=False):
        """ Routine to split feature matrix and return sublists. This can be
            useful for bootstrapping, LOOCV, etc.

            nsplit: int
                The number of bins that data should be devided into.

            fix_size: int
                Define a fixed sample size, e.g. nsplit=5 and fix_size=100,
                this generate 5 x 100 data split. Default is None meaning all
                avaliable data is divided nsplit times.

            replacement: boolean
                Set to true if samples are to be generated with replacement
                e.g. the same candidates can be in samles multiple times.
                Default is False.
        """
        if fix_size is not None:
            msg = 'Cannot divide dataset in this way, number of candidates is '
            msg += 'too small'
            assert len(self.X) >= nsplit * fix_size, msg
        dataset = []
        index = list(range(len(self.X)))
        shuffle(index)
        # Find the size of the divides based on all candidates.
        s1 = 0
        if fix_size is None:
            # Calculate the number of items per split.
            n = len(self.X) / nsplit
            # Get any remainders.
            r = len(self.X) % nsplit
            # Define the start and finish of first split.
            s2 = n + min(1, r)
        else:
            s2 = fix_size
        for _ in range(nsplit):
            if replacement:
                shuffle(index)
            dataset.append(self.X[index[int(s1):int(s2)]])
            s1 = s2
            if fix_size is None:
                # Get any new remainder.
                r = max(0, r-1)
                # Define next split.
                s2 = s2 + n + min(1, r)
            else:
                s2 = s2 + fix_size
        return dataset
