"""Project pipelines."""
from typing import Dict
from functools import reduce
from operator import add

from kedro.pipeline import Pipeline
from kedro.pipeline.modular_pipeline import pipeline
import anyconfig
import os.path

from pytest import param

from . import pipeline_ship
from .pipelines import kvlcc2
from .pipelines import vessel_manoeuvring_models
from .pipelines import system_matrixes
from . import pipeline_plot
from .pipelines import captive
from .pipelines import generic_data, generic_data2
from .pipelines import plot_filters
from .pipelines import load_db
from .pipelines import load_cto
from .pipelines import load_hsva
from .pipelines import lowpass_filter_variation

# Full (slow)
# def register_pipelines() -> Dict[str, Pipeline]:
#    """Register the project's pipelines.
#
#    Returns:
#        A mapping from a pipeline name to a ``Pipeline`` object.
#    """
#
#    # Read configs:
#    conf_path = os.path.join(
#        os.path.split(os.path.split(os.path.dirname(__file__))[0])[0],
#        "conf",
#        "base",
#    )
#
#    runs_globals_path = os.path.join(
#        conf_path,
#        "runs_globals.yml",
#    )
#    runs_globals = anyconfig.load(runs_globals_path)
#    model_test_ids = runs_globals["model_test_ids"]
#
#    globals_path = os.path.join(
#        conf_path,
#        "globals.yml",
#    )
#    global_variables = anyconfig.load(globals_path)
#    vmms = global_variables["vmms"]
#
#    update_vmms = global_variables[
#        "update_vmms"
#    ]  # Disable update of vmm and system matrixes in globals.yml.
#    ek_pipelines = {}
#    if update_vmms:
#        ## Vessel Manoeuvring Models (VMMs)
#        vessel_manoeuvring_models_pipeline = vessel_manoeuvring_models.create_pipeline()
#
#        ## Extended Kalman Filters
#        for vmm in vmms:
#            key = f"ek.{vmm}"
#            ek_pipelines[key] = pipeline(
#                system_matrixes.create_pipeline(),
#                namespace=f"{vmm}",
#                inputs={
#                    "vmm": vmm,
#                },
#            )
#    else:
#        vessel_manoeuvring_models_pipeline = Pipeline([])  # Dummy pipiline
#        ek_pipelines = {"dummy": Pipeline([])}
#
#    ## Ships:
#    inputs = {vmm: vmm for vmm in vmms}
#    inputs.update({f"{vmm}.system_matrixes": f"{vmm}.system_matrixes" for vmm in vmms})
#
#    ship_names = [
#        "wpcc",
#        "tanker",
#        "generic_kvlcc2",
#        "LNG",
#        "tanker2",
#        "ropax",
#        "LNG_tanker",
#        "kvlcc2_cto",
#        "kvlcc2_hsva",
#    ]
#
#    ship_names = list(set(ship_names) & set(model_test_ids.keys()))
#
#    ship_pipelines = {}
#    for ship_name in ship_names:
#        ship_pipelines[ship_name] = pipeline(
#            pipeline_ship.create_pipeline(
#                model_test_ids=model_test_ids[ship_name], vmms=vmms
#            ),
#            namespace=ship_name,
#            inputs=inputs,
#            parameters={
#                "params:thrust_channels": f"params:{ship_name}.thrust_channels",
#                "params:initial.ek_covariance_input": f"params:{ship_name}.updated.initial.ek_covariance_input",
#                "params:initial.ek_covariance_input": f"params:{ship_name}.initial.ek_covariance_input",
#                "params:updated.ek_covariance_input": f"params:{ship_name}.updated.ek_covariance_input",
#                "params:motion_regression.exclude_parameters": f"params:{ship_name}.motion_regression.exclude_parameters",
#                "params:lowpass.cutoff": f"params:{ship_name}.lowpass.cutoff",
#                "params:lowpass.order": f"params:{ship_name}.lowpass.order",
#            },
#        )
#
#    ship_pipelines["kvlcc2"] = pipeline(
#        kvlcc2.create_pipeline(model_test_ids=model_test_ids["kvlcc2"], vmms=vmms),
#        namespace="kvlcc2",
#        inputs=inputs,
#        parameters={
#            "params:thrust_channels": "params:kvlcc2.thrust_channels",
#            "params:initial.ek_covariance_input": f"params:kvlcc2.initial.ek_covariance_input",
#            "params:updated.ek_covariance_input": f"params:kvlcc2.updated.ek_covariance_input",
#            "params:motion_regression.exclude_parameters": "params:kvlcc2.motion_regression.exclude_parameters",
#            "params:lowpass.cutoff": "params:kvlcc2.lowpass.cutoff",
#            "params:lowpass.order": "params:kvlcc2.lowpass.order",
#        },
#    )
#
#    pipeline_kvlcc2_captive = pipeline(captive.create_pipeline(), namespace="kvlcc2")
#
#    return_dict = {}
#    return_dict["__default__"] = (
#        vessel_manoeuvring_models_pipeline
#        + reduce(add, ek_pipelines.values())
#        + ship_pipelines["wpcc"]
#        + ship_pipelines["kvlcc2"]
#    )
#
#    for ship in ship_pipelines.keys():
#        return_dict[ship] = (
#            vessel_manoeuvring_models_pipeline
#            + reduce(add, ek_pipelines.values())
#            + ship_pipelines[ship]
#        )
#
#    for ship_name, model_test_ids_ in model_test_ids.items():
#        return_dict[f"plot_{ship_name}"] = pipeline(
#            pipeline_plot.create_pipeline(
#                model_test_ids=model_test_ids_,
#                vmms=vmms,
#            ),
#            namespace=ship_name,
#        )
#
#    for ship_name, model_test_ids_ in model_test_ids.items():
#        return_dict[f"plot_filters_{ship_name}"] = pipeline(
#            plot_filters.create_pipeline(
#                model_test_ids=model_test_ids_,
#                vmms=vmms,
#            ),
#            namespace=ship_name,
#        )
#
#    return_dict["kvlcc2_captive"] = pipeline_kvlcc2_captive
#
#    return_dict["generic_data"] = generic_data.create_pipeline()
#    return_dict["generic_data2"] = generic_data2.create_pipeline(
#        model_test_ids=model_test_ids
#    )
#
#    create_ships = ["LNG", "tanker2", "ropax", "LNG_tanker"]
#    for ship in create_ships:
#        return_dict[f"{ship}_create"] = pipeline(
#            load_db.create_pipeline(),
#            namespace=ship,
#            parameters={
#                "params:ship": f"params:{ship}",
#            },
#        )
#    return_dict["kvlcc2_cto_create"] = pipeline(
#        load_cto.create_pipeline(), namespace="kvlcc2_cto"
#    )
#
#    return_dict["kvlcc2_hsva_create"] = pipeline(
#        load_hsva.create_pipeline(), namespace="kvlcc2_hsva"
#    )
#
#    # work_ships = ["wpcc", "LNG", "tanker2", "ropax", "LNG_tanker"]
#    work_ships = [
#        "wpcc",
#        "LNG",
#        "tanker2",
#        "ropax",
#        "LNG_tanker",
#        "kvlcc2_hsva",
#        "kvlcc2",
#    ]
#    work_ships = list(set(work_ships) & set(model_test_ids.keys()))
#    work = [return_dict[ship] for ship in work_ships]
#    return_dict["work"] = reduce(add, work)
#
#    plot = [return_dict[f"plot_{ship}"] for ship in work_ships]
#    plot += [return_dict[f"plot_filters_{ship}"] for ship in work_ships]
#    return_dict["plot"] = reduce(add, plot)
#
#    lowpass_filter_variation_pipeline = pipeline(
#        lowpass_filter_variation.create_pipeline(model_test_ids=model_test_ids["wpcc"]),
#        namespace="wpcc",
#        inputs={
#            "vmm_martins_simple": "vmm_martins_simple",
#            "ek": f"wpcc.vmm_martins_simple.ek",
#        },
#        parameters={
#            "params:motion_regression.exclude_parameters": "params:wpcc.motion_regression.exclude_parameters"
#        },
#    )
#
#    return_dict["lowpass_study"] = lowpass_filter_variation_pipeline
#
#    return return_dict


# Faster...
def register_pipelines() -> Dict[str, Pipeline]:
    """Register the project's pipelines.

    Returns:
        A mapping from a pipeline name to a ``Pipeline`` object.
    """

    # Read configs:
    conf_path = os.path.join(
        os.path.split(os.path.split(os.path.dirname(__file__))[0])[0],
        "conf",
        "base",
    )

    runs_globals_path = os.path.join(
        conf_path,
        "runs_globals.yml",
    )
    runs_globals = anyconfig.load(runs_globals_path)
    model_test_ids = runs_globals["model_test_ids"]

    globals_path = os.path.join(
        conf_path,
        "globals.yml",
    )
    global_variables = anyconfig.load(globals_path)
    vmms = global_variables["vmms"]

    update_vmms = global_variables[
        "update_vmms"
    ]  # Disable update of vmm and system matrixes in globals.yml.

    lowpass_filter_variation_pipeline = pipeline(
        lowpass_filter_variation.create_pipeline(model_test_ids=model_test_ids["wpcc"]),
        namespace="wpcc",
        inputs={
            "vmm_martins_simple": "vmm_martins_simple",
            "ek": f"wpcc.vmm_martins_simple.ek",
        },
        parameters={
            "params:motion_regression.exclude_parameters": "params:wpcc.motion_regression.exclude_parameters"
        },
    )

    return_dict = {}
    return_dict["lowpass_study"] = lowpass_filter_variation_pipeline

    return return_dict
