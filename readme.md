# IRIS Python Suite
A set of tools and practices (or experiments) using Python as application language and the IRIS as a database 
to observe and learn how to use IRIS Native API. 

## IRIS Python COVID19 Chart
As the pandemy evolves in the world a lot of information are being spreaded so I decided to create an application to audit those information.
Unfortunately each country has a different test policy so I decided to use the death data to avoid the cases subnotifications.

## Tools

irisglobal: A class that I made to be filled as a Graph Data Structure and all recursive. So if you instatiate one irisglobal
object all global data will be in memory in this object.

Imagine a global like this*

```
^covid19("countries", "us")=5000
^covid19("countries", "us", "newyork")=10
^covid19("countries", "brazil", )=100
```

With my class irisglobal in python you have just to instatiate 
to have access to all global nodes in memory and indexed as a dictionary. 

```
obj_global = irisglobal("^covid19")
print(obj_global.subscripts["countries"].subscripts["brazil"].value)
100
```

irisdomestic: A class that I made to show one way I use the Native API extending the native api.  

```
#has the same methods of irisnative + factory of irisglobal class
```

irisjson: An experiment to serialize a json into a global array.

```
#under construction
```

irisyaml: An experiment to serialize a YAML into a global array.

```
Under construction
```

irisglobalgraph: Plot the global in a interactive chart.

## Getting started

### Prerequisites
* git
* docker and docker-compose
* acess to a terminal in your environment

### Installing
After cloning this repo open a terminal go to the iris-python-covid19 and type these commands:

```
docker-compose build

docker-compose up
```

I'm working to find the correctly the compose configuration so you will see some warning of python not working. 
This is because the application is waiting (and restarting) until the IRIS container don't wake up properly.

### Estimated time to up containers
1st time running will depend of your internet link to download the images and dependencies. 
If it last more than 15 minutes probably something goes wrong feel free to communicate here.
After the 1st time running the next ones will perform better and take less then 2 minutes.


### If is everything ok
After a while you can open your browser and go to the address:
 
```
http://localhost:8050
```

### You should look at IRIS Admin Portal

I'm using for now the USER namespace (todo: create my onw namespace)

```
http://localhost:9092
user: _SYSTEM
pass: theansweris42
```


### You should look at IRIS Admin Portal

I'm using for now the USER namespace (todo: create my onw namespace)

```
http://localhost:9092
user: _SYSTEM
pass: theansweris42
```


## Will the data be automatically updated?
No actuallty I just caught a file updated with 2020-05-23 data. 
You can update downloading it from https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv and copying it to this ./data folder.
*Eventually I'll automatize this job and all the data pipeline.   

## How does it work?
This is a python application using the IRIS service to persist and read data. I use globals to store raw data from JHU and plot it using Python community libraries. All code in ./app folder.

## If you don't want to run local
There will be some screenshots to see and a url with you can browse the solution. 

## Note of condolence
For everyone who lost any loved one for COVID-19 I would like to extend my heartfelt condolence. May my condolences bring you peace during this painful time.

## Thanks
Collaboration are welcome! I'll perform some changes here in the code but I think it's a good start to the ones who use python!
