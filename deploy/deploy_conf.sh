#! /bin/bash

for i in 192.168.108.137 192.168.109.153 192.168.110.166;
do
    #scp nginx.conf.wapquan root@$i:/opt/apps/nginx/conf/nginx.conf;
    #ssh root@$i -C 'kill -HUP $(cat /opt/apps/nginx/conf/nginx.pid)';

    ssh root@$i -C 'rm -rf /opt/www/pr/; rm -rf /opt/www/pr.tgz;' 
    scp pr.tgz root@$i:/opt/www/;
    ssh root@$i -C 'cd /opt/www; tar -xzf pr.tgz;';

done

#scp nginx.conf.wapquan root@$i:/opt/apps/nginx/conf/nginx.conf;
update_nginx_conf () {
    scp nginx.conf.wapquan root@$i:/opt/apps/nginx/conf/nginx.conf;
}
restar_nginx () {
    ssh root@$i -C 'kill -HUP $(cat /opt/apps/nginx/conf/nginx.pid)';
}
deploy_back_site () {
    # tar
    tar -czf back_site.tgz ux_quan 

    # scp
    scp back_site.tgz root@$i:/opt/www/pr/;

    # restart nginx
    # restart_nginx;
}
