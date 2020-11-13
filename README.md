# Shirokuma-Cafe

## version 1.0

Built with [R-Studio](https://rstudio.com/) and [Audacity](https://www.audacityteam.org/).

The idea of this project was to aid in Japanese language immersion and reading practice. While one could just watch the videos with Japanese subtitles, I find that just focusing on the text and audio alone is much better for reading and listening practice at the same time. I think of it as kind of like "training wheels" for Japanese literacy and helping to associate symbols with sounds directly. In addition since the html files are viewed in a browser, you can use an extension like Yomichan for easily looking up the meanings of words and kanji. There is no translation included since I find that relying on translation serves as a crutch that might make it easier to understand in the short term, but does get in the way of learning how to read in Japanese.

### Recent changes

I automated the process of adding file names to the `<audio>` tags by using javascript to add the src attribute to them which makes it much easier to produce a new episode. It's all written in markdown with a tiny bit of html thrown in and then Rstudio uses pandoc behind the scenes to generate the html files and javascript fills out the appropriate details both adding a play button and pointing it to each audio file. 
