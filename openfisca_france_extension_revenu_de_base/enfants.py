# -*- coding: utf-8 -*-

from __future__ import division

import os

from numpy import logical_not as not_, maximum as max_, round
from openfisca_core import reforms
from openfisca_france.model.base import (
    CHEF, ENFS, Familles, FloatCol, Individus, PART, Variable, VOUS,
    )
from openfisca_france.model.prestations.prestations_familiales.base_ressource import nb_enf

from . import decompositions


# Build function

def build_reform(tax_benefit_system):
    Reform = reforms.make_reform(
        decomposition_dir_name = os.path.dirname(os.path.abspath(decompositions.__file__)),
        decomposition_file_name = 'decomposition.xml',
        key = 'revenu_de_base_enfants',
        name = u"Revenu de base enfants",
        reference = tax_benefit_system,
        )

    class nbptr(Variable):
        reference = tax_benefit_system.column_by_name['nbptr']

        # On enlève les enfants du calcul du nbptr (quotient_familial.enf*)

        def function(self, simulation, period):
            '''
            Nombre de parts du foyer
            'foy'
            note 1 enfants et résidence alternée (formulaire 2041 GV page 10)

            quotient_familial.conj : nb part associées au conjoint d'un couple marié ou pacsé
            quotient_familial.enf1 : nb part 2 premiers enfants
            quotient_familial.enf2 : nb part enfants de rang 3 ou plus
            quotient_familial.inv1 : nb part supp enfants invalides (I, G)
            quotient_familial.inv2 : nb part supp adultes invalides (R)
            quotient_familial.not31 : nb part supp note 3 : cases W ou G pour veuf, celib ou div
            quotient_familial.not32 : nb part supp note 3 : personne seule ayant élevé des enfants
            quotient_familial.not41 : nb part supp adultes invalides (vous et/ou conjoint) note 4
            quotient_familial.not42 : nb part supp adultes anciens combattants (vous et/ou conjoint) note 4
            quotient_familial.not6 : nb part supp note 6
            quotient_familial.isol : demi-part parent isolé (T)
            quotient_familial.edcd : enfant issu du mariage avec conjoint décédé;
            '''
            period = period.start.offset('first-of', 'month').period('year')
            nb_pac = simulation.calculate('nb_pac', period)
            marpac = simulation.calculate('marpac', period)
            celdiv = simulation.calculate('celdiv', period)
            veuf = simulation.calculate('veuf', period)
            jveuf = simulation.calculate('jveuf', period)
            nbF = simulation.calculate('nbF', period)
            nbG = simulation.calculate('nbG', period)
            nbH = simulation.calculate('nbH', period)
            nbI = simulation.calculate('nbI', period)
            nbR = simulation.calculate('nbR', period)
            nbJ = simulation.calculate('nbJ', period)
            caseP = simulation.calculate('caseP', period)
            caseW = simulation.calculate('caseW', period)
            caseG = simulation.calculate('caseG', period)
            caseE = simulation.calculate('caseE', period)
            caseK = simulation.calculate('caseK', period)
            caseN = simulation.calculate('caseN', period)
            caseF = simulation.calculate('caseF', period)
            caseS = simulation.calculate('caseS', period)
            caseL = simulation.calculate('caseL', period)
            caseT = simulation.calculate('caseT', period)
            quotient_familial = simulation.legislation_at(period.start).ir.quotient_familial

            no_pac = nb_pac == 0  # Aucune personne à charge en garde exclusive
            has_pac = not_(no_pac)
            no_alt = nbH == 0  # Aucun enfant à charge en garde alternée
            has_alt = not_(no_alt)

            # # nombre de parts liées aux enfants à charge
            # que des enfants en résidence alternée
            # enf1 = (no_pac & has_alt) * (quotient_familial.enf1 * min_(nbH, 2) * 0.5
            #                              + quotient_familial.enf2 * max_(nbH - 2, 0) * 0.5)
            # # pas que des enfants en résidence alternée
            # enf2 = (has_pac & has_alt) * ((nb_pac == 1) * (quotient_familial.enf1 * min_(nbH, 1) * 0.5
            #     + quotient_familial.enf2 * max_(nbH - 1, 0) * 0.5) +
            #     (nb_pac > 1) * (quotient_familial.enf2 * nbH * 0.5))
            # # pas d'enfant en résidence alternée
            # enf3 = quotient_familial.enf1 * min_(nb_pac, 2) + quotient_familial.enf2 * max_((nb_pac - 2), 0)

            # enf = enf1 + enf2 + enf3
            # # note 2 : nombre de parts liées aux invalides (enfant + adulte)
            n2 = quotient_familial.inv1 * (nbG + nbI / 2) + quotient_familial.inv2 * nbR

            # # note 3 : Pas de personne à charge
            # - invalide

            n31a = quotient_familial.not31a * (no_pac & no_alt & caseP)
            # - ancien combatant
            n31b = quotient_familial.not31b * (no_pac & no_alt & (caseW | caseG))
            n31 = max_(n31a, n31b)
            # - personne seule ayant élevé des enfants
            n32 = quotient_familial.not32 * (no_pac & no_alt & ((caseE | caseK) & not_(caseN)))
            n3 = max_(n31, n32)
            # # note 4 Invalidité de la personne ou du conjoint pour les mariés ou
            # # jeunes veuf(ve)s
            n4 = max_(quotient_familial.not41 * (1 * caseP + 1 * caseF), quotient_familial.not42 * (caseW | caseS))

            # # note 5
            #  - enfant du conjoint décédé
            n51 = quotient_familial.cdcd * (caseL & ((nbF + nbJ) > 0))
            #  - enfant autre et parent isolé
            n52 = quotient_familial.isol * caseT * (
                ((no_pac & has_alt) * ((nbH == 1) * 0.5 + (nbH >= 2))) + 1 * has_pac)
            n5 = max_(n51, n52)

            # # note 6 invalide avec personne à charge
            n6 = quotient_familial.not6 * (caseP & (has_pac | has_alt))

            # # note 7 Parent isolé
            n7 = quotient_familial.isol * caseT * ((no_pac & has_alt) * ((nbH == 1) * 0.5 + (nbH >= 2)) + 1 * has_pac)

            # # Régime des mariés ou pacsés
            # m = 1 + quotient_familial.conj + enf + n2 + n4
            m = 1 + quotient_familial.conj + n2 + n4

            # # veufs  hors jveuf
            # v = 1 + enf + n2 + n3 + n5 + n6
            v = 1 + n2 + n3 + n5 + n6

            # # celib div
            # c = 1 + enf + n2 + n3 + n6 + n7
            c = 1 + n2 + n3 + n6 + n7

            return period, (marpac | jveuf) * m + (veuf & not_(jveuf)) * v + celdiv * c

    # Suppression des allocations familiales
    class af(Variable):
        reference = tax_benefit_system.column_by_name['af']

        def function(self, simulation, period):
            period = period.start.offset('first-of', 'month').period('month')
            af_base = simulation.calculate('af_base', period)
            # af_majo = simulation.calculate('af_majo', period)
            # af_forf = simulation.calculate('af_forf', period)

            # return period, af_base + af_majo + af_forf
            return period, af_base * 0

    # Suppression du complément familial
    class cf(Variable):
        reference = tax_benefit_system.column_by_name['cf']

        def function(self, simulation, period):
            '''
            L'allocation de base de la paje n'est pas cumulable avec le complément familial
            '''
            period = period.start.offset('first-of', 'month').period('month')
            paje_base_montant = simulation.calculate('paje_base_montant', period)
            apje_temp = simulation.calculate('apje_temp', period)
            ape_temp = simulation.calculate('ape_temp', period)
            cf_montant = simulation.calculate('cf_montant', period)
            residence_mayotte = simulation.calculate('residence_mayotte', period)

            cf_brut = (paje_base_montant < cf_montant) * (apje_temp <= cf_montant) * (ape_temp <= cf_montant) * cf_montant
            # return period, not_(residence_mayotte) * round(cf_brut, 2)
            return period, not_(residence_mayotte) * round(cf_brut, 2) * 0

    # Suppression de l'allocation de rentrée scolaire
    class ars(Variable):
        reference = tax_benefit_system.column_by_name['ars']

        def function(self, simulation, period):
            '''
            Allocation de rentrée scolaire brute de CRDS
            '''

            period = period.start.offset('first-of', 'month').period('month')
            # age_holder = simulation.compute('age', period)
            # af_nbenf = simulation.calculate('af_nbenf', period)
            # smic55_holder = simulation.compute('smic55', period)
            br_pf = simulation.calculate('br_pf', period)

            return period, br_pf * 0

    # Suppression du nombre d'enfants dans le calcul du RSA socle
    class rsa_socle(Variable):
        reference = tax_benefit_system.column_by_name['rsa_socle']

        def function(self, simulation, period):
            period = period.start.offset('first-of', 'month').period('month')
            age_holder = simulation.compute('age', period)
            # smic55_holder = simulation.compute('smic55', period)
            activite_holder = simulation.compute('activite', period)
            nb_par = simulation.calculate('nb_par', period)
            rmi = simulation.legislation_at(period.start).minim.rmi

            age_parents = self.split_by_roles(age_holder, roles = [CHEF, PART])
            activite_parents = self.split_by_roles(activite_holder, roles = [CHEF, PART])
            # age_enf = self.split_by_roles(age_holder, roles = ENFS)
            # smic55_enf = self.split_by_roles(smic55_holder, roles = ENFS)

            nbp = nb_par

            eligib = (
                (age_parents[CHEF] >= rmi.age_pac) *
                not_(activite_parents[CHEF] == 2)
                ) | (
                    (age_parents[PART] >= rmi.age_pac) * not_(activite_parents[PART] == 2)
                    )

            taux = (
                1 + (nbp >= 2) * rmi.txp2 +
                (nbp >= 3) * rmi.txp3 +
                (nbp >= 4) * ((nb_par == 1) * rmi.txps + (nb_par != 1) * rmi.txp3) +
                max_(nbp - 4, 0) * rmi.txps
                )
            return period, eligib * rmi.rmi * taux

    # Suppression du nombre d'enfants dans le calcul du RSA forfait logement
    class rmi_nbp(Variable):
        reference = tax_benefit_system.column_by_name['rmi_nbp']

        def function(self, simulation, period):
            # period = period.start.offset('first-of', 'month').period('month')
            # age_holder = simulation.compute('age', period)
            # smic55_holder = simulation.compute('smic55', period)
            nb_par = simulation.calculate('nb_par', period)
            # P = simulation.legislation_at(period.start).minim.rmi

            # age = self.split_by_roles(age_holder, roles = ENFS)
            # smic55 = self.split_by_roles(smic55_holder, roles = ENFS)

            return period, nb_par  # + nb_enf(age, smic55, 0, P.age_pac - 1)

    # Suppression de la cotisation patronale famille
    class famille(Variable):
        reference = tax_benefit_system.column_by_name['famille']

        def function(self, simulation, period):
            period = period.start.period(u'month').offset('first-of')
            salaire_de_base = simulation.calculate('salaire_de_base', period)

            return period, salaire_de_base * 0

    # Baisse de l'éxonération Fillon
    # TODO /!\ CHANGER LES PARAMÈTRES DE L'ÉXONÉRATION FILLON (-5,25%)
    # def taux_exo_fillon(ratio_smic_salaire, majoration, P):
    #    '''
    #    Exonération Fillon
    #    http://www.securite-sociale.fr/comprendre/dossiers/exocotisations/exoenvigueur/fillon.htm
    #    '''
    #    # La divison par zéro engendre un warning
    #    # Le montant maximum de l’allègement dépend de l’effectif de l’entreprise.
    #    # Le montant est calculé chaque année civile, pour chaque salarié ;
    #    # il est égal au produit de la totalité de la rémunération annuelle telle
    #    # que visée à l’article L. 242-1 du code de la Sécurité sociale par un
    #    # coefficient.
    #    # Ce montant est majoré de 10 % pour les entreprises de travail temporaire
    #    # au titre des salariés temporaires pour lesquels elle est tenue à
    #    # l’obligation d’indemnisation compensatrice de congés payés.
    #
    #    Pf = P.exo_bas_sal.fillon
    #    seuil = Pf.seuil
    #    tx_max = (Pf.tx_max * not_(majoration) + Pf.tx_max2 * majoration) - 0.0525
    #    if seuil <= 1:
    #        return 0
    #    # règle d'arrondi: 4 décimales au dix-millième le plus proche
    #    taux_fillon = round_(tx_max * min_(1, max_(seuil * ratio_smic_salaire - 1, 0) / (seuil - 1)), 4)
    #    return taux_fillon

    # Création d'un revenu de base enfant - Version famille
    class rdb_enfant_famille(Variable):
        column = FloatCol
        entity_class = Familles
        label = u"Revenu de base enfant"

        def function(self, simulation, period):
            period = period.start.offset('first-of', 'month').period('month')
            age_holder = simulation.compute('age', period)
            P = simulation.legislation_at(period.start).fam.af
            bmaf = P.bmaf

            smic55_holder = simulation.compute('smic55', period)
            smic55 = self.split_by_roles(smic55_holder, roles = ENFS)
            age = self.split_by_roles(age_holder, roles = ENFS)

            smic5 = {
                role: array * 0
                for role, array in smic55.iteritems()
                }
            nbenf_inf13 = nb_enf(age, smic5, 0, 13)
            nbenf_sup14 = nb_enf(age, smic5, 14, 18)

            return period, (nbenf_inf13 * 0.41 + nbenf_sup14 * 0.57) * bmaf

    # Les taux 0,41 et 0,16 (0,57-0,41) sont issus des allocations familiales

    # Création d'un revenu de base enfant - Version individus
    class rdb_enf(Variable):
        column = FloatCol
        entity_class = Individus
        label = u"Revenu de base enfant"

        def function(self, simulation, period):
            period = period.start.offset('first-of', 'month').period('month')
            age = simulation.calculate('age')
            P = simulation.legislation_at(period.start).fam.af
            bmaf = P.bmaf

            return period, ((age < 14) * 0.41 + not_(age < 14) * 0.57) * bmaf * (age <= 18)

    # Création d'une CSG enfant
    class csgenf(Variable):
        column = FloatCol
        entity_class = Individus
        label = u"CSG enfant"

        def function(self, simulation, period):
            period = period.start.offset('first-of', 'month').period('month')
            revnet = simulation.calculate('revenu_net_individu', period)

            montant_csg = revnet * 0.025
            return period, - montant_csg

    class csg(Variable):
        reference = tax_benefit_system.column_by_name['csg']

        def function(self, simulation, period):
            """Contribution sociale généralisée"""
            period = period.start.offset('first-of', 'month').period('year')
            csg_imposable_salaire = simulation.calculate('csg_imposable_salaire', period)
            csgsald = simulation.calculate('csgsald', period)
            csgchoi = simulation.calculate('csgchoi', period)
            csgchod = simulation.calculate('csgchod', period)
            csgrsti = simulation.calculate('csgrsti', period)
            csgrstd = simulation.calculate('csgrstd', period)
            csg_fon_holder = simulation.compute('csg_fon', period)
            csg_cap_lib_declarant1 = simulation.calculate('csg_cap_lib_declarant1', period)
            csg_cap_bar_declarant1 = simulation.calculate('csg_cap_bar_declarant1', period)
            csg_pv_mo_holder = simulation.compute('csg_pv_mo', period)
            csg_pv_immo_holder = simulation.compute('csg_pv_immo', period)

            csgenfant = simulation.calculate('csgenf', period)

            csg_fon = self.cast_from_entity_to_role(csg_fon_holder, role = VOUS)
            csg_pv_immo = self.cast_from_entity_to_role(csg_pv_immo_holder, role = VOUS)
            csg_pv_mo = self.cast_from_entity_to_role(csg_pv_mo_holder, role = VOUS)

            return period, (csg_imposable_salaire + csgsald + csgchoi + csgchod + csgrsti + csgrstd +
                    csg_fon + csg_cap_lib_declarant1 + csg_pv_mo + csg_pv_immo + csg_cap_bar_declarant1 + csgenfant)

    class revdisp(Variable):
        reference = tax_benefit_system.column_by_name['revdisp']

        def function(self, simulation, period):
            '''
            Revenu disponible - ménage
            'men'
            '''
            period = period.start.offset('first-of', 'month').period('year')
            rev_trav_holder = simulation.compute('rev_trav', period)
            pen_holder = simulation.compute('pen', period)
            rev_cap_holder = simulation.compute('rev_cap', period)
            psoc_holder = simulation.compute('psoc', period)
            ppe_holder = simulation.compute('ppe', period)
            impo = simulation.calculate('impo', period)
            rdb_enfant_holder = simulation.compute('rdb_enf', period)

            pen = self.sum_by_entity(pen_holder)
            ppe = self.cast_from_entity_to_role(ppe_holder, role = VOUS)
            ppe = self.sum_by_entity(ppe)
            psoc = self.cast_from_entity_to_role(psoc_holder, role = CHEF)
            psoc = self.sum_by_entity(psoc)
            rev_cap = self.sum_by_entity(rev_cap_holder)
            rev_trav = self.sum_by_entity(rev_trav_holder)
            rdb_enfant = self.sum_by_entity(rdb_enfant_holder)

            return period, rev_trav + pen + rev_cap + psoc + ppe + impo + rdb_enfant

    reform = Reform()
    reform.modify_legislation_json(modifier_function = modify_legislation_json)
    return reform


def modify_legislation_json(reference_legislation_json_copy):
    reference_legislation_json_copy['children']['cotsoc']['children']['exo_bas_sal']['children']['fillon']['children']['tx_max']['values'][0]['value'] = 0.2075  # noqa
    reference_legislation_json_copy['children']['cotsoc']['children']['exo_bas_sal']['children']['fillon']['children']['tx_max2']['values'][0]['value'] = 0.2285  # noqa
    reference_legislation_json_copy['children']['cotsoc']['children']['exo_bas_sal']['children']['fillon']['children']['tx_max2']['values'][1]['value'] = 0.2075  # noqa
    return reference_legislation_json_copy
