# -*- coding: utf-8 -*-
"""Classes for gp_next_points_constant_liar endpoints.

Includes:
    1. pretty and backend views
"""
import colander
from pyramid.view import view_config

from moe.views.gp_next_points_pretty_view import GpNextPointsPrettyView, GpNextPointsRequest


class GpNextPointsConstantLiarRequest(GpNextPointsRequest):

    """Extends the standard request moe.views.gp_next_points_pretty_view.GpNextPointsRequest() with a lie value.

    **Required fields**

        :gp_info: a GpInfo object of historical data
        :lie_value: a float representing the 'lie' the Constant Liar heuristic will use

    **Optional fields**

        :num_samples_to_generate: number of next points to generate (default: 1)
        :ei_optimization_parameters: moe.views.schemas.EiOptimizationParameters() object containing optimization parameters (default: moe.optimal_learning.EPI.src.python.constant.default_ei_optimization_parameters)
        :lie_noise_variance: a positive (>= 0) float representing the noise variance of the 'lie' value (default: 0.0)

    **Example Request**

    .. sourcecode:: http

        Content-Type: text/javascrip

        {
            'num_samples_to_generate': 1,
            'lie_value': 0.0,
            'lie_noise_variance': 0.0,
            'gp_info': {
                'points_sampled': [
                        {'value_var': 0.01, 'value': 0.1, 'point': [0.0]},
                        {'value_var': 0.01, 'value': 0.2, 'point': [1.0]}
                    ],
                'domain': [
                    [0, 1],
                    ]
                },
            },
        }

    """

    lie_value = colander.SchemaNode(
            colander.Float(),
            )
    lie_noise_variance = colander.SchemaNode(
            colander.Float(),
            missing=0.0,
            validator=colander.Range(min=0.0),
            )


class GpNextPointsconstant_liar(GpNextPointsPrettyView):

    """Views for gp_next_points_constant_liar endpoints."""

    route_name = 'gp_next_points_constant_liar'
    pretty_route_name = 'gp_next_points_constant_liar_pretty'

    request_schema = GpNextPointsConstantLiarRequest()

    pretty_default_request = GpNextPointsPrettyView.pretty_default_request.copy()
    pretty_default_request['lie_value'] = 0.0
    pretty_default_request['lie_noise_variance'] = 0.0

    @view_config(route_name=pretty_route_name, renderer=GpNextPointsPrettyView.pretty_renderer)
    def pretty_view(self):
        """A pretty, browser interactive view for the interface. Includes form request and response.

        .. http:get:: /gp/next_points/constant_liar/pretty

        """
        return self.pretty_response()

    @view_config(route_name=route_name, renderer='json', request_method='POST')
    def gp_next_points_constant_liar_view(self):
        """Endpoint for gp_next_points_constant_liar POST requests.

        .. http:post:: /gp/next_points/constant_liar

           Calculates the next best points to sample, given historical data, using Constant Liar (CL).

           :input: moe.views.gp_next_points_constant_liar.GpNextPointsConstantLiarRequest()
           :output: moe.views.gp_next_points_pretty_view.GpNextPointsResponse()

           :status 200: returns a response
           :status 500: server error

        """
        params = self.get_params_from_request()
        return self.compute_next_points_to_sample_response(
                params,
                'constant_liar_expected_improvement_optimization',
                self.route_name,
                params.get('lie_value'),
                )