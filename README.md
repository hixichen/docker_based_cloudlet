
[Info]:

author: chen xi
mail: chenx@andrew.cmu.edu

[Test Environment]:
python 2.7.
ubuntu 14.04.


[How to use]:
python cloudlet.py [argv]


[support command]:

cloudlet check
cloudlet -v
cloudlet -h  
cloudlet help

#receive
cloudlet service -l


#for overlay
cloudlet fetch [service name]
cloudlet search [service name]
cloudlet overlay  new_image base image '-o [image_name]'

#for migrate
cloudlet migrate [container id] -t [destionation address]



