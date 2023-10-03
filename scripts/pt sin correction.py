# -*- coding: utf-8 -*-
"""
Created on Thu Dec  2 16:56:07 2021

@author: Invincible
"""
import time
import math

def path(A, B, x):
    f = A *math.sin(B*x)
    return f
    

def jt_correction(p, q, r, step_no):
    
    A = (p+q) # root or /2 or leave?
    
    B = math.pi / r
    
    step = r /step_no
    
    t = 0
    
    for i in range(step_no):
        
        x1 = step*i
        x2 = step*(i+1)
        y1 = path(A,B,x1)
        y2 = path(A,B,x2)
        delta_l = math.sqrt((y2-y1)**2 + (x2-x1)**2)
        t = t + delta_l
    
    return t
s1 = time.time()
test1 = jt_correction(5,7, 23, 100)

test2 = jt_correction(11,2, 50, 100)

test3 = jt_correction(0.2,0.3, 4, 100)

s1_e = time.time()
print('1:', s1_e-s1)

s2 = time.time()
test1_75 = jt_correction(5,7, 23, 75)

test2_75 = jt_correction(11,2, 50, 75)

test3_75 = jt_correction(0.2,0.3, 4, 75)
s2_e = time.time()
print('2:', s2_e-s2)

s3 = time.time()
test1_50 = jt_correction(5,7, 23, 50)

test2_50 = jt_correction(11,2, 50, 50)

test3_50 = jt_correction(0.2,0.3, 4, 50)
s3_e=time.time() 
print('3:', s3_e-s3)


s4=time.time()
test1_25 = jt_correction(5,7, 23, 25)

test2_25 = jt_correction(11,2, 50, 25)

test3_25 = jt_correction(0.2,0.3, 4, 25)
s4_e=time.time()
print('4:', s4_e-s4)


imports = '''
import math
'''

test1_code = '''
def path(A, B, x):
    f = A *math.sin(B*x)
    return f
    

def jt_correction(p, q, r, step_no):
    
    A = (p+q) # root or /2 or leave?
    
    B = math.pi / r
    
    step = r /step_no
    
    t = 0
    
    for i in range(step_no):
        
        x1 = step*i
        x2 = step*(i+1)
        y1 = path(A,B,x1)
        y2 = path(A,B,x2)
        delta_l = math.sqrt((y2-y1)**2 + (x2-x1)**2)
        t = t + delta_l
    
    return t
s1 = time.time()
test1 = jt_correction(5,7, 23, 100)

test2 = jt_correction(11,2, 50, 100)

test3 = jt_correction(0.2,0.3, 4, 100)

s1_e = time.time()
#print('1:', s1_e-s1)
'''

test2_code ='''
def path(A, B, x):
    f = A *math.sin(B*x)
    return f
    

def jt_correction(p, q, r, step_no):
    
    A = (p+q) # root or /2 or leave?
    
    B = math.pi / r
    
    step = r /step_no
    
    t = 0
    
    for i in range(step_no):
        
        x1 = step*i
        x2 = step*(i+1)
        y1 = path(A,B,x1)
        y2 = path(A,B,x2)
        delta_l = math.sqrt((y2-y1)**2 + (x2-x1)**2)
        t = t + delta_l
    
    return t

s2 = time.time()
test1_75 = jt_correction(5,7, 23, 75)

test2_75 = jt_correction(11,2, 50, 75)

test3_75 = jt_correction(0.2,0.3, 4, 75)
s2_e = time.time()
#print('2:', s2_e-s2)

'''

test3_code='''
def path(A, B, x):
    f = A *math.sin(B*x)
    return f
    

def jt_correction(p, q, r, step_no):
    
    A = (p+q) # root or /2 or leave?
    
    B = math.pi / r
    
    step = r /step_no
    
    t = 0
    
    for i in range(step_no):
        
        x1 = step*i
        x2 = step*(i+1)
        y1 = path(A,B,x1)
        y2 = path(A,B,x2)
        delta_l = math.sqrt((y2-y1)**2 + (x2-x1)**2)
        t = t + delta_l
    
    return t

s3 = time.time()
test1_50 = jt_correction(5,7, 23, 50)

test2_50 = jt_correction(11,2, 50, 50)

test3_50 = jt_correction(0.2,0.3, 4, 50)
s3_e=time.time() 
#print('3:', s3_e-s3)
'''

test4_code = '''

def path(A, B, x):
    f = A *math.sin(B*x)
    return f
    

def jt_correction(p, q, r, step_no):
    
    A = (p+q) # root or /2 or leave?
    
    B = math.pi / r
    
    step = r /step_no
    
    t = 0
    
    for i in range(step_no):
        
        x1 = step*i
        x2 = step*(i+1)
        y1 = path(A,B,x1)
        y2 = path(A,B,x2)
        delta_l = math.sqrt((y2-y1)**2 + (x2-x1)**2)
        t = t + delta_l
    
    return t

s4=time.time()
test1_25 = jt_correction(5,7, 23, 25)

test2_25 = jt_correction(11,2, 50, 25)

test3_25 = jt_correction(0.2,0.3, 4, 25)
s4_e=time.time()
#print('4:', s4_e-s4)

'''
import numpy as np 
import timeit 
print('starting1')
test1_time = np.array(timeit.repeat(stmt=test1_code, setup=imports, repeat=10)).mean()
print('test1:', test1_time)
test2_time = np.array(timeit.repeat(stmt=test2_code, setup=imports, repeat=10)).mean()
print('test2:', test2_time)
test3_time = np.array(timeit.repeat(stmt=test3_code, setup=imports, repeat=10)).mean()
print('test3:', test3_time)
test4_time = np.array(timeit.repeat(stmt=test4_code, setup=imports, repeat=10)).mean()
print('test4:', test4_time)


st = time.time()
test1=0 
test2=0 
test3=0 

reps = 2*500000
total = 0
import time
import math
from numpy import sin
for i in range(reps):


    st = time.time()
    def path(A, B, x):
        f = A *sin(B*x)
        return f
        

    def jt_correction(p, q, r, step_no):
        
        A = (p+q) # root or /2 or leave?
        
        B = math.pi / r
        
        step = r /step_no
        
        t = 0
        
        for i in range(step_no):
            
            x1 = step*i
            x2 = step*(i+1)
            y1 = path(A,B,x1)
            y2 = path(A,B,x2)
            delta_l = math.sqrt((y2-y1)**2 + (x2-x1)**2)
            t = t + delta_l
        
        return t

    test1 = jt_correction(5,7, 23, 25)

    #test2 = jt_correction(11,2, 50, 100)

    #test3 = jt_correction(0.2,0.3, 4, 100)

    s1_e = time.time()
    total+= (s1_e-st)


avg=total/reps
print('Average time(s) for:', reps, 'iterations is:', avg,'\nTotal tmie:', total)