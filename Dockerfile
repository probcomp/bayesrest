# parent image
FROM probcomp/notebook

USER root

# Set the working directory to /app
WORKDIR /app
ADD requirements.txt /app/

RUN conda install -n python2 --quiet --yes --file requirements.txt
RUN $CONDA_DIR/envs/python2/bin/pip install aumbry falcon-cors snaql alchemize

ADD . /app
RUN fix-permissions /app

ADD docker-entrypoint.sh /usr/local/bin/

# Make port 5000 available to the world outside this container
EXPOSE 5000

ENV PYTHONPATH /app

USER $NB_UID

ENTRYPOINT ["docker-entrypoint.sh", "start.sh", "python", "bayesapi"]
