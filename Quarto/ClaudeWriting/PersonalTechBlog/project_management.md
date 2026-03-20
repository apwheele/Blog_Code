<!---
Some notes on project management
-->

Have recently participated in several projects that I think went well at the day gig -- these were big projects, multiple parties, and we came together and got to deployment on a shortened timeline. I think it is worth putting together my notes on why *I think* this went well.

My personal guiding star for project management is very simple -- have a list of things to do, and try to do them as fast as reasonably possible. This is important, as anything that distracts from this ultimate goal is not good. Does not matter if it is agile ceremonies or waterfall excessive requirement gathering. In practice if you are too focused on the bureaucracy either of them can get in the way of the core goals -- have a list of things to do and do them in a reasonable amount of time.

For a specific example, we used to have bi-weekly sprints for my team. We stopped doing them for these projects that have IMO gone well, as another group took over project management for the multiple groups. The PM just had an excel spreadsheet, with dates. I did not realize how much waste we had by forcing everything to a two week cycle. We spent too much time trying to plan two weeks out, and ultimately not filling up peoples plates. It is just so much easier to say "ok we want to do this in two days, and then this in the next three days" etc. And when shit happens just be like "ok we need to push X task by a week, as it is much harder than anticipated", or "I finished Y earlier, but I think we should add a task Z we did not anticipate".

If sprints make sense for your team go at it -- they just did not for my team. They caused friction in a way that was totally unnecessary. Just have a list of things to do, and do them as fast as reasonably possible.

## Everything Parallel

So this has avoided the hard part, what to put on the to-do list? Let me discuss another very important high level goal of project management first -- you need to do everything in parallel as much as possible.

For a concrete example that continually comes up in my workplace, you have software engineering (writing code) vs software deployment (how that code gets distributed to the right people). I cannot speak to other places (places with a mono-repo/SaaS it probably looks different), but Gainwell is really like 20+ companies all Frankenstein-ed together through acquisitions and separate big state projects over time (and my data science group is pretty much solution architects for AI/ML projects across the org).

It is more work for everyone in this scenario trying to do both writing code and deployment at the same time. Software devs have to make up some reasonably scoped requirements (which will later change) for the DevOps folks to even get started. The DevOps folks may need to work on Docker images (which will later change). So it is more work to do it in parallel than it is sequential, but drastically reduces the overall deliverable timelines. So e.g. instead of 4 weeks + 4 weeks = 8 weeks to deliver, it is 6 weeks of combined effort.

This may seem like "duh Andy" -- but I see it all the time people not planning out far enough though to think this through (which tends to look more like waterfall than agile). If you want to do things in months and not quarters, you need everyone working on things in parallel.

For another example at work, we had a product person want to do extensive requirements gathering *before* starting on the work. This again can happen in parallel. We have an idea, devs can get started on the core of it, and the product folks can work with the end users in the interim. Again more work, things will change, devs may waste 1 or 2 or 4 weeks building something that changes. Does not matter, you should not wait.

I could give examples of purely "write code as well", e.g. I have one team member write certain parts of the code first, which are inconvenient, because that component not being finished is a blocker for another member of the team. Basically it is almost always worth working harder in the short term if it allows you to do things in parallel with multiple people/teams.

Sometimes the "in parallel" is when team members have slack, have them work on more proof of concept things that *you think* will be needed down the line. For the stuff I work on this can IMO be enjoyable, e.g. "you have some time, lets put a proof of concept together on using Codex + Agents to do some example work". (Parallel is not quite the word for this, it is forseeing future needs.) But it is similar in nature, I am having someone work on something that will ultimately change in ways in the future that will result in wasted effort, but that is OK, as the head start on trying to do vague things is well worth it.

## What things to put on the list

This is the hardest part -- you need someone who understands front to back what the software solution will look like, how it interacts with the world around it (users, databases, input/output, etc.) to be able to translate that vision into a tangible list of things to-do.

I am not even sure if I can articulate how to do this in a general enough manner to even give useful advice. When I don't know things front to back though I will tell you what, I often make mistakes going down paths that often waste months of work (which I think is sometimes inevitable, no one had the foresight to know it was a bad path until we got quite a ways down it).

I used to think we should do the extensive, months long, requirements gathering to avoid this. I know a few examples where I talked for months with the business owners, came up with a plan, and then later on realized it was based on some fundamental misunderstanding of the business. And the business team did not have enough understanding of the machine learning model to know it did not make sense.

I think mistakes like these are inevitable though, as requirements gathering is a two way street (it is not reasonable for any of the projects I work on to expect the people requesting things to put together a full, scoped out list). So just doing things and iterating is probably just as fast as waiting for a project to be fully scoped out.

## Do them as fast as possible

So onto the second part, of "have a list of things to-do and do them as fast as possible". One of the things with "fast as possible", people will fill out their time. If you give someone two weeks to do something, most people will not do it faster, they will spend the full two weeks doing that task.

So you need someone technical saying "this should be done in two days". One mistake I see teams make, is listing out projects that will take several weeks to-do. This is only OK for *very* senior people. Majority of devs tasks should be 1/2/3 days of work at max. So you need to take a big project and break it down into smaller components. This seems like micro-managing, but I do not know how else to do it and keep things on track. Being more specific is almost always worth my time as opposed to less specific.

Sometimes this even works at higher levels, one of the projects that went well, initial estimates were 6+ months. Our new Senior VP of our group said "nope, needs to be 2-3 months". And guess what? We did it (he spent money on some external contractors to do some work, but by god we did it). Sometimes do them as fast as possible is a negotiation at the higher levels of the org -- well you want something by end of Q3, well we can do A and C, but B will have to wait until later then, and the solution will be temporarily deployed as a desktop app instead of a fully served solution.

Again more work for our devs, but shorter timeline to help others have an even smaller MVP totally makes sense.

## AI will not magically save you

Putting this last part in, as I had a few conversations recently about large code conversion projects teams wanted to know if they could just use AI to make short work of it. The answer is yes it makes sense to use AI to help with these tasks, but they expected somewhat of a magic bullet. They each still needed to make a functional CICD framework to test isolated code changes for example. They still needed someone to sit down and say "Joe and Gary and Melinda will work on this project, and have XYZ deliverables in two months". A legacy system that was built over decades is not a weekend project to just let the machine go brr and churn out a new codebase.

Some of them honestly are groups that just do not want to bite the bullet and do the work. I see projects that are mismanaged (for the criminal justice folks that follow me, on-prem CAD software deployments should not take 12 months). They take that long because the team is mismanaged, mostly people saying "I will do this high level thing in 3 months when I get time", instead of being like "I will do part A in the next two days and part B in the three days following that". Or doing things sequentially that should be done in parallel.

To date, genAI has only impacted the software engineering practices of my team at the margins (potentially writing code slightly faster, but probably not). We are currently using genAI in various products though for different end users. (We have deployed many supervised learning models going back years, just more recently have expanded into using genAI for different tasks though in products.)

I do not foresee genAI taking devs jobs in the near future, as there is basically infinite amounts of stuff to work on (everything when you look closely is inefficient in a myriad of ways). Using the genAI tools to write code though looks very much like project management, identifying smaller and more manageable tasks for the machine to work on, then testing those, and moving onto the next steps.




