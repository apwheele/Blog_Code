<!---
Setting conda environments in crontab
-->

I prefer using conda environments to manage python (partly out of familiarity). Conda is a bit different though, in that it is often set up locally for a users environment, and not globally as an installed package. This makes using it in bash scripts (or on windows `.bat` files) somewhat tricky.

So first, in a Unix environment, you can choose where to install conda. Then it adds into your `.bashrc` profile a line that looks something like:

    __conda_setup="$('/mnt/miniconda/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
    if [ $? -eq 0 ]; then
        eval "$__conda_setup"
    else
        if [ -f "/lib/miniconda/etc/profile.d/conda.sh" ]; then
            . "/lib/miniconda/etc/profile.d/conda.sh"
        else
            export PATH="/lib/miniconda/bin:$PATH"
        fi
    fi
    unset __conda_setup

Where here I installed it in `/lib`. This looks complicated at first glance, but really all it is doing is sourcing the `conda.sh` script and pre-pending `miniconda/bin` to the path.

Now to be able to run python code on a regular basis in crontab, I typically have crontab run shell scripts, not python directly, so say that is a file `run_code.sh`:

    #!/bin/sh
    
    # Example shell script
    time_start=`date +%Y_%m_%d_%H:%M`
    echo "Begin script $time_start"
    
    # Sourcing conda
    source /lib/miniconda/etc/profile.d/conda.sh
    
    # activating your particular environment
    # may need to give full path, not just the name
    conda activate your_env
    
    # if you want to check environment
    python --version
    
    # you may need to change the directory at this point
    echo "Current Directory is set to $PWD"
    cd ...
    
    # run your python script
    log_file="main_log_$time_start.txt"
    python main.py > $log_file 2>&1

I do not need to additionally add to the path in my experience, just sourcing that script is sufficient. Now edit your crontab (via `crontab -e` and using the VI editor) to look something like:

    20 3 * * * bash /.../run_code.sh >> /.../cron_log.txt 2>&1

Where `/.../` is shorthand for an explicit path to where the shell script and cron log lives.

This will run the shell script at 3:20 AM and append all of the stuff. In crontab if you just want conda available for all jobs, *I believe* you could do something like:

    # global environment, can set keys, run scripts
    some_key=abc
    export some_key
    source /lib/miniconda/etc/profile.d/conda.sh

    20 3 * * * bash /.../run_code.sh >> /.../cron_log.txt 2>&1

But I have not tested this. If this works, you could technically run python scripts directly, but if you need to change environments you would still really need a shell script. It is good to know to be able to inject environment variables though in the crontab environment.

About the only other gotcha is file permissions. Sometimes in business applications you have service accounts running things, so a crontab as the service account. And you just need to make sure to `chmod` files so the service account has appropriate permissions. I tend to have more issues with log files by accident than I do conda environments though.

Note for people setting up scheduled jobs on windows, I have an example of setting a conda environment in a [windows bat file](https://github.com/apwheele/Blog_Code/blob/master/Python/jupyter_reports/ExampleBat.bat).

Additional random pro-tip with conda environments while I am here -- if you by default don't want conda to set up new environments in your home directory (due to space or production processes), as well as download packages into a different cache location, you can do something like:

    conda config --add pkgs_dirs /lib/py_packages
    conda config --add envs_dirs /lib/conda_env

Have had issues in the past of having too much junk in home.


