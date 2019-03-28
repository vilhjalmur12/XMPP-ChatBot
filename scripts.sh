sudo su
sudo /opt/ejabberd-16.09/bin/ejabberdctl muc_online_rooms global
sudo /opt/ejabberd-16.09/bin/ejabberdctl create_room botroom conference.3.18.234.195 3.18.234.195
sudo /opt/ejabberd-16.09/bin/ejabberdctl register bot4 3.18.234.195 password