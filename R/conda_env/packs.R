#  .libPaths()
# should point to the correct location inside 
# conda environment

library(devtools)
install_github("apwheele/ptools")

# Specifying specific version url
gh_url <- "https://cran.r-project.org/src/contrib/groundhog_1.5.0.tar.gz"
install.packages(gh_url,repos=NULL,type="source")

library(ptools)
library(groundhog)