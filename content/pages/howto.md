Title: How to use this blog
Date: 2015-01-16
Tags: howto, blog
Slug: howto
Author: arnulf.heimsbakk@met.no
Modified: 2015-03-12

[Pelican]: http://docs.getpelican.com/en/3.5.0/content.html
[github]: https://github.io

This is a short HowTo on how this blog is updated. To update the blog you need access to the git repository on [github].

## Pre request

This blog is generated by [Pelican]. To start with we need to install the blog engine and check out the Git repository on [github] where the blog resides.

### Install Pelican 

Start with installing latest version of the Pelican blog engine. 

```bash
sudo apt-get install python-pip git 
sudo pip install pelican markdown ghp-import docutils pygments feedgenerator unidecode
```

### Check out the blog

Make a local copy of the blog repository.

```bash
git clone --recurse-submodules git@github.com:metno/metno.github.io.git
```

## Add an article 

Now we are going to add an article to the blog. 

- Go into the git repository and ensure that you are on the blog branch.

```bash
cd metno.github.io 
git checkout blog
```

- Ensure you have the latest updates.

```bash
git pull
```

- Add your article under `blog` in `content` folder. Tips is to use `YYYYMMDD-` as a prefix for your filename.

```bash
cd content/blog
vim 20150116-example-article.md
```

- Fill out the standardized header of the blog.

```
Title: Example title
Date: 2015-01-16
Tags: example, tag, list 
Slug: example
Author: example.name@met.no
Status: draft

Example ingress.

## Examle headline

New example paragraph here.
```

- Remove the `Status: draft` when you are ready to publish the article.

- Add the new article to the git repository and push it to github.

```bash
git add 20150116-example-article.md
git commit -a -m "Added example article"
git push
```

- Publish the article by generating the blog from the main folder of the repository.

```bash
make github
```

Since I didn't remove the `Status: draft` of this example, it is accessible under the draft folder on the blog [/drafts/example.html](/drafts/example.html).


###### vim: set syn=markdown spell spl=en:


