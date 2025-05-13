%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
CuLater README for code submission
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

Group: A1
GitHub repo link: https://github.com/OmerEgeOzyaba/CSCI3100-project

Branches:
1. Main: Where the latest documentation and code will be at (after thorough testing and 100% assurance).
2. shentest0405: Major rework of 16 tasks, branched out to avoid internal conflict and ensure damage/source control.
3. shenDebugged: Debugging branch to ensure rapidfire debugging can be implemented without affecting source code and better control internal conflict and source.



Final remarks and summary of running CuLater:

1. Implement postgresql in docker and start it  {READ BELOW}
2. Implement redis                              {dir: code_groupA1\coding\middleware\redis_guide}
2. Run middleware_app.py/flask                  {dir: code_groupA1\coding\middleware\README}
3. Run the frontend (npm install + npm run dev) {dir: code_groupA1\coding\frontend\README}
4. Sign up an account 
    4.1 Generate license key (in this case: iamakey123) by using command: 
    psql -h localhost -p 5432 -W -U postgres #password 口令 is culater
    INSERT INTO "SoftwareLicenses" (key, created_at, used_status) VALUES ('iamakey123', CURRENT_TIMESTAMP, false);
    4.2 sign up
5. Thank you for your time.



%%%%%%%%%%%%%%%%%%%%%%%%%%%
POSTGRESQL in docker guide:
%%%%%%%%%%%%%%%%%%%%%%%%%%%
1. Download Docker Desktop 4.39.0

2. Start Docker

3. Settings:
    3.1. Check Kubernetes is disabled
    3.2. Check all software is up-to-date

4. Open Terminal
    4.1. Type docker run -d -p 5432:5432 --name postgres-culater -e POSTGRES_PASSWORD=culater postgres:17.4
    4.2. This installs and runs postgres version 17.4 and sets culater as the admin password. Postgres will be exposed on localhost port 5432

5. If you go to the Containers tab, you should see the running container

6. You can start, stop and delete the container in the Docker app
    6.1. Alternatively, you can use the docker start <name> and docker stop <name> commands in the Terminal

7. Install postgres cli tool
    7.1. https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
    7.2. Download version 17.4
    7.3. Execute the Installer
    7.4. Choose just to install the CLI tools
    7.5. Finish Installer
    7.6. Add the binary to the path (f.e. C:\Program Files\PostgreSQL\17\bin)
        7.6.1 https://stackoverflow.com/questions/9546324/adding-a-directory-to-the-path-environment-variable-in-windows
    7.7. The Installer might start a postgres server after finishing. Go to the task manager and close all running postgres tasks, if there are any. We just need Docker.

8. Connect to the Docker container
    8.1. Type psql -h localhost -p 5432 -U postgres in Terminal
    8.2. Enter password culater
    8.3. Try out command SELECT datname FROM pg_database;