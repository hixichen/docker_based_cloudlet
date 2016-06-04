#Dockee file for moped
#Version 12.04
FROM ubuntu:precise
MAINTAINER chen xi

COPY moped /home/moped
WORKDIR /home/moped

RUN apt-get update &&\
     apt-get install -y libgomp1 libglew1.6 freeglut3 libdevil-dev libopencv-core2.3 \
     libopencv-imgproc2.3 libopencv-highgui2.3 \
     libopencv-ml2.3 libopencv-features2d2.3 \
     libopencv-calib3d2.3 libopencv-objdetect2.3 libopencv-contrib2.3 libopencv-legacy2.3 \
     && rm -rf /var/lib/apt/lists/*

#EXPOSE 9092
ENTRYPOINT ["./moped_server"]
CMD ["-h"]
