*https://twitter.com/estebanjq3/status/1034296298235736064
*using sem to estimate multiple equations, IV through two stages
*Andy Wheeler, https://andrewpwheeler.wordpress.com/

*Stata simulation
clear
set more off
set seed 10
set obs 100000

generate z1 = rnormal(0,1)
generate w = rnormal(0,1)

generate e = rnormal(0,1)
generate u = 0.5*e + rnormal(0,1)
generate v = 0.5*u + rnormal(0,1)

generate z2 = 0.5*z1 + 0.5*w + e
generate x = -0.4*z2 + -0.2*w + u
generate y = 1.3*x + -0.3*w + v

*normal regression is biased
reg x z2 w
reg y x w

*Need to let errors correlate for all three equations
sem (z2 <- z1 w)(x <- z2 w)(y <- x w), covstruct(e.z2 e.x e.y, unstructured)
*Thought that e and v did not need to be correlated
*but if you only do cov(e.z2*e.x e.x*e.y) the y equation
*is not unbiased

*other suggestion in thread is to just use z1 as instrument for each
ivreg y (x = z1) w
ivreg x (z2 = z1) w
reg z2 z1 w
*which looks to me like the same standard errors as the sem code