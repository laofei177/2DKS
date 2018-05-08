# Code créé par Gabriel Taillon le 7 Mai 2018
#  Test bench for the 2D Kolmogorov-Smyrnov Test.
import sys, os, numpy as np, scipy.stats
import matplotlib.pyplot as plt
Scriptpath=os.path.dirname(os.path.abspath(__file__)) # Path of this script
Path2Res=os.path.join(Scriptpath,os.path.splitext(os.path.basename(__file__))[0])
if not os.path.exists(Path2Res): os.makedirs(Path2Res)

def CountQuads(Arr2D,point,silent=1,plotcheck=0):
    # Counts the number of points of Arr2D in each 4 quadrant defined by a vertical and horizontal line crossing the point.
    # A bit of checking. if Arr2D and point are not lists or ndarray, exit.
    if isinstance(point, list):
        if not silent: print('point is a list')
        pass
    elif type(point).__module__+type(point).__name__=='numpyndarray':
        point=np.ravel(point.copy())
        if not silent: print('point is a numpy.ndarray')
    else:
        if not silent: print('point is neither a list not a numpy.ndarray. Exiting.')
        return
        
    if isinstance(Arr2D, list):
        if not silent: print('Arr2D is a list')
        Arr2D=np.asarray((Arr2D))
    elif type(Arr2D).__module__+type(Arr2D).__name__=='numpyndarray':
        if not silent: print('Arr2D is a ndarray')
    else:
        if not silent: print('Arr2D is neither a list not a numpy.ndarray. Exiting.')
        return
    if Arr2D.shape[1]>Arr2D.shape[0]:
        Arr2D=Arr2D.copy().T
    
    # The pp of Qpp refer to p for 'positive' and m for 'negative' quadrants. In order. first subscript is x, second is y.
    Qpp=Arr2D[(Arr2D[:,0]>=point[0])&(Arr2D[:,1]>=point[1]),:]
    Qmp=Arr2D[(Arr2D[:,0]<=point[0])&(Arr2D[:,1]>=point[1]),:]
    Qpm=Arr2D[(Arr2D[:,0]>=point[0])&(Arr2D[:,1]<=point[1]),:]
    Qmm=Arr2D[(Arr2D[:,0]<=point[0])&(Arr2D[:,1]<=point[1]),:]
    if not silent: print('Same number of points in Arr2D as in all Quadrants: '+str((len(Qpp)+len(Qmp)+len(Qpm)+len(Qmm))==len(Arr2D)))
    if plotcheck:
        plt.plot(Arr2D[:,0],Arr2D[:,1],'.k')
        plt.savefig(os.path.join(Path2Res,'QuadCheckArr2D.png'), bbox_inches='tight',dpi=500, edgecolor='w')
        plt.plot(Qpp[:,0],Qpp[:,1],'.b')
        plt.plot(Qmp[:,0],Qmp[:,1],'.g')
        plt.plot(Qpm[:,0],Qpm[:,1],'.c')
        plt.plot(Qmm[:,0],Qmm[:,1],'.y')
        plt.plot(point[0],point[1],'.r')
        plt.savefig(os.path.join(Path2Res,'QuadCheck.png'), bbox_inches='tight',dpi=500, edgecolor='w')
        plt.close('all')
    # Normalized fractions:
    ff=1./len(Arr2D)
    fpp=len(Qpp)*ff
    fmp=len(Qmp)*ff
    fpm=len(Qpm)*ff
    fmm=len(Qmm)*ff
    return(fpp,fmp,fpm,fmm)
    
def Qks(alam,iter=101,prec=1e-6):
    # Computes the value of the KS probability function. Complicated. 
    # From Numerical recipes in C page 623: '[...] the K–S statistic useful is that its distribution in the case of the null hypothesis (data sets drawn from the same distribution) can be calculated, at least to useful approximation, thus giving the significance of any observed nonzero value of D.' (D being thet maximum value of the absolute difference between two cumulative distribution functions)
    toadd=[1]
    qks=0.
    j=1
    while (j<iter) & (abs(toadd[-1])>prec):
        toadd.append(2.*(-1.)**(j-1.)*np.exp(-2.*j**2.*alam**2.))
        qks+=toadd[-1]
        j+=1
    if j==iter:
        return(1.0)
    return(qks)

def ks2d2s(Arr2D1,Arr2D2):
    # ks2d2s: ks stands for Kolmogorov-smirnov, 2dfor  2 dimensional, 2s for 2 samples.
    # Executes the KS test for goodness-of-fit on two samples in a 2D plane: tests if the hypothesis that the two samples are from the same distribution can be rejected.
    d1,d2=0.,0.
    for point1 in Arr2D1:
        fpp1,fmp1,fpm1,fmm1=CountQuads(Arr2D1,point1)
        fpp2,fmp2,fpm2,fmm2=CountQuads(Arr2D2,point1)
        d1=max(d1,abs(fpp1-fpp2))
        d1=max(d1,abs(fpm1-fpm2))
        d1=max(d1,abs(fmp1-fmp2))
        d1=max(d1,abs(fmm1-fmm2))
    for point2 in Arr2D2:
        fpp1,fmp1,fpm1,fmm1=CountQuads(Arr2D1,point2)
        fpp2,fmp2,fpm2,fmm2=CountQuads(Arr2D2,point2)
        d2=max(d2,abs(fpp1-fpp2))
        d2=max(d2,abs(fpm1-fpm2))
        d2=max(d2,abs(fmp1-fmp2))
        d2=max(d2,abs(fmm1-fmm2))
    d=(d1+d2)/2.
    sqen=np.sqrt(len(Arr2D1)*len(Arr2D2)/(len(Arr2D1)+len(Arr2D2)))
    R1=scipy.stats.pearsonr(Arr2D1[:,0],Arr2D1[:,1])[0]
    R2=scipy.stats.pearsonr(Arr2D2[:,0],Arr2D2[:,1])[0]
    RR=np.sqrt(1.-(R1*R1+R2*R2)/2.)
    prob=Qks(d*sqen/(1.+RR*(0.25-0.75/sqen)))
    # d and prob significance: if d is lowe than you significance level, cannot reject the hypothesis that the 2 datasets come form the same functions. Higher prob is better. From numerical recipes in C: When the indicated probability is > 0.20, its value may not be accurate, but the implication that the data and model (or two data sets) are not significantly different is certainly correct.
    return(d,prob)
 
# Making phony data: 
testdata1=np.random.uniform(size=(100,2))
testdata2=np.random.uniform(size=(100,2))
testdata3=np.random.uniform(0.2,0.5,size=(100,2))
testlist1=np.random.uniform(size=(100,2)).tolist()
testlist2=np.random.uniform(size=(100,2)).T.tolist()    
    
# Test list:
CountQuads(testdata1,[0.1,0.5]) 
CountQuads(testdata1,'a') 
CountQuads('1',[0.1,0.5]) 
CountQuads(testlist1,[0.1,0.5]) 
CountQuads(testlist2,[0.1,0.5]) 
# Test ndarray
CountQuads(testdata1,np.array([0.1,0.5])) 
CountQuads(testdata1.T,np.array([[0.1],[0.5]])) 
# Test Qks
print(Qks(0))
print(Qks(0.01))
print(Qks(0.1))
print(Qks(.5))
# Test the actual algo.
print(ks2d2s(testdata1,testdata2))
print(ks2d2s(testdata1,testdata3))