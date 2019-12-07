import SudokuBoard
import Variable
import Domain
import Trail
import Constraint
import ConstraintNetwork
import time
import random

class BTSolver:

    # ==================================================================
    # Constructors
    # ==================================================================

    def __init__ ( self, gb, trail, val_sh, var_sh, cc ):
        self.network = ConstraintNetwork.ConstraintNetwork(gb)
        self.hassolution = False
        self.gameboard = gb
        self.trail = trail

        self.varHeuristics = var_sh
        self.valHeuristics = val_sh
        self.cChecks = cc

    # ==================================================================
    # Consistency Checks
    # ==================================================================

    # Basic consistency check, no propagation done
    def assignmentsCheck ( self ):
        for c in self.network.getConstraints():
            if not c.isConsistent():
                return False
        return True

    """
        Part 1 TODO: Implement the Forward Checking Heuristic

        This function will do both Constraint Propagation and check
        the consistency of the network

        (1) If a variable is assigned then eliminate that value from
            the square's neighbors.

        Note: remember to trail.push variables before you assign them
        Return: a tuple of a dictionary and a bool. The dictionary contains all MODIFIED variables, mapped to their MODIFIED domain.
                The bool is true if assignment is consistent, false otherwise.
    """
    def forwardChecking ( self ):

        modified = dict()

        for v in self.network.variables:
            if v.isAssigned():
                for n in self.network.getNeighborsOfVariable(v):
                    if v.getAssignment() == n.getAssignment():
                        return ({},False)
                    if v.getAssignment() in n.getValues():
                        # trail.push variables before assign
                        self.trail.push(n)
                        # remove v from n's domain
                        n.removeValueFromDomain(v.getAssignment())
                        modified[n] = n.getDomain()
                        
                    if (n.size() == 0):
                        return ({},False)

        return (modified,True)


    # =================================================================
	# Arc Consistency
	# =================================================================

    def arcConsistency( self ):
        assignedVars = []
        for c in self.network.constraints:
            for v in c.vars:
                if v.isAssigned():
                    assignedVars.append(v)
        while len(assignedVars) != 0:
            av = assignedVars.pop(0)
            for neighbor in self.network.getNeighborsOfVariable(av):
                if neighbor.isChangeable and not neighbor.isAssigned() and neighbor.getDomain().contains(av.getAssignment()):
                    neighbor.removeValueFromDomain(av.getAssignment())
                    if neighbor.domain.size() == 1:
                        neighbor.assignValue(neighbor.domain.values[0])
                        assignedVars.append(neighbor)

    
    """
        Part 2 TODO: Implement both of Norvig's Heuristics

        This function will do both Constraint Propagation and check
        the consistency of the network

        (1) If a variable is assigned then eliminate that value from
            the square's neighbors.

        (2) If a constraint has only one possible place for a value
            then put the value there.

        Note: remember to trail.push variables before you assign them
        Return: a pair of a dictionary and a bool. The dictionary contains all variables 
		        that were ASSIGNED during the whole NorvigCheck propagation, and mapped to the values that they were assigned.
                The bool is true if assignment is consistent, false otherwise.
    """
    # def norvigCheck ( self ):
    #     return ({}, False)

    def norvigCheck ( self ):
        assigned = {}
        if not self.forwardChecking():
            return (assigned, False)

        for i in self.network.getConstraints():
            a={}
            for j in i.vars:
                for q in j.getValues():
                    if q not in a:
                        a[q]=1
                    else:
                        a[q]+=1
            for j in i.vars:
                for q in j.getValues():
                    if a[q]==1 and not j.isAssigned():
                        self.trail.push(j)
                        j.assignValue(q)
                        assigned[j] = q

        if not self.forwardChecking():
            return ({}, False)
        return (assigned, True)

    """
         Optional TODO: Implement your own advanced Constraint Propagation

         Completing the three tourn heuristic will automatically enter
         your program into a tournament.
     """
    def getTournCC ( self ):
        return False

    # ==================================================================
    # Variable Selectors
    # ==================================================================

    # Basic variable selector, returns first unassigned variable
    def getfirstUnassignedVariable ( self ):
        for v in self.network.variables:
            if not v.isAssigned():
                return v

        # Everything is assigned
        return None

    """
        Part 1 TODO: Implement the Minimum Remaining Value Heuristic

        Return: The unassigned variable with the smallest domain
    """
    def getMRV ( self ):

        # current Minimum Remaining Value
        min_MRV = float('inf')
        # current variable with Minimum Remaining Value
        v_minMRV = None

        for v in self.network.variables:
            if not v.isAssigned():
                if v.size() < min_MRV or not v_minMRV:
                    # update 
                    min_MRV = v.size()
                    v_minMRV = v

        return v_minMRV

    """
        Part 2 TODO: Implement the Degree Heuristic

        Return: The unassigned variable with the most unassigned neighbors
    """
    def getDegree ( self ):
        dhVariable = None
        maxUnassigned = -1
        
        for var in self.network.variables:
            if not var.isAssigned():
                cc = self.network.getConstraintsContainingVariable(var)
                degC = []
                for constraint in cc:
                    varsC = constraint.vars
                    for v2 in varsC:
                        if not v2.isAssigned():
                            degC.append(v2)
                if len(degC) > maxUnassigned:
                    dhVariable = var
                    maxUnassigned = len(degC)
                                
        return dhVariable
    """
        Part 2 TODO: Implement the Minimum Remaining Value Heuristic
                       with Degree Heuristic as a Tie Breaker

        Return: The unassigned variable with the smallest domain and affecting the  most unassigned neighbors.
                If there are multiple variables that have the same smallest domain with the same number of unassigned neighbors, add them to the list of Variables.
                If there is only one variable, return the list of size 1 containing that variable.
    """


    def MRVwithTieBreaker(self):
        temp = self.getfirstUnassignedVariable()

        if not temp:
            return []

        res = [temp]

        for v in self.network.getVariables():
            if v.isAssigned() == False:
                if v.size() < temp.size():
                    # new smallest domain
                    temp = v
                    res = [temp]
                elif v.size() == temp.size():
                    neighborsOfV = self.network.getNeighborsOfVariable(v)
                    degreeOfV = sum([1 for i in neighborsOfV if not i.isAssigned()])
                    neighborsOftemp = self.network.getNeighborsOfVariable(v)
                    degreeOftemp = sum([1 for i in neighborsOftemp if not i.isAssigned()])

                    if (degreeOfV > degreeOftemp):
                        # update new max affecting neis
                        temp = v
                        res = [temp]
                    elif (degreeOfV == degreeOftemp):
                        res.append(v)

        return res



    # test_MAD92 (test_MAD.Test_MAD) (0.0/1.0)
    # Test Failed: (1, 6) not found in [(2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6), (8, 2)] : Variable returned is incorrect. Returned (1, 6). Should be [(2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6), (8, 2)].


    """
         Optional TODO: Implement your own advanced Variable Heuristic

         Completing the three tourn heuristic will automatically enter
         your program into a tournament.
     """
    def getTournVar ( self ):
        return None

    # ==================================================================
    # Value Selectors
    # ==================================================================

    # Default Value Ordering
    def getValuesInOrder ( self, v ):
        values = v.domain.values
        return sorted( values )

    """
        Part 1 TODO: Implement the Least Constraining Value Heuristic

        The Least constraining value is the one that will knock the least
        values out of it's neighbors domain.

        Return: A list of v's domain sorted by the LCV heuristic
                The LCV is first and the MCV is last
    """
    def getValuesLCVOrder ( self, v ):

        # LCV[v] = # of values it can knock out from it's neighbors domain

        LCV = dict()

        if not v.isAssigned():
            for n1 in v.getValues():
                curr_CV = 0
                for n2 in self.network.getNeighborsOfVariable(v):
                    if n2.domain.contains(n1):
                        # if n1 in n2's domain
                        curr_CV+=1

                LCV[n1] = curr_CV

        return [key for key, _ in sorted(LCV.items(), key=lambda kv: kv[1])]

    """
         Optional TODO: Implement your own advanced Value Heuristic

         Completing the three tourn heuristic will automatically enter
         your program into a tournament.
     """
    def getTournVal ( self, v ):
        return None

    # ==================================================================
    # Engine Functions
    # ==================================================================

    def solve ( self ):
        if self.hassolution:
            return

        # Variable Selection
        v = self.selectNextVariable()

        # check if the assigment is complete
        if ( v == None ):
            for var in self.network.variables:

                # If all variables haven't been assigned
                if not var.isAssigned():
                    print ( "Error" )

            # Success
            self.hassolution = True
            return

        # Attempt to assign a value
        for i in self.getNextValues( v ):

            # Store place in trail and push variable's state on trail
            self.trail.placeTrailMarker()
            self.trail.push( v )

            # Assign the value
            v.assignValue( i )

            # Propagate constraints, check consistency, recurse
            if self.checkConsistency():
                self.solve()

            # If this assignment succeeded, return
            if self.hassolution:
                return

            # Otherwise backtrack
            self.trail.undo()

    def checkConsistency ( self ):
        if self.cChecks == "forwardChecking":
            return self.forwardChecking()[1]

        if self.cChecks == "norvigCheck":
            return self.norvigCheck()[1]

        if self.cChecks == "tournCC":
            return self.getTournCC()

        else:
            return self.assignmentsCheck()

    def selectNextVariable ( self ):
        if self.varHeuristics == "MinimumRemainingValue":
            return self.getMRV()

        if self.varHeuristics == "Degree":
            return self.getDegree()

        if self.varHeuristics == "MRVwithTieBreaker":
            return self.MRVwithTieBreaker()[0]

        if self.varHeuristics == "tournVar":
            return self.getTournVar()

        else:
            return self.getfirstUnassignedVariable()

    def getNextValues ( self, v ):
        if self.valHeuristics == "LeastConstrainingValue":
            return self.getValuesLCVOrder( v )

        if self.valHeuristics == "tournVal":
            return self.getTournVal( v )

        else:
            return self.getValuesInOrder( v )

    def getSolution ( self ):
        return self.network.toSudokuBoard(self.gameboard.p, self.gameboard.q)
