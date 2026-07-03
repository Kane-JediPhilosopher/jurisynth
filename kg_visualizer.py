from pyvis.network import Network
from rdflib import Dataset
import streamlit as st
import streamlit.components.v1 as components


def shorten(uri):
    uri = str(uri)
    return uri.split("/")[-1].split("#")[-1]


def build_pyvis_graph(knowledge_graph, height="700px"):
    net = Network(height=height, width="100%", directed=True, bgcolor="#ffffff")
    net.toggle_physics(False)

    kg = Dataset()
    kg.parse(knowledge_graph, format="nquads")

    for source in kg.contexts():
        source_name = str(source.identifier)

        for s, p, o in source:
            s_str = str(s)
            p_str = str(p)
            o_str = str(o)

            s_label = shorten(s)
            p_label = shorten(p)
            o_label = shorten(o)

            net.add_node(s_str, label=s_label, title=f"{s_str}\nSource: {source_name}")
            net.add_node(o_str, label=o_label, title=f"{o_str}\nSource: {source_name}")

            net.add_edge(
                s_str,
                o_str,
                label=p_label,
                title=f"{p_str}\nSource: {source_name}"
            )

    net.set_options("""
    var options = {
      "edges": {
        "arrows": { "to": true }
      }
    }
    """)

    return net


def render_pyvis(net):
    components.html(net.generate_html(), height=750, scrolling=True)


st.title("Knowledge Graph Viewer")

net = build_pyvis_graph("C:\\Users\\Roxas\\OneDrive\\Desktop\\Project_Space\\eu_legislation_graph.nq")
render_pyvis(net)