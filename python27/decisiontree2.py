# -*- coding: utf-8 -*-
"""
Created on Tue Aug 12 14:26:49 2014

@author: karthik.ganapathy
"""

from sklearn.datasets import load_iris
from StringIO import StringIO
import pydot

from sklearn import tree
iris = load_iris()
clf = tree.DecisionTreeClassifier()
clf = clf.fit(iris.data, iris.target)
# print iris.keys
dot_data = StringIO()
# Below command ot output the tree to a file
# get hte tree into the out StringIO
tree.export_graphviz(clf, out_file=dot_data) 
graph = pydot.graph_from_dot_data(dot_data.getvalue()) 
type(graph)
graph.write_pdf("iris.pdf") 
#Below line prints the tree out
#print out.getvalue()

#print clf.__class__


#k = clf(0)
#print k['splitter']
