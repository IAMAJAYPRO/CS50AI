## load_data
I started with the project then i experimented with some options for getting the file names and path and finnaly came to the option for using
```py
os.listdir(path) # to get list of all the files/folder in the directory

os.path.join(front,end) # to join paths independently
```
I used listdir on the main to get the labels, then on the labels to get the image file names, then cv2 to read the image and resize

When i was running the file, i stumbled upon .DS_Store folder/file which i didnt had in my folder, turned out it was a system file, so i strted to ignore all names starting with ".".

## get_model

Here i experimented with the numbers in layers, ie: units,number of filters.
