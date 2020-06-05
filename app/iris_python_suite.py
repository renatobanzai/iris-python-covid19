import irisnative
import json
import networkx as nx
import plotly.graph_objects as go

class irisdomestic():
    def __init__(self, iris_config):
        self.iris_connection = None
        self.get_iris_connection(iris_config)
        self.iris_native = irisnative.createIris(self.iris_connection)
        return

    def isDefined(self, *args):
        self.iris_native.isDefined(*args)

    def kill(self, *args):
        self.iris_native.kill(*args)

    def set(self, value, *args):
        return self.iris_native.set(value, *args)

    def get(self, *args):
        return self.iris_native.get(*args)

    def iterator(self, *args):
        return self.iris_native.iterator(*args)

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

    def view_global_chart(self, *global_array, **otherargs):
        newargs = otherargs.copy()
        if not "iris_connection" in otherargs:
            newargs["iris_connection"] = self.iris_connection
        return irisglobalchart(*global_array, **newargs)

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
                irisglobal(*(self.global_array+(subscript_name,)),
                           iris_connection=self.iris_connection)
        else:
            for subscript_name in self.subscripts_filter:
                irisglobal(*(self.global_array+(subscript_name,)),
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
                new_global_array = self.global_array + (subscript_name,)
                self.obj_nx.add_edge(self.global_array, new_global_array)
                irisglobalchart(*new_global_array,
                                iris_connection=self.iris_connection,
                                obj_nx=self.obj_nx)
        else:
            for subscript_name in self.subscripts_filter:
                new_global_array = self.global_array + (subscript_name,)
                self.obj_nx.add_edge(self.global_array, new_global_array)
                irisglobalchart(*new_global_array,
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
            line=dict(width=1, color='#888'),
            hoverinfo='none',
            mode='lines')

        node_text = []
        node_hovertext = []
        node_x = []
        node_y = []
        for node in _nx.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(node[-1])
            node_hovertext.append(node)

        qtt = len(node_text)
        size = 50
        mode = 'markers+text'
        if qtt > 0 and qtt < 40:
            size = 50
            mode = 'markers+text'
        elif qtt > 39 and qtt< 80:
            size = 50
            mode = 'markers+text'
        elif qtt > 79 and qtt < 300:
            size = 10
            mode = 'markers'
        elif qtt > 299:
            size = 5
            mode = 'markers'




        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode=mode,
            hoverinfo='text',
            marker=dict(size=50),
            text=node_text,
            hovertext=node_hovertext
        )

        fig = go.Figure(data=[edge_trace, node_trace],
                        layout=go.Layout(
                            title='Global Graph View: ' + ",".join(self.global_array),
                            titlefont_size=12,
                            showlegend=False,
                            hovermode='closest',
                            annotations=[dict(
                                showarrow=False,
                                xref="paper", yref="paper",
                                x=0.005, y=-0.002)],
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                        )
        fig.update_layout(
            autosize=False,
            width=1200,
            height=600,
            margin=dict(
                l=0,
                r=0,
                b=0,
                t=0,
                pad=4
            ),
            paper_bgcolor="LightSteelBlue",
        )
        return fig
