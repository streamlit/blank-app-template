import streamlit as st

##st.title("🎈 My new app")
##st.write(
##    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
##)

import datetime
import re
from collections import defaultdict, namedtuple

import streamlit as st
from notion_client import Client

st.set_page_config("Roadmap", "https://streamlit.io/favicon.svg")
TTL = 24 * 60 * 60

Project = namedtuple(
    "Project",
    [
        "id",
        "title",
        "icon",
        "public_description",
        "stage",
        "quarter",
    ],
)


@st.cache_data(ttl=TTL, show_spinner="Fetching roadmap...")
def _get_raw_roadmap():
    notion = Client(auth=st.secrets.notion.token)

    # Only retrieve projects with an end date in the last twelve months, so we
    # don't have too many items (which slow down the app + make it look cluttered).
    twelve_months_ago = (
        datetime.datetime.now() - datetime.timedelta(days=365)
    ).isoformat()

    # We need this function to handle pagination because the Notion API
    # limits results to 100 items per request. This ensures we get all items
    # that m
