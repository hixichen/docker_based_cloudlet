#Dockerfile for graphics test
FROM ubuntu
RUN apt-get update && apt-get install -y libgomp1 && rm -rf /var/lib/apt/lists/*
#EXPOSE 9093
COPY graphics /home/graphics
WORKDIR /home/graphics
RUN chmod 0766 cloudlet_test
ENV LD_LIBRARY_PATH=.:$LD_LIBRARY_PATH
ENTRYPOINT ["./cloudlet_test"]
CMD ["-h"]

