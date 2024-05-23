# How to use
The actual site is built by running the `driver.py` in the `site_manager` directory.

To create a new article just write it in the blod_md directory, it must start with a title and date of the format:

`# Title`  
`Month Day, Year`

From there just run the `driver.py` script as `python3 driver.py -cbu` to convert the markdown to html and update the `articles.html` page and `index.html` page with the new links to the article.

Any changes to the site itself (besides styling) should be done in the `templates` directory, such as changes to the layout of the navigation bar. After these changes are done run `python3 driver.py -r` to refresh all the pages within the site to have these updates.

# Layout

.  
├── blog_md  
├── docs  
├── project_md  
├── site_manager  
└── templates  

**blog_md:** Contains the markdown articles  
**docs:** Contains the built site  
**project_md:** Contains the makrdown projects  
**site_manager:** Contains the scripts used to build the site  
**templates:** Contains the html parts used to generate teh site