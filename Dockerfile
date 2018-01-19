# current problem: running "docker run -p 4000:80 bayesrest"
#
#Traceback (most recent call last):
#  File "app.py", line 3, in <module>
#    from flask import Flask, request
#ImportError: No module named flask
#
# Tried to fix this by adding the ["/bin/bash" etc.] instead of just running commands directly, but no luck

# parent image
FROM jupyter/scipy-notebook:da2c5a4d00fa

# use bash instead of sh for Conda
#ENTRYPOINT ["/bin/bash", "-c"]

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN ["/bin/bash", "-c", "conda create --name myenv python=2.7"]
RUN ["/bin/bash", "-c", "source activate myenv && pip install Flask"]
RUN ["/bin/bash", "-c", "source activate myenv && pip install flask-cors"]
RUN ["/bin/bash", "-c", "source activate myenv && pip install pyopenssl"]
RUN ["/bin/bash", "-c", "conda install -n myenv --quiet --yes -c probcomp -c cidermole -c fritzo -c  ursusest \
    	'apsw' \
   	 'bayeslite=0.3.2' \
   	 'cgpm=0.1.2' \
   	 'crosscat=0.1.56.1' \
    	'distributions=2.2.1' \
    	'libprotobuf=2.6.1' \
    	'loom=0.2.10' \
    	'iventure=0.2.2' \
    	'venture=0.5.1.1'"]

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python2.7", "app.py"]
