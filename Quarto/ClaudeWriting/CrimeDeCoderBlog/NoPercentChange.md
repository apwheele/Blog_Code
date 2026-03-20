## Don't use percent change for crime data, use this statistic instead

CRIME De-Coder has sat in on CompStat meetings in police departments across the county. Almost verbatim, I have heard this statement in the majority of them:

> Crime [X] has increased by 200% so far this year, but ignore that number because it is a small baseline rate.

So to solve this continual problem, [CRIME De-Coder has created a methodology](https://apwheele.github.io/Class_CrimeAnalysis/Lab03_TemporalAnalysis.html) relevant to monitor small counts of crime over time. It is super simple, to calculate this metric, it is:

    2 * ( sqrt(Current) - sqrt(Past) )

If this value is greater than 3, this is a signal that crime is increasing more than you would expect by chance. If it is less than -3, it is decreasing more than you would expect by chance.

So for example, if you currently have 9 crimes, and in the past period had 4 crimes, you then have `2*(sqrt(9) - sqrt(4)) = 2*(3 - 2) = 2`. So in that scenario, instead of saying "we have a 125% increase", you can say "the increase from 4 to 9 crimes is within the typical range one would expect with low crime count data".

I call this statistic a *Poisson Z-score* -- for all the crime analysts out there, do yourself a favor and stop using noisy metrics to monitor crime stats and use this stat instead.

CRIME De-Coder has the experience of working with police departments and crime analysts as well as the mathematical background to develop custom solutions to solve regular problems. If your agency would like help with developing metrics or analyzing crime trends, do not hesitate to get in touch with [CRIME De-Coder](mailto:consult@crimede-coder.com) for a free consultation.