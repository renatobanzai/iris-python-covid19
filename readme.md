## IRIS Native API + Python + COVID-19 Data
A project solution using Python as application language and the IRIS as a database to observe and learn how to use IRIS Native API. 

## Why COVID-19 Data?
As the pandemy evolves in the world a lot of information are being spreaded so I decide to create an application to audit those information.
Unfornatelly each country has a different test policy so I decided to use the death data to avoid the cases subnotifications.

## How to run local?
After clone this repo, open a terminal and go to the iris-python-covid19 and type this command:

```
docker-compose up
```

# Do the data will be automatically updated?
No actuallty I just caught a file updated with 2020-05-23 data. 
You can update downloading it from https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv and copying it to this ./data folder.
*Eventually I'll automatize this job and all the data pipeline.   

After a while you can open your browser and go to the address, you will see some warnings of error because maybe the python container will start first and will restart until the IRIS container be prepared.

```
http://localhost:8050
```

##If you don't want to run local
There will be some screenshots to see. 

##Thanks
Collaboration are welcome! I'll perform some changes here in the code but I think it's a good start to the ones who use python!

## Note of condolence
For everyone who lost any loved one for COVID-19 I would like to extend my heartfelt condolence. May my condolences bring you peace during this painful time.