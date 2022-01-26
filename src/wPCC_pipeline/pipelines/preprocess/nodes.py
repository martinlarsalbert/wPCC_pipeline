"""
This is a boilerplate pipeline 'lowpass'
generated using Kedro 0.17.6
"""

import pandas as pd
from src.visualization import plot
import matplotlib.pyplot as plt

from numpy import cos as cos
from numpy import sin as sin
import numpy as np
from src.data.lowpass_filter import lowpass_filter


def load(raw_data: pd.DataFrame):

    data = raw_data.copy()

    ## Zeroing:
    data.index -= data.index[0]
    data["x0"] -= data.iloc[0]["x0"]
    data["y0"] -= data.iloc[0]["y0"]
    # data["psi"] -= data.iloc[0]["psi"]

    return data


def add_thrust(df: pd.DataFrame, thrust_channels: list) -> pd.DataFrame:

    assert isinstance(thrust_channels, list), "'thrust_channels' should be a list"

    if len(thrust_channels) > 0:
        df["thrust"] = df[thrust_channels].sum(axis=1)

    return df


def track_plot(df: pd.DataFrame, ship_data: dict):

    fig, ax = plt.subplots()
    fig.set_size_inches(10, 10)
    plot.track_plot(
        df=df,
        lpp=ship_data["L"],
        x_dataset="x0",
        y_dataset="y0",
        psi_dataset="psi",
        beam=ship_data["B"],
        ax=ax,
    )

    return fig


def filter(df: pd.DataFrame, cutoff: float = 1.0, order=1) -> pd.DataFrame:
    """Lowpass filter and calculate velocities and accelerations with numeric differentiation

    Parameters
    ----------
    df : pd.DataFrame
        [description]
    cutoff : float
        Cut off frequency of the lowpass filter [Hz]
    order : int, optional
        order of the filter, by default 1

    Returns
    -------
    pd.DataFrame
        lowpassfiltered positions, velocities and accelerations
    """

    df_lowpass = df.copy()
    t = df_lowpass.index
    ts = np.mean(np.diff(t))
    fs = 1 / ts

    position_keys = ["x0", "y0", "psi"]
    for key in position_keys:
        df_lowpass[key] = lowpass_filter(
            data=df_lowpass[key], fs=fs, cutoff=cutoff, order=order
        )

    df_lowpass["x01d_gradient"] = x1d_ = np.gradient(df_lowpass["x0"], t)
    df_lowpass["y01d_gradient"] = y1d_ = np.gradient(df_lowpass["y0"], t)
    df_lowpass["r"] = r_ = np.gradient(df_lowpass["psi"], t)

    psi_ = df_lowpass["psi"]

    df_lowpass["u"] = x1d_ * cos(psi_) + y1d_ * sin(psi_)
    df_lowpass["v"] = -x1d_ * sin(psi_) + y1d_ * cos(psi_)

    velocity_keys = ["u", "v", "r"]
    for key in velocity_keys:
        df_lowpass[key] = lowpass_filter(
            data=df_lowpass[key], fs=fs, cutoff=cutoff, order=order
        )

    return df_lowpass


def assemble_data(df_lowpass: pd.DataFrame, raw_data: pd.DataFrame) -> pd.DataFrame:

    data = df_lowpass.copy()

    # This is giving numpy.linalg.LinAlgError: SVD did not converge in the EK
    for key in ["x0", "y0", "psi"]:
        data[key] = raw_data[key].values  # Initial position measurements are preserved

    # data = data.iloc[200:-100].copy()
    # data.index -= data.index[0]

    # data.dropna(subset=["x0", "y0", "psi", "u", "v", "r"], inplace=True)

    return data
