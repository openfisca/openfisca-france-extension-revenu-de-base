# -*- coding: utf-8 -*-

from __future__ import division

from openfisca_core import reforms
from openfisca_france.model.base import FloatCol, Individus, SimpleFormulaColumn


# Build function

def build_reform(tax_benefit_system):
    Reform = reforms.make_reform(
        key = 'revenu_de_base_cotisations',
        name = u"Réforme des cotisations pour un Revenu de base",
        reference = tax_benefit_system,
        )

    @Reform.formula
    class cotisations_contributives(SimpleFormulaColumn):
        column = FloatCol
        entity_class = Individus
        label = u"Nouvelles cotisations contributives"

        def function(self, simulation, period):
            ags = simulation.calculate('ags', period)
            agff_tranche_a_employeur = simulation.calculate('agff_tranche_a_employeur', period)
            apec_employeur = simulation.calculate('apec_employeur', period)
            arrco_tranche_a_employeur = simulation.calculate('arrco_tranche_a_employeur', period)
            assedic_employeur = simulation.calculate('assedic_employeur', period)
            cotisation_exceptionnelle_temporaire_employeur = simulation.calculate(
                'cotisation_exceptionnelle_temporaire_employeur', period)
            fonds_emploi_hospitalier = simulation.calculate('fonds_emploi_hospitalier', period)
            ircantec_employeur = simulation.calculate('ircantec_employeur', period)
            pension_civile_employeur = simulation.calculate('pension_civile_employeur', period)
            prevoyance_obligatoire_cadre = simulation.calculate('prevoyance_obligatoire_cadre', period)
            rafp_employeur = simulation.calculate('rafp_employeur', period)
            vieillesse_deplafonnee_employeur = simulation.calculate('vieillesse_deplafonnee_employeur', period)
            vieillesse_plafonnee_employeur = simulation.calculate('vieillesse_plafonnee_employeur', period)
            allocations_temporaires_invalidite = simulation.calculate('allocations_temporaires_invalidite', period)
            accident_du_travail = simulation.calculate('accident_du_travail', period)
            agff_tranche_a_employe = simulation.calculate('agff_tranche_a_employe', period)
            agirc_tranche_b_employe = simulation.calculate('agirc_tranche_b_employe', period)
            apec_employe = simulation.calculate('apec_employe', period)
            arrco_tranche_a_employe = simulation.calculate('arrco_tranche_a_employe', period)
            assedic_employe = simulation.calculate('assedic_employe', period)
            cotisation_exceptionnelle_temporaire_employe = simulation.calculate(
                'cotisation_exceptionnelle_temporaire_employe', period)
            ircantec_employe = simulation.calculate('ircantec_employe', period)
            pension_civile_employe = simulation.calculate('pension_civile_employe', period)
            rafp_employe = simulation.calculate('rafp_employe', period)
            vieillesse_deplafonnee_employe = simulation.calculate('vieillesse_deplafonnee_employe', period)
            vieillesse_plafonnee_employe = simulation.calculate('vieillesse_plafonnee_employe', period)

            cotisations_contributives = (
                # cotisations patronales contributives dans le prive
                ags +
                agff_tranche_a_employeur +
                apec_employeur +
                arrco_tranche_a_employeur +
                assedic_employeur +
                cotisation_exceptionnelle_temporaire_employeur +
                prevoyance_obligatoire_cadre +  # TODO contributive ou pas
                vieillesse_deplafonnee_employeur +
                vieillesse_plafonnee_employeur +
                # cotisations patronales contributives dans le public
                fonds_emploi_hospitalier +
                ircantec_employeur +
                pension_civile_employeur +
                rafp_employeur +
                # anciennes cot patronales non-contributives classées ici comme contributives
                allocations_temporaires_invalidite +
                accident_du_travail +
                # anciennes cotisations salariales contributives dans le prive
                agff_tranche_a_employe +
                agirc_tranche_b_employe +
                apec_employe +
                arrco_tranche_a_employe +
                assedic_employe +
                cotisation_exceptionnelle_temporaire_employe +
                vieillesse_deplafonnee_employe +
                vieillesse_plafonnee_employe +
                # anciennes cotisations salariales contributives dans le public
                ircantec_employe +
                pension_civile_employe +
                rafp_employe
                )
            return period, cotisations_contributives

    @Reform.formula
    class nouv_salaire_de_base(SimpleFormulaColumn):
        reference = tax_benefit_system.column_by_name['salaire_de_base']

        # Le salaire brut se définit dans la réforme comme le salaire super-brut auquel
        # on retranche les cotisations contributives

        def function(self, simulation, period):
            period = period.start.period('month').offset('first-of')
            salsuperbrut = simulation.calculate('salsuperbrut', period)
            cotisations_contributives = simulation.calculate('cotisations_contributives', period)

            nouv_salaire_de_base = (
                salsuperbrut -
                cotisations_contributives
                )
            return period, nouv_salaire_de_base

    @Reform.formula
    class nouv_csg(SimpleFormulaColumn):
        reference = tax_benefit_system.column_by_name['csg_imposable_salaire']

        # On applique une CSG unique à 22,5% qui finance toutes les prestations non-contributives

        def function(self, simulation, period):
            period = period.start.period('month').offset('first-of')
            nouv_salaire_de_base = simulation.calculate('nouv_salaire_de_base', period)

            nouv_csg = (
                -0.225 * nouv_salaire_de_base
                )
            return period, nouv_csg

    @Reform.formula
    class salaire_net(SimpleFormulaColumn):
        reference = tax_benefit_system.column_by_name['salaire_net']

        # On retire la nouvelle CSG (pas celle qui finance le RDB) pour trouver le nouveau salaire net

        def function(self, simulation, period):
            period = period.start.period('month').offset('first-of')
            nouv_salaire_de_base = simulation.calculate('nouv_salaire_de_base', period)
            nouv_csg = simulation.calculate('nouv_csg', period)

            salaire_net = (
                nouv_salaire_de_base +
                nouv_csg
                )
            return period, salaire_net

    @Reform.formula
    class salaire_imposable(SimpleFormulaColumn):
        reference = tax_benefit_system.column_by_name['salaire_imposable']

        # Nous sommes partis du nouveau salaire net et par rapport au salaire imposable actuel,
        # nous avons supprimé : les heures sup, la déductibilité de CSG

        def function(self, simulation, period):
            period = period
            hsup = simulation.calculate('hsup', period)
            salaire_net = simulation.calculate('salaire_net', period)
            primes_fonction_publique = simulation.calculate('primes_fonction_publique', period)
            indemnite_residence = simulation.calculate('indemnite_residence', period)
            supp_familial_traitement = simulation.calculate('supp_familial_traitement', period)
            rev_microsocial_declarant1 = simulation.calculate('rev_microsocial_declarant1', period)

            return period, (
                salaire_net +
                primes_fonction_publique +
                indemnite_residence +
                supp_familial_traitement +
                hsup +
                rev_microsocial_declarant1
                )

    return Reform()
