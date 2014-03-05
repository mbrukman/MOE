from pyramid.response import Response
from pyramid.view import view_config

from optimal_learning.EPI.src.python.models.optimal_gaussian_process_linked_cpp import OptimalGaussianProcessLinkedCpp
from optimal_learning.EPI.src.python.models.covariance_of_process import CovarianceOfProcess
from optimal_learning.EPI.src.python.models.sample_point import SamplePoint

from moe.schemas import GpMeanVarRequest, GpEiRequest, GpEiResponse, GpMeanVarResponse

@view_config(route_name='home', renderer='moe:templates/index.mako')
def index_page(request):
    return {
            'nav_active': 'home',
            }

@view_config(route_name='about', renderer='moe:templates/about.mako')
def about_page(request):
    return {
            'nav_active': 'about',
            }

@view_config(route_name='docs', renderer='moe:templates/docs.mako')
def docs_page(request):
    return {
            'nav_active': 'docs',
            }

# GP routes

def _make_default_covariance_of_process(signal_variance=None, length=None):
    """Make a default covariance of process with optional parameters
    """
    hyperparameters = [signal_variance]
    hyperparameters.extend(length)

    return CovarianceOfProcess(hyperparameters=hyperparameters)

def _make_gp_from_gp_info(gp_info):
    """Create and return a C++ backed GP from a gp_info dict

    gp_info has the following form:
    gp_info = {
        ...
        }

    """
    # Load up the info
    points_sampled = gp_info['points_sampled']
    domain = gp_info['domain']
    signal_variance = gp_info.get('signal_variance', 1.0)
    length = gp_info.get('length_scale', [0.5])

    # Build the required objects
    covariance_of_process = _make_default_covariance_of_process(
            signal_variance=signal_variance,
            length=length,
            )
    GP = OptimalGaussianProcessLinkedCpp(
            domain=domain,
            covariance_of_process=covariance_of_process,
            )

    # Sample from the process
    for point in points_sampled:
        sample_point = SamplePoint(
                point['point'],
                point['value'],
                point['value_var'],
                )
        GP.add_sample_point(sample_point, point['value_var'])

    return GP

@view_config(route_name='gp_mean_var', renderer='json', request_method='POST')
def gp_mean_var_view(request):
    params_schema = GpMeanVarRequest()
    params = params_schema.deserialize(request.json_body)

    points_to_sample = params.get('points_to_sample')
    gp_info = params.get('gp_info')

    GP = _make_gp_from_gp_info(gp_info)

    mean, var = GP.get_mean_and_var_of_points(points_to_sample)

    json_var = list([list(row) for row in var])

    resp_schema = GpMeanVarResponse()
    resp = resp_schema.serialize({
            'endpoint': 'gp_mean_var',
            'mean': list(mean),
            'var': json_var,
            })

    return resp

@view_config(route_name='gp_ei', renderer='json', request_method='POST')
def gp_ei_view(request):
    params_schema = GpEiRequest()
    params = params_schema.deserialize(request.json_body)

    points_to_evaluate = params.get('points_to_evaluate')
    points_being_sampled = params.get('points_being_sampled')
    mc_iterations = params.get('mc_iterations')

    gp_info = request.json_body.get('gp_info')
    if not gp_info:
        raise(ValueError, "POST request to /gp/ei needs gp_info")

    GP = _make_gp_from_gp_info(gp_info)

    expected_improvement = GP.evaluate_expected_improvement_at_point_list(
            points_to_evaluate,
            points_being_sampled=points_being_sampled,
            )

    resp_schema = GpEiResponse()
    resp = resp_schema.serialize({
            'endpoint': 'gp_ei',
            'expected_improvement': expected_improvement,
            })

    return resp