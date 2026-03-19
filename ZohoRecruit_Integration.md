# Using Zoho recruit Integration -


**Zoho API console** - https://api-console.zoho.in		(Create API auth creds)

**Zoho recruit dashboard** - https://recruit.zoho.in

**Zoho API guide** - https://www.zoho.com/recruit/developer-guide/apiv2/get-associated-records.html




1. **Create Oauth in api-zoho.console.in** - Create client, set Redirect uri (not same as homepage url, like http://localhost:3000/zoho)


2. **Generate grant auth code** - https://help.zoho.com/portal/en/kb/recruit/developer-guide/oauth-authentication/authorization-request/articles/authorization-request

	1. use this on browser - https://accounts.zoho.com/oauth/v2/auth?scope=ZohoRecruit.modules.ALL&client_id={client_id}&response_type=code&access_type=offline&redirect_uri={redirect_uri}
	
	2. Access_type should be offline to get refresh token on next step. (online to get short time access token for 1 time)
	
	3. Then it will ask to grant permissions
	
	4. Then when no server is running on that redirect uri, it will say 404, Then on url copy the 'Code=1000.xxxxx .....' - It's the auth code
	
	
3. **Access token** - https://help.zoho.com/portal/en/kb/recruit/developer-guide/oauth-authentication/generating-tokens/articles/generating-tokens

	1. In postman use - params. (The auth code in prev step is valid for few mins)  (The access token is only valid for 1 hour)

	2. Use url - 
			https://accounts.zoho.in/oauth/v2/token?grant_type=authorization_code&client_id=1{client_id}&client_secret={client_secret}&redirect_uri={redirect_uri}&code={auth_code}

	3. It will return the access token and refresh token.
	
	
4. **Refresh the _Access token_** - https://help.zoho.com/portal/en/kb/recruit/developer-guide/oauth-authentication/refreshing-access-tokens/articles/refreshing-access-tokens

	1. Use params in postman.

	2. Use the url (post method) (Not as headers) - https://accounts.zoho.in/oauth/v2/token?refresh_token={refresh_token}&client_id={client_id}&client_secret={client_secret}&grant_type=refresh_token

	3. endpoint - https://accounts.zoho.in/oauth/v2/token  , others are params passed on post request


# APIs -

**If Client auth is generated for India, then they must use zoho.in in the API endpoint**

https://www.zoho.com/recruit/developer-guide/apiv2/upsert-records.html


1. **See job openings** -

	1. endpoint - https://recruit.zoho.in/recruit/v2/Job_Openings

	2. Header - Authorization:Zoho-oauthtoken {access_token}


2. **Create candidate** -

	1. endpoint - https://recruit.zoho.in/recruit/v2/Candidates/upsert
	
	2. **Headers** -
		Authorization : Zoho-oauthtoken {auth_token}, 
		Content-type : application/json

	3. Body -
			```json
			{
				"data": [
					{
						"First_Name": "john",
						"Last_Name": "nolan",
						"Email": "abcd@gmail.com",
						"Phone": "8988889992"
					}
				]
			}
			```


3. **Update candidate data - Adding resume file** -

	1. endpoint - https://recruit.zoho.in/recruit/v2/Candidates/{candidate_id}/Attachments

	2. Headers -
		Authorization:Zoho-oauthtoken {access_token}

	3. **Files** - file content can be fetch from file url using requests.get
		files = {
            "file":("resume.pdf", resumeFile-content, "application/pdf")
        }

	4. **Implementation** - response = requests.post(endpoint, headers=headers, data=data, files=files)


4. **Associate candidate to a job** -
	1. endpoint - https://recruit.zoho.in/recruit/v2/Candidates/actions/associate

	2. Headers -
		Authorization:Zoho-oauthtoken {access_token}

	3. Json body -
		```json
		{
            "data": [
                {
                    "jobids": ["job_id1", "job_id2 (if multiple association)"],
                    "ids": ["candidate_id1"],
                    "comments":"Candidate successfully associated"
                }
            ]
        }
		```


5. **Check associated candidates** -
	1. endpoint - https://recruit.zoho.in/recruit/v2/Job_Openings/{job_id}/associate

	2. Headers -
		Authorization:Zoho-oauthtoken {access_token}

	3. GET method
