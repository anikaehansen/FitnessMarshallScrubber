
<!-- ABOUT THE PROJECT -->
## About The Project

I follow a dance-fitness Youtube channel, and often find myself
scanning the comments of multiple videos before finding one with
a playlist I like. I decided to integrate Youtube and Spotify
APIs in order to create a searchable database of songs and videos.
The end goal is to be able to select certain song to include/exclude, 
and it will output a list of video links matching the parameters.

## Current Status

A majority of the backend work is done. I can scrub videos and 
associate them with Songs + Artists. I still need to:

* Create a front-end for the searching, and create an html page to host it
* The Youtube API currently does not allow access to Community posts (where the fitness
videos are posted). I have a more manual workaround currently - but would like to:
  * Automate the adding of the community posts to a playlist, so the database is automatically updated when a new video is posted
  * When/If the Youtube API is updated to handle community posts, update this code accordingly.