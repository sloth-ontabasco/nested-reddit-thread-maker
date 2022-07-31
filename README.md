# nested-reddit-thread-maker
Convert a csv file into nested reddit mega threads for managing big events

- **After cloning the repository, install to get started**
```
pip install -r requirements.txt
```
- **Excel file must be formatted like image attached below with the names of the thread replacing the cells**
![image](https://user-images.githubusercontent.com/42805453/182010366-63d1316b-2473-4af9-8147-25d00019cb28.png)

- **Remove any unwanted cells before downloading the .csv file**
- **Follow the instructions in setup.py by running**
 ```
 python3 setup.py
 ```
 - **Now run the actual script, this may take some time if you have a lot of threads. Avoid getting API banned by running it constantly**
 ```
 python3 run.py
 ```
 - **You can delete all the posts later if you'd like by running**
 ```
 python3 run.py --delete
 ```
