# Using Lasso & Conformal Inference

This is a set of code to go with my blogpost, ???????????

This uses the lasso to estimate synthetic control weights, and conformal inference to estimate standard errors for the lasso predictions. I like this approach because it tends to have smaller intervals than placebos in state level designs. Also I like lasso as a better default optimization algorithm than the stochastic gradient descent in the original Abadie method.

I took the data/idea from Charles Fain Lehmans substack post, [*Did Drug Decriminalization Increase OD Deaths?*](https://thecausalfallacy.com/p/did-drug-decriminalization-increase), that discusses two recent papers examining the effects of different laws in Oregon/Washington on opioid fatalities.

## Steps to Reproduce

A python environment with much of the usual scientific stack (sklearn, pandas, matplotlib), plus the [mapie](https://mapie.readthedocs.io/en/latest/) library for conformal inference, is the main thing you need. So something like (using conda):

    conda create --name cinf python=3.10 sklearn mapie jupyter matplotlib pandas

First, to create the csv file, I cribbed this R code from Charles (and the data files from CDC Wonder):

    # R code to make the OpioidDeathRates.csv merged file
    library(tidyverse)
    
    #don't forget to rename this file
    deaths <- read.csv("OverdoseFile.txt", sep = "\t") %>%
      filter(Notes == "") %>%
      select(-Notes, -Occurrence.State.Code, -Month, -Population, -Crude.Rate) %>%
      separate(Month.Code, c("Year", "Month"), sep = "/", convert = T) %>%
      #I fill supprressed cells with values between 0 and 9
      complete(Occurrence.State = unique(Occurrence.State), Year = 2018:2022, Month = 1:12, fill = list(Deaths = floor(runif(1, 0, 10)))) %>%
      filter(!Year == 2023, !(Year == 2022 & Month > 3)) %>%
      rename(State = Occurrence.State)
    
    #don't forget to rename this file
    population <- read.csv("PopFile.txt", sep = "\t") %>%
      filter(Notes == "") %>%
      select(Residence.State, Year.Code, Population) %>%
      rename(Year = Year.Code,
             #WONDER won't give you population estimates unless you use residence state, but it shouldn't matter
             State = Residence.State)
    
    merge(deaths, population, by = c("State", "Year")) %>%
      mutate(Rate = Deaths/Population * 100000) %>%
      group_by(State) %>%
      arrange(Year, Month) %>%
      mutate(Period = 1:n()) -> opioid.death.rates
    
    write.csv(opioid.death.rates,'OpioidDeathRates.csv',row.names=FALSE)

Second, then you can check out the notebook code, `OpioidAnalysis_Synth.ipynb`, on how to run the code and check out the results.