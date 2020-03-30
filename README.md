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
