# -*- coding: utf-8 -*-

"""
Support Vector Machine Classifier
"""

import numpy
from sklearn import svm
from collections import defaultdict
from simpleai.machine_learning import Classifier


class SVMClassifier(Classifier):
    def learn(self):
        vectors = []
        answers = []
        for data in self.dataset:
            vector = self.vectorize(data)
            vectors.append(vector)
            answer = self.problem.target(data)
            answers.append(answer)
        if not vectors:
            raise ValueError("Cannot train on empty set")
        self.svm = svm.SVC()
        self.svm.fit(vectors, answers)

    def classify(self, data):
        vector = self.vectorize(data)
        return self.svm.predict(vector)[0], 1

    def score(self, data):
        """
        True class is positive, False class is negative.
        """
        vector = self.vectorize(data)
        return float(self.svm.decision_function(vector))

    def vectorize(self, data):
        vector = [attr(data) for attr in self.attributes]
        vector = numpy.array(vector)
        # FIXME: This is OUR convention (values in 0..1) not in general.
        #        Consider moving.
        assert vector.all() >= 0
        assert vector.all() <= 1
        return vector

    def __getstate__(self):
        result = self.__dict__.copy()
        if "dataset" in result:
            del result["dataset"]
        return result


def correlation(classifier, dataset=None):
    """
    Calculates the correlation of the attributes on a classifier.
    For more information see:
        - http://en.wikipedia.org/wiki/Correlation_and_dependence
    """
    if dataset is None:
        assert hasattr(classifier, "dataset")
        dataset = classifier.dataset

    result = {}
    answers = []
    attributes = defaultdict(list)

    for data in dataset:
        answers.append(int(classifier.problem.target(data)))
        for i, attr in enumerate(classifier.attributes):
            attributes[i].append(attr(data))

    answers_std = numpy.std(answers)
    for i in xrange(len(attributes)):
        cov = numpy.cov(attributes[i], answers)[0][1]
        std = numpy.std(attributes[i]) * answers_std
        if std == 0:
            corr = numpy.nan
        else:
            corr = cov / std
        result[classifier.attributes[i]] = corr
    return result
