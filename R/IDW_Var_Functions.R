#######################################################################################
#Example of having spatstat return the numerator for calculating inverse distance 
#weighting, can be useful to estimate the variance

#see source for C function, https://github.com/spatstat/spatstat/blob/35532d5d3a121fb1c499f3fb9e9c00b836f9d326/src/idw.c
#That was simple, C function returns the numerator and the denominator
#Just prevent idw from only returning the ratio, and return the full z object
#also accumulates necessary info to calculate the variance

library(spatstat)
library(inline)

UpdateIDW_c <-"
  int N, i, Nx, Ny, ix, iy;
  double xg, yg, x0, dx, y0, dy, pon2, d2, w, sumw, delta, mean, m2, r, sumw2;
  
  N  = *n;
  Nx = *nx;
  Ny = *ny;
  x0 = *xstart;
  y0 = *ystart;
  dx = *xstep;
  dy = *ystep;

  pon2 = (*power)/2.0;

  if(pon2 == 1.0) {
    /* slightly faster code when power=2 */
    for(ix = 0, xg=x0; ix < Nx; ix++, xg+=dx) {
      if(ix % 256 == 0) R_CheckUserInterrupt();
      for(iy = 0, yg=y0; iy < Ny; iy++, yg+=dy) {
	    sumw = 0;
		sumw2 = 0;
	    mean = 0;
		m2 = 0;
	  /* loop over data points, online variance estimate, see http://stats.stackexchange.com/a/235151/1036 */
	for(i = 0; i < N; i++) {
	  d2 = (xg - x[i]) * (xg - x[i]) + (yg - y[i]) * (yg - y[i]);
	  w = 1.0/d2;
	  sumw += w;
	  sumw2 += w*w;
	  delta = v[i] - mean;
	  r = delta*w / sumw;
	  mean += r;
	  m2 += (sumw - w) * delta * r;
	}
	/* compute ratio and variance, replace denominator with sumw for ML estimate */
	MAT(rat, ix, iy, Ny) = mean;
	MAT(var, ix, iy, Ny) = m2 / sumw;
      }
    }
  } else {
    /* general case */
    for(ix = 0, xg=x0; ix < Nx; ix++, xg+=dx) {
      if(ix % 256 == 0) R_CheckUserInterrupt();
      for(iy = 0, yg=y0; iy < Ny; iy++, yg+=dy) {
	  	sumw = 0;
		sumw2 = 0;
	    mean = 0;
		m2 = 0;
	/* loop over data points, accumulating numerator and denominator */
	for(i = 0; i < N; i++) {
	  d2 = (xg - x[i]) * (xg - x[i]) + (yg - y[i]) * (yg - y[i]);
	  w = 1.0/pow(d2, pon2);
	  sumw += w;
	  sumw2 += w*w;
	  delta = v[i] - mean;
	  r = delta*w / sumw;
	  mean += r;
	  m2 += (sumw - w) * delta * r;
	}
	/* compute ratio and variance, use sumw for the denominator for ML estimate */
	MAT(rat, ix, iy, Ny) = mean;
	MAT(var, ix, iy, Ny) = m2 / sumw;
      }
    }
  }  
"

#Took out #include "chunkloop.h"

HeadInc <- "
#include <Rmath.h>
#include <R_ext/Utils.h>

#define MAT(X,I,J,NROW) (X)[(J) + (NROW) * (I)]
"

Cidw2 <- cfunction(signature(x = "numeric", y = "numeric", 
            v = "numeric", n = "integer", 
            xstart = "numeric", xstep = "numeric", 
            nx = "integer", ystart = "numeric", 
            ystep = "numeric", ny = "numeric", 
            power = "numeric", rat = "numeric",
			var = "numeric"), UpdateIDW_c, language = "C", includes=HeadInc, convention = ".C")

idw2 <- function (X, power = 2, at = "pixels", ...) 
{
    stopifnot(is.ppp(X) && is.marked(X))
    marx <- marks(X)
    if (is.data.frame(marx)) {
        if (ncol(marx) > 1) {
            out <- list()
            for (j in 1:ncol(marx)) out[[j]] <- idw(X %mark% 
                marx[, j], power = power, at = at, ...)
            names(out) <- names(marx)
            switch(at, pixels = {
                out <- as.solist(out)
            }, points = {
                out <- as.data.frame(out)
            })
            return(out)
        }
        else marx <- marx[, 1]
    }
    if (!is.numeric(marx)) 
        stop("Marks must be numeric")
    check.1.real(power)
    switch(at, pixels = {
        W <- as.mask(as.owin(X), ...)
        dim <- W$dim
        npixels <- prod(dim)
        z <- Cidw2(x = as.double(X$x), y = as.double(X$y), 
            v = as.double(marx), n = as.integer(npoints(X)), 
            xstart = as.double(W$xcol[1]), xstep = as.double(W$xstep), 
            nx = as.integer(dim[2]), ystart = as.double(W$yrow[1]), 
            ystep = as.double(W$ystep), ny = as.integer(dim[1]), 
            power = as.double(power), rat = as.double(numeric(npixels)),
			var = as.double(numeric(npixels)))
		#z$sd <- sqrt(z$var)
		retImg <- vector(length=2, mode="list")
		rast_names <- c("rat","var")
		for (i in 1:2){
		  outTemp <- as.im(matrix(z[[rast_names[i]]], dim[1], dim[2]), W = W)
		  retImg[[i]] <- outTemp[W, drop = FALSE]	
		}
		names(retImg) <- rast_names
    }, points = {
        npts <- npoints(X)
        z <- .C("idwloo", x = as.double(X$x), y = as.double(X$y), 
            v = as.double(marx), n = as.integer(npts), power = as.double(power), 
            rat = as.double(numeric(npts)), var = as.double(numeric(npixels)))
		#z$sd <- sqrt(z$var)
		retImg <- vector(length=2,mode="list")
		rast_names <- c("rat","var")
		for (i in 1:2){
		  outTemp <- as.im(matrix(z[[rast_names[i]]], dim[1], dim[2]), W = W)
		  retImg[[i]] <- outTemp[W, drop = FALSE]	
		}
		names(retImg) <- rast_names
    }
	)
    return(retImg)
}

#################################################################
#Functions for Bisquare weighted, input distance to consider

BiSq_weighted_c <-"
  int N, i, Nx, Ny, ix, iy;
  double xg, yg, x0, dx, y0, dy, d, d2, w, sumw, delta, mean, m2, r, sumw2, bD;
  
  N  = *n;
  Nx = *nx;
  Ny = *ny;
  x0 = *xstart;
  y0 = *ystart;
  dx = *xstep;
  dy = *ystep;
  bD = *b_dist;
  
  for(ix = 0, xg=x0; ix < Nx; ix++, xg+=dx) {
    for(iy = 0, yg=y0; iy < Ny; iy++, yg+=dy) {
      sumw = 0;
	  sumw2 = 0;
	  mean = 0;
	  m2 = 0;
	  /* loop over data points, online variance estimate, see http://stats.stackexchange.com/a/235151/1036 */
	  for(i = 0; i < N; i++) {
	    d = sqrt( (xg - x[i]) * (xg - x[i]) + (yg - y[i]) * (yg - y[i]) );
		if (d < bD) {
		  d2 = (d/bD) * (d/bD);
		  w = (1 - d2)*(1 - d2);
	      sumw += w;
	      sumw2 += w*w;
	      delta = v[i] - mean;
	      r = delta*w / sumw;
	      mean += r;
	      m2 += (sumw - w) * delta * r;
		}
	  }
	/* compute ratio and variance, replace denominator with sumw for ML estimate */
	MAT(rat, ix, iy, Ny) = mean;
	MAT(var, ix, iy, Ny) = m2 / sumw;
      }
    } 
"

CbiSq2 <- cfunction(signature(x = "numeric", y = "numeric", 
            v = "numeric", n = "integer", 
            xstart = "numeric", xstep = "numeric", 
            nx = "integer", ystart = "numeric", 
            ystep = "numeric", ny = "numeric", 
            b_dist = "numeric", rat = "numeric",
			var = "numeric"), BiSq_weighted_c, language = "C", includes=HeadInc, convention = ".C")

#need to update, if variance is null then the estimate should be null as well			
			
biSqW <- function (X, b_dist, ...) 
{
    stopifnot(is.ppp(X) && is.marked(X))
    marx <- marks(X)
    if (!is.numeric(marx)) 
        stop("Marks must be numeric")
	if (b_dist < 0)
        stop("b_dist must be a positive value")
    W <- as.mask(as.owin(X), ...)
    dim <- W$dim
    npixels <- prod(dim)
    z <- CbiSq2(x = as.double(X$x), y = as.double(X$y), 
                n = as.integer(npoints(X)), b_dist = as.double(b_dist), v = as.double(marx),
                xstart = as.double(W$xcol[1]), xstep = as.double(W$xstep), 
                nx = as.integer(dim[2]), ystart = as.double(W$yrow[1]), 
                ystep = as.double(W$ystep), ny = as.integer(dim[1]), 
                rat = as.double(numeric(npixels)),
			    var = as.double(numeric(npixels)))
	retImg <- vector(length=2, mode="list")
	rast_names <- c("rat","var")
    z$rat[is.na(z$var)] <- NaN  #those with missing variance are not a mean of zero
	for (i in 1:2){
		  outTemp <- as.im(matrix(z[[rast_names[i]]], dim[1], dim[2]), W = W)
		  retImg[[i]] <- outTemp[W, drop = FALSE]	
	}
	names(retImg) <- rast_names
    return(retImg)
}
#################################################################

#This returns images for the numerator, denominator, ratio, variance, and standard error
#the ratio is the usual IDW estimate
#the den is the sum of the weights
#num/den is then the ratio
#var is the variance, computed in the same loop!, this is the maximum likelihood variance estimate, so no Bessel correction
#sd is the standard deviation, sqrt(var)

#example use
#set.seed(10)
#n <- 100
#mydat <- runifpoint(n, win=owin(c(0,1000),c(0,1000)))
#mydat$marks <- runif(n)
#orig <- idw(mydat)
#plot(orig)
#
#test <- idw2(mydat)
#plot(test$var)
#points(mydat, pch=".", cex=10)
#
#tv <- test$rat
#sum(tv$v == orig$v)
#sum(orig$v == orig$v)
#all.equal(tv$v,orig$v) #within machine error
#
#example for bisquare kernel
#ttt <- biSqW(mydat,b_dist=100)
#as.matrix(ttt$var)
#######################################################################################