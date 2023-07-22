# Age-Period-Cohort analysis
# sucides and overdose

library(ggplot2)

# My ggplot2 theme
# check out https://rpubs.com/mclaire19/ggplot2-custom-themes
theme_andy <- function(){
  theme_gray() %+replace% theme(
     panel.grid.major= element_line(linetype = "longdash"),
     panel.grid.minor= element_blank(),
     axis.title.y=element_text(margin=margin(0,30,0,0))
) }


# Read in data
suicide <- read.csv('Suicides.csv')
overdose <- read.csv('Overdoses.csv')

# Calculate Rate & Cohort
suicide$Cohort <- suicide$Year - suicide$Age
suicide$Rate <- (suicide$Deaths/suicide$Population)*100000

overdose$Cohort <- overdose$Year - overdose$Age
overdose$Rate <- (overdose$Deaths/overdose$Population)*100000

# Suicide only 11-84
suicide <- suicide[suicide$Age >= 11,]

# Overdose only 14-84
overdose <- overdose[overdose$Age >= 14,]

# Year/Age graph
# Age X-axis, Rate Y-axis
# group/color by year
ap <- ggplot(data=suicide, aes(x = Age, y = Rate, color=Year, group=Year)) + 
             geom_line() +
             scale_colour_distiller(palette = "PuOr") +
             scale_x_continuous(breaks=seq(10,80,10)) +
             scale_y_continuous(breaks=seq(0,30,5)) + 
             labs(x='Age',y=NULL,title='Suicide Rate per 100,000',caption="USA Rates via CDC Wonder") +
             theme_andy()

png(file = "YearPlot_Suicide.png", bg = "transparent", height=5, width=9, units="in", res=1000)
ap
dev.off()


op <- ggplot(data=overdose, aes(x = Age, y = Rate, color=Year, group=Year)) + 
             geom_line() +
             scale_colour_distiller(palette = "PuOr") +
             scale_x_continuous(breaks=seq(10,80,10)) +
             scale_y_continuous(breaks=seq(0,60,10)) + 
             labs(x='Age',y=NULL,title='Overdose Rate per 100,000',caption="USA Rates via CDC Wonder") +
             theme_andy()

png(file = "YearPlot_Overdose.png", bg = "transparent", height=5, width=9, units="in", res=1000)
op
dev.off()


# Outlier year
suicide[(suicide$Age == 75 & suicide$Year == 2022),c('Rate')]

# Lets just drop 2022 data, since it is provisional
#suicide <- suicide[suicide$Year < 2022,]

# Cohort graph
# Age X-axis, Rate Y-axis
# group/color by cohort
cp <- ggplot(data=suicide, aes(x = Age, y = Rate, color=Cohort, group=Cohort)) + 
             geom_line() +
             scale_colour_distiller(palette = "Spectral") +
             scale_x_continuous(breaks=seq(10,80,10)) +
             scale_y_continuous(breaks=seq(0,30,5)) +
             labs(x='Age',y=NULL,title='Suicide Rate per 100,000',caption="USA Rates via CDC Wonder") +
             theme_andy()

png(file = "CohortPlot_Suicide.png", bg = "transparent", height=5, width=9, units="in", res=1000)
cp
dev.off()


co <- ggplot(data=overdose, aes(x = Age, y = Rate, color=Cohort, group=Cohort)) + 
             geom_line() +
             scale_colour_distiller(palette = "Spectral") +
             scale_x_continuous(breaks=seq(10,80,10)) +
             scale_y_continuous(breaks=seq(0,60,10)) + 
             labs(x='Age',y=NULL,title='Overdose Rate per 100,000',caption="USA Rates via CDC Wonder") +
             theme_andy()

png(file = "CohortPlot_Overdose.png", bg = "transparent", height=5, width=9, units="in", res=1000)
co
dev.off()



