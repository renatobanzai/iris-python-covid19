import irisnative
import datetime
import csv
import json

#todo: implement exception treatment
#todo: implement unit test
#todo: join population data to use rate instead of absolute number of deaths
#todo: create a data pipeline
#todo: todo
class IRISCOVID19():
    def __init__(self):
        self.deaths_file_path = ""
        self.countries_lookup_file_path = ""
        self.iris_config = None
        self.iris_native = None
        self.iris_connection = None

    def get_iris_native(self):
        #todo: understand the behavior of connection object and implement the correct way
        if not self.iris_connection:
            self.iris_connection = irisnative.createConnection(self.iris_config["host"],
                                                               self.iris_config["port"],
                                                               self.iris_config["namespace"],
                                                               self.iris_config["username"],
                                                               self.iris_config["password"])


        print("Connected to InterSystems IRIS")
        # Create an iris object
        self.iris_native = irisnative.createIris(self.iris_connection)
        return self.iris_native

    def import_countries_lookup(self):
        self.get_iris_native()
        #cleaning the global
        self.iris_native.kill("^countrydetails")
        with open(self.countries_lookup_file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row["Province_State"] == "":
                    self.iris_native.set(row["Population"], "^countrydetails", row["Country_Region"].lower(), "population")
                else:
                    self.iris_native.set(row["Population"], "^countrydetails", row["Country_Region"].lower(), "state", row["Province_State"].lower(), "population")


    def import_global_deaths(self):
        self.get_iris_native()
        #cleaning the global
        self.iris_native.kill("^raw.covid19")
        with open(self.deaths_file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                #todo: summarize if the country just have province data
                #todo: broke the string cause globals allow just 32k chars/node
                #todo: exception if goes wrong
                #todo: rollback to last version
                if row["Province/State"] == "":
                    self.iris_native.set(json.dumps(list(row.items())), "^raw.covid19", "countries", row["Country/Region"].lower(), "deaths")
                else:
                    self.iris_native.set(json.dumps(list(row.items())), "^raw.covid19", "countries", row["Country/Region"].lower(), "state", row["Province/State"].lower(), "deaths")

    #todo: create a object like to iterate the globals
    #creates a specialized data layer
    def process_global_deaths(self):
        iris = self.get_iris_native()
        # todo: concatenate if the node has more than 32k char
        self.iris_native.kill("^end.timeless.deaths")
        self.iris_native.kill("^end.date.deaths")
        
        leverl1_subscript_iter = iris.iterator("^raw.covid19", "countries")
        result = []
        # Iterate over all nodes forwards
        for level1_subscript, level1_value in leverl1_subscript_iter:
            population = iris.getFloat("^countrydetails", level1_subscript, "population")
            timeless_deaths = self. get_raw_country_time_series(level1_subscript)
            if timeless_deaths and population and population > 0:
                date_deaths_x = [format(datetime.datetime.strptime(x[0], "%m/%d/%y").date()) for x in timeless_deaths[4:len(timeless_deaths) - 1]]
                date_deaths_y = [int(x[1]) for x in timeless_deaths[4:len(timeless_deaths) - 1]]
                date_deaths_y_rate = [(int(x[1])*100000/population) for x in timeless_deaths[4:len(timeless_deaths) - 1]]
                timeless_deaths_y = [int(x[1]) for x in timeless_deaths[4:len(timeless_deaths) - 1] if x[1] != "0"]
                timeless_deaths_y_rate = [(int(x[1])*100000/population) for x in timeless_deaths[4:len(timeless_deaths) - 1] if x[1] != "0"]
                result.append((level1_subscript, timeless_deaths))
                iris.set(json.dumps(timeless_deaths_y), "^end.timeless.deaths", "countries", level1_subscript, "y")
                iris.set(json.dumps(timeless_deaths_y_rate), "^end.timeless.deaths", "countries", level1_subscript, "y_rate")
                iris.set(json.dumps(list(range(0, len(timeless_deaths_y)-1))), "^end.timeless.deaths", "countries",level1_subscript, "x")
                iris.set(json.dumps(date_deaths_x), "^end.date.deaths", "countries", level1_subscript, "x")
                iris.set(json.dumps(date_deaths_y), "^end.date.deaths", "countries", level1_subscript, "y")
                iris.set(json.dumps(date_deaths_y_rate), "^end.date.deaths", "countries", level1_subscript, "y_rate")
        return result

    # Get the raw data from IRIS from one country
    # todo: create a specialized layer of data to avoid processing
    def get_raw_country_time_series(self, country):
        iris = self.get_iris_native()
        # todo: concatenate if the node has more than 32k char
        value = iris.get("^raw.covid19", "countries", country, "deaths")
        if value:
            return json.loads(iris.get("^raw.covid19", "countries", country, "deaths"))
        else:
            return None

    #Get the raw data from IRIS from one country
    #todo: create a specialized layer of data to avoid processing
    def get_country_time_series(self, country):
        iris = self.get_iris_native()
        #todo: concatenate if the node has more than 32k char
        return json.loads(iris.get("^covid19", "countries", country.lower(), "deaths"))

    #Takes only days after 1st death in country
    #simplifying the time series to just values
    def get_country_timeless_deaths(self, deaths_list):
        #todo: find bycode the right position to start
        timeless_deaths_list = []
        for country in deaths_list:
            timeless_deaths_list.append((country[0],[int(x[1]) for x in country[1][4:len(country[1]) - 1] if x[1] != "0"]))
        return timeless_deaths_list

    #Get RAW Data from each country in countries list
    def get_time_series(self, countries):
        result = []
        for country in countries:
            result.append((country, self.get_country_time_series(country)))
        return result

    #Get a formatted time series just as plotly needs
    def get_plotly_formatted_time_series(self, countries, time_series_type="", count_type=""):
        result = []
        iris = self.get_iris_native()

        global_name = "^end.timeless.deaths"
        if time_series_type== "timeless":
            global_name="^end.timeless.deaths"
        elif time_series_type== "date":
            global_name = "^end.date.deaths"

        y_subscript = "y"
        if count_type=="rate":
            y_subscript = "y_rate"


        # todo: concatenate if the node has more than 32k char
        for country in countries:
            x = json.loads(iris.get(global_name, "countries", country.lower(), "x"))
            y = json.loads(iris.get(global_name, "countries", country.lower(), y_subscript))
            result.append({
                "y": y,
                "x": x,
                "name": country
            })
        return result

    #Get a list of countries to show in a dropdown style input
    def get_dash_formatted_countries(self):
        iris = self.get_iris_native()
        # todo: concatenate if the node has more than 32k char
        subscript_iter = iris.iterator("^end.date.deaths", "countries")
        result = []
        # Iterate over all nodes forwards
        for subscript, value in subscript_iter:
            result.append({
                "label":subscript,
                "value":subscript
            })
        return result

    def set_default_countries(self, countries):
        s_value = json.dumps(countries)
        iris = self.get_iris_native()
        iris.set(s_value, "^config", "defaultcountries")

    def get_default_countries(self):
        iris = self.get_iris_native()
        return json.loads(iris.get("^config", "defaultcountries"))