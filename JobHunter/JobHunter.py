# This script pulls from a job website and stores positions into a database. If there is a new posting it notifies the user.
# CNA 330
# Zachary Rubin, zrubin@rtc.edu
import mysql.connector
import sys
import json
import urllib.request
import os
import time
import pandas as pd

# Connect to database
# You may need to edit the connect function based on your local settings.
def connect_to_sql():
    conn = mysql.connector.connect(user='root', password='',
                                  host='127.0.0.1',
                                  database='cna330')
    return conn

# Create the table structure
def create_tables(cursor, table):
    ## Add your code here. Starter code below
    cursor.execute('''CREATE TABLE IF NOT EXISTS jobs (id INT PRIMARY KEY auto_increment, type varchar(10), title varchar(100), description text, job_id varchar(50), created_at varchar(200), company varchar(100), location varchar(200), how_to_apply varchar(10000));''')
    return
# Query the database.
# You should not need to edit anything in this function
def query_sql(cursor, query):
    cursor.execute(query)
    return cursor
# Add a new job
def add_new_job(cursor, jobdetails):
    cols = "`,`".join([str(i) for i in jobdetails.columns.tolist()])
    for i, row in jobdetails.iterrows():
        sql = "INSERT INTO `jobs` (`" + cols + "`) VALUES (" + "%s," * (len(row) - 1) + "%s)"
        query = cursor.execute(sql, tuple(row))
    return query_sql(cursor, query)
# Check if new job
def check_if_job_exists(cursor, jobdetails):
    ## Add your code here
    job_id = jobdetails['job_id']
    query = "SELECT * FROM jobs WHERE title = \"%s\"" % job_id
    return query_sql(cursor, query)
def delete_job(cursor, jobdetails):
    title = jobdetails['job_id']
    query = "DELETE FROM jobs WHERE job_id = \"%s\"" % job_id
    return query_sql(cursor, query)
def add_or_delete_job(cursor, jobdetails):
    # Add your code here to parse the job page
    for job in jobdetails:  # EXTRACTS EACH job from list
        # Add in your code here to check if the job already exists in the DB
        check_if_job_exists(cursor, jobdetails)
        is_job_found = len(cursor.fetchall()) > 0  # https://stackoverflow.com/questions/2511679/python-number-of-rows-affected-by-cursor-executeselect
        if is_job_found:
            print("Job is found: "+ jobdetails["title"] + " from " + jobdetails["company"])
        else:
            print("New job is found: " + jobdetails["title"] + " from " + jobdetails["company"])
            add_new_job(cursor, jobdetails)
    return
# Grab new jobs from a website
def fetch_new_jobs(arg_dict):
    # Code from https://github.com/RTCedu/CNA336/blob/master/Spring2018/Sql.py
    query = "https://jobs.github.com/positions.json?search=SQL&location=Remote" ## Add arguments here
    jsonpage = 0
    try:
        contents = urllib.request.urlopen(query)
        response = contents.read()
        jsonpage = json.loads(response)
    except:
        pass
    return jsonpage
# Load a text-based configuration file
def load_config_file(filename):
    argument_dictionary = 0
    # Code from https://github.com/RTCedu/CNA336/blob/master/Spring2018/FileIO.py
    rel_path = os.path.abspath(os.path.dirname(__file__))
    file = 0
    file_contents = 0
    try:
        file = open(filename, "r")
        file_contents = file.read()
    except FileNotFoundError:
        print("File not found, it will be created.")
        file = open(filename, "w")
        file.write("")
        file.close()
    ## Add in information for argument dictionary
    return argument_dictionary
# Main area of the code.
def jobhunt(cursor, arg_dict):
    # Fetch jobs from website
    jobpage = fetch_new_jobs(arg_dict)
    #print(jobpage)
    #df[["type", "title", "description", "created_at", "id", "company", "location", "how_to_apply"]]
    ## Add your code here to parse the job page
    jp = pd.DataFrame(jobpage)
    jp = jp[["type", "title", "description", "created_at", "id", "company", "location", "how_to_apply"]]
    jp = jp.rename(columns={"id": "job_id"})
    ## Add in your code here to check if the job already exists in the DB
    check_if_job_exists(cursor, jp)
    add_or_delete_job(cursor, jp)
    ## Add in your code here to notify the user of a new posting
    ## EXTRA CREDIT: Add your code to delete old entries
# Setup portion of the program. Take arguments and set up the script
# You should not need to edit anything here.
def main():
    # Connect to SQL and get cursor
    conn = connect_to_sql()
    cursor = conn.cursor(buffered=True)
    create_tables(cursor, "table")
    # Load text file and store arguments into dictionary
    #arg_dict = load_config_file(sys.argv[1])
    arg_dict = ""
    while(1):
        jobhunt(cursor, arg_dict)
        conn.commit()
        time.sleep(3600) # Sleep for 1h
if __name__ == '__main__':
    main()