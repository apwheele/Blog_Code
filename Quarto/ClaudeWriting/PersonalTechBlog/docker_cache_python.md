<!---
Recommend reading The Idea Factory, Docker tips
-->

A friend recently recommended [*The Idea Factory: Bell Labs and the Great Age of American Innovation*](https://www.amazon.com/Idea-Factory-Great-American-Innovation/dp/0143122797) by Jon Gertner. It is one of the best books I have read in awhile, so also want to recommend to the readers of my blog.

![](https://upload.wikimedia.org/wikipedia/en/9/92/The_idea_factory_gertner.jpg)

I was vaguely familiar with Bell Labs given my interest in stats and computer science. John Tukey makes a few honorable mentions, but Claude Shannon is a central character of the book. What I did not realize is that almost *all* of modern computing can be traced back to innovations that were developed at Bell Labs. For a sample, these include:

 - the transistor
 - fiber optic cables (I did not even know, fiber is very thin strands of glass)
 - the cellular network with smaller towers
 - satellite communication

And then you get smattering of different discussions as well, such as the material science that goes into making underwater cables durable and shark resistant.

The backstory was that AT&T in the early 20th century had a monopoly on landline telephones. Similar now to how most states have a single electric provider -- they were a private company but blessed by the government to have that monopoly. AT&T intentionally had a massive research arm that they used to improve communications, but also they provided that research back into the public coffers. Shannon was a pure mathematician, he was not under the gun to produce revenue.

Gertner basically goes through a series of characters that were instrumental in developing some of these ideas, and in creating and managing Bell Labs itself. It is a high level recounting of Gertner mostly from historical notebooks. One of the things I really want to understand is how institutions even tackle a project that lasts a decade -- things I have been involved in at work that last a year are just dreadful due to transaction costs between so many groups. I can't even imagine trying to keep on schedule for something so massive. So I do not get that level of detail from the book, just moreso someone had an idea, developed a little tinker proof of concept, and then Bell Labs sunk a decade an a small army of engineers to figure out how to build it in an economical way.

This is not a critique of Gertner (his writing is wonderful, and really gives flavor to the characters). Maybe just sinking an army of engineers on a problem is the only reasonable answer to my question.

Most of the innovation in my field, criminal justice, is [coming from the private sector](https://andrewpwheeler.com/2025/06/12/build-stuff/). I wonder (or maybe hope and dream is a better description) if a company, like Axon, could build something like that for our field.

------------

Part of the point for writing blog posts is that I do the same tasks over and over again. Having a nerd journal is convenient to reference.

One of the things that I do not have to commonly do, but it seems like once a year at my gig, I need to putz around with Docker containers. For note for myself 1, when building python apps, to get the correct caching you want to install the libraries first, and then copy the app over.

So if you do this:

    FROM python:3.11-slim
    COPY . /app
    RUN pip install --no-cache-dir -r /app/requirements.txt
    CMD ["python", "main.py"]

Everytime you change a single line of code, you need to re-install all of the libraries. This is painful. (For folks who like uv, this does not solve the problem, as you still need to *download* the libraries everytime in this approach.

A better workflow then is to copy over the single requirements.txt file (or .toml, whatever), install that, and then copy over your application.

    FROM python:3.11-slim
    COPY requirements.txt ./
    RUN pip install --no-cache-dir -r requirements.txt
    COPY . /app
    CMD ["python", "main.py"]

So now, only when I change the `requirements.txt` file will I need to redo that layer.

Now I am a terrible person to ask about dev builds and testing code in this set up. I doubt I am doing things the way I should be. But most of the time I am just building this.

    docker build -t py_app .

And then I will have logic in `main.py` (or swap out with a `test.py`) that logs whatever I need to the screen. Then you can either do:

    docker run --rm py_app

Or if you want to bash into the container, you can do:

    docker run -it --rm py_app bash

Then from in the container you can go into the python REPL, edit a file using vim if you need to, etc.

Part of the reason I want data scientists to be full stack is because at work, if I need another team to help me build and test code, it basically adds 3 months at a minimum to my project. Probably one of the most complicated things myself and team have done at the day job is figure out the correct magical incantations to properly build ODBC connections to various databases in Docker containers. If you can learn about boosted models, you can learn how to build Docker containers.