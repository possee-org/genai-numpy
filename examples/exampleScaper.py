import requests
import threading
import os
import shutil

# Your API key and search engine ID will be placed in the following variables
# Follow along with the following link, specifically in the 'prerequisites' section to get your own key and ID
# https://developers.google.com/custom-search/v1/overview
key = '[Your API key here]'
cx = '[Your search engine ID here]'

# You can request any google search, one example would be 'np.linalg.svdvals examples', limit to 2048 characters
question = '[Your qoogle search here]'

# construct google custom search api request link
link = f'https://www.googleapis.com/customsearch/v1?key={key}&cx={cx}&q={question}&num=10&lr=lang_en'

def create_txt_copy(link, i):
    '''
    Given a specific link and an iteration,
    create a txt file specific to that link and
    iteration that contains the html contents of
    said link.
    '''

    # create unique file name for the link
    file_name = 'html_text/top_link_txt_' + str(i) + '.txt'
    if os.path.exists(file_name):
        os.remove(file_name)

    # get html contents of the link and paste it into txt file
    page = requests.get(link)

    with open(file_name, 'w', encoding="utf-8") as file:
        file.write(page.text)

def get_top_10_txt(link):
    '''
    Given the google custom search api link,
    get the top 10 links for the given search
    and place the html of each link in a txt
    file in the folder 'html_text'.
    '''
    response = requests.get(link)

    # if we get the expected response
    if response.status_code == 200:

        # make sure we have a new directory known as 'html_text'
        new_directory = 'html_text'
        if os.path.exists(new_directory) and os.path.isdir(new_directory):
            shutil.rmtree(new_directory)

        os.makedirs(new_directory, exist_ok=True)

        # set up variables required to get links as txt files
        items = response.json()['items']
        i = 1
        threads = []

        # thread the task of making requests to speed up 'IO bound' problem
        for object in items:
            t = threading.Thread(target=create_txt_copy, args=(object['link'], i))
            threads. append(t)
            i+=1

        for t in threads:
            t.start()

        for t in threads:
            t.join()

    # if we do not get the expected response
    else:
        print('ERROR: ' + response.status_code)


# run program, 100 runs a day per api key
get_top_10_txt(link)

