import numpy as np
import pandas as pd
from typing import Literal, Any
import matplotlib.pyplot as plt
import scipy as sc
from scipy.stats import qmc

'''
Service centres - in square grid equal distance away
Customer locations:
    IN:
        - Some space dimensions (WxH)
        - Number of customers
    - Split space into chunks
    - Each chunk some random density value which will define poisson disc r
    - fill each chunk using poisson - disc
    
Option 2:
    - Use poisson disc to create the random space
    - Randomly select N samples
'''


if __name__ == "__main__":
    pass