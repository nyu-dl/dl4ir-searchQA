# SearchQA

Associated paper:  
COMING SOON

Here are the files used in the training testing and validation:  
https://drive.google.com/open?id=0B51lBZ1gs1XTR3BIVTJQWkREQU0

-------

One can collect the original json files through web search using the scripts in qacrawler. Please refer to the README in the folder for further details on how to use the scraper. Furthermore, one can use the files in the test folder to try it.

Here are the json files that are collecting using the Jeopardy! dataset:  
https://drive.google.com/open?id=0B51lBZ1gs1XTMVFsQlNEQUtpWVU

And here is the link for the Jeopardy! files themselves:  
https://www.reddit.com/r/datasets/comments/1uyd0t/200000_jeopardy_questions_in_a_json_file/  

NOTE: We will release the the script that converts these to the training files above with appropriate restrictions.

-------

Some requirements:
nltk==3.2.1  
pandas==0.18.1  
selenium==2.53.6  
pytest==3.0.2  
pytorch==0.1.11  
