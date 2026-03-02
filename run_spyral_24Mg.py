import dotenv
dotenv.load_dotenv()

from spyral import (
    Pipeline,
    start_pipeline,
    PointcloudPhase,
    ClusterPhase,
    OverlapJoinParameters,
    EstimationPhase,
    InterpSolverPhase,
)

from spyral.core.config import TripclustParameters, HdbscanParameters, ContinuityJoinParameters

from spyral import (
    PadParameters,
    GetParameters,
    FribParameters,
    DetectorParameters,
    ClusterParameters,
    SolverParameters,
    EstimateParameters,
    DEFAULT_MAP,
)

from pathlib import Path
import multiprocessing

workspace_path = Path("/Volumes/researchEXT/24Mg/mg24_spyral/")
trace_path = Path("/Volumes/researchEXT/24Mg/run_24Mg/")

run_min = 84
run_max = 84
n_processes = 1

pad_params = PadParameters(
    pad_geometry_path= DEFAULT_MAP, #Path("/Users/pranjalsingh/Desktop/research_space_spyral/Spyral_1.0/Mg24_rcnp_map.csv")
    pad_time_path=DEFAULT_MAP,
    pad_scale_path=DEFAULT_MAP,
)

# AT-TPC GET trace analysis
get_params = GetParameters(
    baseline_window_scale=20.0,
    peak_separation=30.0, #was 50
    peak_prominence=30.0,
    peak_max_width=120.0,
    peak_threshold=50.0,
)

frib_params = FribParameters(
    baseline_window_scale=100.0,
    peak_separation=50.0,
    peak_prominence=20.0,
    peak_max_width=500.0,
    peak_threshold=100.0,
    ic_delay_time_bucket=150, #was 1100
    ic_multiplicity=1,
)

det_params = DetectorParameters(
    magnetic_field=0,
    electric_field=9690,
    detector_length=1000.0,
    beam_region_radius=25.0,
    micromegas_time_bucket=10.0,
    window_time_bucket=500.0,
    get_frequency=3.125,
    garfield_file_path=Path("/path/to/some/garfield.txt"),
    do_garfield_correction=False,
)

cluster_params = ClusterParameters(
    min_cloud_size=50,
    hdbscan_parameters= HdbscanParameters(
    min_points=3,min_size_scale_factor=0.05,
    min_size_lower_cutoff=10, 
    cluster_selection_epsilon=10.0,
    ),
    # hdbscan_parameters= None,
    tripclust_parameters=None,
    # tripclust_parameters=TripclustParameters(
    #     r=6,
    #     rdnn=True,
    #     k=12,
    #     n=3,
    #     a=0.03,
    #     s=0.3,
    #     sdnn=True,
    #     t=0.0,
    #     tauto=True,
    #     dmax=0.0,
    #     dmax_dnn=False,
    #     ordered=True,
    #     link=0,
    #     m=50,
    #     postprocess=False,
    #     min_depth=25,
    # ),
    overlap_join=OverlapJoinParameters(
        min_cluster_size_join=15,
        circle_overlap_ratio=0.25,
    ),
    # overlap_join=None,
    continuity_join = ContinuityJoinParameters(
    join_radius_fraction=0.4,
    join_z_fraction=0.4),
    direction_threshold= 0.5,
    outlier_scale_factor=0.1,
    
)

estimate_params = EstimateParameters(
    min_total_trajectory_points=20, smoothing_factor=100.0
)

solver_params = SolverParameters(
    gas_data_path=Path("/Users/pranjalsingh/Desktop/research_space_spyral/e20020_analysis/solver_gas_16O.json"),
    particle_id_filename=Path("/Users/pranjalsingh/Desktop/research_space_spyral/Spyral_1.0/particle_test.json"),
    ic_min_val=-10,
    ic_max_val=850.0,
    n_time_steps=1300,
    interp_ke_min=0.01,
    interp_ke_max=40.0,
    interp_ke_bins=100,
    interp_polar_min=0.1,
    interp_polar_max=179.9,
    interp_polar_bins=500,
    fit_vertex_rho=True,
    fit_vertex_phi=True,
    fit_azimuthal=True,
    fit_method="lbfgsb",
)

pipe = Pipeline(
    [
        PointcloudPhase(
            get_params,
            frib_params,
            det_params,
            pad_params,
        ),
        ClusterPhase(cluster_params, det_params),
        EstimationPhase(estimate_params, det_params),
        InterpSolverPhase(solver_params, det_params),
    ],
    [True, False, False, False],
    workspace_path,
    trace_path,
)


def main():
    start_pipeline(pipe, run_min, run_max, n_processes)


if __name__ == "__main__":
    multiprocessing.set_start_method("spawn")
    main()