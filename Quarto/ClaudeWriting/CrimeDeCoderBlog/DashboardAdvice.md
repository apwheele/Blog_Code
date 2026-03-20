## What to put in your dashboard?

Although data dashboards showing metrics are very popular, many are ineffective in helping drive key decision making. They tend to be driven by mimicry of what people *think* a data dashboard should look like, instead of being built to help accomplish specific end goals.

It is difficult to give general advice about what you should place on a dashboard. You could have the same set of data, and two different people would need different information. So the first step, before drawing any graphs, is to figure out whom the intended audience of the dashboard is meant for, and what key pieces of information do they need. It is not a good start when someone says "we have this data, what can we do with it". Spreadsheets don't sing, you need external context of what the data will be used for.

In this post, I will attempt to give general, high level advice about how I think about what to place on a dashboard.

### KPIs over time

The term "dashboard" is meant to be an analogy with your car dashboard. This analogy is not that great though -- you really only care about your *instantaneous* speed when you are driving, you don't care about your speed 10 minutes ago. This is not the case with most dashboards showing metrics. If you are examining crime trends over time in your city, you often want to know what the crime rate is this month, as well as what it was last month.

The trends over time, and any recent anomalous spikes or changes, are often what is important in the policing context. In the business world, we call these *key performance indicators*, KPIs. Most (but not all) dashboards showing data are monitoring metrics over time. Is crime going up or down?

There are situations in which you just want to know the instantaneous value. For example, if you are running a 911 call center, you may be keeping a tally of the number of operators available, or the number of calls in the queue. The analogy with the car dashboard though is again strained, it may be easier to simply send an alert in those situations if some metric reaches a critical threshold. There is no point in waiting for a human to maybe click on a graph and then respond if you can automate a response in certain critical siutations.

### Understanding What to Compare

Once your KPIs have been defined, a second component is understanding how to make comparisons for your data. OK, so there were 10 robberies in Patrol Zone A last month, is that high or low? Or is that within the typical variance you would expect?

One way to think about this is *within* changes versus *between changes*. So you may compare Patrol Zone A this month versus last month -- within changes. You may also compare Patrol Zone A to Patrol Zone B -- between comparisons. You may also even want to do both at the same time, e.g. compare the change over time in Patrol Zone A to the change over time in Patrol Zone B.

Many dashboards have *filters* for data -- you select a dropdown for a particular slice of data, and the entire set of charts on the dashboard changes. This is an example of where mimicry dominates dashboards; this is easy to do, but is often not what is needed. This can be effective for within comparisons, but is not for between comparisons.

One simple example to keep in mind that is effective for many situations, is to compare subset A vs the rest of the data. So instead of comparing Patrol Zone A to Patrol Zone B, you can create a graph to show Patrol Zone A vs the rest of the city. Or you can make a graph to show robberies vs trends in all other crimes. Knowing what you want to compare should drive the subsequent visualizations the dashboard displays.

### Cause and Effect

Going back to the car dashboard analogy, you see that you are driving over or under the speed limit, and you can modulate how much pressure you are putting on the pedal to change your speed. Most data metric dashboards don't have such an obvious speed pedal that provides immediate feedback, but the dashboard should allow sufficient flexibility to be able to drill down into *potential* causal factors that impact the KPIs of interest.

For example, say your city has a use of force dashboard. If you identify that use of force has been going up over time, you may be interested to see the types of incidents that precipitate the force, or breakdowns by particular shifts. The statistical way to think about this is via conditional relationships -- use of force is conditional on incident, officer, and civilian characteristics. If force is going up over time, you will likely want to see if you can pinpoint which of those factors is causing the increase.

To be specific, if you show rates of use of force conditional on race, you might show a bar graph where the Y axis is the *rates of deadly force* per arrests, and the X axis is the race of the person being arrested. In conditional terms, it is `Rate | Race`, it does not make sense to show a pie graph of the total proportion of race of arrests, which is showing `Race | Arrest`. The latter pie is very likely to misinterpreted as signaling the department is racist, when in reality you need to switch the conditional. 

You should be building your dashboards with these types of decompositions in mind from the beginning. It may be easier to have graphs to show those contributing factors directly, instead of making a human go and click buttons to figure out that information. If robberies are going up, is this concentrated in a particular hotspot? (So have hotspots shown by default.) Or is it concentrated during a particular time of day (so have a graph of within day time trends by default).

### The Tech Behind Dashboards

This has been very high level advice -- once these questions are answered, things like "what type of graph" do I use, or "what do I select as slicers" are much easier to answer. Many of the current popular dashboard software, such as Tableau of PowerBI, often have functionality that is not that helpful to accomplish specific goals (very rarely do dashboards need brushing interactivity between graphs for example, it is much more important to be updated with current data). Many dashboards do not even need to be interactive, e.g. a standard report with key metrics may be a better solution to accomplish your end goal. The tech should not drive the dashboard, you should adopt the technology to meet your particular end goals.

I actually prefer many of the open source solutions to building dashboards, see the examples I have built using python ([Dallas Crime Trends](/graphs/Dallas_Dashboard), and D3 & supabase ([City trends in sworn hiring rates](/graphs/sworn)). These tend to be much easier to integrate with myriad systems and different requirements than do the paid for solutions such as Tableau and PowerBI.

If you are interested in building dashboards for your agency, feel free to [get in touch](/contact). I have several example automated dashboards on [my demo's page](/demos), and have experience in the majority of major software applications building dashboards.




