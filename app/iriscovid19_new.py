import irisnative
import datetime
import csv
import json
import sys
from iris_python_suite import irisglobal, irisdomestic

#todo: implement exception treatment
#todo: implement unit test
#todo: join population data to use rate instead of absolute number of deaths
#todo: create a data pipeline
#todo: todo


''''''
class IRISCOVID19_new():
    def __init__(self, config):
        self.iris_connection = None
        self.iris_domestic = None
        self.deaths_file_path = ""
        self.countries_lookup_file_path = ""
        self.iris_config = config["iris"]
        self.get_iris_connection()
        self.get_iris_domestic(self.iris_config)

    def get_iris_connection(self):
        #todo: understand the behavior of connection object and implement the correct way
        if not self.iris_connection:
            self.iris_connection = irisnative.createConnection(self.iris_config["host"],
                                                               self.iris_config["port"],
                                                               self.iris_config["namespace"],
                                                               self.iris_config["username"],
                                                               self.iris_config["password"])

        return self.iris_connection

    def get_iris_domestic(self, config):
        self.iris_domestic = irisdomestic(config)

    def import_countries_lookup(self):
        #cleaning the global
        self.iris_domestic.kill("^countrydetails")
        with open(self.countries_lookup_file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row["Province_State"] == "":
                    name_global = ("^countrydetails",row["Country_Region"].lower(), "population")
                else:
                    name_global = ("^countrydetails", row["Country_Region"].lower(), "state",
                                   row["Province_State"].lower(),
                                   "population")

                self.iris_domestic.set(row["Population"], *name_global)

    def import_global_deaths(self):
        #todo: improve the iris global class to use
        self.iris_domestic.kill("^raw.covid19")
        with open(self.deaths_file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                #todo: summarize if the country just have province data
                #todo: exception if goes wrong
                #todo: rollback to last version
                if row["Province/State"] == "":
                    obj_global = self.iris_domestic.view_global("^raw.covid19", "countries", row["Country/Region"].lower(), "deaths")
                else:
                    obj_global = self.iris_domestic.view_global("^raw.covid19", "countries", row["Country/Region"].lower(), "state", row["Province/State"].lower(), "deaths")

                obj_global.set_json(list(row.items()))


    #todo: create a object like to iterate the globals
    #creates a specialized data layer
    def process_global_deaths(self):
        # todo: concatenate if the node has more than 32k char
        self.iris_domestic.kill("^end.timeless.deaths")
        self.iris_domestic.kill("^end.date.deaths")

        result = []

        countries = self.iris_domestic.view_global("^raw.covid19", "countries")
        for country in countries.subscripts:
            population = self.iris_domestic.view_global("^countrydetails", country, "population").value
            if population:
                population = int(population)
            else:
                population = 0
            timeless_deaths = self.get_raw_country_time_series(country)
            if timeless_deaths and population and population > 0:
                date_deaths_x = [format(datetime.datetime.strptime(x[0], "%m/%d/%y").date()) for x in
                                 timeless_deaths[4:len(timeless_deaths) - 1]]
                date_deaths_y = [int(x[1]) for x in timeless_deaths[4:len(timeless_deaths) - 1]]
                date_deaths_y_rate = [(int(x[1]) * 100000 / population) for x in
                                      timeless_deaths[4:len(timeless_deaths) - 1]]
                timeless_deaths_y = [int(x[1]) for x in timeless_deaths[4:len(timeless_deaths) - 1] if x[1] != "0"]
                timeless_deaths_y_rate = [(int(x[1]) * 100000 / population) for x in
                                          timeless_deaths[4:len(timeless_deaths) - 1] if x[1] != "0"]
                result.append((country, timeless_deaths))
                self.iris_domestic.set(json.dumps(timeless_deaths_y), "^end.timeless.deaths", "countries", country, "y")
                self.iris_domestic.set(json.dumps(timeless_deaths_y_rate), "^end.timeless.deaths", "countries", country,
                         "y_rate")
                self.iris_domestic.set(json.dumps(list(range(0, len(timeless_deaths_y) - 1))), "^end.timeless.deaths", "countries",
                         country, "x")
                self.iris_domestic.set(json.dumps(date_deaths_x), "^end.date.deaths", "countries", country, "x")
                self.iris_domestic.set(json.dumps(date_deaths_y), "^end.date.deaths", "countries", country, "y")
                self.iris_domestic.set(json.dumps(date_deaths_y_rate), "^end.date.deaths", "countries", country, "y_rate")
        return result

    # Get the raw data from IRIS from one country
    def get_raw_country_time_series(self, country):
        value = self.iris_domestic.view_global("^raw.covid19", "countries", country, "deaths").value
        if value:
            return json.loads(value)
        else:
            return None

    #Takes only days after 1st death in country
    #simplifying the time series to just values
    def get_country_timeless_deaths(self, deaths_list):
        #todo: find bycode the right position to start
        timeless_deaths_list = []
        for country in deaths_list:
            timeless_deaths_list.append((country[0],[int(x[1]) for x in country[1][4:len(country[1]) - 1] if x[1] != "0"]))
        return timeless_deaths_list

    #Get a formatted time series just as plotly needs
    def get_plotly_formatted_time_series(self, countries, time_series_type="", count_type=""):
        result = []

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
            country_axis = self.iris_domestic.view_global(global_name, "countries", country.lower()).subscripts
            x = json.loads(country_axis["x"].value)
            y = json.loads(country_axis[y_subscript].value)

            result.append({
                "y": y,
                "x": x,
                "name": country
            })
        return result

    #Get a list of countries to show in a dropdown style input
    def get_dash_formatted_countries(self):
        subscript_iter = self.iris_domestic.view_global("^end.date.deaths", "countries").subscripts
        result = []
        # Iterate over all nodes forwards
        for country in subscript_iter:
            result.append({
                "label":country,
                "value":country
            })
        return result