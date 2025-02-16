# MkDocs for PuePy

This is the PuePy documentation. You can see it on [docs.puepy.dev](https://docs.puepy.dev/).

## Set Up

### Cloning the repo

Start by cloning the repo and using docker compose to serve the documentation:

```
git clone git@github.com:kkinder/puepy-mkdocs.git
cd puepy-mkdocs/
```

### Initializing submodules

Because the documentation includes a peupy submodule, you need to initialize it too:

```
git submodule update --init --recursive
```

### Serving content with mkdocs

From there, you can either use docker or a local Python interpreter with poetry to serve the documentation live as you edit it. Using docker is probably simplest:

```
docker compose up
```

Documentation should be served and updated live as you edit on http://localhost:8000/

## Contribution Guide

Once you're familiar with [mkdocs](https://www.mkdocs.org) and [mkdocs-material](https://squidfunk.github.io/mkdocs-material/), you can contribute with relative ease. The project layout is:

- docs/tutorial: The step-by-step tutorial for PuePy learners
- docs/guide: The developer guide is intended to cover specific technical areas in-depth
- docs/reference: Stubs that mostly build off of auto-generated documentation from the docstrings
- docs/cookbook: Instructions on completing specific tasks

### Examples

Some examples reference code on [pyscript.com](https://pyscript.com/). Examples can be embedded inline in the docs using a special puepy tag:

```
<puepy src="(SOURCE)" edit="(EDIT)"/>
```

The source will be rendered in a stylized iframe, with an edit link for readers to experiment directly.

### Style and tips

PuePy does not have any specific style guide at this time for documentation, but docs should be written as clearly as possible, with an assumption of only standard Python programming knowledge and basic HTML/web development knowledge. When feasible, link-out to other helpful sites that might be helpful. Remember that not all readers speak English natively and unless more complex language is necessary, write to a 12th grade reading level.

Remember also that most programmers skim documentation rather than reading it, trying to find specific paragraphs that fill information in for them. Use headings and subheadings to help them find relevant information and try to write each paragraph as "atomically" as possible, such that it can be understood without context, if doing so is feasible.






