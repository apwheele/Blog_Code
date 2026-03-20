## Evaluating Predictive Policing Systems

There are many vendors who provide predictive policing software. When purchasing software that claims to do predictions, you should always have the vendor perform predictions on your local data, so you can evaluate the efficacy of the software firsthand. The reason for this is that vendors obviously have the incentive to overpromise on what they can provide -- they only way to get a realistic gauge of their efficacy is to make them provide a demonstration on your local data.

The main way people evaluate predictions is to have a train set of data, and then a test set of data. The reason for this is that if you give a vendor all of the data, they can always generate perfect predictions on that same data. You need to hold out some data, and do the evaluations yourself on that held out test set of data, to get an accurate guage of how well the software can make predictions.

This post I will describe different ways you may do this for different types of predictive policing systems.

### Spatial based predictions

Spatial based predictive policing systems, like PredPol or RTM, generate predictions in a particular area based on historical crime trends. For example, in this square I expect there to be 10 crimes in the next year (for RTM long term predictions), or expected 1 crime in the day (for the shorter term PredPol predictions).

The way to do train/test data splits in this scenario is based on time period. So for RTM, you may give them 2022 data, have them generate predictions, and then evaluate their predictions based on 2023 crime data.

One of the metrics you should then be interested in is the accuracy of the predictions. If the software predicts and area to have 10 crimes, and then in reality it has 5 crimes, that is a positive bias. If the software consistently has a positive bias, you will be led astray and think more crime is occurring in a particular area based on the software than their is in reality. 

Another common metric for spatial based crime forecasting is the *Predictive Accuracy Index* (PAI). This is related to identifying hotspots. So say you wanted the software to identify the top 5% of the city area to prioritize for hotspots policing. The PAI metric is `% Crime in Area / % Area of City`, so if the software identified hotspots captured 25% of the overall robberies in 5% of the city, you would have a PAI of 5.

A rule of thumb is that Weisurd's law of crime concentration is that 5% of your street blocks contain around 50% of the crime in your jurisdiction, so a predictive policing software should have a PAI much higher than 10. Just doing a simple ranking, prior crime on street segments, is likely to get a higher PAI than that.

### Person based predictions

Person based forecasting, or chronic offender systems, are based on prior criminal histories. You may do a train/test set split in this scenario based on dates, e.g. criminal history from 2010 through 2022, and forecast out individuals into 2023. But another way would be you split people, give the vendor criminal histories on a sample of 10,000 people, and have a hold out of 5,000 people, and see how the predictions do on that hold out sample.

For person based predictions, you will likely want to determine how to weight different crime types. Do you want to focus on gun violence? Or more general offending? Offenders tend to be generalists, so generating a chronic offender list based on [crime harm weights](https://andrewpwheeler.com/2022/06/22/estimating-criminal-lifetime-value/) is one way to evaluate how well the predictions do to help prioritize chronic offenders in your jurisdiction.

Because serious violence is much rarer, you will often need to have a larger number of people to capture a smaller number of incidents. Based on my experience, the highest probability you can get for [gun violence is around 10% per year](https://andrewpwheeler.com/2022/05/21/the-limit-on-the-cost-efficiency-of-gun-violence-interventions/), so if the software identifies many people with probabilities of serious violence near 100% that is likely suspect.

### Early Intervention Systems

Early intervention systems (EIS) are very similar to person based offender predictions -- but the prediction is internal to identify problematic officers within the department. A major problem with most EIS's on the market are *false positives* -- they tend to have 3 strike systems, which identify a large number of officers as problematic.

A good EIS system should not only prioritize potentially problematic officers, but also should take into account their activity. Streets officers that are more proactive will ultimately have more events such as use of force or civilian complaints, the EIS should be based on *the rate* of problematic interactions, not the total count of events.

Also note that having more variables in the predictive system *does not* mean it is a good system. I have seen several EIS vendors claim to measure 100's of variables -- how many variables you measure has no direct bearing whether the system is any good at generating predictions. You can feed a system an infinite number of variables that have no correlation with the behavior you are trying to predict, and it will result in less accurate predictions. Having more variables can be a clear negative -- if it requires your department to measure and input many more field than you currently do, it may be a negative to the system, not a positive.

If you have the vendor do a demonstration on your data, and find that you have dozens of officers flagged as problematic, it is likely the software is not well calibrated to actually identify problematic officers. Good EIS software should likely only be flagging a very small percentage of your officers.

### Evaluating Tech Purchases

Most of these software licenses for police departments are at the low end mid 5 digits, and at the high end mid 6 digits. PDs should be doing their due diligence before making such large tech purchases. If you would like an outside evaluation for these software purchases, I would likely charge somewhere around $10,000 to conduct that analysis.

I have published on various predictive policing systems (see references). If you have internal capacity for your crime analysts, you can often make simple predictive policing systems internally that are very competitive with any of the paid for software.

So I think having an outside reference to evaluate the cost and benefits of that predictive system are worth it. Especially if I can provide some simple alternatives that you can do in house for free.

### References

Spatial Predictive Policing Applications

 - Wheeler, A.P., and Reuter, S. (2021) Redrawing hot spots of crime in Dallas, Texas. *Police Quarterly* 24(2): 159-184. ([Preprint](https://www.crimrxiv.com/pub/wmelrli9/release/1)). Evaluating DBSCAN crime weighted harm spots.
 - Wheeler, A.P., & Steenbeek, W. (2021). Mapping the risk terrain for crime using machine learning. *Journal of Quantitative Criminology*, 37, 445-480. ([Preprint](https://osf.io/preprints/socarxiv/xc538/download)), spatial predictive models outperform RTM

Time Series Predictive Forecasting

 - Wheeler, A.P. (2016). Tables and graphs for monitoring temporal crime trends: Translating theory into practical crime analysis advice. *International Journal of Police Science & Management*, 18(3), 159-172. ([Preprint](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2551472)), simple statistics to identify anomalous upticks in low count crime data
 - Wheeler, A. P., & Kovandzic, T. V. (2018). Monitoring volatile homicide trends across US cities. Homicide Studies, 22(2), 119-144. ([Preprint](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2977556)), model that has good coverage of homicide rate forecasts across US.
 - Yim, H.N., Riddell, J.R., & Wheeler, A.P. (2020). Is the recent increase in national homicide abnormal? Testing the application of fan charts in monitoring national homicide trends over time. Journal of criminal justice, 66, 101656.([Preprint](https://osf.io/7g32n/download)), national level homicide rate forecasts

Chronic Offender and EIS

 - Circo, G. M., & Wheeler, A. P. (2022). An Open Source Replication of a Winning Recidivism Prediction Model. *International Journal of Offender Therapy and Comparative Criminology*. ([Preprint](https://www.crimrxiv.com/pub/bc7mptfb/release/1)). NIJ winning solution to predict recidivism.
 - Wheeler, A.P., Phillips, S.W., Worrall, J.L., & Bishopp, S.A. (2017). What factors influence an officer’s decision to shoot? The promise and limitations of using public data. *Justice Research and Policy*, 18(1), 48-76. ([Preprint](https://www.dropbox.com/s/sxc4ctvfi90a623/Wheeler_Dallas_Shootings.pdf?dl=0)), work related to EIS
 - Wheeler, A.P., Worden, R.E., & Silver, J. R. (2019). The accuracy of the violent offender identification directive tool to predict future gun violence. *Criminal Justice and Behavior*, 46(5), 770-788. ([Preprint](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3122636)), Chronic offender predictions


