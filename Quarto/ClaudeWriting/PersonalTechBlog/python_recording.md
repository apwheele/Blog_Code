<!---
Recording your mouse and keyboard with python
-->


The differently LLM providers have released computer use tools, [Google's Gemini](https://ai.google.dev/gemini-api/docs/computer-use) being one of the most recent ones. They way these work, it submits and image, and then does tasks given general instruction, actually manipulating the mouse and keyboard, asking for human in the loop input at various stages, etc. They seem cool but I am lacking clear examples where I would use them.

They really make sense for very complicated workflows that vary. The things that make the most sense to spend some time trying to automate though are boring things -- things that have a specific set of inputs and outputs, and the machine can entirely make those route decisions based on rules you define at the onset. When I was a crime analyst, I worked with all sorts of janky and old desktop software that I would need to generate reports and email those results to key individuals for example.

Here as a day project, I created a set of python functions to record your keyboard and mouse inputs, and then replay those inputs. The [python code is here](https://github.com/apwheele/Blog_Code/tree/master/Python/record_keyboard_mouse), it ends up being pretty simple (mostly written by ChatGPT and slightly modified by me). And here is a YouTube video demonstration showing what you can do.

https://www.youtube.com/watch?v=mA8XSCCvyQE

So even if you have software that does not have an easy way to integrate with other code, here you can just record your movements and replay them with python on a schedule to accomplish that monotonous task.