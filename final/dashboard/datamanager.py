import plotly.graph_objects as go
import pandas as pd


class DataManager:
    def __init__(self, filepath):
        self.data = pd.read_csv(filepath)

    def get_data(self):
        return self.data


class TreeDiagram:
    def __init__(self, data):
        self.data = data

    def create_tree(self, hierarchy_columns):
        # Generate hierarchical data
        path = [col for col in hierarchy_columns if col in self.data.columns]
        values = self.data.groupby(path)['Quantity in Millions'].sum().reset_index()

        # Building the hierarchy for the sunburst chart
        labels = []
        parents = []
        ids = []

        for row in zip(*[values[col] for col in path]):
            for i in range(len(row)):
                id_path = "/".join(row[:i + 1])
                parent_path = "/".join(row[:i])
                if id_path not in ids:
                    ids.append(id_path)
                    labels.append(row[i])
                    parents.append(parent_path if i > 0 else "")

        fig = go.Figure(go.Sunburst(
            labels=labels,
            parents=parents,
            values=values['Quantity in Millions'],
            branchvalues="total"
        ))
        fig.update_layout(margin=dict(t=0, l=0, r=0, b=0))
        return fig




