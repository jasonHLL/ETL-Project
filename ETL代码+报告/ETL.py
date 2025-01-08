# Creator: Hongliang Liu

# Final project: Use the New York Times article research API to do an ETL project on analyzing the top 10 keywords in the first 10 pages of articles about AI over three periods.
# The goal of this project is to analyze the change of keywords from one period to another.
# For example, comparing the keyword changes from 2020/01/01 to 2022/01/01 and from 2022/01/01 to 2024/01/01.

import requests,pickle,pathlib,time
from math import ceil
import pandas as pd
import matplotlib.pyplot as plt

print("This code is use to find the top 10 keywords in first 10 pages of articles about AI in a period")

# Create a directory to store subsequent files
kw_dir = pathlib.Path().cwd()/'kw dir'                                              
kw_dir.mkdir(exist_ok=True)

# URL and API key for the New York times API
API_KEY = "example api key"
URL = "https://api.nytimes.com/svc/search/v2/articlesearch.json"

def get_hits(URL,params):
    """Get the number of articles about AI through the API.

    Args:
        URL (str): URL for the API.
        params (dict): Dictionary of parameters for API access.

    Returns:
        int: numbers of article.
    """
    response = requests.get(URL, params=params)                                       # Send a request to the specified API endpoint using the provided parameters.
    if response.status_code == 200:                                                   # Check if the endpoint is responding correctly.
        data = response.json()                                                    
        return data['response']['meta']['hits']                                       # return numbers of article.                                           
    else:                                                                             
        return "API request failed with status code " + str(response.status_code)     # If not responding correctly, output error code.


def get_docs(page,params,URL):
    """According to the page, search and return all contents under the 'docs'.

    Args:
        page (int): Use to get the new data that is in different pages.
        params (dict): Dictionary of parameters for API access.
        URL (str): URL for the API.

    Returns:
        list: Contents that are in 'docs'.
    """
    params['page'] = page
    response = requests.get(URL, params=params)                                      # Send a request to the specified API endpoint using the provided parameters.
    if response.status_code == 200:                                                  # Check if the endpoint is responding correctly.
        data = response.json()                                                    
        return data['response']['docs']                                              # Select all the content in response and docs.
    else:                                                                            # If not responding correctly, output error code.
        return "API request failed with status code " + str(response.status_code)


def get_docs_between_dates(URL,params):
    """Get all key words from the URL and put them into a pkl file

    Args:
        URL (str): URL for the API.
        params (dict): Dictionary of parameters for API access.
    """
    max_page = min(10, ceil(get_hits(URL,params)/10))                                 # Call the 'get_hits' method, then choose the first 10 pages or the minimum number of pages if the URL has fewer than 10 pages. 
    keyword_list = []
    for page in range(max_page): 
        docs = get_docs(page,params,URL)                                              # Call the 'get_docs' method to get the all contents under docs.
        # Loop through each article in the docs to find the keywords dictionary.
        for doc in docs:
            article_keywords = doc['keywords']
            # Loop through the keywords dictionary and find the article tag. 
            for keyword in article_keywords:
                value = keyword['value']
                keyword_list.append(value)

        time.sleep(15)                                                                # Sleep for 15 seconds to avoid short-term high-frequency API access.
        print(f"Page completed search: {page+1}")

    file_name = f"{begin_date}_{end_date}_keywords.pkl"                               # Set the pkl file name according to when start and end the search. 
    file_path = kw_dir/file_name                                                          
    with file_path.open(mode='wb') as file:                                           # Open the file and write all key words into the pkl file.
        pickle.dump(keyword_list, file)


def get_keyword_counts(begin_date,end_date):
    """Read the pkl file and use the dictionary to find the count for each keyword. 
        Then sort from largest to smallest and return the dictionary of the top 10 keywords with the largest values.

    Args:
        begin_date (str): Search start
        end_date (str): Search end
        
    Returns:
        dict: The top 10 keywords with the largest values.
    """
    keyword_values = {}
    kw_file = kw_dir / f"{begin_date}_{end_date}_keywords.pkl"                       # Find the pkl file.  
    with kw_file.open(mode='rb') as file:                                            # Read the pkl file and load it into a list.
        kw_list = pickle.load(file)
    # Create a dictionary for all key words.
    for keyword in kw_list:    
        if keyword in keyword_values:                                                # if the tag in the keyword_values dictionary, its value + 1.
            keyword_values[keyword] += 1
        else:                                                                        # if not, add it into the keyword_values dictionary and set its vlaue = 1.
            keyword_values[keyword] = 1
    # print(keyword_values)
    
    # From big to small, sort the dictionary according to the value.
    sort_keyword_values = {k:v for k,v in sorted(keyword_values.items(), key = lambda kv:kv[1], reverse= True)}
    
    # Choose the top 10 keywords with the largest values and save them in a new dictionary.
    top_10_keywords = dict(list(sort_keyword_values.items())[:10])
        
    # print(sort_keyword_values)
    return top_10_keywords


def transfer_into_CSV(top_10_keywords,begin_date, end_date):
    """Tranfer contents in a dictionary into a human reable CVS file.

    Args:
        top_10_keywords (dict): Top 10 keywords with the largest values.
        begin_date (str): Search start
        end_date (str): Search end
    """
    # Use pandas to transfer a dictionary into a CSV file with column 1 = Keyword and column 2 = Count.
    word_count_df = pd.DataFrame(list(top_10_keywords.items()), columns=['Keyword', 'Count'])               
    final_result = kw_dir / f"{begin_date}_{end_date}_word_counts.csv"
    word_count_df.to_csv(final_result, index=False)
    print(word_count_df)


def chart (top_10_keywords):
    """Draw a bar chart base on the top 10 keywords.

    Args:
        top_10_keywords (dict): Top 10 keywords with the largest values.
    """
    # Extract keys and values.
    key = list(top_10_keywords.keys())
    values = list(top_10_keywords.values())

    # Create a bar chart.
    plt.bar(key, values, color='skyblue')  

    # Set the chart title and the x,y label.
    plt.title(f'On Page {0} ~ {9}, Top Ten Common Keywords In AI Articles During {begin_date} ~ {end_date}')
    plt.xlabel('keywords')
    plt.ylabel('Amount')

    # Show the chart and optimize the display.
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout() 
    plt.show()


def data_analysis(begin_date, end_date):
    """Do a data analysis based on the begin_date and end_date.
        1. Find the top 10 keywords.
        2. Make the top 10 keywords into a CSV file.
        3. Draw a bar chart based on the top 10 keywords.

    Args:
        begin_date (str): Search start
        end_date (str): Search end
    """

    top_10_keywords = get_keyword_counts(begin_date, end_date)                       # Find the top 10 keywords.
    transfer_into_CSV(top_10_keywords,begin_date, end_date)                          # Make the top 10 keywords into a CSV file.
    chart(top_10_keywords)                                                           # Draw a bar chart based on the top 10 keywords.

# Main code below: get the begin_date and end_date to do the analysis.
begin_end_dates = [[20180101,20200101],[20200101,20220101],[20220101,20240101]]      # Three period of time for doing the search.

# Loop through the three periods for doing the analysis.
for period in begin_end_dates:
    begin_date = period[0]
    end_date = period[1]
    
    params = {
        'q': "AI",                                                                   # The query that what to search.
        'begin_date': begin_date,                                                    # Search from when (YY/MM/DD).  
        'end_date': end_date,                                                        # When to end the search  (YY/MM/DD).
        'api-key': API_KEY, 
        'sort': 'relevance',                                                         # Sort articles by relevance.
        'fq' : 'document_type:("article")',
    }

    print()    
    print(f"Now viewing the period of {begin_date} ~ {end_date}.")
    
    # Check if the file already exist 
    file_path = kw_dir /f"{begin_date}_{end_date}_keywords.pkl"
    if file_path.exists():                                                           # If the file it already exists, start offline analysis directly
        data_analysis(begin_date, end_date)
    else :                                                                           # There is no file for this period yet.
        get_docs_between_dates(URL,params)                                           # Call the 'get_docs_between_dates' function to obtain information online and write a pkl file before doing the analysis.
        data_analysis(begin_date, end_date)
