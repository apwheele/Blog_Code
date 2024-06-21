# Compile notes

So the usual:

    quarto render test.qmd

Works as expected. If you have word installed on your computer, and the python library [docx2pdf](https://pypi.org/project/docx2pdf/) installed, you can then do:

    quarto render test.qmd
    docx2pdf test.docx

If you are like me and use conda on Windows, you can often do something like this in a `.bat` file:

    @echo on
    set "base=%cd%"
    set conda_act=D:\Python\Scripts\activate.bat
    call %conda_act%
    call conda activate <your_environment>
    call quarto render test.qmd
    call docx2pdf test.docx

A minimal python environment for this to work is something like:

    requests
    pandas
    tabulate
    matplotlib
    notebook==6.4.12
    nbconvert[webpdf]
    jupyter_contrib_nbextensions
    jupyter-cache
    docx2pdf

Jupyter is super annoying, so this is my default python environment for that. (And you don't technically need `nbconvert` for this, but whatever.) I wish the `tabulate` library was default with pandas -- superhelpful to format tables in notebooks.

# Working with the template

So if you do 

    quarto pandoc -o custom-reference-doc.docx --print-default-data-file reference.docx

That will produce a default template. I don't even know how I figured out how to get the tables to inherit correctly anymore (it is not straightforward, something to do with the change in the default Table vs TableNormal or something like that in the newer docx).

Tables to me are super-important, so I spent much time getting a nice looking default table that works nicely with Quarto/Pandoc. So you can set the column format mostly the in Python side using the Ipython function `Markdown`, and they turn into nice word tables. Tables and different elements in the default template share certain things, so if you change one they sometimes propogate to the other (so I can't figure out how to make a table have a different default font for example).

See some of the notes about multi-column layouts in the qmd file. If you want multi-column *without* borders, you need to not have a border in your default tables.

# Using DocX

These are notes for myself for future, in Powershell word to PDF has a few more bells & whistles than are currently exposed in the python docx2pdf library:

 - <https://gist.github.com/mkoertgen/2087bacda9cff0fa68aa> shows using powershell directly
 - <https://github.com/AlJohri/docx2pdf/blob/master/docx2pdf/__init__.py> is where the magic happens calling the wincom32 processes (on windows).

So if there is something I can figure out directly in word, I can maybe patch `docx2pdf` (or call the windows process directly).

# LibreOffice

Now, above in a fully automated process relies on word being installed, which is really only possible on windows machines (I don't think you can install anything like that in unix environment). An alternative is LibreOffice, which once installed you can then do:

    soffice --headless --convert-to pdf test.docx

And works decently with this template (I intentionally changed some aspects of the header/footer so they do work out nice). Now really the only thing I have not figured out in this way is that the *table of contents* is not auto-rendered (and I cannot figure out how to do that). So if you know how to make a python (or some other script) to auto-render the TOC in this file I would appreciate letting me know!

Otherwise you can open the docx file in libreoffice, manually create the TOC, and export to PDF. Here is my current attempt to write a python script to do this, but is unsuccessful, first you need to run:

    soffice --writer --accept="socket,host=localhost,port=2002;urp;StarOffice.ServiceManager" test.docx

And then in a seperate process start up python:

    import uno
    
    url = r"G:\Blog_Code\Quarto\ReportTemplate\test.docx"
    document = desktop.loadComponentFromURL(url, "_blank", 0, ())
    
    localContext = uno.getComponentContext()
    resolver = localContext.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", localContext)
    context = resolver.resolve("uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext")
    desktop = context.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", context)
    document = desktop.getCurrentComponent()
    
    # searching
    stext = "Table of contents"
    search = document.createSearchDescriptor()
    search.SearchString = stext
    search.SearchWords = True  # Match whole words
    found_range = document.findFirst(search)
    
    # setting the cursor
    #cursor = document.Text.createTextCursor()
    #cursor = document.getCurrentController().getViewCursor()
    cursor = document.Text.createTextCursor()
    cursor.gotoRange(found_range,1)
    
    # creating the toc
    toc = document.createInstance("com.sun.star.text.ContentIndex")
    toc.setPropertyValue("Level", 1)
    toc.CreateFromOutline = True
    
    # now setting and updating the TOC
    #cursor = document.Text.createTextCursor()
    document.Text.insertTextContent(cursor, toc, 1)
    #document.Text.insertString(cursor, 'Hello world!', 1)
    #toc.update()

And this to be clear does not work to update the TOC! It does work to insert a "hello world" string in the document.

Or if you have an alternate (would like a way in Unix to go `word -> nice pdf`, to create automated reports in different environments).