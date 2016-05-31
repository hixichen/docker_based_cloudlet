Summer project: case for container-based cloudlet

mail: chenx@andrew.cmu.edu


[Test Environment]:

python 2.7.

ubuntu 14.04.


[How to use]:

#need root privilege now

        python cloudlet.py [argv]
        example:
        
        VM1:
        
        $python cloudlet.py check
        $python cloudlet.py overlay new_ubuntu  ubuntu
        $docker run -d --name test0 ubuntu
        $python cloudlet.py migrate test0 -t 192.168.x.x(ip of vm2)
        
        VM2:
        $python cloudlet.py service -l
        

[support command]:

        cloudlet check

        cloudlet -v

        cloudlet -h

        cloudlet help


[receive and restore]:

        cloudlet service -l


[overlay]:

        cloudlet fetch [service name]

        cloudlet search [service name]

        cloudlet overlay  new_image  base image '-o [image_name]'


[migrate]:

        cloudlet migrate [container id] -t [destionation address]



