<!---
Some notes on self-publishing a tech book
-->

So my book, *Data Science for Crime Analysis with Python*, is finally out for purchase on my [Crime De-Coder website](https://crimede-coder.com/store). Folks anywhere in the world can purchase a paperback or epub copy of the book. You can see this post on [Crime De-Coder for a preview of the first two chapters](https://crimede-coder.com/blogposts/2024/PythonDataScience), but I wanted to share some of my notes on self publishing. It was some work, but in retrospect it was worth it. Prior books I have been involved with (Wheeler 2017; Wheeler et al. 2021) plus my peer review experience I knew I did not really need help copy-editing, so the notes are mostly about creating the physical book and logistics of selling it.

![](https://crimede-coder.com/images/CoverPage.png)

Academics may wish to go with a publisher for CV prestige reasons (I get it, I was once a professor as well). But it is quite nice once you have done the legwork to publish it yourself. You have control of pricing, and if you want to make money you can, or have it cheap/free for students you can.

Here I will detail some of the set up of compiling the book, and then the bit of work to distribute it.

# Compiling the documents

So the way I compiled the book is via [Quarto](https://quarto.org/). I posted my config notes on how to get the book contents to look [how I wanted on GitHub](https://github.com/apwheele/Blog_Code/tree/master/Quarto/BookExample). Quarto is meant to run code at the same time (so works nicely for a learning to code book). But even if I just wanted a more typical science/tech book with text/images/equations, I would personally use Quarto since I am familiar with the set up at this point. (If you do not need to run dynamic code you could do it in Pandoc directly, not sure if there is a way to translate a Quarto yaml config to the equivalent Pandoc code it turns into.)

One thing that I think will interest many individuals -- you write in plain text markdown. So my writing looks like:

    # Chapter Heading
    
    blah, blah blah
    
    ## Subheading
    
    Cool stuff here ....

In a series of text files for each chapter of the book. And then I tell Quarto `quarter render`, and it turns my writing in those text files into both an Epub *and* a PDF (and other formats if you cared, such as word or html). You can set up the configuration for the book to be different for the different formats (for example I use different fonts in the PDF vs the epub, nice fonts in one look quite bad in the other). See the [`_quarto.yml` file](https://github.com/apwheele/Blog_Code/blob/master/Quarto/BookExample/_quarto.yml) for the set up, in particular config options that are different for both PDF and Epub.

One thing is that ebooks are hard to format nicely -- if I had a book I wanted to redo to be an epub, I would translate it to markdown. There are services online that will translate, they will do a bad job though with scientific texts with many figures (and surely will not help you choose nice fonts). So just learn markdown to translate. Folks who write in one format and save to the other (either Epub/HTML to PDF, or PDF to Epub/HTML) are doing it wrong and the translated format will look very bad. Most advice online is for people who have just books with just text, so science people with figures (and footnotes, citations, hyperlinks, equations, etc.) it is almost all bad advice.

So even for qualitative people, learning how to write in markdown to self-publish is a good skill to learn in my opinion.

# Setting up the online store

For awhile I have been confused how SaaS companies offer payment plans. (Many websites just seem to copy from generic node templates.) Looking at the Stripe API it just seems over the top for me to script up all of my own solution to integrate Stripe directly. If I wanted to do a subscription I may need to figure that out, but it ended up being for my Hostinger website I can set up a sub-page that is Wordpress (even though the entire website is not), and turn on WooCommerce for that sub-page. 

WooCommerce ends up being easy, and you can set up the store to host web-assets to download on demand (so when you purchase it generates a unique URL that obfuscates where the digital asset is saved). No programming involved to set up my webstore, it was all just point and click to set things up one time and not that much work in the end.

I am not sure about setting up any DRM for the epub (so in reality people will purchase epub and share it illegally). I don't know of a way to prevent this without using Amazon+Kindle to distribute the book. But the print book should be OK. (If there were a way for me to donate a single epub copy to all libraries in the US I would totally do that.)

I originally planned on having it on Amazon, but the low margins on both plus the formatting of their idiosyncratic kindle book format (as far as I can tell, I cannot really choose my fonts) made me decide against doing either the print or ebook on Amazon.

# Print on Demand using LuLu

For print on demand, I use [LuLu.com](https://www.lulu.com/). They have a nice feature to integrate with WooCommerce, the only thing I wish shipping was dynamically calculated. (I need to make a flat shipping rate for different areas around the globe the way it is set up now, slightly annoying and will change the profit margins depending on area.)

LuLu is a few more dollars to print than Amazon, but it is worth it for my circumstance I believe. Now if I had a book I expected to get many "random Amazon search buys" I could see wanting it on Amazon. I expect more sales will be via personal advertising (like here on the blog, social media, or other crime analyst events). My Crime De-Coder site (and this blog) will likely be quite high in google searches for some of the keywords fairly quickly, so who knows, maybe just having on personal site is just as many sales.

LuLu does has an option to turn on distribution to other wholesalers (like Barnes & Noble and Amazon) -- have not turned that on but maybe I will in the future.

LuLu has a pricing calculator to see how much to print on their website. Paperback and basically the cheapest color option for letter sized paper (which is quite large) is just over $17 for my 310 page book (Amazon was just over $15). For folks if you are less image heavy and more text, you could get away with a smaller size book (and maybe black/white) and I suspect will be much cheaper. LuLu's printing of this book is higher quality compared to Amazon as well (better printing of the colors and nicer stock for the paperback cover).

Another nice thing about print on demand is I can go in and edit/update the book as I see fit. No need to worry about new versions. Not sure what that exactly means for citing the work (I could always go and change it), you can't have a static version of record and an easy way to update at the same time.

# Other Random Book Stuff

I purchased ISBNs on [Bowker](https://www.myidentifiers.com/), something like 10 ISBNs for $200. (You want a unique ISBN for each type of the book, so you may want three in the end if you have epub/paperback/hardback.) Amazon and LuLu though have options to have them give you an ISBN though, so that may have not been necessary. I set the imprint to be my LLC though in Bowker, so CRIME De-Coder is the publisher.

You don't technically need an ISBN at all, but it is a simple thing, and there may be ways for me to donate to libraries in the future. (If a University picks it up as a class text, I have been at places *you need* at least one copy for rent at the Uni library.)

I have not created an index -- I may have a go at feeding my book through LLMs and seeing if I can auto-generate a nice index. (I just need a list of key words, after that can just go [and find-replace the relevent text in the book](https://quarto.org/docs/books/book-structure.html#creating-an-index) to fill in so it auto-compiles an index.) I am not sure that is really necessary though for a how-to book, you should just look at the table of contents to see the individual (fairly small) sections. For epub you can just doing a direct text search, so not sure if people use an index at all in epubs.

# Personal Goals

So I debated on releasing the book open source, I do want to try and see if I can make some money though. I don't have this expectation, but there is potential to get some "data science" spillover, and if that is the case sales could in theory be quite high. (I was surprised in searching the "data science python" market on Amazon, it is definitely not saturated.) Personally I will consider at least 100 sales to be my floor for success. That is if I can sell at least 100 copies, I will consider writing more books. If I can't sell 100 copies I have a hard time justifying the effort -- it would just be too few of people buying the book to have the types of positive spillovers I want.

To make back money relative to the amount of work I put in, I would need more than 1000 sales (which I think is unrealistic). I think 500 sales is about best case, guesstimating the size of the crime analyst community that may be interested plus some additional sales for grad students. 1000 sales it would need to be in the multiple professors using it for a class book over several years. (Which if you are a professor and interested in this for a class let me know, I will give your class a discount.)

Another common way for individuals to make money off of books is not for sales, but to have training's oriented around the book. I am hoping to do more of that for crime analysts directly in the future, but those opportunities I presume will be correlated with total sales.

I do enjoy writing, but I am busy, so cannot just say "I am going to drop 200 hours writing a book". I would like to write additional python topics oriented towards crime analysts/criminology grad students like:

 - GIS analysis in python
 - Regression
 - Machine Learning & Optimization
 - Statistics for Crime Analysis
 - More advanced project management in python

Having figured out much of this grunt work definitely makes me more motivated, but ultimately in the end need to have a certain level of sales to justify the effort. So please if you like the blog pick up a copy and tell a friend you like my work!

# References

 - Wheeler, A.P. (2024) [*Data Science for Crime Analysis with Python*. CRIME De-Coder. ISBN 979-8-9903770-1-1](https://crimede-coder.com/blogposts/2024/PythonDataScience)
 - Wheeler, A.P. (2017) Geospatial analytics. [In *SPSS® Statistics for Data Analysis and Visualization*. Eds. McCormick, K. & Salcedo J., with contributions by Peck J. & Wheeler, A.P. Wiley. ISBN 978-1119003557](https://www.amazon.com/SPSS-Statistics-Data-Analysis-Visualization/dp/1119003555)
 - Wheeler, A.P., Herrmann C.R., & Block R.L. (2021). [*Micro-place homicide patterns in Chicago*. Springer. ISBN 978-3-030-61445-4](https://link.springer.com/book/10.1007/978-3-030-61446-1)