#!/bin/bash
echo "Generating Databases..."
rm todolist_server/todolist.db
rm authentication_server/users.db
rm social_media_server/family.db
python3 make_db.py
chmod 777 todolist.db
chmod 777 users.db
chmod 777 family.db
mv todolist.db todolist_server
mv users.db authentication_server
mv family.db social_media_server
echo "Created Databases..."
echo "Configuring Google Cloud"
PROJECT_ID='numeric-replica-272011'
gcloud config set project "$PROJECT_ID"
echo "Set Project to $PROJECT_ID"

echo "Removing all old instances & firewall-rules"
yes | gcloud compute instances delete auth-server

yes | gcloud compute instances delete todo-server

yes | gcloud compute instances delete soc-server

yes | gcloud compute firewall-rules delete rule-allow-tcp-5000 

echo "Creating new instances & firewall rules"
gcloud compute instances create auth-server --machine-type n1-standard-1 --image-family debian-9 --image-project debian-cloud --tags http-server --metadata-from-file startup-script=./auth_startup.sh

gcloud compute instances create todo-server --machine-type \
	n1-standard-1 --image-family debian-9 --image-project \
	debian-cloud --tags http-server --metadata-from-file \
	startup-script=./todolist_startup.sh

gcloud compute instances create soc-server --machine-type \
	n1-standard-1 --image-family debian-9 --image-project \
	debian-cloud --tags http-server --metadata-from-file \
	startup-script=./soc_startup.sh

gcloud compute firewall-rules create rule-allow-tcp-5000 \
	--source-ranges 0.0.0.0/0 --target-tags http-server --allow tcp:5000


gcloud compute scp --recurse  ./authentication_server auth-server:~
gcloud compute scp --recurse ./todolist_server/ todo-server:~
gcloud compute scp --recurse ./social_media_server soc-server:~

sleep 300  # DO THIS BECAUSE FLASK NEEDS TO INSTALL THINGS.

gcloud compute ssh auth-server --command="cd /home/samuelstein/authentication_server && python3 auth_server.py" &
gcloud compute ssh todo-server --command="cd /home/samuelstein/todolist_server && python3 server.py" &
gcloud compute ssh soc-server --command="cd /home/samuelstein/social_media_server && python3 family_network.py" &

export AUTH_IP=`gcloud compute instances list \
	--filter="name=auth-server" --format="value(EXTERNAL_IP)"`	
export TODO_IP=`gcloud compute instances list \
	--filter="name=todo-server" --format="value(EXTERNAL_IP)"`	
export SOCIAL_IP=`gcloud compute instances list \
	--filter="name=soc-server" --format="value(EXTERNAL_IP)"`	

rm ./main_server/api_ip.txt

echo "$AUTH_IP $TODO_IP $SOCIAL_IP" > ./main_server/api_ip.txt

docker build -t gcr.io/${PROJECT_ID}/web-app:v1 ./main_server/

docker push gcr.io/${PROJECT_ID}/web-app:v1

yes | gcloud container clusters delete social-to-do

gcloud container clusters create social-to-do 

kubectl create deployment social-to-do --image=gcr.io/${PROJECT_ID}/web-app:v1

kubectl expose deployment social-to-do --type=LoadBalancer --port 5000 --target-port 5000

sleep 120 

kubectl get services