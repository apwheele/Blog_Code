## Predictive Analytic Services

Predictive analytics, also commonly referred to as machine learning or artificial intelligence, is using statistical models to predict the probability of a future event occurring, or forecast a numeric value that is likely to occur in the future. Examples in policing are predicting the number of crimes likely to occur in an area in the future, such as this street segment is likely to have 5 robberies in the next month, or predicting the probability an individual is going to be involved in gun violence in the next year.

Note that this is decidedly not like predictions in Minority Report -- it is probabilistic identifying people and places of high risk for an event. It does not call for pre-preemptively arresting people before they have committed a crime, but using different proactive tactics to *prevent* crime before it even occurs.

The **CRIME** De-Coder has extensive experience in prior predictive applications. I have previously won several different prediction competitions ([NIJ recidivism forecasting](https://nij.ojp.gov/funding/recidivism-forecasting-challenge), [NASA Algae Bloom](https://www.drivendata.org/competitions/143/tick-tick-bloom/page/649/)), as well as have published extensively in peer reviewed journals on the topic. There are broadly three different applications of forecasting commonly in use in the criminal justice system; spatial based forecasts, person based predictions, and time series based forecasts.

### Spatial Based Forecasts

Since hot spots of crime are one of the most well vetted criminal justice interventions, there has been much research in methods to identify hotspots of crime. The **CRIME** De-Coder has published several method pieces using models to forecast the most concentrated areas of crime. Examples are using DBSCAN clusters to identify hotspots of crime responsible for over a million dollars of police labor costs per year (Wheeler & Reuter, 2021). I have also published papers using risk terrain modelling to identify spatial areas of high risk for homeless offending and victimization (Yoo & Wheeler, 2019). Finally, I have published on using machine learning to better forecast hot spots of crimes *and* identify the elements of the built environment likely contributing to those hot spots (Wheeler & Steenbeek, 2021).

Below is an example million dollar hotspot in Dallas using the methodology I developed in Wheeler & Reuter (2021):

![](./images/MillionDollarHotSpot.PNG)

### Person Based Predictions

Examples of person based forecasting are chronic offender systems (Wheeler et al., 2019), and personal risk assessments for parole or bail (Circo & Wheeler, 2022). Chronic offender systems are commonly used by police departments and prosecutors offices to identify individuals with which to target specialized services. Personal risk assessments are commonly used to assign individuals certain levels of parole supervision, or in the case of bail reform [identify individuals of low risk to release on their own recognizance](https://andrewpwheeler.com/2020/02/15/setting-the-threshold-for-bail-decisions/).

### Time Series Forecasting

Time series forecasting is the use of historical data to forecast the total number of events likely to occur in the future. For example, using historical data to forecast there are likely to be 10 homicides in the next year. The majority of such applications in policing are to identify anomalous patterns, and generate a policing strategy in response to such upticks in crime (Wheeler, 2016). Below is an example of showing how national level homicide rates in 2020 were anomalous, based on forecasted prediction intervals using historical data:

![](./images/HomicideForecast.PNG)

The **CRIME** De-Coder has developed methodology specifically intended to forecast rare crime data (Wheeler & Kovandzic, 2018; Yim et al., 2020), and actively monitor crime patterns to identify spikes that may demand police response (Wheeler, 2016).

### Fair Application of Predictive Analytics

One of the [critiques of predictive analytics is its racist](https://www.technologyreview.com/2021/02/05/1017560/predictive-policing-racist-algorithmic-bias-data-crime-predpol). This is largely misleading though -- predictive policing is a method to identify areas or people that can *benefit* the greatest from specific interventions. Police departments, or other agencies, have the ability to choose particular tactics that mitigate harm. the **CRIME** De-Coder has developed methodology to make predictive analytics more fair and racially equitable (Circo & Wheeler, 2022; Wheeler, 2020). Complaints about predictive analytics being intrinsically racist are misleading and are not considering the state of the art methods in predictive analytics.

In most settings, a small number of places or people [cause the most crime harm](https://andrewpwheeler.com/2022/06/22/estimating-criminal-lifetime-value/). Targeting resources to those highest risk people and places, in the most fair way possible, is the best approach to tackle difficult crime and violence problems in communities.

If you are interested in predictive analytics, contact the [**CRIME** De-Coder](mailto:crimede-coder@crimede-coder.com) today to discuss your agencies needs.

### References

 - Circo, G.M., & Wheeler, A.P. (2022). An Open Source Replication of a Winning Recidivism Prediction Model. [*International Journal of Offender Therapy and Comparative Criminology*, Online First](https://journals.sagepub.com/doi/abs/10.1177/0306624X221133004).
 - Wheeler, A.P. (2016). Tables and graphs for monitoring temporal crime trends: Translating theory into practical crime analysis advice. [*International Journal of Police Science & Management*, 18(3), 159-172](https://journals.sagepub.com/doi/abs/10.1177/1461355716642781).
 - Wheeler, A.P. (2020). Allocating police resources while limiting racial inequality. [*Justice Quarterly*, 37(5), 842-868](https://www.tandfonline.com/doi/abs/10.1080/07418825.2019.1630471).
 - Wheeler, A.P., & Kovandzic, T.V. (2018). Monitoring volatile homicide trends across US cities. [*Homicide Studies*, 22(2), 119-144](https://journals.sagepub.com/doi/abs/10.1177/1088767917740171).
 - Wheeler, A.P., & Reuter, S. (2021). Redrawing Hot Spots of Crime in Dallas, Texas. [*Police Quarterly*, 24(2), 159-184](https://journals.sagepub.com/doi/abs/10.1177/1098611120957948).
 - Wheeler, A.P., & Steenbeek, W. (2021). Mapping the risk terrain for crime using machine learning. [*Journal of Quantitative Criminology*, 37, 445-480](https://link.springer.com/article/10.1007/s10940-020-09457-7).
 - Wheeler, A.P., Worden, R.E., & Silver, J.R. (2019). The accuracy of the violent offender identification directive tool to predict future gun violence. [*Criminal Justice and Behavior*, 46(5), 770-788](https://journals.sagepub.com/doi/abs/10.1177/0093854818824378).
 - Yim, H.N., Riddell, J.R., & Wheeler, A.P. (2020). Is the recent increase in national homicide abnormal? Testing the application of fan charts in monitoring national homicide trends over time. [*Journal of Criminal Justice*, 66, 101656](https://www.sciencedirect.com/science/article/abs/pii/S0047235219304672).
 - Yoo, Y., & Wheeler, A.P. (2019). Using risk terrain modeling to predict homeless related crime in Los Angeles, California. [*Applied Geography*, 109, 102039](https://www.sciencedirect.com/science/article/pii/S0143622819300931).