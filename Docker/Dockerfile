# Docker to run dose calc remotely
FROM ubuntu:baseline
MAINTAINER O.K. <https://github.com/Kri-Ol/Geant4-on-GCE>

# making run directory
RUN mkdir -p /home/beamuser/run
COPY run /home/beamuser/run

# now copying G4 installation
RUN mkdir -p /opt/Geant/v4.10.01.p03
COPY v4.10.01.p03 /opt/Geant/v4.10.01.p03

# magic
COPY magickey.json /home/beamuser/run/magickey.json

COPY config_gs.json /home/beamuser/run/config_gs.json

# python environment
ENV PYTHONPATH /home/beamuser/run/XcDefinitions:/home/beamuser/run/XcMath:/home/beamuser/run/XcMCCore:/home/beamuser/run/XcIO

# GEANT environment
ENV G4LEVELGAMMADATA /opt/Geant/v4.10.01.p03/share/Geant4-10.1.3/data/PhotonEvaporation3.1
ENV G4NEUTRONXSDATA /opt/Geant/v4.10.01.p03/share/Geant4-10.1.3/data/G4NEUTRONXS1.4
ENV G4LEDATA /opt/Geant/v4.10.01.p03/share/Geant4-10.1.3/data/G4EMLOW6.41
ENV G4NEUTRONHPDATA /opt/Geant/v4.10.01.p03/share/Geant4-10.1.3/data/G4NDL4.5
ENV G4RADIOACTIVEDATA /opt/Geant/v4.10.01.p03/share/Geant4-10.1.3/data/RadioactiveDecay4.2
ENV G4ABLADATA /opt/Geant/v4.10.01.p03/share/Geant4-10.1.3/data/G4ABLA3.0
ENV G4PIIDATA /opt/Geant/v4.10.01.p03/share/Geant4-10.1.3/data/G4PII1.3
ENV G4SAIDXSDATA /opt/Geant/v4.10.01.p03/share/Geant4-10.1.3/data/G4SAIDDATA1.1
ENV G4REALSURFACEDATA /opt/Geant/v4.10.01.p03/share/Geant4-10.1.3/data/RealSurface1.0

ENV LD_LIBRARY_PATH /opt/Geant/v4.10.01.p03/lib:$LD_LIBRARY_PATH
ENV XZ_OPT=-9e

# running the show

WORKDIR /home/beamuser/run
CMD /home/beamuser/run/main.py
