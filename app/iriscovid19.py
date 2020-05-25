import irisnative
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

    def import_global_deaths(self):
        self.get_iris_native()
        #cleaning the global
        self.iris_native.kill("^covid19")
        with open(self.deaths_file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                #todo: summarize if the country just have province data
                #todo: broke the string cause globals allow just 32k chars/node
                if row["Province/State"] == "":
                    self.iris_native.set(json.dumps(list(row.items())), "^covid19", "countries", row["Country/Region"].lower(), "deaths")
                else:
                    self.iris_native.set(json.dumps(list(row.items())), "^covid19", "countries", row["Country/Region"].lower(), row["Province/State"].lower(), "deaths")

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
    def get_plotly_formatted_time_series(self, countries):
        timeless_cases = self. get_time_series(countries)
        timeless_cases = self.get_country_timeless_deaths(timeless_cases)
        result = []
        for country in timeless_cases:
            result.append({
                "y": country[1],
                "name": country[0]
            })
        return result

    #Get a list of countries to show in a dropdown style input
    def get_dash_formatted_countries(self):
        iris = self.get_iris_native()
        # todo: concatenate if the node has more than 32k char
        subscript_iter = iris.iterator("^covid19", "countries")
        result = []
        # Iterate over all nodes forwards
        for subscript, value in subscript_iter:
            result.append({
                "label":subscript,
                "value":subscript
            })
        return result