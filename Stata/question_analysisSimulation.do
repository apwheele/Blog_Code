*Stata simulation of different item probabilities
*Often comes up with survey items of delinquency, where some items are much more prevalent than others
*I think modelling the individual delinquency item probabilities makes more sense than aggregating to binomial models
*Or using a global scale
*Any questions, feel free to email, apwheele@gmail.com
*Andy Wheeler, https://andrewpwheeler.wordpress.com/

clear
set more off
set seed 10
set obs 1000
generate caseid = _n
generate group = ceil(caseid/100) 
generate self_control = rnormal(0,1)
generate rand_int = rnormal(0,1)

*generating 20 outcomes that just have a varying intercept for each
forval i = 1/20 { 
  generate logit_`i' = -0.4 -0.5*self_control -0.1*group + 0.1*(`i'-10) + rand_int
  generate prob_`i' = 1/(1 + exp(-1*logit_`i'))
  generate outcome_`i' = rbinomial(1,prob_`i')
}
summarize prob_*
drop logit_* prob_* rand_int

*The above dataset should look similar to how you collected the data
*Each row is an individual (caseid)
*you have twenty outcome 0/1 variables (outcome_1, outcome_2, etc.) - these would be equivalent to the bullying outcomes (victim or perpetration)
*each individual has a measure of self control ("self_control")
*each student is nested within a school ("group"), 10 schools overall in this set

*first I will show the binomial model in Britt [not the zero inflated though]
egen bully_total = rowtotal(outcome_*)
tab bully_total
*MODEL 1
glm bully_total self_control i.group, family(binomial 20) link(logit)

*reshape wide to long
reshape long outcome_, i(caseid) j(question)
*see each person now has 20 questions each
*tab caseid

*regression model with the individual level data, should be equivalent to the aggregate binomial model
*MODEL 2
glm outcome_ self_control i.group, family(binomial) link(logit)

*MODEL 1 AND MODEL 2 ARE EQUIVALENT

*will use this later to show fit per each individual question
predict prob_mod2, mu

*but you can do more with this model, such as model the differences across each question
*MODEL 3
glm outcome_ self_control i.group i.question, family(binomial) link(logit)

*MODEL 3 IS DIFFERENT, BECAUSE EACH QUESTION CAN HAVE A VARYING BASELINE PREVALENCE
*I THINK THIS IS THE MOST APPROPRIATE GIVEN THE DIFFERING PERCENTAGES IN THE MARGINAL DATA
*MODEL 1 AND MODEL 2 assumes that the end predicted probability for each question is the same give the person + school level
*covariates, which I doubt that is true.

*see how the outcome has a different intercept for each question?
*the aggregate binomial model forces this to be equal for each question
*this is a highly questionable presumption, since some things (like calling names)
*are much more prevalent than the other items

*you can look to see if the self control effect is equivalent across the different items
*MODEL 4
glm outcome_ self_control i.group i.question (c.self_control#i.question), family(binomial) link(logit)
*you can see the effect of self control is the same for each question, but the probality across each question still changes

*can do a test of all the interactions equal to zero at once
testparm c.self_control#i.question


*These don't take into account the clustering of persons though, what I would probably do is a multi-level model
*with a random intercept for person

*MODEL 5 (this is technically the correct model given how I simulated the data)
melogit outcome_ self_control i.group i.question || caseid:

*This is the first model that has a non-biased estimate of self-control, others are all too small

*To check the fit, you want to generate the probabilities for each question and then see
*if the means are nearby one another

predict prob_mod5, mu
sort question
by question: summarize outcome_ prob_mod2 prob_mod5
*See mod2 has the same predicted numbers across each question - a result of the model used
*Mod7 though has different predictions across each question, and so is a much better fit

*note you could do this for both perpetration and victimization at the same time
*say in this set questions 1-10 are perp, and 11-20 are victim
*MODEL 6
gen vic = floor((question-1)/10)

melogit outcome_ self_control i.group i.question (c.self_control#i.vic) || caseid:
*here the effect of self-control is equal across both victimizations and bullying

*the traditional item-response model has random intercepts for both questions and persons
*MODEL 7
*melogit outcome_ self_control i.group || caseid: || question:
*with only 20+ questions though this is a bit harder to estimate, just as easy to interpret the fixed effects
*this takes abit to converge, because the random effect estimate for questions is small here, despite there being actual appreciable differences
*across questions
*If I was dead set on random effects for both persons and questions I would do it in R, 
*Stata calculates a bunch of extra covariance terms between the random effects by default, whereas R
*does not