# parent image
FROM probcomp/notebook

# Set the working directory to /app
WORKDIR /app

# Make port 5000 available to the world outside this container
EXPOSE 5000

RUN npm install -g redoc-cli

COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY . /app

ENV PYTHONPATH /app

CMD ["python", "bayesapi"]
