import numpy as np
import time
from numpy.linalg import inv
from scipy.optimize import newton
from scipy.linalg.blas import dgemm,sgemm,sgemv


def derivative_minim_sub(y_sub, X_sub, X_subT, G_selected, A_selc, subsample_size):
 def smaller_predproc_exponential(param):
  h = param
  C_inv = inv(h*G_selected+(1-h)*np.identity(subsample_size))
  C_invX = sgemm(alpha=1,a=C_inv,b=X_sub)
  beta = sgemm(alpha=1,a=inv(sgemm(alpha=1,a=X_subT.reshape(1,subsample_size),b=C_invX)),b=sgemm(alpha=1,a=C_invX,b=y_sub,trans_a=1))
  residual = (np.array(y_sub).reshape(subsample_size,1) - np.matmul(np.array(X_sub).reshape(subsample_size,1),beta))
  C_invResid = sgemm(alpha=1,a=C_inv,b=residual,trans_b=0)
  qf = sgemm(alpha=1,a=residual,b=C_invResid,trans_a=1)
  diff1 = np.sum(np.multiply(C_inv, A_selc))-subsample_size/qf*sgemm(alpha=1,a=C_invResid.T,b=sgemm(alpha=1,a=A_selc,b=C_invResid))
  #print(h)
  return(diff1)
 start_time = time.time()
 try:
  pc_minimizer_easy = newton(smaller_predproc_exponential,0.5,tol=0.0000001)
 except:
  pc_minimizer_easy=0
 if pc_minimizer_easy>1:
    pc_minimizer_easy = 1   
 if pc_minimizer_easy<0:
    pc_minimizer_easy = 0
 h = pc_minimizer_easy
 C_inv = inv(h*G_selected+(1-h)*np.identity(subsample_size))
 C_invX = sgemm(alpha=1,a=C_inv,b=X_sub)
 beta = sgemm(alpha=1,a=inv(sgemm(alpha=1, a=np.array(X_subT).reshape(1,subsample_size),b=C_invX)),b=sgemm(alpha=1,a=C_invX,b=y_sub,trans_a=1))
 residual = (np.array(y_sub).reshape(subsample_size,1) - np.matmul(np.array(X_sub).reshape(subsample_size,1),beta))
 C_invResid = sgemm(alpha=1,a=C_inv,b=residual,trans_b=0)
 sigma = sgemm(alpha=1,a=residual,b=C_invResid,trans_a=1)/subsample_size
 GRM_array_sub = sgemm(alpha=1,a=C_inv,b=A_selc) #V_pp^-1 A_ppc
 W = np.maximum(GRM_array_sub, GRM_array_sub.transpose() )
 a = np.sum(np.multiply(W,W))
 del C_inv; del W;
 sd_sub = np.sqrt(2/a)
 t1 = (time.time() - start_time)
 #result = np.hstack((np.asscalar(pc_minimizer_easy),np.asscalar(sd_sub),np.asscalar(sigma),t1))
 result = {'Heritability estimate':pc_minimizer_easy, 'SD of heritability estimate':sd_sub, 'Variance estimate':  sigma, 'Time taken':t1}
 return(result)


def derivative_minim_full(y, X, X_T, Ct, id_diag, add, G_selected, GRM_array, N):
 def der_predproc_exponential(param):
  h = param
  addedId = np.reshape((1-h)+ h*add,N)
  addedId_invU = np.multiply((1/addedId)[:,np.newaxis], Ct.T)
  CTadded_Id_invC = sgemm(alpha=1,a=Ct,b=addedId_invU)
  C_inv = (-sgemm(alpha=1,a=h*addedId_invU, b=sgemm(alpha=1,a=inv(G_selected+h*CTadded_Id_invC),b=addedId_invU.T)))
  np.fill_diagonal(C_inv,(1/addedId + C_inv[id_diag]))
  C_invX = sgemm(alpha=1,a=C_inv,b=X)
  beta = sgemm(alpha=1,a=inv(sgemm(alpha=1,a=X_T,b=C_invX)),b=sgemm(alpha=1,a=C_invX,b=y,trans_a=1))
  residual = (np.array(y).reshape(N,1) - np.matmul(X,beta)).T
  C_invResid = sgemm(alpha=1,a=C_inv,b=residual,trans_b=1)
  qf = sgemm(alpha=1,a=residual,b=C_invResid,trans_a=0)
  diff1 = np.sum(np.multiply(C_inv, GRM_array))-N/qf*sgemm(alpha=1,a=C_invResid.T,b=sgemm(alpha=1,a=GRM_array,b=C_invResid))
  del C_inv,addedId,addedId_invU,CTadded_Id_invC
  #print(h)
  return(diff1)
 start_time = time.time()
 pc_minimizer_f = newton(der_predproc_exponential,0.5,tol=0.000005)
 if pc_minimizer_f>1:
    pc_minimizer_f = 1   
 if pc_minimizer_f<0:
    pc_minimizer_f = 0
 h = pc_minimizer_f
 addedId = np.reshape((1-h)+ h*add,N)
 addedId_invU = np.multiply((1/addedId)[:,np.newaxis], Ct.T)
 CTadded_Id_invC = sgemm(alpha=1,a=Ct,b=addedId_invU)
 C_inv = (-sgemm(alpha=1,a=h*addedId_invU, b=sgemm(alpha=1,a=inv(G_selected+h*CTadded_Id_invC),b=addedId_invU.T)))
 np.fill_diagonal(C_inv,(1/addedId + C_inv[id_diag]))
 C_invX = sgemm(alpha=1,a=C_inv,b=X)
 beta = sgemm(alpha=1,a=inv(sgemm(alpha=1,a=X_T,b=C_invX)),b=sgemm(alpha=1,a=C_invX,b=y,trans_a=1))
 residual = (np.array(y).reshape(N,1) - np.matmul(X,beta)).T
 C_invResid = sgemm(alpha=1,a=C_inv,b=residual,trans_b=1)
 sigma = sgemm(alpha=1,a=residual,b=C_invResid,trans_a=0)/N
 GRM_array= sgemm(alpha=1,a=C_inv,b=GRM_array) #V_pp^-1 A_ppc
 W = np.maximum(GRM_array, GRM_array.transpose())
 a = np.sum(np.multiply(W,W))
 print(a)
 del C_inv;
 sd = np.sqrt(2/a)
 t1 = (time.time() - start_time)
 #result = np.hstack((np.asscalar(pc_minimizer_f),np.asscalar(sd),np.asscalar(sigma),t1))
 result = {'Heritability estimate':pc_minimizer_f, 'SD of heritability estimate':sd, 'Variance estimate':  sigma, 'Time taken':t1}
 return(result)