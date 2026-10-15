"""Execute actual Streamlit pages, including empty filters, against the local DB."""
from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest

pytestmark = pytest.mark.skipif(not Path('data/processed/courtiq.sqlite').exists(), reason='Run data pipeline first')


@pytest.mark.parametrize('section',['Overview','Player comparison','Model evaluation','Data and limitations'])
def test_sections(section):
    app=AppTest.from_file('app.py').run(timeout=30)
    app.sidebar.radio[0].set_value(section).run(timeout=30)
    assert not app.exception
    assert app.title[0].value=='Same player. Different court.'


def test_empty_selection():
    app=AppTest.from_file('app.py').run(timeout=30)
    app.sidebar.multiselect[0].set_value([]).run(timeout=30)
    assert not app.exception
    assert any('No matches' in info.value for info in app.info)
