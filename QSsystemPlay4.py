# -*- coding: utf-8 -*-
"""
Created on Thu Jul 16 23:00:17 2015
restrict vocabulary only to the presented facts
work on yes no
@author: rtwik
"""

from pyNN import nest as sim
import numpy
import pylab as plt
import speechRecog as spr

def getSpikeData(InputRaw,InputLabel):
    data =[]
    sptList= []
    c=0
    
    typ = type(InputRaw) is dict
    if typ == 1:      
        for i in InputLabel:
            data.append(InputRaw[i].get_data().segments[0])    
            sptList.append(numpy.array(data[c].spiketrains))
            c=c+1

    c=0
    typ = type(InputRaw) is list
    if typ == 1:      
        for i in InputRaw:
            data.append(i.get_data().segments[0])    
            sptList.append(numpy.array(data[c].spiketrains))
            c=c+1
            
    return sptList

def getFiring_activity(spt,nNeu,length):
    bins = length/10
    h = numpy.zeros([nNeu,bins])
            
    for r in range(nNeu):
        h[r,:] = numpy.histogram(numpy.array(spt[r]),bins=bins,range = [0,length])[0]
        times = numpy.histogram(numpy.array(spt[r]),bins=bins,range = [0,length])[1]
            
    hsump = numpy.sum(h,0)/nNeu
    return hsump,times
    
def CreateRandomMatrix(nNeuX,nNeuY,p,seed,selfcon):    
    '''
    nNeuX: nu,ner of neurons input population
    '''
    
    import itertools
    
    indexX = numpy.arange(0,nNeuX,1)
    indexY = numpy.arange(0,nNeuY,1)
    indexXY = list(itertools.product(indexX,indexY))
    
    if selfcon==0:
        for i in indexXY:
            if i[0]==i[1]:
                indexXY.remove(i)

    numpy.random.seed(seed)
    numpy.random.shuffle(indexXY)
    
    indexXYp = indexXY[0:int(nNeuX*nNeuY*p)]
    
    return indexXYp

def AssociateCAs(Ip,Lexicon,LexSem,Sem,Syn,stdp_paramsLS,spks):
    words = []
    for i in Ip.split():
        if i in Lexicon and LexSem[i] != 'function':
            words.append(i)
            Syn[i+LexSem[i]]=sim.Projection(Lexicon[i],Sem[LexSem[i]],sim.AllToAllConnector(),stdp_params[0])
            Syn[LexSem[i]+i]=sim.Projection(Sem[LexSem[i]],Lexicon[i],sim.AllToAllConnector(),stdp_params[0])
    
       
    for i in range(len(words)-1):
        for j in range(1,len(words)):
            if words[i] in Lexicon and words[j] in Lexicon:
                if LexSem[words[i]] != 'function' and LexSem[words[j]] != 'function':  
                    stdpval=stdp_params[1]
                if LexSem[words[i]] == 'function' or LexSem[words[j]] == 'function':
                    stdpval=stdp_params[2]
                 
                Syn[words[i]+words[j]]=sim.Projection(Lexicon[words[i]],Lexicon[words[j]],sim.AllToAllConnector(),stdpval)
                Syn[words[j]+words[i]]=sim.Projection(Lexicon[words[j]],Lexicon[words[i]],sim.AllToAllConnector(),stdpval)
    
    for i in range(len(words)):    
        drS=sim.Population(1,sim.SpikeSourceArray(spike_times=numpy.arange(spks[0],spks[1],spks[2])))
        sim.Projection(drS,Sem[LexSem[words[i]]],sim.AllToAllConnector(),sim.StaticSynapse(weight=1.0))    
        
        drL=sim.Population(1,sim.SpikeSourceArray(spike_times=numpy.arange(spks[0],spks[1],spks[2])))
        sim.Projection(drL,Lexicon[words[i]],sim.AllToAllConnector(),sim.StaticSynapse(weight=1.0))    
    
def AskQs(Ip,Lexicon,Sem,nNeu,spks):
    q=Ip.split()[0]     
    Lexicon[q] = sim.Population(nNeu,sim.IF_cond_exp(**cell_params1),label=q)
    Syn[q+QsSem[q]]=sim.Projection(Lexicon[q],Sem[QsSem[q]],sim.AllToAllConnector(),sim.StaticSynapse(weight=0.5))
    lex.append(q)
    Lexicon[q].record('spikes')

    
    for i in Ip.split():
        if i in Lexicon:        
            drQ=sim.Population(1,sim.SpikeSourceArray(spike_times=numpy.arange(spks[0],spks[1],spks[2])))
            sim.Projection(drQ,Lexicon[i],sim.AllToAllConnector(),sim.StaticSynapse(weight=1.0))    
        
#def getAns(Lexicon,lex,LexSem,Sem,S,nNeu,IpQ,spksQ):
#    sptListLex = getSpikeData(Lexicon,lex)
#    sptListSem = getSpikeData(Sem,S)
#    falex=[]
#    c=0
#    ans = []
#    for i in range(len(Lexicon)):
#        fa,t = getFiring_activity(sptListLex[i],nNeu)
#        falex.append([fa,t])
#        
#        ansIndx = numpy.where(t==spksQ[i])
#        if numpy.max(fa[ansIndx[0]:])>0 and LexSem[lex[c]] != 'question' and lex[c] not in IpQ[j].split():
#            ans.append(lex[c])
#            print 'mean', numpy.mean(fa[ansIndx[0]:])                
#        c=c+1
#    print 'Answer:', ans 

IpF = []  
IpQ =[]
nFacts=4
nQs =3


for i in range(nFacts):
    IpF.append(raw_input('Fact'+str(i+1)+':').lower())


#IpF = ['bob is in italy','bob has a ball','alice is in india']
#IpQ = ['where is ball','where is the ball','who is in india']

#for i in range(nFacts):
#    IpF.append(spr.TakeCommand('Fact'))
#
#for i in range(nQs):
#    x= spr.TakeCommand('Question').lower()
#    if 'is' in x.split()[0]:
#       x=x.replace('is','Is')    
#    IpQ.append(x)
#    


sim.setup(timestep=0.1, min_delay=0.1, max_delay=10.0)

nNeu=10

cell_params1 = {'tau_refrac': 5.0, 'cm': 1.0, 'tau_syn_E': 5.0, 'v_rest': -65.0, 'tau_syn_I': 5.0, 
                'tau_m': 20.0, 'e_rev_E': 0.0, 'i_offset': 0.0, 'e_rev_I': -70.0, 'v_thresh': -55,
                'v_reset': -65.0}

stdp_paramsLS = sim.STDPMechanism(
                timing_dependence=sim.SpikePairRule(tau_plus=20, tau_minus=20,
                                                    A_plus=0.011, A_minus=0.1),
                weight_dependence=sim.MultiplicativeWeightDependence(w_min=0, w_max=0.008),
                weight=0.00000005,
                delay=1.0)

stdp_paramsLL = sim.STDPMechanism(
                timing_dependence=sim.SpikePairRule(tau_plus=20, tau_minus=20,
                                                    A_plus=0.011, A_minus=0.1),
                weight_dependence=sim.MultiplicativeWeightDependence(w_min=0, w_max=0.01),
                weight=0.00000005,
                delay=1.0)

stdp_paramsLF = sim.STDPMechanism(
                timing_dependence=sim.SpikePairRule(tau_plus=20, tau_minus=20,
                                                    A_plus=0.011, A_minus=0.1),
                weight_dependence=sim.MultiplicativeWeightDependence(w_min=0, w_max=0.002),
                weight=0.00000005,
                delay=1.0)
                
stdp_params = [stdp_paramsLS,stdp_paramsLL,stdp_paramsLF]  
             
S = ['person','location','object','question','time','exist','function']
P = [0,'john','mary','bob','alice']
L = [1,'kitchen','lab','mumbai','telluride']
O = [2,'ball','apple','hat','cup']
Q = [3,'who','where','what','when','Is','does']
T = [4,'monday','tuesday','wednesday','thursday','friday','saturday','sunday']
V = [5,'is','has']
F = [6,'yes','in','a','an','with','on','the']

#lex = Q[1:]+P[1:]+L[1:]+O[1:]+T[1:]+V[1:]

lex = []
for i in IpF:
    for j in i.split():
        if j == 'none':
            continue
        if j not in lex:
            lex.append(j)


Lexicon={}
for i in lex:
    Lexicon[i] = sim.Population(nNeu,sim.IF_cond_exp(**cell_params1),label=i)

Sem = {}
for i in S:
    Sem[i] = sim.Population(nNeu,sim.IF_cond_exp(**cell_params1),label=i)

Function = {}
for i in F[1:]:
    Function[i] = sim.Population(nNeu,sim.IF_cond_exp(**cell_params1),label=i)

LexSem = {}
LexCat=[Q,P,L,O,T,V,F]

for j in LexCat:
    for i in range(1,len(j)):
        LexSem[j[i]] = S[j[0]]
 
Syn = {}
spksF = 10.0
dur = 200
for i in range(nFacts):
    spks1=[(i*(dur+200))+spksF,(i*(dur+200))+spksF+dur,2]
    AssociateCAs(IpF[i],Lexicon,LexSem,Sem,Syn,stdp_params,spks1)



QsSem = {}
S1=['person','location','object','time','exist','exist']
for i in range(len(Q)-1):
    QsSem[Q[i+1]]=S1[i]
    #print(Q[i+1],S1[i])

if 'is' in Lexicon:
    sim.Projection(Lexicon['is'],Function['yes'],sim.AllToAllConnector(),sim.StaticSynapse(weight=0.0025))    
if 'has' in Lexicon:
    sim.Projection(Lexicon['has'],Function['yes'],sim.AllToAllConnector(),sim.StaticSynapse(weight=0.0025))    


    

#length = tQs + nQs*400

for i in Lexicon:
    Lexicon[i].record('spikes')
for i in Sem:
    Sem[i].record('spikes')
for i in Function:
    Function[i].record('spikes')


for i in range(nQs):
    x= raw_input('Question'+str(i+1)+':').lower()
    if 'is' in x.split()[0]:
       x=x.replace('is','Is')    
    if 'is' in x.split():
        x=x.replace('is','')
    IpQ.append(x)
    
    tQs = nFacts*(dur+200.0)
        
    spksQ=[(i*(dur+200))+tQs,(i*(dur+200))+tQs+dur,2]
    AskQs(IpQ[i],Lexicon,Sem,nNeu,spksQ)
    qstime=(i*(dur+200))+tQs
    length=(i*(dur+200))+tQs+dur+100
    sim.run_until(length)    
        


    wts = []
    wtsLabel=[]
    for j in Syn:
        wts.append(numpy.nan_to_num(Syn[j].getWeights(format='array')))
        wtsLabel.append(j)
    
    sptListLex = getSpikeData(Lexicon,lex)
    sptListSem = getSpikeData(Sem,S)
    sptListFun = getSpikeData(Function,F[1:])
    
    falex=[]
    c=0
    ans = numpy.zeros((1,2),dtype='S50')
    for j in range(len(Lexicon)):
        fa,t = getFiring_activity(sptListLex[j],nNeu,length)
        falex.append([fa,t])    
                
        ansIndx1 = numpy.where(t==qstime)[0][0]
        ansIndx2 = numpy.where(t==qstime+dur+50)[0][0]
        if numpy.max(fa[ansIndx1:ansIndx2])>0 and LexSem[lex[c]] != 'question' and lex[c] not in IpQ[i].split():
            ans[0,0]= ans[0,0] + lex[c] +' '         
            ans[0,1]= ans[0,1] + str(round(numpy.mean(fa[ansIndx1:ansIndx2]),3)) + ' '   
                                                
        c=c+1
    
    #AnsFA = numpy.nan_to_num(numpy.array(ansList[:,1],dtype=float))
    #answer = ansList[numpy.where(AnsFA==numpy.max(AnsFA)),0]
    
#    for j in range(nFacts):
#        print 'Fact' + str(i+1) +':',IpF[i]
#    for j in range(nQs):
#    print 'Question' + str(i+1) +':',IpQ[i]
#    print 'Answer Firing Rates:', ans
       
    
    #import pyttsx
    #e = pyttsx.init()
    #e.setProperty('rate', 100)
    #for i in ans:
    #    e.say(i)
    #e.runAndWait()
    
    
    fasem=[]
    for j in range(len(Sem)):
        fasem.append(getFiring_activity(sptListSem[j],nNeu,length))
    
        
    AnswerT=[]
    AnswerFr=[]
    AnswerFinal=[]
    if 'Is' in IpQ[i].split()[0] or 'does' in IpQ[i].split()[0]:
        fafun,t = getFiring_activity(sptListFun[0],nNeu,length)
        ansIndx1 = numpy.where(t==qstime)[0][0]
        ansIndx2 = numpy.where(t==qstime+dur+100)[0][0]
        yes= numpy.mean(fafun[ansIndx1:ansIndx2])
        if yes>0:
            print 'Yes'
        else: print 'No'
        
    else:
        c=0
        for j in ans[0][0].split():
            if LexSem[j]==QsSem[IpQ[i].split()[0]]:
                AnswerT.append(j)
                AnswerFr.append(map(float,ans[0][1].split())[c])
            c=c+1

    ansList = numpy.zeros((len(AnswerT),),dtype=('a50,f1'))
    for k in range(len(AnswerT)):
        if (LexSem[AnswerT[k]] != 'time' or LexSem[AnswerT[k]] != 'location') and abs(AnswerFr[k]-numpy.max(AnswerFr)) <0.07:
            AnswerFinal.append(AnswerT[k])
        elif AnswerFr[k]==numpy.max(AnswerFr):
            AnswerFinal.append(AnswerT[k])
        ansList[k][0]=AnswerT[k]
        ansList[k][1]=numpy.round(AnswerFr[k],3)        
    #if len(AnswerFinal)>0: print AnswerFinal

    x=numpy.sort(ansList,order='f1')
    for k in x[::-1]:
        print k[0],numpy.round(k[1],3)
    
sim.end()

c=0
fg1 = plt.figure(1)
fg1.clear()
maxy=0
for i in falex:
    ax1 = fg1.add_subplot(6,5,c+1)
    ax1.plot(i[1][1:],i[0])
    ax1.text(3,0,lex[c],fontsize=15)
    ax1.set_xlim(-0.1,length)
    ax1.set_ylim(-0.1,3.0)
    c=c+1
    for tick in ax1.xaxis.get_major_ticks():
                tick.label.set_fontsize(8) 
    for tick in ax1.yaxis.get_major_ticks():
                tick.label.set_fontsize(10) 
fg1.show()



c=0
fg2 = plt.figure(2)
fg2.clear()
maxy=0
for i in fasem:
    ax2 = fg2.add_subplot(5,5,c+1)
    ax2.plot(i[1][1:],i[0])
    ax2.text(3,0,S[c],fontsize=15)
    ax2.set_xlim(-0.1,length)
    ax2.set_ylim(-0.1,3.0)
    c=c+1   
fg2.show()

c=0
fg3 = plt.figure(3)
fg3.clear()
nsp = int(numpy.ceil(numpy.sqrt(len(wts))))
for i in wts:
    ax3 = fg3.add_subplot(nsp,nsp,c+1)
    im=ax3.pcolormesh(i,cmap='jet',norm=plt.Normalize(vmin=0,vmax=0.005,clip=False))
    ax3.set_title(wtsLabel[c])
    c=c+1 
fg3.colorbar(im)
fg3.show()

