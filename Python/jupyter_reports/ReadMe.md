# ReadMe

To replicate the results, first run at the command line (have the current directory at the location for these files, e.g. `cd C:\Users\whatever`):

    python 00_CreateDB.py

This should create a sqlite DB named `DPD.sqlite` in the folder, and update to the newest Dallas PD data on the open data portal.

Then to create the nice, report HTML file, run:

    jupyter nbconvert --execute example_report.ipynb --no-input --to html

The code `01_CreateReport.py` shows how to insert the current date into the report html file name (e.g. save it as `report_2021_07_09.html` instead of `report_example.html`), for if you want to keep various versions of the report over time. (So just run `python 01_CreateReport.py` at the command line.)

If you want to view the notebook and the underlying code, just run `jupyter notebook` from the command line and then navigate to the notebook in the folder.

# Fully Automating

The above command line suggestions are still not 100% automated (you would need to log into the system and run the commands). You can however fully automate this if you can have your computer consistently running, and schedule a system task. [See here for an example running R scripts](https://trinkerrstuff.wordpress.com/2015/02/11/scheduling-r-tasks-via-windows-task-scheduler/), but it works the same way when you have a bat file that runs your script all the way.

On Windows with conda, it is sometimes more difficult to get the python path recognized. I have provided a file on how to do this at the windows command prompt in the  `ExampleBat.bat` file. (If on Mac I assume you can do `.sh` files and use the `chron`, same as on Unix?)

# PDF?

You can compile directly to PDF using either Latex as a go-between or webpdf directly. Here is an example using webpdf:

    jupyter nbconvert --execute example_report.ipynb --no-input --to webpdf --allow-chromium-download

I have a harder time getting this to look nice though and get all the page breaks you want, so user beware.

# ToDo

 - Example slides
 - Example markdown with inline items
 - Example interactive table (?plotly?)
 - Example interactive graph (?plotly?)
 - Example slippy map (Folium)
 - Example email the report

# What is python?

If you are unfamiliar with what python is, I suggest you download the [Anaconda python distribution](https://www.anaconda.com/products/individual). It is free, and will come with all the typical packages you need to do number crunching. Then you should be able to run commands at the command line (or use the Conda shell), like above.