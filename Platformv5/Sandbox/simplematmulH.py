import random
import sys
from datetime import datetime
random.seed(datetime.now())
import re
import ast
from random import randrange
import os

#print((sys.argv[1]))
file_path = sys.argv[1]
if str(sys.argv[1]) == "chooseRandom":
    sqdim = randrange(1,100)
    coldim = randrange(1,100)
    rowdim = sqdim
    #print("file_path",file_path)
    #ulim = int(sys.argv[1])
    #file_path = "SuperBreakdown.txt"

    matrix1 = [[randrange(1,10) for i in range(sqdim)] for j in range(sqdim)]
    matrix2 = [[randrange(1,10) for i in range(coldim)] for j in range(rowdim)]
    matrix3 = [[ 0 for i in range(coldim)] for j in range(sqdim)]

    for i in range(sqdim):
        for j in range(coldim):
            val =[[]]
            for k in range(rowdim):         
                    matrix3[i][j] += matrix1[i][k] * matrix2[k][j]        


    
    print(matrix3)
    print("Finished matmul")

elif str(sys.argv[1]) == "choose_A_Random_B_Sandbox":
   # print("hdgfjhsdg")
    mlist = os.listdir("/home/harshini/CloudPlatform/Platformv5/Sandbox/MatrixB")
    r = randrange(0,(len(mlist)))
    #print(mlist[r])
    file1 = open("/home/harshini/CloudPlatform/Platformv5/Sandbox/MatrixB/" + mlist[r], 'r')
    Lines = file1.readlines() 
    count = 0
    # Strips the newline character
    for line in Lines:         
            matrix2 = ast.literal_eval(line)
            
             #Converting string to list of strings


    i=0
    while i<len(matrix2):   #Converting each string element to integer for m1
        j=0
        while j < len(matrix2[0]):
            matrix2[i][j] = int(matrix2[i][j],16)
            j+=1
        i+=1
    sqdim = len(matrix2)
    #print(sqdim, len(matrix2), len(matrix2[0]))
    matrix1 = [[randrange(1,10) for i in range(sqdim)] for j in range(sqdim)]

    matrix3 = [[ 0 for i in range(len(matrix2[0]))] for j in range(len(matrix1))]

    

    for i in range(len(matrix1)):
        r = []
        for j in range(len(matrix2[0])):
            val =[[]]
            for k in range(len(matrix2)):       
                    matrix3[i][j] += matrix1[i][k] * matrix2[k][j]
            r.append(val)
         
   #print("matrix3", len(matrix3), len(matrix3[0]))
    print(matrix3)
    print("Finished matmul")
 #   print("Finished matmul")

elif str(sys.argv[1]) == "choosefromdisk":
    file_path = sys.argv[2]   
    sqdim = int(sys.argv[3])
    rand1 = int(sys.argv[4])
    rand2 = int(sys.argv[5])
    file = open(file_path,"r")
    Counter = 0
    
    # Reading from file
    Content = file.read()
    CoList = Content.split("\n")
    
    for i in CoList:
        if i:
            Counter += 1 #No. of lines in the files -- To count the number of matrices present in the file

    rand = randrange(1,Counter+1) #Choosing a random line 
    #print(rand)
    file1 = open(file_path, 'r')
    Lines = file1.readlines() 
    count = 0
    # Strips the newline character
    for line in Lines:
        count += 1
        if count == rand:  
           # print(line)          
            res = ast.literal_eval(line) #Converting string to list of strings

    i=0
    while i<len(res):   #Converting each string element to integer for m1
        j=0
        while j < len(res[0]):
            res[i][j] = int(res[i][j],16)
            j+=1
        i+=1

    row_matrix_dim = sqdim #randomly choosing either of the dimensions of m1 and making m2 as square matrix
    col_matrix_dim = randrange(rand1, rand2) #randomly choosing either of the dimensions of m1 and making m2 as square matrix
    m1 = res
    m2 = []
    for i in range(0, row_matrix_dim):  #initilizing values to the rect matrix (m2) Randomly
        m2.append([])
        for j in range(0,col_matrix_dim):
            m2[i].append(int(random.randrange(1,10)))
    matrix3 = [[0 for i in range(col_matrix_dim)] for j in range(row_matrix_dim)]

    for i in range(len(m1)):
        r = []
        for j in range(len(m2[0])):
            val =[[]]
            for k in range(len(m2)):       
                    matrix3[i][j] += m1[i][k] * m2[k][j]
            r.append(val)
    print(matrix3)
    print("Finished matmul")
