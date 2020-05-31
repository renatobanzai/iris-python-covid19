import irisnative
import json

class irisdomestic():
    def __init__(self, iris_config):
        self.iris_connection = None
        self.get_iris_connection(iris_config)
        self.iris_native = irisnative.createIris(self.iris_connection)
        return

    def kill(self, *args):
        self.iris_native.kill(*args)

    def set(self, value, *args):
        return self.iris_native.set(value, *args)

    def get(self, *args):
        return self.iris_native.get(*args)

    def get_iris_connection(self, iris_config):
        #todo: understand the behavior of connection object and implement the correct way
        if not self.iris_connection:
            self.iris_connection = irisnative.createConnection(iris_config["host"],
                                                               iris_config["port"],
                                                               iris_config["namespace"],
                                                               iris_config["username"],
                                                               iris_config["password"])

        return self.iris_connection

    def view_global(self, *global_array, **otherargs):
        newargs = otherargs.copy()
        if not "iris_connection" in otherargs:
            newargs["iris_connection"] = self.iris_connection
        return irisglobal(*global_array, **newargs)

class irisglobal():
    def __init__(self, *global_array, **otherargs):
        if "subscripts_filter" in otherargs:
            self.subscripts_filter = otherargs["subscripts_filter"]
        else:
            self.subscripts_filter = None
        self.global_array = global_array
        self.has_value = False
        self.subscripts = {}
        self.value = None
        self.isDefined = 0
        if "iris_connection" in otherargs:
            self.iris_connection = otherargs["iris_connection"]
            self.iris_native = irisnative.createIris(self.iris_connection)
            self.fill()
        return

    def fill(self):
        self.isDefined = self.iris_native.isDefined(*self.global_array)
        if self.isDefined == 0:
            return

        self.value = self.iris_native.get(*self.global_array)
        if self.value:
            self.has_value = True
        subscripts_iterator = self.iris_native.iterator(*self.global_array)
        if not self.subscripts_filter:
            for subscript_name, subscript_value in subscripts_iterator:
                self.subscripts[subscript_name] = irisglobal(*(self.global_array+(subscript_name,)),
                                                             iris_connection=self.iris_connection)
        else:
            for subscript_name in self.subscripts_filter:
                self.subscripts[subscript_name] = irisglobal(*(self.global_array+(subscript_name,)),
                                                             iris_connection=self.iris_connection)
        return

    def kill(self):
        self.iris_native.kill(*self.global_array)
        self.has_value = False
        return

    def get(self):
        self.value = self.iris_native.get(*self.global_array)
        return self.value

    def get_json(self):
        self.value = json.loads(self.iris_native.get(*self.global_array))
        return self.value

    def set_json(self, value):
        self.value = value
        return self.iris_native.set(json.dumps(value), *self.global_array)

    def set(self, value):
        self.value = value
        return self.iris_native.set(value, *self.global_array)

