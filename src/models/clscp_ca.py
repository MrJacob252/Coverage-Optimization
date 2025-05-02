'''
Capacitated Location Set Covering Problem - Closest Assignment
From: R. L. Church, Alan Murray; Location Covering Models History, Applications and Advancements 
ISBN: 978-3-319-99846-6
'''

from gamspy import Container, Set, Parameter, Variable, Equation, Sum, Model, Sense
import pandas as pd
import numpy as np
from numpy.typing import NDArray
from typing import Any
import pathlib

import src.tools.load_data as load
import src.tools.dataset_visualisation as vis