## API screenshot
http://127.0.0.1:8000/docs
![Screenshot-api.jpeg](./faas-api/Screenshot-api.jpeg)

## API Run
![Screenshot API Run.png](./faas-api/Screenshot%20API%20Run.png)

## docker DB
```bash
docker ps -a
docker container stop 
docker system prune -a # clean out all old images
#podman system prune -a # clean out all old images
docker run --name some-postgres -e POSTGRES_DB=python -e POSTGRES_USER=user -e POSTGRES_PASSWORD=mysecretpassword -p 5432:5432 -d postgres:13.2
docker exec -it some-postgres psql -U user python -p 5432 -h localhost
  \l # list databases
  \c python # change database to python
  create table test ( n  integer primary key not null);
  \d # list schema
  select * from test;
  insert into test values (1);
  select * from test;
  exit
```

## docker DB connectivity verification
```bash
podman exec -it hutemplatedb psql -U python -d python

OR

docker exec -it hutemplatedb psql -U python -d python -h localhost bash

OR

psql -h localhost -p 5432 -U postman -d postman


Connecting via pgAdmin or Any PostgreSQL Client
Host: localhost
Port: 5432
Database Name:python 
Username: python
Password: python
```

## Environment variables in .env based on podman 
### podman run -d --name postgres -e POSTGRES_DB=python -e POSTGRES_USER=python -e POSTGRES_PASSWORD=python -p 5432:5432 postgres:13.2
### docker run --name templatedb -e POSTGRES_PASSWORD=python -e POSTGRES_DB=python -e POSTGRES_USER=python -p 5432:5432 -d postgres:13.2
```bash
DATABASE_URL=postgresql://python:python@localhost:5432/python
GROQ_API_KEY="gsk_....."
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
LANGCHAIN_API_KEY="lsv2_pt_..."
LANGSMITH_PROJECT="pr-...."
MEDIA_PATH="C:\\~Desktop\\....\\" # or for linux: "/.../media/"
```

## For local
#### DATABASE_URL=postgresql://user:mysecretpassword@localhost:5432/postgres

## on windows set var=... for each var in .env

## windows run
```bash
#windows set all the environment varibles - set DATABASE_URL=...
cd faas-api 
python -m venv venv
.\venv\Scripts\activate 
pip3 install -r requirements.txt
```

## go below linux section to continue confirm groq ai is working!

## linux 
```bash
## linux source the environment variables and on windows export var=... for each var in .env
set -o allexport && source .env && set +o allexport
printenv
cd faas-api 
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip3 install -r requirements.txt
```

## resume the validation
```bash
## confirm groq ai is working!
python test.py

## confirm groq ai is processing Images
python testImageProcessing.py

rm -Rf project-root/ # or del on windows this sub-folder which contains the generated code

## start the faas-app
uvicorn app.main:app --reload

```

## API server 
## Steps to Run JSON Server:
```bash
cd api-server
## Install JSON Server

npm install -g json-server@0.17.0 # linux: sudo npm install -g json-server@0.17.0 
npm install json-server@0.17.0 --save  
## Start JSON Server

json-server --watch db.json --port 3000
```

### API Endpoints:
### Dashboard Data: GET /api/dashboard  # http://localhost:3000/api/dashboard
### Apply for Leave: POST /api/lms/leave/apply
### Approve Leave (Manager Only): POST /api/lms/leave/approve
### View Pod Details: GET /api/pods/details
### Recommend Employee to Pod: POST /api/pods/recommend
### View Recommendations: GET /api/pods/recommend
### Login: POST /api/auth/login
### Fetch Current User: GET /api/auth/me

## Test API endpoints
```bash
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword"
  }'

curl -X GET http://localhost:3000/api/auth/me \
  -H "Authorization: Bearer jwt-token-here"

curl -X POST http://localhost:3000/api/lms/leave/approve \
  -H "Authorization: Bearer jwt-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "leaveId": "12345",
    "status": "approved"
  }'

curl -X GET http://localhost:3000/api/pods/details \
  -H "Authorization: Bearer jwt-token-here"

curl -X POST http://localhost:3000/api/pods/recommend \
  -H "Authorization: Bearer jwt-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "podId": "56789",
    "recommendedUserId": "3"
  }'

curl -X GET http://localhost:3000/api/pods/recommend \
  -H "Authorization: Bearer jwt-token-here"
```

#### Test run
#### Ensure the MEDIA_PATH is set correctly in your .env like other API 
#### and they are set (windows) or exported (linuc)
#### browse to 127.0.0.1:8080/docs swagger docs url 
#### click on POST and browse to SRS document and type in the screenshotimage.jpg
#### screenshot_url has to be only a file name which should be in the MEDIA_PATH

#### view Langchain logs at https://smith.langchain.com/

![Screenshot-langchain-logs.png](./faas-api/Screenshot-langchain-logs.png)

#### command prompt run snippet below from uvicorn run logs

=================================================


INFO:root: validate_ui: success! 
INFO:root:

=================================================

INFO:root:UI Validation Report: *Validation Report*

*Overview*

The provided Software Requirements Document (SRD) outlines the requirements for the frontend development of three microservices/applications within the DNA ecosystem: 
Dashboard, LMS (Leave Management System), and PODs. The focus is on UI/UX design, API contracts for integration, and overall frontend development guidelines.

*Validation Results*

*UI Requirements and Design Specifications*

1. *Color Scheme*:
	* Primary Color: #007bff (Blue - for primary actions) - *Valid*
	* Secondary Color: #6c757d (Gray - for secondary actions) - *Valid*
	* Background Color: #f8f9fa (Light Gray - for application background) - *Valid*
	* Success Color: #28a745 (Green - for success messages) - *Valid*
	* Error Color: #dc3545 (Red - for error messages) - *Valid*
2. *Typography*:
	* Font Family: "Inter", sans-serif - *Valid*
	* Heading Font Size: 24px (Bold) - *Valid*
	* Subheading Font Size: 18px (Medium) - *Valid*
	* Body Text Size: 16px (Regular) - *Valid*
	* Button Text Size: 14px (Bold) - *Valid*
3. *Components*:
	* Buttons: Rounded corners (8px), filled for primary actions, outlined for secondary actions. - *Valid*
	* Cards: Shadow (box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1)) with padding (16px). - *Valid*
	* Modals: Centered popups with a semi-transparent background. - *Valid*
	* Forms: Input fields with a border radius of 5px and padding of 10px. - *Valid*

*Application Features*

1. *Dashboard*:
	* Displays multiple tiles reflecting highlights from various applications. - *Valid*
	* Each tile fetches real-time data from APIs. - *Valid*
	* Users can customize which tiles appear on their dashboard. - *Valid*
2. *LMS (Leave Management System)*:
	* General User Features: Apply for leave, View granted leaves, Check available leave balance. - *Valid*
	* Manager Features: Approve/reject leave requests, View team leave history. - *Valid*
3. *PODs*:
	* Managers can add employees to a pod. - *Valid*
	* Employees can view their pod details. - *Valid*
	* Employees can recommend other employees to join their pod. - *Valid*

*API Contracts*

1. *Login*:
	* Request: POST /api/auth/login - *Valid*
	* Response: { "token": "jwt-token-here", "user": { "id": "1", "role": "manager" } } - *Valid*
2. *Fetch Dashboard Data*:
	* Request: GET /api/dashboard - *Valid*
	* Response: { "tiles": [ { "id": "1", "title": "Leave Summary", "content": "10 leaves remaining" }, { "id": "2", "title": "Pod Members", "content": "3 active members" } ] } - *Valid*
3. *Apply for Leave*:
	* Request: POST /api/lms/leave/apply - *Valid*
	* Response: { "message": "Leave request submitted successfully", "status": "pending" } - *Valid*
4. *Approve Leave (Manager Only)*:
	* Request: POST /api/lms/leave/approve - *Valid*
	* Response: { "message": "Leave request approved", "status": "approved" } - *Valid*
5. *View Pod Details*:
	* Request: GET /api/pods/details - *Valid*
	* Response: { "podId": "56789", "podName": "Innovation Team", "members": [ { "id": "1", "name": "John Doe", "role": "Lead Developer" }, { "id": "2", "name": "Jane Smith", "role": "UI/UX Designer" } ] } - *Valid*
6. *Recommend an Employee for a Pod*:
	* Request: POST /api/pods/recommend - *Valid*
	* Response: { "message": "Recommendation sent successfully" } - *Valid*

*Deployment & Hosting Considerations*

1. *Frontend Framework: Angular with Material UI. - **Valid*
2. *Hosting: Vercel, Netlify, or S3 with CloudFront. - **Valid*
3. *CI/CD: GitHub Actions or GitLab CI/CD for automated deployment. - **Valid*

*Screenshot Details*

The provided screenshot details describe a dashboard with various UI components, design language, and layout details. The dashboard is divided into different sections, each with its own set of features and functionalities.

*Validation Conclusion*

The provided Software Requirements Document (SRD) outlines the requirements for the frontend development of three microservices/applications within the DNA ecosystem: Dashboard, LMS (Leave Management System), and PODs. The focus is on UI/UX design, API contracts for integration, and overall frontend development guidelines.

The validation results show that the UI requirements and design specifications are valid, and the application features, API contracts, and deployment & hosting considerations are also valid.

However, there are some potential issues that need to be addressed:

1. The screenshot details do not match the UI requirements and design specifications.
2. The API contracts do not include any error handling or validation.
3. The deployment & hosting considerations do not include any information about security or scalability.

Overall, the provided Software Requirements Document (SRD) is a good starting point for the frontend development of the three microservices/applications within the DNA ecosystem. However, there are some potential issues that need to be addressed to ensure the successful development and deployment of the applications.
INFO:root:

=================================================


INFO:root: save_generated_files: success! 
INFO:root:

=================================================


INFO:     127.0.0.1:50106 - "POST /projects/ HTTP/1.1" 200 OK
