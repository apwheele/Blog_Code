def NormLeven(a,b):
    """Calculates the Levenshtein distance between strings a and b after removing trailing blanks.
    Returns a number or None."""
    a = a.rstrip()
    b = b.rstrip()
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a,b = b,a
        n,m = m,n        
    current = range(n+1)
    for i in range(1,m+1):
        previous, current = current, [i]+[0]*n
        for j in range(1,n+1):
            add, delete = previous[j]+1, current[j-1]+1
            change = previous[j-1]
            if a[j-1] != b[i-1]:
                change = change + 1
            current[j] = min(add, delete, change)
    minL = m - n  #normalization part      
    norm = (float(current[n]) - minL)/(m - minL)
    return norm

#Might consider Damerau - includes transpositions
#https://en.wikipedia.org/wiki/Damerau%E2%80%93Levenshtein_distance

#a1 = "ABCDEFG"
#a2 = "BCDZYX"
#l = NormLeven(a1,a2)
#print l

#date calculations, SPSS passes dates as seconds since along time ago
def dayDiff(a,b):
  sD = abs(b - a)
  res = sD/86400
  return int(res)


exc = [20,27,28,30,31,60,90]
def closeDate(a):
  if a < 11:
    res = 1
  elif a in exc:
    res = 1
  elif a > 1100:
    res = 0
  elif a > 354:
    mo = a % 365
    if mo < 10:
      res = 1
    elif 355 <= mo <= 364:
      res = 1
    else:
      res = 0
  else:
    res = 0 
  return res

#tes = [5,11,27,31,32,365,355,732,728,500]
#for i in tes:
#  print [i,closeDate(i)]

#needs to be close in birthdays, and needs to be close in name distance
#resulting function will take, [full name,dob]
def DistFun(d,s):
  dobDis = dayDiff(d[1],s[1])
  if dobDis == 0:
    sDis = NormLeven(d[0],s[0])
    if sDis < 0.1:
      t = 1
    else:
      t = 0
  elif closeDate(dobDis) == 1:
    sDis = NormLeven(d[0],s[0])
    if sDis < 0.05:
      t = 1
    else:
      t = 0
  else:
    t = 0
  return t


#test two vectors
#t1 = ['last, first',1000]
#t2 = ['last, first',1000]
#print DistFun(t1,t2)
