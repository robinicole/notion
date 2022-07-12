"""
Plot a graph of your Zettelkasten notes
"""

import requests
import networkx as nx
from pyvis.network import Network
import sys


class DataBaseGraph:
    """
    High level interface on top of a notion database
    """
    def __init__(self, token: str, database_id: str):
        self._data = self.download_data(token, database_id)

    def download_data(self, token: str, database_id: str) -> dict:
        """
        Download the data from of a database with the notion API
        """
        headers = {
            "Authorization": f"Bearer {token}",
            "Notion-Version": "2022-02-22",
            "Content-Type": "application/json",
        }
        resp = requests.post(
            f"https://api.notion.com/v1/databases/{database_id}/query", headers=headers
        )
        resp = resp.json()
        return resp["results"]

    @staticmethod
    def get_title(result: dict) -> str:
        """
        Extract the title from 1 item of the database
        """
        return result["properties"]["Name"]["title"][0]["plain_text"]

    @staticmethod
    def get_id(result: dict) -> str:
        """
        Extract the id from 1 item of the database
        """
        return result["id"]

    @staticmethod
    def get_children(result: str) -> list:
        """
        Extract the children from 1 item of the database
        """
        return [el["id"] for el in result["properties"]["Children"]["relation"]]

    @property
    def id_to_title(self) -> dict:
        return {row["id"]: row["title"] for row in self.data}

    @property
    def data(self) -> dict:
        """
        Return a pruned version of the data
        """
        return [
            {
                "title": self.get_title(result),
                "id": self.get_id(result),
                "children": self.get_children(result),
            }
            for result in self._data
        ]

    @property
    def graph(self) -> nx.DiGraph:
        """
        Return the graph of how the elements in the database are connected together
        """
        edges = []
        for row in self.data:
            for children in row["children"]:
                edges.append((self.id_to_title[row["id"]], self.id_to_title[children]))
        return nx.DiGraph(edges)

    def show_graph(self, output="example.html", **kwargs):
        """
        Plot the graph in an HTML file
        """
        net = Network(notebook=True, directed=True)
        net.from_nx(self.graph)
        net.force_atlas_2based(**kwargs)
        return net.show(output)


if __name__ == "__main__":
    try:
        token = sys.argv[1]
        database_id = sys.argv[2]
        output = sys.argv[3]
        notion_db_perso = DataBaseGraph(token=token, database_id=database_id)
        notion_db_perso.show_graph(output=output)
        print(f"results in {output}")
    except Exception as e:
        print(f"Exception raised {e}")
        print(
            "Did you use this script with poetry run python -m notion_graph.main {secret_token} {database_id} {output}"
        )
