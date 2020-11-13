### How to roll your own

This project was built with the following open source tools:

**Rstudio**: an IDE developed for the programming language R, but which is also a great front end for pandoc which is another open source program that converts one document type to another. The basic idea here is that Rstudio allows you to write plain text files, add bits of html as you need to, format things with the simple syntax of markdown and have it automatically generate a static website. There is no need to write tons of html code since pandoc does it for you.

**ffmpeg**: a program for manipulating multimedia files. It is what I use for extracting the audio from the orginal video files. There are lots of ways to do this, but ffmpeg enables you to type one line on the command line and it automagically extracts the audio to an .mp3 file.

**Audacity**: an easy to use but powerful audio editing tool. I use this to extract audio clips with dialogue.


#### Step 0: Prequisites

First you'll need to install [Rstudio](https://rstudio.com/products/rstudio/), [ffmpeg](https://ffmpeg.org/) and [Audacity](https://www.audacityteam.org/). Depending on your machine those might require additional software as dependencies but it's all free and open source. I use linux Mint on my computer, but this all should work on machines running other operating systems.

In addition to this software you'll also need the Japanese subtitle files rather than substitles that are hard coded into the video. Many are available at [kitsuneko](https://kitsunekko.net/). Typically these are in the form of .ass or .srt files which are just plain text files with lots of additional code with timestamps that tell your video player when to insert each line. I clean these of extra code in a text editor (knowledge of regular expressions helps make this much easier) and use the resulting plain text files.

#### Step 1: Create a new Rstudio project.

From the Rstudio main menu select "File" > "New Project" then choose "simple R Markdown website", give it a name and put it in whatever location you want. (NOTE: if you do not see this option in RStudio, you will have to first install the package called "rmarkdown" in the packages tab wihch should appear in the lower left pane of Rstudio. I forget whether this is installed by default.)  This creates a directory with the name you gave it as well as four files:

`_site.yml` which has basic configuration instructions for the site.

`your-folder-name.Rproj` which just stores information about your project for Rstudio's use.

And two .Rmd files. `about.Rmd` and `index.rmd` which will be used to create two html pages `about.html` and `index.html`. This is the default setup and you can add as many additional pages as you want and remove the `about.Rmd` file if you dont want it.

#### Step 1.5: Configure site

By default your site will have an `index.html` page and an `about.html` page, will use a default theme and will have a simple top menu with links to these pages. All of that can be changed by editing the `_site.yml` page. By default it looks like this:

```

name: "my-website"
navbar:
  title: "My Website"
  left:
    - text: "Home"
      href: index.html
    - text: "About"
      href: about.html


```

If you edit this be careful with indentation, since pandoc is pretty picky about consistent indentation. Change the title to your own title and if you don't want the "About" page remove those two lines. You can also add more menu items if you like. Other [configuration options can be found here](https://bookdown.org/yihui/rmarkdown/rmarkdown-site.html) that enable you to pick other themes and so on.

If you are using my orginal github repo as the starting point for your project, you'll need to add the following to the `_site.yml' file.

```
output:
  html_document:
    theme: simplex
    includes:
      after_body: "includes/footer.html"
    css: "includes/style.css"

```

Indenting should look just like that. There are [other themes available](https://www.datadreaming.org/post/r-markdown-theme-gallery/) if you like. The "includes" are for modifying the orginal stylesheet and for adding javascript that will automatically add audio play buttons and references to the individual audio files. These are in a subdirectory called "includes" in this example and on the [github repo](https://github.com/gwmatthews/Shirokuma-Cafe) where all of this stuff lives.

#### Step 2: Extract audio

All of this assumes that you have a copy of the relevant video files. I start with .mkv files, but other formats will work as well as long as you adjust the command below accordingly.

`ffmpeg -i file.mkv -f mp3 -ab 192000 -vn file.mp3 `

I keep all of the original files in a media folder which is then NOT uploaded to github because that would violate copyrights. I believe that uploading the extacted clips is fine from a legal and ethical standpoint since it strikes me as "Fair Use" -- it is not for profit, and involves changes to the originals for a use which is for educational purposes and is substantially different than that of the orginal. This is not a legal opinion, but my sense of things at this point. Should this use of the audio be a violation of copyright, I'll quit sharing things, but for now it seems legit to me.

#### Step 3: Extract audio clips

I use Audacity for this as it has a simple workflow but you can use other audio editing tools if you like. 

Useful keyboard shortcuts:

- `[spacebar]` starts and stops play.
- `[` While audio is playing, pressing the left square bracket key marks the beginning of a selection.
- `]` and the right square bracket key marks the end.
- `[ctrl + b]` adds a "label" to the actively selected part of the audio file. This will be useful for exporting multiple audio clips all at once later. The first time you do this a new track will be created to hold the labels. Note that adding a label also makes the label track the active one so you will have to use the up arrow to move back to the audio track before continuing. Once you get the basic idea down you can pretty quickly add labels to segments of audio while the file is playing. Labels are what Audacity will use to extract indivudal segments of the orginal audio file as a series of individual sound clip files. Each label has a box for a title, but those can remain blank.

You can adjust the beginning and ending points of each label by clicking and dragging on the arrow shaped handles on either side of each.

When you are done adding labels to the whole audio file "File" > "Export" > "Export Multiple" opens up a dialogue box that enables you to save all labelled bits as individual files. By default it will save them all as a sequence of numbered files starting with "Untitled-1.mp3" if you save them as .mp3 files. I use a medium quality to make the files smaller. 

##### Side note: file organization and naming conventions

I export all audio files to an `audio/x/` subdirectory where `x` is the number of the episode. I rename them all starting with `0.mp3` in numbered sequence. The numbering is used by the javascript code that gets stuck in the end of each page to find the right file later. Each episode is titled `project-name-x.html`. This keeps things consistent for doing the next step. 


#### Step 4: Create a page for each set of audio files.

- Copy the extracted subtitle text to a new Rmd file. It should have this at the very top:

```
---
title: "your title"

---
```

The two sets of three dashes are a yaml header that contains the minimum meta-data for generating an html page with this system.

Assuming you are using my orginal repo on gihub for your project with the rest of the file looks like this:

```

<span id="episode-title" data-episode="01">シロクマ　カフェー へようこそ</span>

<audio></audio><hr>

笹を食べながらのんびりするのは最高だなぁ

```

The first line is the first line of the audio which I use as a title for the episode. The `id="episode-title"` tells the javascript where to look for the episode number which is in the `data-episode=` attribute. This corresponds the name of the directory the audio files are.

The `<audio>` tags don't need anything else since they get loaded with the correct file numbers as sources by the javascript. So you just need to copy that snippet just below each bit of text and the corresponding audio file will get attached to a button that plays it. Check out the javascript in the orginal [footer.html file](https://github.com/gwmatthews/Shirokuma-Cafe/blob/master/includes/footer.html). It's pretty minimal -- it just saves me having to do a of extra editing of file locations and names and ads a nicer looking play button than the default html audio player.


#### Step 5: Add links to home page

That's pretty much it. You can add links to each episode file like so:

`(title)[filename-01.html]`
 
 You do this for each Rmd file you create for an episode or part of your project. When you build the site after a change it **should** all work just like this site. 🤞 




