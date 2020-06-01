import irisnative
import json
import networkx as nx
import plotly.graph_objects as go


class irisdomestic_chart():
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

    def view_global_chart(self, *global_array, **otherargs):
        newargs = otherargs.copy()
        if not "iris_connection" in otherargs:
            newargs["iris_connection"] = self.iris_connection
        return irisglobalchart(*global_array, **newargs)

class irisglobalchart():
    def __init__(self, *global_array, **otherargs):
        self.id = ".".join(global_array)
        self.obj_nx = otherargs["obj_nx"]
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
                self.obj_nx.add_edge(self.id, ".".join((self.global_array + (subscript_name,))))
                self.subscripts[subscript_name] = irisglobalchart(*(self.global_array + (subscript_name,)),
                                                                  iris_connection=self.iris_connection,
                                                                  obj_nx=self.obj_nx)
        else:
            for subscript_name in self.subscripts_filter:
                self.obj_nx.add_edge(self.id, ".".join((self.global_array + (subscript_name,))))
                self.subscripts[subscript_name] = irisglobalchart(*(self.global_array + (subscript_name,)),
                                                                  iris_connection=self.iris_connection,
                                                                  obj_nx=self.obj_nx)
        return

    def get_fig(self):
        _nx = self.obj_nx
        pos = nx.spring_layout(_nx)
        edge_x = []
        edge_y = []
        for edge in _nx.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.append(x0)
            edge_x.append(x1)
            edge_x.append(None)
            edge_y.append(y0)
            edge_y.append(y1)
            edge_y.append(None)

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines')

        node_text = []
        node_x = []
        node_y = []
        for node in _nx.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(node)

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            hoverinfo='text',
            marker=dict(size=10)
        )
        node_trace.text = node_text
        fig = go.Figure(data=[edge_trace, node_trace],
                        layout=go.Layout(
                            title='<br>Global Graph View: ' + ",".join(self.global_array),
                            titlefont_size=16,
                            showlegend=False,
                            hovermode='closest',
                            annotations=[dict(
                                showarrow=False,
                                xref="paper", yref="paper",
                                x=0.005, y=-0.002)],
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                        )
        return fig



iris_config = {
    "host": "localhost",
    "port": 51773,
    "namespace" : "USER",
    "username" : "_SYSTEM",
    "password":"theansweris42"
}

_nx = nx.Graph()
iris_domestic = irisdomestic_chart(iris_config)
countries = iris_domestic.view_global("^end.date.deaths", obj_nx=_nx)
countries.get_fig().show()
