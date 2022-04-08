#  .libPaths()
# should point to the correct location inside 
# conda environment

library(devtools)

# Install specific commit/version from github
install_github("apwheele/ptools",ref=" 9826241c93e9975804430cb3d838329b86f27fd3")

# Specifying specific version url for cran package (not on conda-forge)
gh_url <- "https://cran.r-project.org/src/contrib/groundhog_1.5.0.tar.gz"
install.packages(gh_url,repos=NULL,type="source")

library(ptools)
library(groundhog)