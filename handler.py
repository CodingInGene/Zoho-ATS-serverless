import json
from dotenv import load_dotenv
from collections import defaultdict
import os
import requests
from handleAuth import refresh_auth_token

load_dotenv()


'''
Zoho api structure - https://recruit.zoho.com/recruit/v2/{module_api_name}/{extra}
Headers - Authorization : Zoho-oauthtoken {auth_token}
'''

def get_access_token():
    file_read = open("auth-details.json", "r")

    data = json.load(file_read)
    last_used = data["last_accessed"]


# Show all jobs
def jobs(event, context):
    # Get access token
    access_token = refresh_auth_token()

    # Call Zoho api
    endpoint = "https://recruit.zoho.in/recruit/v2/Job_Openings"
    headers = {
        "Authorization":f"Zoho-oauthtoken {access_token}"
    }

    response = requests.get(endpoint, headers=headers)

    # print(response.json())

    # If 400 error
    if response.status_code == 400:
        return {"statusCode": 400,"body": json.dumps("No job openings to show")}

    # If no job openings
    if response.status_code == 204:
        return {"statusCode": 200,"body": json.dumps({"message":"No job openings to show"})}
    elif response.status_code != 200:
        return {"statusCode": 400,"body": json.dumps({"message":f"{response.json()['message']}"})}

    # Format Zoho response
    customJson = defaultdict(str)

    try:
        data = response.json()["data"]      # Arr of json(all jobs) -> data:[ {j1}, {j2} ]

        for index, job in enumerate(data):
            job_name = job["Posting_Title"]         # job is a dict
            job_id = job["id"]
            job_opening_id = job["Job_Opening_ID"]
            job_desc = job["Job_Description"]
            posted_by = job["Client_Name"]["name"]
            date_opened = job["Date_Opened"]
            valid_till_date = job["Target_Date"]
            required_skills = job["Required_Skills"]
            experience = job["Work_Experience"]
            job_type = job["Job_Type"]
            salary = "Salary not disclosed" if job["Salary"] == "null" or job["Salary"] == None else job["Salary"]

            # Add element in dict
            customJson[job_name] = {
                "job_id":job_id,
                "job_desc":job_desc,
                "posted_by":posted_by,
                "date_opened":date_opened,
                "valid_till_date":valid_till_date,
                "required_skills":required_skills,
                "experience_needed":experience,
                "job_type":job_type,
                "salary":salary
            }
            # print(customJson)

    except Exception as e:
        print("Error during response formatting in jobs -", e)
        return {"statusCode": 400, "body": json.dumps({"status":"Something went wrong"})}


    response = {"statusCode": 200, "body": json.dumps(customJson)}

    return response


# Create candidate
def candidates(event, context):
    # Get access token
    access_token = refresh_auth_token()

    event = json.loads(event["body"])

    fname = event["first_name"]
    lname = event["last_name"]
    phone = event["phone"]
    email = event["email"]
    resume_url = event["resume_url"]
    job_id = event["job_id"]

    if fname == None or lname == None or phone == None or email == None or resume_url == None or job_id == None:    # If blank fields
        return {"statusCode": 400,"body": json.dumps({"message":"Fields missing"})}

    # Create candidate in Zoho recruit
    try:
        endpoint = "https://recruit.zoho.in/recruit/v2/Candidates/upsert"
        headers = {
            "Authorization":f"Zoho-oauthtoken {access_token}",
            "Content-type":"application/json"
        }

        body = {
            "data": [
                {
                    "First_Name": fname,
                    "Last_Name": lname,
                    "Email": email,
                    "Phone": phone
                }
            ]
        }

        response = requests.post(endpoint, headers=headers, json=body)

        data = response.json()

        candidate_id = data["data"][0]["details"]["id"]

        if response.status_code != 200:
            return {"statusCode": 400,"body": json.dumps({"message":f"{data['message']}"})}

        if response.status_code == 200:     # Just print steps
            print("Candidate created, id", candidate_id)

    except Exception as e:
        print("Error during candidate creation -", e)
        return {"statusCode": 400, "body": json.dumps({"status":"Something went wrong"})}

    # Updating candidate details
    try:
        # Get the resume file
        file_resume = requests.get(resume_url)

        files = {
            "file":(f"resume-{candidate_id}.pdf", file_resume.content, "application/pdf")
        }

        data = {
            "attachments_category":"Resume"
        }

        # Now add the candidate resume
        endpoint = f"https://recruit.zoho.in/recruit/v2/Candidates/{candidate_id}/Attachments"
        headers = {
            "Authorization":f"Zoho-oauthtoken {access_token}"
        }

        response = requests.post(endpoint, headers=headers, data=data, files=files)

        if response.status_code != 200:
            return {"statusCode": 400,"body": json.dumps({"message":f"{data['message']}"})}

        if response.status_code == 200:     # Just print steps
            print("Candidate resume added")

    except Exception as e:
        print("Error during candidate creation -", e)
        return {"statusCode": 400, "body": json.dumps({"status":"Something went wrong"})}

    # Associate candidate
    try:
        endpoint = "https://recruit.zoho.in/recruit/v2/Candidates/actions/associate"
        headers = {
            "Authorization":f"Zoho-oauthtoken {access_token}"
        }

        body = {
            "data": [
                {
                    "jobids": [job_id],
                    "ids": [candidate_id],
                    "comments":f"Candidate {candidate_id} successfully associated"
                }
            ]
        }

        response = requests.put(endpoint, headers=headers, json=body)

        if response.status_code != 200:
            print(response.json())
            return {"statusCode": 400,"body": json.dumps({"message":f"{data['message']}"})}

        if response.status_code == 200:     # Just print steps
            print(f"Candidate associated to {job_id}")

    except Exception as e:
        print("Error during candidate association -", e)
        return {"statusCode": 400, "body": json.dumps({"status":"Something went wrong"})}


    # Show response
    response = {"statusCode": 200, "body": json.dumps({"message": f"Candidate created successfully", "candidate_id":candidate_id})}

    return response


# Show all candidates who applied to a job with job_id
def applications(event, context):
    # Get access token
    access_token = refresh_auth_token()

    header_data = event.get("headers")

    job_id = header_data["job_id"]

    # Fetch associated candidates details
    endpoint = f"https://recruit.zoho.in/recruit/v2/Job_Openings/{job_id}/associate"
    headers = {
        "Authorization":f"Zoho-oauthtoken {access_token}"
    }

    response = requests.get(endpoint, headers=headers)

    # Format response
    customJson = defaultdict(str)

    data = response.json()

    for candidate in data["data"]:      # Returns arr of associated candidates
        candidate_id = candidate["id"]
        first_name = candidate["First_Name"]
        last_name = candidate["Last_Name"]
        full_name = candidate["Full_Name"]
        phone = candidate["Phone"]
        email = candidate["Email"]
        skills = "Not updated" if candidate["Skill_Set"] == None else candidate["Skill_Set"]
        experience = "Not updated" if candidate["Experience_in_Years"] == None else candidate["Experience_in_Years"]
        application_status = candidate["Application_Status"]
        candidate_stage = candidate["Candidate_Stage"]

        customJson[full_name] = {
            "candidate_id":candidate_id,
            "first_name":first_name,
            "last_name":last_name,
            "phone":phone,
            "email":email,
            "skills":skills,
            "experience":experience,
            "application_status":application_status,
            "candidate_stage":candidate_stage
        }

    
    response = {"statusCode": 200, "body": json.dumps(customJson)}

    return response