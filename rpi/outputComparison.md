# Comaprsion of outputs
| variant | real output frequency |
| --- | ---|
|`scraping: every three samples, writing: every 300 samples` | from 91 to 100 samples/second|
|`scraping: every three samples, writing: every 1000 samples` | from 68 to 104 samples/second; big range due to long writing time |
| `scraping: every three samples, writing: every 1000 samples using second thread` | from 63 to 97 samples/second; irregular gathering frequency in the middle of the run|
|`scraping: every 0.01s, writing: every 300 samples` | from 75 to 100 samples/second; mostly within 90-100 samples/second range| 