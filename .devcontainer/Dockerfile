FROM python:3.11.14-slim-trixie
# Set up working directory
WORKDIR /app
ARG USERNAME=acsaba
ENV WORKDIR="/app"

RUN TZ=Etc/UTC apt-get update && apt-get install -y sudo python3-pip curl git

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && \
    apt-get install -y udev picocom && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y udev systemd

RUN echo 'ACTION=="add", SUBSYSTEM=="tty", ATTRS{idVendor}=="2e8a", ATTRS{idProduct}=="0005", RUN+="/bin/mknod %N c %M %m"' \
    > /etc/udev/rules.d/99-pico.rules && \
    echo 'ACTION=="remove", SUBSYSTEM=="tty", ATTRS{idVendor}=="2e8a", ATTRS{idProduct}=="0005", RUN+="/bin/rm -f %N"' \
    >> /etc/udev/rules.d/99-pico.rules

# Add user to be used. 1000 seems to be the default for WSL 
RUN groupadd --gid 1000 acsaba \
    && adduser --uid 1000 --gid 1000 acsaba && echo "acsaba:acsaba" | chpasswd && adduser acsaba sudo\
    # Save bash history
    && mkdir /commandhistory \
    && touch /commandhistory/.bash_history \
    && chown -R acsaba:acsaba /commandhistory \
    && chown acsaba:acsaba ${WORKDIR} \
    && apt-get install lsof -y \
    && apt-get install screen -y \
    # && apt-get install -y fuser \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && echo "export PROMPT_COMMAND='history -a' && export HISTFILE=/commandhistory/.bash_history" >> "/home/acsaba/.bashrc"

RUN usermod -a -G dialout acsaba

RUN echo "acsaba ALL=(ALL) NOPASSWD: /lib/systemd/systemd-udevd, /bin/mknod, /usr/bin/udevadm" \
    > /etc/sudoers.d/acsaba-udev && chmod 440 /etc/sudoers.d/acsaba-udev

USER acsaba



# Set default command
CMD ["bash"]