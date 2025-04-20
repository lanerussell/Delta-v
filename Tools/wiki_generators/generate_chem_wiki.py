"""
Generates content for the Delta-V wiki to simplify updates following changes to
medical, chemical, and other recipes in code. This aims to make the wiki as accurate
and up-to-date as possible by generating wiki entries directly from source code.
"""

import yaml
from any_yaml import Loader, Tagged
from jinja2 import Environment, FileSystemLoader


def read_yaml(file_path: str, encoding: str = "utf-8") -> list:
    """
    Returns a Python list defined by provided yaml file

    :param file_path: Path of yaml file to read
    :type file_path: str
    :param encoding: File encoding, defaults to "utf-8"
    :type encoding: str, optional
    :return: List representation of yaml file
    :rtype: list
    """
    with open(file_path, encoding=encoding) as stream:
        try:
            return yaml.load(stream, Loader=Loader)

        except Exception as e:
            print(f"Failed to parse yaml file {file_path} with error: {e}")
            return []


class Chem:
    """
    Generic class to handle effects and conditions
    common to all different types of chems
    """

    def __init__(self):
        self.chem_effects_raw = []
        self.chem_recipes_raw = []
        self.chems = {}
        self.rendered_wiki_block = ""

    def generate_effect_string(self, effect: Tagged) -> str:
        """
        Generates a human-readable string to describe the passed effect, including any
        requisite conditions the effect has

        :param effect: The effect object
        :type effect: Tagged
        :return: human-readable string describing the passed effect
        :rtype: str
        """
        effect_string = ""

        match effect.tag:
            case "HealthChange":
                damage = effect.get("damage", {})
                damage_types = damage.get("types", {})
                damage_groups = damage.get("groups", {})
                conditions = effect.get("conditions", [])

                for damage_type, damage_value in damage_types.items():
                    if damage_value <= 0:
                        effect_string += (
                            f"Heals {{{{DMG|{damage_type}|+|{abs(damage_value)}}}}} "
                        )
                    else:
                        effect_string += (
                            f"Deals {{{{DMG|{damage_type}|-|{abs(damage_value)}}}}} "
                        )

                for damage_group, damage_value in damage_groups.items():
                    if damage_value <= 0:
                        effect_string += (
                            f"Heals {{{{DMG|{damage_group}|+|{abs(damage_value)}}}}} "
                        )
                    else:
                        effect_string += (
                            f"Deals {{{{DMG|{damage_group}|-|{abs(damage_value)}}}}} "
                        )

                for condition in conditions:
                    effect_string += self.generate_sub_condition_string(condition)

                return effect_string

            case "AdjustReagent":
                conditions = effect.get("conditions", [])
                reagent_amount = effect.get("amount")
                reagent_name = effect.get("reagent")
                probability = effect.get("probability")

                if not reagent_amount or not reagent_name:
                    return ""

                if probability:
                    effect_string += f"Has a {int(probability * 100)}% chance to "

                if reagent_amount >= 0:
                    effect_string += "add " if probability else "Adds "
                    effect_string += (
                        f"{abs(reagent_amount)}u of {reagent_name} to the solution "
                    )
                elif reagent_amount < 0:
                    effect_string += "remove " if probability else "Removes "
                    effect_string += (
                        f"{abs(reagent_amount)}u of {reagent_name} from the solution "
                    )
                else:
                    return ""

                for condition in conditions:
                    effect_string += self.generate_sub_condition_string(condition)

                return effect_string

            case "Drunk":
                conditions = (
                    effect.get("conditions", []) if isinstance(effect, dict) else []
                )

                effect_string += "Causes drunkenness "
                for condition in conditions:
                    effect_string += self.generate_sub_condition_string(condition)

                return effect_string

            case "Jitter":
                conditions = (
                    effect.get("conditions", []) if isinstance(effect, dict) else []
                )

                effect_string += "Causes jittering "
                for condition in conditions:
                    effect_string += self.generate_sub_condition_string(condition)

                return effect_string

            case "ChemVomit":
                conditions = (
                    effect.get("conditions", []) if isinstance(effect, dict) else []
                )
                probability = effect.get("probability")
                if not probability:
                    return ""

                effect_string += (
                    f"Has a {int(probability * 100)}% chance to cause vomiting "
                )
                for condition in conditions:
                    effect_string += self.generate_sub_condition_string(condition)

                return effect_string

            case "SatiateThirst":
                effect_string += (
                    f"Satiates thirst at {effect.get('factor', 'unknown')}x rate"
                )

                return effect_string

            case "SatiateHunger":
                effect_string += (
                    f"Satiates hunger at {effect.get('factor', 'unknown')}x rate"
                )

                return effect_string

            case "ModifyBleedAmount":
                effect_string += (
                    f"Modifies bleed amount by {effect.get('amount', 'unknown')}"
                )

                return effect_string

            case "ModifyBloodLevel":
                conditions = (
                    effect.get("conditions", []) if isinstance(effect, dict) else []
                )

                effect_string += (
                    f"Modifies blood level by {effect.get('amount', 'unknown')} "
                )

                for condition in conditions:
                    effect_string += self.generate_sub_condition_string(condition)

                return effect_string

            case "AdjustTemperature":
                conditions = (
                    effect.get("conditions", []) if isinstance(effect, dict) else []
                )

                amount = effect.get("amount")
                if not amount:
                    return ""

                effect_string += f"Modifies body temperature by {amount / 1000} kJ "

                for condition in conditions:
                    effect_string += self.generate_sub_condition_string(condition)

                return effect_string

            case "ReduceRotting":
                conditions = (
                    effect.get("conditions", []) if isinstance(effect, dict) else []
                )

                rot_seconds = effect.get("seconds")
                if not rot_seconds:
                    return ""

                effect_string += f"Regenerates {rot_seconds} seconds of rotting "

                for condition in conditions:
                    effect_string += self.generate_sub_condition_string(condition)

                return effect_string

            case "CureZombieInfection":
                conditions = (
                    effect.get("conditions", []) if isinstance(effect, dict) else []
                )

                effect_string += "Cures an ongoing zombie infection "
                if effect.get("innoculate"):
                    effect_string += "and provides immunity to future infections "

                for condition in conditions:
                    effect_string += self.generate_sub_condition_string(condition)

                return effect_string

            case "MakeSentient":
                conditions = (
                    effect.get("conditions", []) if isinstance(effect, dict) else []
                )

                effect_string += "Makes the metabolizer sentient "

                for condition in conditions:
                    effect_string += self.generate_sub_condition_string(condition)

                return effect_string

            case "ResetNarcolepsy":
                conditions = (
                    effect.get("conditions", []) if isinstance(effect, dict) else []
                )

                effect_string += "Temporarily staves off narcolepsy "

                for condition in conditions:
                    effect_string += self.generate_sub_condition_string(condition)

                return effect_string

            case "ChemHealEyeDamage":
                conditions = (
                    effect.get("conditions", []) if isinstance(effect, dict) else []
                )

                effect_string += "Heals eye damage"

                for condition in conditions:
                    effect_string += self.generate_sub_condition_string(condition)

                return effect_string

            case "PopupMessage":
                return ""

            case "Emote":
                return ""

            case "GenericStatusEffect":
                effect_type = effect.get("type", "Cause")

                effect_string += (
                    f"{effect_type} effect \"{effect.get('key', "unknown status")}\""
                )
                effect_time = effect.get("time")
                if effect_time:
                    effect_string += f" for at least {effect_time} seconds"

                return effect_string

            # catch-all in case new effect types are added
            case _:
                return f"undefined tag: {effect.tag}"

    def generate_sub_condition_string(self, condition: Tagged) -> str:
        """
        Generates a human-readable string to describe the passed condition

        :param condition: The condition object
        :type condition: Tagged
        :return: human-readable string describing the passed condition
        :rtype: str
        """
        condition_string = ""
        match condition.tag:
            case "ReagentThreshold":
                specific_reagent = condition.get("reagent")
                if specific_reagent:
                    condition_string += (
                        f"when there's at least {condition.get("min", "?")}u "
                        f"of {specific_reagent} present "
                    )
                else:
                    condition_string += (
                        f"when there's at least {condition.get("min", "?")}u "
                        f"of this reagent "
                    )
            case "Temperature":
                condition_string += "when the body's temperature is "
                max_temp = condition.get("max")
                min_temp = condition.get("min")
                if max_temp and min_temp:
                    condition_string += f"above {min_temp} K and below {max_temp} K "
                elif max_temp:
                    condition_string += f"below {max_temp} K "
                elif min_temp:
                    condition_string += f"above {min_temp} K "

            case "MobStateCondition":
                condition_string += (
                    f"when the mob is {condition.get("mobstate", "unknown_state")} "
                )

            case "HasComponent":
                for component in condition.get("components"):
                    component_type = component.get("type")
                    if component_type:
                        condition_string += (
                            f"when the mob has component type {component_type} "
                        )

        return condition_string

    def construct_chem_effect_bodies(self):
        """
        Construct effect bodies for all chems
        """
        for chem in self.chem_effects_raw:
            self.construct_single_chem_effect_body(chem)

    def construct_single_chem_effect_body(self, chem: dict):
        """
        Construct effect body for a single chem

        :param chem: A chem object describing its effects
        :type chem: dict
        """
        chem_name = chem.get("id")
        chem_color = chem.get("color", "").upper()
        if not chem_name:
            return
        if chem.get("abstract"):
            return

        chem_metabolisms = chem.get("metabolisms", {})
        effects = []
        effects.extend(chem_metabolisms.get("Medicine", {}).get("effects", []))
        effects.extend(chem_metabolisms.get("Poison", {}).get("effects", []))

        body = ""
        for effect in effects:
            effect_string = self.generate_effect_string(effect)
            if not effect_string:
                continue
            body += f"{effect_string}<br>"

        self.chems[chem_name] = {
            "name": chem_name,
            "color": chem_color,
            "recipe": None,
            "effects": body,
        }

    def construct_chem_recipe_bodies(self):
        """
        Construct recipe bodies for all chems
        """
        for chem in self.chem_recipes_raw:
            self.construct_single_chem_recipe_body(chem)

    def construct_single_chem_recipe_body(self, chem: dict):
        """
        Construct recipe body for a single chem

        :param chem: A chem object describing its recipe
        :type chem: dict
        """
        chem_name = chem.get("id")
        min_temp = chem.get("minTemp")

        if not chem_name or chem_name not in self.chems:
            return

        recipe_string = "Mix "
        recipe_string += f"above {min_temp} K<br>" if min_temp else "<br>"
        for reactant, reactant_info in chem.get("reactants", {}).items():
            recipe_string += f"{reactant_info.get("amount", "?")} part {reactant}<br>"

        self.chems[chem_name]["recipe"] = recipe_string


class Medicine(Chem):
    """
    Represents all medicine chems
    """

    def __init__(self):
        super().__init__()

        self.read_in_medicine_effect_files()
        self.read_in_medicine_recipe_files()

        self.construct_chem_effect_bodies()
        self.construct_chem_recipe_bodies()

    def read_in_medicine_effect_files(self):
        """
        Reads in medicine files describing their effects
        """
        self.chem_effects_raw.extend(
            read_yaml(file_path="Resources/Prototypes/Reagents/medicine.yml")
        )
        self.chem_effects_raw.extend(
            read_yaml(file_path="Resources/Prototypes/_DV/Reagents/medicine.yml")
        )

    def read_in_medicine_recipe_files(self):
        """
        Reads in medicine files describing their recipes
        """
        self.chem_recipes_raw.extend(
            read_yaml(file_path="Resources/Prototypes/Recipes/Reactions/medicine.yml")
        )
        self.chem_recipes_raw.extend(
            read_yaml(
                file_path="Resources/Prototypes/_DV/Recipes/Reactions/medicine.yml"
            )
        )


if __name__ == "__main__":
    medicines = Medicine()
    sorted_medicines = dict(sorted(medicines.chems.items()))

    environment = Environment(
        loader=FileSystemLoader("Tools/wiki_generators/templates")
    )
    template = environment.get_template("chem_wiki_section.j2")
    output = template.render(
        wiki_section="Medicine", chem_list=sorted_medicines.values()
    )
    print(output)

    pass
