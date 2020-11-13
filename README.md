# Shirokuma-Cafe

## version 1.0

Built with [R-Studio](https://rstudio.com/) and [Audacity](https://www.audacityteam.org/).

The idea of this project was to aid in Japanese language immersion and reading practice. While one could just watch the videos with Japanese subtitles, I find that just focusing on the text and audio alone is much better for reading and listening practice at the same time. I think of it as kind of like "training wheels" for Japanese literacy and helping to associate symbols with sounds directly.

Recent changes:

I automated the process of adding file names to the `<audio>` tags by using javascript to add the src attribute to them which makes it much easier to produce a new episode. It's all written in markdown and then Rstudio uses pandoc behind the scenes to generate the html files and javascript fills out the appropriate details both adding a play button and pointing it to each audio file.
