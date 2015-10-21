# Docker to run dose calc remotely
FROM ubuntu:baseline
MAINTAINER O.K. <oleg.krivosheev@xcision.com>

# commands and configuration
RUN apt-get update && \
    apt-get install -y python-numpy && \
    apt-get install -y python-paramiko && \
    apt-get install -y net-tools && \
    apt-get install -y sshpass && \
    apt-get install -y iputils-ping && \
    apt-get install -y xz-utils && \
    apt-get install -y wget && \
    apt-get install -y wput && \
    apt-get autoremove; apt-get clean; apt-get autoclean

# make home dir
RUN mkdir -p /home/beamuser

# copy HEN_HOUSE & egsnrc

RUN mkdir -p /home/beamuser/run
COPY run /home/beamuser/run

RUN mkdir -p /opt/Geant/
COPY v4.10.01.p02 /opt/Geant/

# python environment
ENV PYTHONPATH /home/beamuser/runEGS/XcDefinitions:/home/beamuser/runEGS/XcMath:/home/beamuser/runEGS/XcMCCore:/home/beamuser/runEGS/XcIO

# GEANT environment
ENV G4LEVELGAMMADATA /opt/Geant/v4.10.01.p02/share/Geant4-10.1.2/data/PhotonEvaporation3.1
ENV G4NEUTRONXSDATA /opt/Geant/v4.10.01.p02/share/Geant4-10.1.2/data/G4NEUTRONXS1.4
ENV G4LEDATA /opt/Geant/v4.10.01.p02/share/Geant4-10.1.2/data/G4EMLOW6.41
ENV G4NEUTRONHPDATA /opt/Geant/v4.10.01.p02/share/Geant4-10.1.2/data/G4NDL4.5
ENV G4RADIOACTIVEDATA /opt/Geant/v4.10.01.p02/share/Geant4-10.1.2/data/RadioactiveDecay4.2
ENV G4ABLADATA /opt/Geant/v4.10.01.p02/share/Geant4-10.1.2/data/G4ABLA3.0
ENV G4PIIDATA /opt/Geant/v4.10.01.p02/share/Geant4-10.1.2/data/G4PII1.3
ENV G4SAIDXSDATA /opt/Geant/v4.10.01.p02/share/Geant4-10.1.2/data/G4SAIDDATA1.1
ENV G4REALSURFACEDATA /opt/Geant/v4.10.01.p02/share/Geant4-10.1.2/data/RealSurface1.0

ENV LD_LIBRARY_PATH /opt/Geant/v4.10.01.p02/lib:$LD_LIBRARY_PATH
ENV XZ_OPT=-9e

# running the show

WORKDIR /home/beamuser/
#CMD /home/beamuser/main
