FROM htcondor/submit

RUN yum install -y pip && pip install jupyterlab ipywidgets
RUN mv /etc/supervisord.conf /etc/supervisord-condor.conf

COPY supervisord.conf /etc/supervisord.conf
COPY ssh_config /etc/ssh_config


