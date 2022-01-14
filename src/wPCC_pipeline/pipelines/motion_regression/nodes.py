"""
This is a boilerplate pipeline 'motion_regression'
generated using Kedro 0.17.6
"""

from src.models.regression import MotionRegression
import pandas as pd
import src.prime_system as prime_system
import src.models.vmm_martin as vmm
import src.symbols as s
from typing import Union
from src.models.vmm import ModelSimulator
import matplotlib.pyplot as plt


def fit_motions(
    data: pd.DataFrame, added_masses: dict, ship_data: dict
) -> Union[MotionRegression, pd.DataFrame]:

    ps = prime_system.PrimeSystem(**ship_data)  # model

    regression = MotionRegression(
        vmm=vmm,
        data=data,
        added_masses=added_masses,
        ship_parameters=ship_data,
        prime_system=ps,
        base_features=[s.u, s.v, s.r, s.delta, s.thrust],
    )

    parameters = pd.DataFrame(regression.parameters)
    return regression, parameters


def motion_regression_summaries(regression: MotionRegression) -> Union[str, str, str]:
    return (
        regression.model_X.summary().as_text(),
        regression.model_Y.summary().as_text(),
        regression.model_N.summary().as_text(),
    )


def create_model_from_motion_regression(regression: MotionRegression) -> ModelSimulator:

    model = regression.create_model(
        control_keys=["delta", "thrust"],
    )

    return model
