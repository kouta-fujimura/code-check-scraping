import requests
from bs4 import BeautifulSoup


def get_jra_soup_object(base_url, page_param):
    """Get soup object from jra base page by requests.
    Parse it by BeautifulSoup.
    """

    payload = {"cname": page_param}
    r = requests.post(url=base_url, data=payload)
    r.encoding = "shift-jis"

    soup = BeautifulSoup(r.text, "html.parser")

    return soup


def get_page_param(a_tag_text):
    """get page param from onclick argument in html <a>."""
    onclick_text = a_tag_text.get("onclick")
    onclick_text = onclick_text.split(", ")[1]
    page_param = onclick_text.strip("'").strip("');")

    return page_param
