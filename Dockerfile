FROM continuumio/anaconda3:latest

# copy all files and directories
COPY . .

# give executable permissions
RUN chmod +x ./app/entrypoint.sh

# create and activate conda environment
RUN conda env create -f environment.yml
RUN echo "conda activate myenv" >> ~/.bashrc
SHELL ["/bin/bash", "--login", "-c"]

# get gcc (indic-trans requirement)
# get wget (for mallet later)
# get java (LID_tool requirement)
# get aspell-hi dictionary and enchant (preprocessing requirement)
RUN apt-get update && apt-get -y install build-essential
RUN apt-get -y install wget
RUN apt -y install default-jre
RUN apt-get -y install aspell-hi
RUN apt-get -y install python3-enchant

# cd into /app/indic-trans and install
WORKDIR /app/indic-trans
RUN pip install -r requirements.txt
RUN pip install .

# cd into /app and get mallet for LID_tool
WORKDIR /app
RUN wget https://mallet.cs.umass.edu/dist/mallet-2.0.8.tar.gz
RUN tar -xvzf mallet-2.0.8.tar.gz
RUN mv mallet-2.0.8 LID_tool/
RUN rm -rf mallet-2.0.8.tar.gz
RUN rm ._mallet-2.0.8

# set workdir to /app
WORKDIR /app

# run api
ENTRYPOINT ["./entrypoint.sh"]