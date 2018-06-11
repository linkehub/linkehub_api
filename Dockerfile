# Grab the latest alpine image
FROM alpine:latest

# Install dependencies that are missing in the default Alpine distribution
RUN echo "http://dl-8.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories
RUN apk update
RUN apk add --upgrade apk-tools
RUN apk add --no-cache --update-cache gcc musl-dev linux-headers gfortran python3 python3-dev py3-pip bash build-base wget freetype-dev libpng-dev openblas-dev
RUN ln -s /usr/include/locale.h /usr/include/xlocale.h

# Add our code
ADD ./webapp /opt/webapp/
WORKDIR /opt/webapp

# Upgrade pip
RUN pip3 install --upgrade pip
RUN pip3 install --upgrade --no-cache-dir setuptools
RUN pip3 install --upgrade --no-cache-dir wheel
RUN pip3 install --upgrade --no-cache-dir virtualenv
RUN source ENV/bin/activate

# Install dependencies
ADD ./webapp/requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -q -r /tmp/requirements.txt

# Install AI and ML related libraries
RUN pip3 install --no-cache-dir numpy==1.14.3
RUN pip3 install --no-cache-dir scipy
RUN pip3 install --no-cache-dir pandas
RUN pip3 install --no-cache-dir -U scikit-learn

# Run the image as a non-root user
RUN adduser -D myuser
USER myuser

# Expose is NOT supported by Heroku
# EXPOSE 5000

# Run the app.  CMD is required to run on Heroku
# $PORT is set by Heroku			
CMD gunicorn --bind 0.0.0.0:$PORT wsgi