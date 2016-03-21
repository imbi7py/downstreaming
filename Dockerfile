FROM fedora:23
MAINTAINER Nick Coghlan <ncoghlan@gmail.com>

RUN dnf install -y python-pip

WORKDIR /home/downstreaming
RUN groupadd -r downstreaming && \
    useradd -r -g downstreaming -d /home/downstreaming \
            -c "Downstream Review Service" downstreaming && \
    chown -R downstreaming:downstreaming /home/downstreaming
ENV PYTHONPATH /home/downstreaming:$PYTHONPATH
USER downstreaming

# Only reinstall dependencies if they change
COPY requirements.txt .
RUN pip install --user -r requirements.txt
# For the time being, copy in the entire source checkout
COPY . .
# Using a local DB until this is set up for use with Compose & Kubernetes
RUN python createdb.py

# Mount a git checkout at /home/downstreaming for live editing

# This will ultimately be running under httpd with Flask-User but switching
# over to mod_wsgi-express as the WSGI server can wait for now
CMD ["/home/downstreaming/runserver.py", "--public"]
