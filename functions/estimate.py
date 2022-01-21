# import pandas as pd
import numpy as np
# =============================================================================
# import sys
# import os
# import psutil
# import scipy.sparse as sp
# import scipy.sparse.linalg
# import inspect
# from scipy.sparse import csr_matrix, rand
# from struct import unpack, calcsize
# from numpy.linalg import inv
# =============================================================================
# =============================================================================
# from numpy.linalg import multi_dot
# import timeit
# import logging
# import resource
# 
# =============================================================================
def AdjHE_estimator(A,y, npc=0, std=False, PCs = None):
    # remove identifiers form y for linear algebra 
    y = y.drop(["FID", "IID"], axis = 1)
    # If standardized AdjHE is chosen 
    if (std == True) :
        # Standardize the y
        std_y = (y-np.mean(y))/np.std(y)
        
        
        trA = np.sum(np.diag(A))
        trA2 = np.sum(np.multiply(A,A))
        n = A.shape[1]
        yay = np.dot(std_y.T, np.dot(A,std_y)).flatten()
        yty = np.dot(std_y.T, std_y).flatten()
        if (npc==0):
            denominator = trA2 - 2*trA + n
            nominator = n - trA + yay - yty
        else:
            pc = PCs
            s = np.diag(np.dot(pc.T,np.dot(A,pc)))
            b = s - 1
            c = np.dot(std_y.T, pc)**2 - 1
            denominator = trA2 - 2*trA + n - np.sum(b**2)
            nominator = n - trA + yay - yty - np.sum(b*c)
        h2 = nominator/denominator
        h2 = h2[0]
        var_ge = 2/denominator
        #    tau = n/nmarkers
        #    b1 = (1-np.sqrt(tau))**2
        #    b2 = (1+np.sqrt(tau))**2
        #    r = b2-b1
        #    a1 = h2-1
        #    a2 = 1-2*h2
        #    trace_A2_MP = 0.5*(r+2*b1)*n
        #    trace_A3_MP = (5/16*r**2+b1*b2)*n
        #    trace_A4_MP = (7*r**3+30*b1*r**2+48*b1**2*r+32*b1**3)/32*n
        #    if (npc==0):
        #    #    var_MP = 2/denominator
        #        var_ge = 2/denominator
        #    else:
        #        trace_A_MP = trA - np.sum(s)
        #        a = denominator
        #    #    var_MP=2/a**2*(h2**2*trace_A4_MP+(n-npc)*a1**2+(a2**2+2*h2*a1)*trace_A2_MP+2*a1*a2*trace_A_MP+2*h2*a2*trace_A3_MP)
        #        var_ge = 2/a

        
    else :
        
    # else we solve the unstandardized version
        trA2 = np.sum(np.multiply(A,A))
        trA = np.sum(np.diag(A))

        n = A.shape[1]
        yay = np.dot(y.T, np.dot(A,y)).flatten()
        yty = np.dot(y.T, y).flatten()
        tn = np.sum(y)**2/n # all 1s PC
        if (npc==0):
            sigg = n*yay - trA*yty
            sigg = sigg-yay+tn*trA # add 1's
            sige = trA2*yty - trA*yay
            sige = sige-tn*trA2 # add 1's
            denominator = trA2 - 2*trA + n
        else:
            # remove identifiers for linear algebra
            pc = PCs.drop(["FID", "IID"], axis = 1)
            pcA = np.dot(pc.T,A)
            pcApc = np.dot(pcA,pc)
            s = np.diag(pcApc) #pciApci
            b = s-1
            t = np.dot(y.transpose(),pc)**2 #ypcipciy
            a11 = trA2 - np.sum(s**2) 
            a12 = trA - np.sum(s)
            b1 = yay - np.sum(s*t)
            b2 = yty - np.sum(t)
            sigg = (n-npc)*b1 - a12*b2
            sigg = sigg.flatten() - yay.flatten() + tn * a12 # add 1's
            sige = a11*b2 - a12*b1
            sige = sige.flatten()-tn*a11 # add 1's
            denominator = trA2 - 2*trA + n - np.sum(b**2)
        h2 = sigg/(sigg+sige)
        h2 = h2[2]
        var_ge = 2/denominator
    return h2,np.sqrt(var_ge)

    