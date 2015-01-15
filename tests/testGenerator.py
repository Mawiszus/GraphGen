import logging
import sys
import unittest

from PGC.Generator import Generator
from PGC.Graph.Graph import Graph
from PGC.Production import Production
from PGC.Graph.Vertex import Vertex

# TODO: Test Call Graph
# applyProductions
#   _applyProduction
#       _deleteMissingVertices

class TestGenerator(unittest.TestCase):

    #--------------------------------------------------------------------------
    def testAddNewEdges(self):
        # rhs has no edges, so nothing changes.
        g = Graph()
        lhs = Graph()
        rhs = Graph()
        p = Production(lhs,rhs)
        rhsMapping = {}
        gen = Generator()
        self.assertEqual(len(g._edges), 0)
        gen._addNewEdges(g, p, rhsMapping)
        self.assertEqual(len(g._edges), 0)

        # rhs has an edge, but it already exists in the graph.
        g = Graph()
        g.addEdge(Vertex('g0', 'A'), Vertex('g1', 'B'))
        lhs = Graph()
        rhs = Graph()
        rhs.addEdge(Vertex('r0', 'A'), Vertex('r1', 'B'))
        p = Production(lhs,rhs)
        rhsMapping = {'r0':'g0', 'r1':'g1'}
        gen = Generator()
        self.assertEqual(len(g._edges['g0']), 1)
        gen._addNewEdges(g, p, rhsMapping)
        self.assertEqual(len(g._edges['g0']), 1)

        # rhs has a new edge not in graph.
        g = Graph()
        g.addVertex(Vertex('g0', 'A'))
        g.addVertex(Vertex('g1', 'B'))
        lhs = Graph()
        rhs = Graph()
        rhs.addEdge(Vertex('r0', 'A'), Vertex('r1', 'B'))
        p = Production(lhs,rhs)
        rhsMapping = {'r0':'g0', 'r1':'g1'}
        gen = Generator()
        self.assertEqual(len(g._edges['g0']), 0)
        gen._addNewEdges(g, p, rhsMapping)
        self.assertEqual(len(g._edges['g0']), 1)
        self.assertEqual(g._edges['g0'][0].id, 'g1')

    #--------------------------------------------------------------------------
    def testAddNewVertices(self):
        # Production rhs has no vertices, so nothing done.
        g = Graph()
        lhs = Graph()
        rhs = Graph()
        p = Production(lhs, rhs)
        gen = Generator()
        self.assertEqual(len(g._vertices), 0)
        gen._addNewVertices(g, p, {})
        self.assertEqual(len(g._vertices), 0)
        
        # Production rhs has vertices, but they all appear in the LHS. Hence
        # they aren't new and nothing is done.
        lhs.addVertex(Vertex('l1', 'A'))
        rhs.addVertex(Vertex('r1', 'A'))
        self.assertEqual(len(g._vertices), 0)
        gen._addNewVertices(g, p, {})
        self.assertEqual(len(g._vertices), 0)

        # rhs has one new vertex not in the lhs.
        rhsMapping = {}
        rhs.addVertex(Vertex('r2', 'B'))
        self.assertEqual(len(g._vertices), 0)
        gen._addNewVertices(g, p, rhsMapping)
        self.assertEqual(len(g._vertices), 1)
        self.assertIn('v0', g._vertices)               # new vertex is v0
        self.assertEqual(g._vertices['v0'].label, 'B') # with label B
        self.assertIn('r2', rhsMapping)                # now appears in rhsMapping
        self.assertEqual(rhsMapping['r2'], 'v0')       # r2 mapped to v0 (the newly added vertex) in graph

    #--------------------------------------------------------------------------
    def testDeleteMissingEdges(self):
        # If lhs has no edges, then there's nothing missing from the rhs.
        # Nothing is done to the graph.
        g = Graph()
        g.addEdge(Vertex('g0', 'A'), Vertex('g1', 'B'))
        lhs = Graph()
        rhs = Graph()
        p = Production(lhs,rhs)
        lhsMapping = {}
        rhsMapping = {}
        gen = Generator()
        self.assertEqual(len(g._edges['g0']), 1)
        gen._deleteMissingEdges(g, p, lhsMapping, rhsMapping)
        self.assertEqual(len(g._edges['g0']), 1)

        # lhs has an edge, but it also appears on the rhs. Nothing done.
        g = Graph()
        g.addEdge(Vertex('g0', 'A'), Vertex('g1', 'B'))
        lhs = Graph()
        lhs.addEdge(Vertex('l0', 'A'), Vertex('l1', 'B'))
        rhs = Graph()
        rhs.addEdge(Vertex('r0', 'A'), Vertex('r1', 'B'))
        p = Production(lhs,rhs)
        lhsMapping = {'l0':'g0', 'l1':'g1'}
        rhsMapping = {'r0':'g0', 'r1':'g1'}
        gen = Generator()
        self.assertEqual(len(g._edges['g0']), 1)
        gen._deleteMissingEdges(g, p, lhsMapping, rhsMapping)
        self.assertEqual(len(g._edges['g0']), 1)

        # lhs has an edge, but it's gone from the rhs. It should be deleted
        # from the graph.
        g = Graph()
        g.addEdge(Vertex('g0', 'A'), Vertex('g1', 'B'))
        lhs = Graph()
        lhs.addEdge(Vertex('l0', 'A'), Vertex('l1', 'B'))
        rhs = Graph()
        rhs.addVertex(Vertex('r0', 'A'))
        rhs.addVertex(Vertex('r1', 'B'))
        p = Production(lhs,rhs)
        lhsMapping = {'l0':'g0', 'l1':'g1'}
        rhsMapping = {'r0':'g0', 'r1':'g1'}
        gen = Generator()
        self.assertEqual(len(g._edges['g0']), 1)
        gen._deleteMissingEdges(g, p, lhsMapping, rhsMapping)
        self.assertEqual(len(g._edges['g0']), 0)

    #--------------------------------------------------------------------------
    def testFindMatchingProductions(self):
        # Providing no productions should result in no matches.
        gen = Generator()
        g = Graph()
        self.assertEquals( len(gen._findMatchingProductions(g, [])), 0)        
        
        # We have a production, but the LHS can't be found in the graph.
        # No solutions.
        g = Graph()
        g.addEdge(Vertex('u1', 'A'), Vertex('u2', 'B'))
        lhs = Graph()
        lhs.addEdge(Vertex('v1', 'C'), Vertex('v1', 'D'))
        rhs = Graph()
        p1 = Production(lhs, rhs)
        gen = Generator()
        self.assertEquals( len(gen._findMatchingProductions(g, [p1])), 0)        

        # One matching production, a simple vertex "A".
        g = Graph()
        g.addEdge(Vertex('u1', 'A'), Vertex('u2', 'B'))
        lhs = Graph()
        lhs.addVertex(Vertex('u1', 'A'))
        rhs = Graph()
        p1 = Production(lhs, rhs)
        self.assertEquals( len(gen._findMatchingProductions(g, [p1])), 1)

        # Two matching productions.
        g = Graph()
        g.addEdge(Vertex('u1', 'A'), Vertex('u2', 'B'))
        lhs = Graph()
        lhs.addVertex(Vertex('u1', 'A'))
        rhs = Graph()
        p1 = Production(lhs, rhs)
        p2 = Production(lhs, rhs)
        self.assertEquals( len(gen._findMatchingProductions(g, [p1, p2])), 2)
        
    #--------------------------------------------------------------------------
    def testMapRHSToGraph(self):
        # No vertices in rhs. Mapping returned is empty.
        g = Graph()
        lhs = Graph()
        rhs = Graph()
        p = Production(lhs, rhs)
        gen = Generator()
        rhsMapping = gen._mapRHSToGraph(g, p, {})
        self.assertEqual(len(rhsMapping), 0)

        # rhs has vertex r1, but it doesn't appear in the lhs. Mapping returned
        # is empty.
        rhs.addVertex(Vertex('r1', 'A'))
        rhsMapping = gen._mapRHSToGraph(g, p, {})
        self.assertEqual(len(rhsMapping), 0)

        # rhs vertex r1 also appears in lhs as l1, which is mapped to g1. 
        # r1 should appear in rhsMapping mapped to g1.
        lhs.addVertex(Vertex('l1', 'A'))
        rhsMapping = gen._mapRHSToGraph(g, p, {'l1':'g1'})
        self.assertEqual(len(rhsMapping), 1)
        self.assertIn('r1', rhsMapping)
        self.assertEqual(rhsMapping['r1'], 'g1')







    #--------------------------------------------------------------------------
# TODO
    def XXXtestApplyProductions(self):
        # Test applyProductions(self, startGraph, productions, config):
        self.assertTrue(True)

   #--------------------------------------------------------------------------
    def XXXtestApplyProduction_NoChange(self):
        # Check that if no changes are specified, no changes are made.

        # Basic graph with one vertex A.
        graph = Graph()
        graph.addVertex(Vertex('v1', 'A'))

        # Simple production A ==> A.
        lhs = Graph()
        lhs.addVertex(Vertex('u1', 'A'))
        rhs = Graph()
        rhs.addVertex(Vertex('u1', 'A'))
        production = Production(lhs, rhs)
        
        lhsMapping = {'u1':'v1'}
        rhsMapping = {'u1':'v1'}

        # Applying the production should produce no change.
        gen = Generator()
        gen._applyProduction(graph, production, lhsMapping)
        self.assertEquals(graph.numVertices, 1)
        
    #--------------------------------------------------------------------------
# TODO
    def XXXtestApplyProduction(self):
        # Test complex change: add/delete edges, add/delete vertices.

        self.assertTrue(True)
 
      
    #--------------------------------------------------------------------------
    def XXXtestDeleteMissingVertices(self):
        # Test deleteMissingVertices(graph, production, lhsMapping)

        # Build a graph A->B
        graph = Graph()
        graph.addEdge(Vertex('v0', 'A'), Vertex('v1', 'B'))
   
        # Simple production A->B ==> A
        lhs = Graph()
        lhs.addEdge(Vertex('u0', 'A'), Vertex('u1', 'B'))
        rhs = Graph()
        rhs.addVertex(Vertex('u0', 'A'))
        production = Production(lhs, rhs)
        
        lhsMapping = {'u0':'v0','u1':'v1'}  # normally created by Graph.search()

        self.assertEqual(len(graph.vertices), 2)
        gen = Generator()
        gen._deleteMissingVertices(graph, production, lhsMapping)
        self.assertEqual(len(graph.vertices), 1)
        self.assertTrue('v1' not in graph.vertices)

# debug, info, warning, error and critical
if __name__ == '__main__':
	logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
	unittest.main()
# vim:nowrap
