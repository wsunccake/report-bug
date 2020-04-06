# report-bug

## required package

- Python3


## developed tool

- IntelliJ IDEA/PyCharm


## install

```bash
linux:~ # git clone https://github.com/wsunccake/report-bug.git
linux:~ # cd report-bug
linux:report-bug # pip3 install -r requirements.txt
linux:report-bug # python -c 'import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import nltk
nltk.download()'
```


## run command

```bash
linux:report-bug # bin/get_failed_test.sh /tmp/output.xml
```


## run as docker

```bash
# pull image
linux:~ # docker pull python:3.6.10-alpine
linux:~ # docker run -itd -v <report-bug-path>:/app -v /data:/data -u $UID --name report-bug python:3.6.10-alpine

# install package
linux:~ # docker exec -it -u 0 report-bug pip install -r /app/requirements.txt

# copy xml
linux:~ # mv output.xml /data

# run app
linux:~ # docker exec -it report-bug /app/bin/get_failed_test.sh /data/output.xml
```


## faq

1. mac os download issue

error message: "urllib.error.URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate>

```bash
mac:~ $ open /Applications/Python\ 3.7/Install\ Certificates.command
```
