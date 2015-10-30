# -*- coding: utf-8 -*-


# OpenFisca -- A versatile microsimulation software
# By: OpenFisca Team <contact@openfisca.fr>
#
# Copyright (C) 2011, 2012, 2013, 2014 OpenFisca Team
# https://github.com/openfisca
#
# This file is part of OpenFisca.
#
# OpenFisca is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# OpenFisca is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE,  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program,  If not, see <http://www.gnu.org/licenses/>.


from datetime import date

from openfisca_france.tests.base import tax_benefit_system
from openfisca_core.tools import assert_near

import openfisca_france_reform_revenu_de_base_enfants


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

    reform = openfisca_france_reform_revenu_de_base_enfants.build_reform(tax_benefit_system)
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

    error_margin = 0.01

    assert_near(
        reform_simulation.calculate('nbptr'),
        [2],
        error_margin = error_margin,
        )
    assert_near(
        reform_simulation.calculate('af'),
        [0],
        error_margin = error_margin,
        )
    assert_near(
        reform_simulation.calculate('cf'),
        [0],
        error_margin = error_margin,
        )
    assert_near(
        reform_simulation.calculate('ars'),
        [0],
        error_margin = error_margin,
        )
    assert_near(
        reform_simulation.calculate('rsa'),
        [334.37060547],
        error_margin = error_margin,
        )
    assert_near(
        reform_simulation.calculate('rmi_nbp'),
        [24],
        error_margin = error_margin,
        )
    assert_near(
        reform_simulation.calculate('famille'),
        [0., 0., 0., 0., 0],
        error_margin = error_margin,
        )
    assert_near(
        reform_simulation.calculate('rdb_enfant_famille'),
        [6765.49121094],
        error_margin = error_margin,
        )
    assert_near(
        reform_simulation.calculate('rdb_enf'),
        [0., 0., 1995.57678223, 1995.57678223, 2774.33837891],
        error_margin = error_margin,
        )
    assert_near(
        reform_simulation.calculate('csgenf'),
        [-299.99996948, -1188.52087402, -0., -0., -0.],
        error_margin = error_margin,
        )
    assert_near(
        reform_simulation.calculate('csg'),
        [-1392.48596191, -5347.15185547, 0., 0., 0],
        error_margin = error_margin,
        )
    assert_near(
        reform_simulation.calculate('revdisp'),
        [62391.12890625],
        error_margin = error_margin,
        )
    assert_near(
        reform_simulation_pauvre.calculate('revdisp'),
        [25799.73828125],
        error_margin = error_margin,
        )
    assert_near(
        reform_simulation.calculate('salaire_imposable'),
        [12000, 46000, 0, 0, 0],
        error_margin = error_margin,
        )
    assert_near(
        reform_simulation.calculate('salsuperbrut'),
        [16272.94433594, 77621.3125, 0., 0., 0.],
        error_margin = error_margin,
        )
    assert_near(
        reform_simulation.calculate('salaire_net'),
        [11577.5703125, 45932.82421875, 0., 0., 0.],
        error_margin = error_margin,
        )
    assert_near(
        reform_simulation.calculate('pfam'),
        [0],
        error_margin = error_margin,
        )
    assert_near(
        reform_simulation_pauvre.calculate('pfam'),
        [0],
        error_margin = error_margin,
        )
    assert_near(
        reform_simulation.calculate('irpp'),
        [-4798.390625],
        error_margin = error_margin,
        )
