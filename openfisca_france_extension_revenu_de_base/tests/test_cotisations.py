# -*- coding: utf-8 -*-

from datetime import date

from openfisca_france.tests.base import tax_benefit_system
from openfisca_core.tools import assert_near

from openfisca_france_extension_revenu_de_base.cotisations import build_reform


def test():
    reform = build_reform(tax_benefit_system)
    reform_simulation = reform.new_scenario().init_single_entity(
        period = 2014,
        parent1 = dict(
            birth = date(1980, 1, 1),
            salaire_imposable = 12000,
            ),
        parent2 = dict(
            birth = date(1980, 1, 1),
            salaire_imposable = 6000,
            ),
        enfants = [
            dict(
                birth = date(2014, 1, 1),
                ),
            ],
        ).new_simulation(debug = True)

    absolute_error_margin = 0.01

    assert_near(
        reform_simulation.calculate('salsuperbrut'),
        [17051.3046875, 8525.65234375, 0],
        absolute_error_margin = absolute_error_margin,
        )
    assert_near(
        reform_simulation.calculate('cotisations_contributives'),
        [-5141.63378906, -2570.81689453, 0],
        absolute_error_margin = absolute_error_margin,
        )
    assert_near(
        reform_simulation.calculate('nouv_salaire_de_base'),
        [22192.93945312, 11096.46972656, 0],
        absolute_error_margin = absolute_error_margin,
        )
    assert_near(
        reform_simulation.calculate('salaire_de_base'),
        [14825.93261719, 7412.96630859, 0],
        absolute_error_margin = absolute_error_margin,
        )
    assert_near(
        reform_simulation.calculate('salaire_net'),
        [17199.52734375, 8599.76367188, 0],
        absolute_error_margin = absolute_error_margin,
        )
