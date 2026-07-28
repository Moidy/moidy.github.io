# moidy.github.io

Personal portfolio site — live at **[moidy.github.io](https://moidy.github.io)**.

Built with Jekyll and hosted on GitHub Pages. The index showcases selected projects; each project has a full write-up reachable via `/projects/<name>/`.

## Local preview

Requires Ruby. First-time setup:

```powershell
gem install bundler
bundle install
```

Then to serve with live reload:

```powershell
bundle exec jekyll serve --livereload
```

Site is available at `http://localhost:4000`.

## Adding a project

1. Create `_projects/your-project-name.md` with front matter:

```yaml
---
title: Project Name
subtitle: One-line descriptor
status: Active          
image: /img/folder/main-image.png
image_alt: Description of the image
tags: [Python, SomeLib, AnotherThing]
gallery:                
  - src: /img/folder/extra.png
    alt: Description
---

Write the blog post content here in Markdown.
```

2. Add a card to `index.html` following the existing pattern, with a `data-tags` attribute matching the filter categories (`ai`, `audio`, `streaming`, `web`, `social`) and a `card-read-more` link pointing to `/projects/your-project-name/`.

3. Drop images into `img/<project-folder>/`.

## Branch rules

`main` is protected — all changes go through a pull request.

```
git checkout main && git pull
git checkout -b fix/your-change
# make changes
git add . && git commit -m "Description"
git push --set-upstream origin fix/your-change
# open PR on GitHub
```
