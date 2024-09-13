#/bin/bash
VERSION="1.2.7"

docker build --platform linux/amd64 -t engiecofely/ocpi_server:v$VERSION .
docker push engiecofely/ocpi_server:v$VERSION
echo -en "\007"


### VERSION HISTORY ###

#   Version User    Change
#   4.0.15  EBU     Add optiboard utilization
#   4.0.16  JFI     fix(Datalake)--Changed required option 
#   4.0.17  EBU     fix(Optiboard) Datetime to timestamp UTC
#   4.0.18  EBU     fix(MSGraph) Datetime to timestamp UTC
#   4.0.20  JFI     feat(all) Added CORS
#   4.0.21  EBU     fix(Optiboard) Change body
#   4.0.24  EBU     fix(Optiboard) Fix body
#   4.1.0   EBU     Add new TOKEN with old token
#   4.1.1   EBU     Add new request for form to get quantesx url
#   4.1.2   EBU     Add new request for EV parking + queue
#   4.1.3   EBU     Security Update
#   4.1.4   JFI     back to one requirements.txt / emi call removed