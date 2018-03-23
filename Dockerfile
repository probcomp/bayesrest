# parent image
FROM probcomp/notebook

# Set the working directory to /app
WORKDIR /app
# Copy the current directory contents into the container at /app
ADD . /app

RUN conda install -n python2 --quiet --yes --file requirements.txt

# Define environment variable
ENV NAME World

# Make port 5000 available to the world outside this container
EXPOSE 5000

ENTRYPOINT ["/app/docker-entrypoint.sh", "start.sh", "python", "app.py"]
