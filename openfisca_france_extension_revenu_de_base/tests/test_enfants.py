# -*- coding: utf-8 -*-

from datetime import date

from openfisca_france.tests.base import tax_benefit_system
from openfisca_core.tools import assert_near

from openfisca_france_extension_revenu_de_base.enfants import build_reform


def test():
    # simulation = tax_benefit_system.new_scenario().init_single_entity(
    #     period = 2014,
    #     parent1 = dict(
    #         birth = date(1980, 1, 1),
    #         salaire_imposable = 12000,
    #         statmarit = u'Marié',
    #         ),
    #     parent2 = dict(
    #         birth = date(1980, 1, 1),
    #         salaire_imposable = 46000,
    #         statmarit = u'Marié',
    #         ),
    #     enfants = [
    #         dict(
    #             birth = date(2010, 1, 1),
    #             ),
    #         dict(
    #             birth = date(2005, 1, 1),
    #             ),
    #         dict(
    #             birth = date(1999, 1, 1),
    #             ),
    #         ],
    #     ).new_simulation(debug = True)

    reform = build_reform(tax_benefit_system)
    reform_simulation = reform.new_scenario().init_single_entity(
        period = 2014,
        parent1 = dict(
            birth = date(1980, 1, 1),
            salaire_imposable = 12000,
            statmarit = u'Marié',
            ),
        parent2 = dict(
            birth = date(1980, 1, 1),
            salaire_imposable = 46000,
            statmarit = u'Marié',
            ),
        enfants = [
            dict(
                birth = date(2010, 1, 1),
                ),
            dict(
                birth = date(2005, 1, 1),
                ),
            dict(
                birth = date(1999, 1, 1),
                ),
            ],
        ).new_simulation(debug = True)

    reform_simulation_pauvre = reform.new_scenario().init_single_entity(
        period = 2014,
        parent1 = dict(
            birth = date(1980, 1, 1),
            salaire_imposable = 12000,
            statmarit = u'Marié',
            ),
        parent2 = dict(
            birth = date(1980, 1, 1),
            salaire_imposable = 6000,
            statmarit = u'Marié',
            ),
        enfants = [
            dict(
                birth = date(2010, 1, 1),
                ),
            dict(
                birth = date(2005, 1, 1),
                ),
            dict(
                birth = date(1999, 1, 1),
                ),
            ],
        ).new_simulation(debug = True)

    absolute_error_margin = 0.01

    assert_near(
        reform_simulation.calculate('nbptr'),
        [2],
        absolute_error_margin = absolute_error_margin,
        )
    assert_near(
        reform_simulation.calculate('af', "2015-01"),
        [0],
        absolute_error_margin = absolute_error_margin,
        )
    assert_near(
        reform_simulation.calculate('cf', "2015-01"),
        [0],
        absolute_error_margin = absolute_error_margin,
        )
    assert_near(
        reform_simulation.calculate('ars', "2015-01"),
        [0],
        absolute_error_margin = absolute_error_margin,
        )
    assert_near(
        reform_simulation.calculate('rsa', "2015-01"),
        [334.37060547],
        absolute_error_margin = absolute_error_margin,
        )
    assert_near(
        reform_simulation.calculate('rmi_nbp'),
        [24],
        absolute_error_margin = absolute_error_margin,
        )
    assert_near(
        reform_simulation.calculate('famille'),
        [0., 0., 0., 0., 0],
        absolute_error_margin = absolute_error_margin,
        )
    assert_near(
        reform_simulation.calculate('rdb_enfant_famille'),
        [6765.49121094],
        absolute_error_margin = absolute_error_margin,
        )
    assert_near(
        reform_simulation.calculate('rdb_enf'),
        [0., 0., 1995.57678223, 1995.57678223, 2774.33837891],
        absolute_error_margin = absolute_error_margin,
        )
    assert_near(
        reform_simulation.calculate('csgenf'),
        [-299.99996948, -1188.52087402, -0., -0., -0.],
        absolute_error_margin = absolute_error_margin,
        )
    assert_near(
        reform_simulation.calculate('csg'),
        [-1392.48596191, -5347.15185547, 0., 0., 0],
        absolute_error_margin = absolute_error_margin,
        )
    assert_near(
        reform_simulation.calculate('revdisp'),
        [62391.12890625],
        absolute_error_margin = absolute_error_margin,
        )
    assert_near(
        reform_simulation_pauvre.calculate('revdisp'),
        [25799.73828125],
        absolute_error_margin = absolute_error_margin,
        )
    assert_near(
        reform_simulation.calculate('salaire_imposable'),
        [12000, 46000, 0, 0, 0],
        absolute_error_margin = absolute_error_margin,
        )
    assert_near(
        reform_simulation.calculate('salsuperbrut'),
        [16272.94433594, 77621.3125, 0., 0., 0.],
        absolute_error_margin = absolute_error_margin,
        )
    assert_near(
        reform_simulation.calculate('salaire_net'),
        [11577.5703125, 45932.82421875, 0., 0., 0.],
        absolute_error_margin = absolute_error_margin,
        )
    assert_near(
        reform_simulation.calculate('pfam'),
        [0],
        absolute_error_margin = absolute_error_margin,
        )
    assert_near(
        reform_simulation_pauvre.calculate('pfam'),
        [0],
        absolute_error_margin = absolute_error_margin,
        )
    assert_near(
        reform_simulation.calculate('irpp'),
        [-4798.390625],
        absolute_error_margin = absolute_error_margin,
        )
