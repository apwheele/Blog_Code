## Dashboards Should be Up-to-Date

The point of data visualization dashboards is to examine *up to date* detailed information. The term "dashboard" comes from your car dashboard -- knowing your speed a few minutes ago is quite worthless when you are driving.

Many crime analysis vendors offer services such as creating dashboards for your agency, but they [are not automated](https://crimede-coder.com/services/ProcessAutomation) to be up to date. For one example, Dallas PD has a dashboard on use of force information that displays (as of May 2023) data that is over [a year old](https://dallaspolice.net/reports/Pages/force-analysis-data.aspx).

As a proof of concept illustration of creating a dashboard that has updated information, I have created a [demo dashboard using Dallas's open crime data](https://crimede-coder.com/graphs/Dallas_Dashboard). This uses various open source tools and open Dallas PD data to automate updating of the dashboard, so is at most a day old. Here is a screenshot gif in action:

![](/images/DemoDashboard.gif)

So although Dallas PD has been in the news abit [for decreasing crime trends due to hotspots policing](https://www.nbcdfw.com/news/local/violent-crime-down-in-dallas-police-chief-says/3226751/), you can see they currently have an upward trend in motor vehicle thefts ([consistent with many other agencies](https://jasher.substack.com/p/how-tiktok-caused-a-surge-in-auto)). 

This isn't to say you should *always* use a dashboard. Sometimes having a few weeks old data is fine, such as [for a standardized report](https://andrewpwheeler.com/2021/07/10/creating-automated-reports-using-python-and-jupyter-notebooks/) disseminated to the public. Also dashboards do not on their own generate automated alerts -- it may be better to auto-identify an increasing crime trend, as opposed to having an analyst click around and hope they spot a noteworthy increase. Either way though, you should not rely on vendors that deliver a static, one time dashboard/report. You should get in contact with CRIME De-Coder to develop a truly automated report.

If you are interested in creating reliable and up-to-date dashaboards with your own data, I encourage you to reach out to [**CRIME** De-Coder](mailto:crimede-coder@crimede-coder.com) to discuss what I can do for your agency.