# Translating book using OpenAI

This is a simple python example of translating my book, [Data Science for Crime Analysis with Python](https://crimede-coder.com/blogposts/2024/PythonDataScience).

The environment is pretty tame, to do the translation, it is just base python and openai, e.g.

    pip install openai --upgrade

Should be fine. And this uses the `OPENAI_API_KEY` environment variable.

Then just run (need to make command line configs for different languages)

    python translate_quarto.py

This will not be 100%, will just do the `.qmd` files, and try to be smart about not translating code snippets and other specific markdown. If you want to change the title, ISBN, copyright statements, you will need to do that manually. (No doubt you could make a smarter parser to make 100% sure special markdown is not converted.)

The cost to translate the entire book (not just these chapters) to French was $6.69. Translation to Spanish was $6.43.

