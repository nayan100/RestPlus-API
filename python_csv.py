
import csv 
  

filename = "student_records.csv"
 
fields = [] 
rows = [] 

counter=0
counter2=0

with open(filename, 'r') as csvfile: 
     
    csvreader = csv.reader(csvfile) 
       
    fields = next(csvreader) 
  
    
    for row in csvreader: 
        rows.append(row) 
  
C=0

topsubject=[0,0,0,0,0,0]
topsubnames=['','','','','','']
def subtotal(col,counter,counter2):
    global topsubject
    global topsubnames
    
    C=int(col)
    marks=topsubject[counter]
    name=topsubnames[counter]
    N=str(rows[counter2+1][0])
    
    if(marks<C):
        marks=C
        name=N
    elif(marks==C):
        marks=C
        name=name+' and '+N
    topsubject[counter]=marks
    topsubnames[counter]=name


topmarks=[0,0,0]
topnames=['','','']
def alltotal(sum,row):
    global topmarks
    t=topmarks[0]
    t1=topmarks[1]
    t2=topmarks[2]
    n=topnames[0]
    n1=topnames[1]
    n2=topnames[2]
    C=sum
    N=str(row[0])
    
    if(t2<C):
        if(t1<C):
            if(t<C):
                tem=t
                temN=n
                tem1=t1
                temN1=n1
                t=C
                n=N
                t1=tem
                n1=temN
                t2=tem1
                n2=temN1
            else:
                tem=t1
                temN=n1
                t1=C
                n1=N
                t2=tem
                n2=temN
        else:
            t2=C
            n2=N
    topmarks[0]=t
    topmarks[1]=t1
    topmarks[2]=t2
    topnames[0]=n
    topnames[1]=n1
    topnames[2]=n2   



for row in rows[1:]: 
    summarks=0
    counter=0
    for col in row[1:]:
        summarks=summarks+int(col)
        subtotal(int(col),counter,counter2)
        counter=counter+1
        
    alltotal(summarks,row) 
    counter2=counter2+1


# print('Maths:',topsubnames[0],':',topsubject[0],'\nBiology:',topsubnames[1],':',topsubject[1],'\nEnglish',topsubnames[2],':',topsubject[2],
# '\nPhysics',topsubnames[3],':',topsubject[3],'\nChemistry',topsubnames[3],':',topsubject[3],'\nHindi',topsubnames[5],':',topsubject[5]) 
# print('Toppers:',topnames[0],':',topmarks[0],'\n',topnames[1],':',topmarks[1],'\n',topnames[2],':',topmarks[2]) 


print('Topper in Maths is ',topsubnames[0],'\nTopper in Biology is ',topsubnames[1],
'\nTopper in English is ',topsubnames[2],'\nTopper in Physics is ',topsubnames[3],
'\nTopper in Chemistry is',topsubnames[3],'\nTopper in Hindi is ',topsubnames[5]) 
print('Best students in the class are:\n',topnames[0],' : Rank first','\n',topnames[1],' : Rank second',
'\n',topnames[2],': Rank third') 