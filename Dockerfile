FROM python:latest
MAINTAINER Ryan Kortmann "ryankortmann@gmadil.com"

# Packages
ADD docker/packages.txt /tmp/packages.txt
RUN apt-get update -y
RUN cat /tmp/packages.txt | xargs apt-get install -y

# PIP
ADD docker/pip.txt /tmp/pip.txt
RUN pip install --upgrade pip
RUN pip install -r /tmp/pip.txt

# Start server
WORKDIR /opt/emogi
EXPOSE 5000
CMD ["python", "run.py"]