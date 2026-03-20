<!---
Reloading classes in python and shared borders
-->

For some housekeeping, if you are not signed up, also make sure to sign up for the RSS feed of my [crime de-coder blog](https://crimede-coder.com/blog). I have not been cross posting here consistently. For the last few posts:

 - [Using the SPPT to Monitor Changes in Crime](https://crimede-coder.com/blogposts/2025/SPPT) (soft launching my [crimepy](https://github.com/apwheele/crimepy) python package)
 - [Cost-benefit analysis of Gun Shot Detection Tech](https://crimede-coder.com/blogposts/2025/CostBenefitGSD) (this is a repost from the *Criminal Justician* series on the American Society of Evidence Based Policing)
 - [Using LLMs to Extract Data from Text](https://crimede-coder.com/blogposts/2025/StructuredOutputs)
 - [Finding outliers in proportions](https://crimede-coder.com/blogposts/2025/OutlierProportions)

![](https://raw.githubusercontent.com/apwheele/Blog_Code/refs/heads/master/Python/OutlierProportion/FunnelProportion.png)

For ASEBP, [conference submissions for 2026 are open](https://americansebp.org/page/annual-conference). (I will actually be going to this in 2026, submitted a 15 minute talk on [planning experiments](https://andrewpwheeler.com/2024/03/18/poisson-designs-and-minimum-detectable-effects/).)

Today will just be a quick post on two pieces of code I thought might be useful to share. The first is useful for humans, when testing code in functions, you can use the `importlib` library to *reload* functions. That is, imagine you have code:

    import crimepy as cpy
    
    test = cpy.func1(....)

And then when you run this, you see that `func1` has an error. You can edit the source code, and then run:

    from importlib import reload
    
    reload(cpy)
    test = cpy.func1(....)

This is my preferred approach to testing code. Note you need to import a library and reload the library. Not `from crimepy import *`, this will not work unfortunately.

Recently was testing out code that took quite a while to run, my [Patrol Districting](https://github.com/apwheele/crimepy/blob/main/notebooks/PatrolDistricts.ipynb). This is a class, and I was editing my methods to make maps. The code itself takes around 5 minutes to run it through when remaking the entire class. What I found was a simpler approach, I can dump out the file to pickle, then reload the library, then load the pickle object. The may the pickle module works, it pulls the method definition from the global environment (pickle just saves the dict items under the hood). So the code looked like this:

    from crimepy import pmed
    ...
    pmed12 = pmed.pmed(...)
    pmed12.map_plot() # causes error

And then instead of using the reload method as is (which would require me to create an entirely new object), use this approach for de-bugging:

    # save file
    import pickle
    with open('pmed12.pkl', 'wb') as file:
        # Dump data with highest protocol for best performance
        pickle.dump(pmed12, file)
    
    from importlib import reload
    # edit method
    reload(pmed)
    
    # reload the object
    with open('pmed12.pkl', 'rb') as file:
        # Load the pickled data
        pmed12_new = pickle.load(file)
    
    # retest the method
    pmed12_new.map_plot()

Writing code itself is often not the bottleneck -- testing is. So figuring out ways to iterate testing faster is often worth the effort (I might have saved a day or two of work if I did this approach sooner when debugging that code).

The second code snippet is useful for the machines; I have been having Claude help me write quite a bit of the crimepy work. Here was one though it was having trouble with -- calculating [the shared border length between two polygons](https://claude.ai/share/e4d81ae2-8e26-480e-8c56-dec688cc7eb9). Basically it went down an overly complicated path to get the exact calculation, whereas here I have an approximation using tiny buffers that works just fine and is much simpler.

    def intersection_length(poly1,poly2,smb=1e-15):
        '''
        Length of the intersection between two shapely polygons
        
        poly1 - shapely polygon
        poly2 - shapely polygon
        smb - float, defaul 1e-15, small distance to buffer
        
        The way this works, I compute a very small buffer for
        whatever polygon is simpler (based on length)
        then take the intersection and divide by 2
        so not exact, but close enough for this work
        '''
        # buffer the less complicated edge of the two
        if poly1.length > poly2.length:
            p2, p1 = poly1, poly2
        else:
            p1, p2 = poly1, poly2
        # This basically returns a very skinny polygon
        pb = p1.buffer(smb,cap_style='flat').intersection(p2)
        if pb.is_empty:
            return 0.0
        elif hasattr(pb, 'length')
            return (pb.length-2*smb)/2
        else:
            return 0.0

And then for some tests:

    from shapely.geometry import Polygon
    
    poly1 = Polygon([(0, 0), (4, 0), (4, 3), (0, 3)])  # Rectangle
    poly2 = Polygon([(2, 1), (6, 1), (6, 4), (2, 4)])  # Overlapping rectangle
    
    intersection_length(poly1,poly2) # should be close to 0
    
    poly3 = Polygon([(0, 0), (2, 0), (2, 2), (0, 2)])
    poly4 = Polygon([(2, 0), (4, 0), (4, 2), (2, 2)])
    
    intersection_length(poly3,poly4) # should be close to 2
    
    poly5 = Polygon([(0, 0), (2, 0), (2, 2), (0, 2)])
    poly6 = Polygon([(2, 0), (4, 0), (4, 3), (1, 3), (1, 2), (2, 2)])
    
    intersection_length(poly5,poly6) # should be close to 3
    
    poly7 = Polygon([(0, 0), (2, 0), (2, 2), (0, 2)])
    poly8 = Polygon([(3, 0), (5, 0), (5, 2), (3, 2)])
    
    intersection_length(poly7,poly8) # should be 0

Real GIS data often has imperfections (polygons that do not perfectly line up). So using the buffer method (and having an option to increase the buffer size) can often help smooth out those issues. It will not be exact, but the inexactness we are talking about will often be to well past the 10th decimal place.
