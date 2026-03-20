<!---
Suits, Money Laundering, and Linear Programming
-->

Currently watching Suits with the family, and an interesting little puzzle came up in the show. In Season 1, episode 8, there is a situation with money laundering from one account to many smaller accounts.

So the set up is something like "transfer out 100 million", and then you have some number of smaller accounts that *sum to* 100 million.

When Lewis brought this up in the show, and Mike had a stack of papers to go through to identify the smaller accounts that summed up to the larger account, my son pointed out it would be too difficult to go through all of the permutations to figure it out. The total number of permutations would be something like:

    N = Sum(b(A choose k) for 1 to k)

Where A is the total number of accounts to look over, and k is the max number of potential accounts the money was spread around. `b(A choose k)` is my cheeky text format for binomial coefficients.

So this will be a very large number. 10,000 choose 4 for example is `416 416 712 497 500` -- over 416 trillion. You still need to add in `b(10,000 choose 2)` + `b(10,000 choose 3)` + ..... `b(10,000 choose k)`. With even a small number of accounts, the number of potential combinations will be very large.

But, I said in response to my son I could write a linear program to find them. And this is what this post shows, but doing so made me realize there are likely too many permutations in real data to make this a feasible approach in conducting fraud investigations. You will have many random permutations that add up to the same amount. (I figured *some* would happen, but it appears to me many happen in random data.) 

(Note I have not been involved with any financial fraud examinations in my time as an analyst, I would like to get a CFA time permitting, and if you want to work on projects let me know! So all that said, I cannot speak to the veracity of whether this is a real thing people do in fraud examinations.)

So here I use python and the pulp library (and its default open source CBC solver) to show how to write a linear program to pick bundles of accounts that add up to the right amount. First I simulate some lognormal data, and choose 4 accounts at random.

    import pulp
    import numpy as np
    
    # random values
    np.random.seed(10)
    simn = 10000
    x = np.round(np.exp(np.random.normal(loc=5.8,scale=1.2,size=simn)),2)
    
    # randomly pick 4
    slot = np.arange(0,simn)
    choice = np.random.choice(slot,size=4,replace=False)
    tot = x[choice].sum()
    print(tot,choice)

![](https://lh3.googleusercontent.com/pw/AP1GczNS_CTpqQlivXQx7jrX2tb61Gj1pOsNlzl5P6fFVVMvKJJ1LcadHBIADxBBABVtO69q9hXsGbF9uRmt5B9QguVYrdXDNvluf5rIYrSW1rdoV8Ne09tCE0xVFo3FyXGPiuWvHW8bQJvKgKuOHNts5K9z=w945-h436-s-no-gm?authuser=0)

So we are expecting the answer to be accounts `2756 5623 5255 873`, and the solution adds up to `1604.51`. So the linear program is pretty simple.

    # make a linear program
    P = pulp.LpProblem("Bundle",pulp.LpMinimize)
    D = pulp.LpVariable.dicts("D",slot,cat='Binary')
    
    # objective selects smallest group
    P += pulp.lpSum(D)
    
    # Constraint, equals the total
    P += pulp.lpSum(D[i]*x[i] for i in range(simn)) == tot
    
    # Solving with CBC
    P.solve()
    
    # Getting the solution
    res = []
    for i in range(simn):
        if D[i].varValue == 1:
            res.append(i)

In practice you will want to be careful with floating point (later I convert the account values to ints, another way though is instead of the equal constraint, make it `<= tot + eps` and `>= tot - eps`, where `eps = 0.001`. But for the CBC solver this ups the time to solve by quite a large amount.)

You could have an empty objective function (and I don't know the SAT solvers as much, I am sure you could use them to find feasible solutions). But here I have the solution by the minimal number of accounts to look for.

So here is the solution, as you can see it does not find our expected four accounts, but two accounts that also add up to `1604.51`.

![](https://lh3.googleusercontent.com/pw/AP1GczOsr9nhpOT6Ls7V8ULd0ZC-A0KqQ35H_8GHwN1QYMyHobhMstWBqnAH5Ou2LsxRfvrw3bFRNEJe3ot5OKapLMLXe6-bHJI8qQ_bNeZXZg1j_1nE3aZqQCIDOpDbnRof_as7KFGz90Xav0_7IYcrC_xU=w988-h457-s-no-gm?authuser=0)

You can see it solved it quite fast though, so maybe we can just go through all the potential feasible solutions. I like making a python class for this, that contains the "elimination" constraints to prevent that same solution from coming up again.

    # Doing elimination to see if we ever get the right set
    class Bundle:
        def __init__(self,x,tot,max_bundle=10):
            self.values = (x*100).astype('int')
            self.totn = len(x)
            self.tot = int(round(tot*100))
            self.pool = []
            self.max_bundle = max_bundle
            self.prob_init()
        def prob_init(self):
            P = pulp.LpProblem("Bundle",pulp.LpMinimize)
            D = pulp.LpVariable.dicts("D",list(range(self.totn)),cat='Binary')
            # objective selects smallest group
            P += pulp.lpSum(D)
            # Constraint, equals the total
            P += pulp.lpSum(D[i]*self.values[i] for i in range(simn)) == self.tot
            # Max bundle size constraint
            P += pulp.lpSum(D) <= self.max_bundle
            self.prob = P
            self.d = D
        def getsol(self,solver=pulp.PULP_CBC_CMD,solv_kwargs={'msg':False}):
            self.prob.solve(solver(**solv_kwargs))
            if self.prob.sol_status != -1:
                res = []
                for i in range(self.totn):
                    if self.d[i].varValue == 1:
                        res.append(i)
                res.sort()
                self.pool.append(res)
                # add in elimination constraints
                self.prob += pulp.lpSum(self.d[r] for r in res) <= len(res)-1
                return res
            else:
                return -1
        def loop_sol(self,n,solver=pulp.PULP_CBC_CMD,solv_kwargs={'msg':False}):
            for i in range(n):
                rf = self.getsol(solver,solv_kwargs)
                if rf != 1:
                    print(f'Solution {i}:{rf} sum: {self.values[rf].sum()}')
                if rf == -1:
                    print(f'No more solutions at {i}')
                    break

And now we can run through and see if the correct solution comes up:

    be = Bundle(x=x,tot=tot)
    be.loop_sol(n=10)

![](https://lh3.googleusercontent.com/pw/AP1GczNHVDzZw9EVfBBvYFF_ckG7OvF_CceDedHvBjQ0phyXUhcn1rH8ktXVlfcpHtyyQQhgFVtqSS0iT1V643kLg0knSOmBt1l_VBMR3Iw6PMgRaIWiMNwn108fj695qfNotgc2gSua59R8057u81H7IYfH=w959-h425-s-no-gm?authuser=0)

Uh oh -- I do not feel like seeing how many potential two solutions there are in the data (it is small enough I could just enumerate those directly). So lets put a constraint in that makes it so *it needs to be* four specific accounts that add up to the correct amount.

    # add in constraint it needs to be 4 selected
    choice.sort()
    be.prob += pulp.lpSum(be.d) == 4
    print(f'Should be {choice}')
    be.loop_sol(n=10)

![](https://lh3.googleusercontent.com/pw/AP1GczOv3WAYHSFNRbmoZTjUJCMCq51nqXr4wISB14H8sEAza7jW0KSOpvt8gWA5-ifSpFBgjOSl2a78WQsQBo6bIenlVBq0JPCPB9UP6sdYHNpVHhEzFpNizLK3Djl2YTn8m9V4gViDvX_PFI90z7ZdptYS=w754-h426-s-no-gm?authuser=0)

And still no dice. I could let this chug away all night and probably come up with the set I expected at some point. But if you have so many false positives, this will not be very useful from an investigative standpoint. So you would ultimately need more constraints.

Lets say our example the cumulative total will be quite large. Will that help limit the potential feasible solutions?

    # Select out a sample of high
    sel2 = np.random.choice(x[x > 5000],size=4,replace=False)
    tot2 = sel2.sum()
    ch2 = np.arange(simn)[np.isin(x,sel2)]
    ch2.sort()
    print(tot2,ch2)
    
    be2 = Bundle(x=x,tot=tot2)
    be2.loop_sol(n=20)

![](https://lh3.googleusercontent.com/pw/AP1GczOudOKbJxkh291tyj3V-7uB9-8mTzJ3tXuLHf0_ZDyXxGVLSMHZiIED7AHLy7KwN5S-l5XWjsRgYueGO5smmREqgP_tYHDCSBkWKiVl9jkdEnstEZFNfzbNuSW1RoOVjrs-Zd1FO8ifJsxsivbeAWwr=w937-h670-s-no-gm?authuser=0)

There are still too many potential feasible solutions. I thought maybe a problem with real data is that you will have fixed numbers, say you are looking at transactions, and you have specific $9.99 transactions. If one of those common transactions results in a total sum, it will just be replicated in the solution over and over again. I figured with random data the sum would still be quite unique, but I was wrong for that.

So I was write in that I could write a linear program to find the solution. I was wrong that there would only be one solution!