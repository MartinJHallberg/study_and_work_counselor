"""Control components for the Streamlit app."""

import streamlit as st
from app.stage_views.stage import Stage
from agent.models import ProfileInformation
from agent.graph import create_main_graph

graph = create_main_graph()


def run_stage(stage: Stage, state: dict):
    """Run the correct node for the current app stage."""


    node_fn = graph.get_node(stage.value)
    result = node_fn(state)
    return result