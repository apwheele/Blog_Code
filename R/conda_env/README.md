# Managing R environments with Conda

This is an example folder on how [to use conda to manage an R environment](https://docs.anaconda.com/anaconda/user-guide/tasks/using-r-language/).

First, from the command line (or more specifically an Anaconda command prompt), you can run:

    conda create --name rnew
    conda activate rnew
    conda install -c conda-forge r-base=4.0.5 --file requirements.txt

The specified `requirements.txt` file should have the libraries listed, on conda-force they need to have a particular set up with `r-*` format:

    # This is the requirements.txt file
    r-spatstat
    r-leaflet
    r-devtools
    r-markdown

And then conda will handle pulling in these libraries and installing into the correct location. 

If you have additional libraries, you can create a second script, here I name it `packs.R`, that has the specific libraries you want to install:

    # This is the packs.R script
    library(devtools) # for install github packages
    
    # Install specific commit/version from github
    install_github("apwheele/ptools",ref=" 9826241c93e9975804430cb3d838329b86f27fd3")
    
    # Install a specific library version from CRAN
    # Specifying specific version url for cran package (not on conda-forge)
    gh_url <- "https://cran.r-project.org/src/contrib/groundhog_1.5.0.tar.gz"
    install.packages(gh_url,repos=NULL,type="source")
    
    # Load the libraries just to make sure they are OK
    library(ptools)
    library(groundhog)

And then back at the command line, can run:

    Rscript packs.R

And your environment will be complete. Note if you want to specify uber specific packages, you may then wish to export the packages from the conda environment back into a more specific requirements.txt file, e.g.

    conda list --export > requirements.txt