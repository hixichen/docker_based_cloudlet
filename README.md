Summer project: case for container-based cloudlet

mail: chenx@andrew.cmu.edu


[Test Environment]:
python 2.7.

ubuntu 14.04.


[How to use]:

[need root privilege now]

python cloudlet.py [argv]

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


[migrate]
cloudlet migrate [container id] -t [destionation address]



