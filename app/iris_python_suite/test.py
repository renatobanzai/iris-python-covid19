from irisjson import irisjson
from irisglobal import irisglobal, irisdomestic
import irisnative


iris_connection = irisnative.createConnection("localhost",
                                                   51773,
                                                   "USER",
                                                   "_SYSTEM",
                                                   "theansweris42")
#test = irisglobal("^countrydetails", iris_connection=iris_connection)
#test2 = irisglobal("^countrydetails", "brazil", iris_connection=iris_connection)

iris_config = {
    "host": "localhost",
    "port": 51773,
    "namespace" : "USER",
    "username" : "_SYSTEM",
    "password":"theansweris42"
}

iris_domestic = irisdomestic(iris_config)
countries = iris_domestic.view_global("^raw.covid19", "countries")
print(countries)