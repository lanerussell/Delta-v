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
    Generic class to handle chem effects and conditions
    """

    def __init__(self):
        self.reagent_files = []
        self.chem_effects_raw = []
        self.chems = {}

    def read_in_chem_effect_files(self):
        """
        Reads in files describing chem effects
        """
        for chem_recipe_file in self.reagent_files:
            self.chem_effects_raw.extend(read_yaml(chem_recipe_file))

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

                effect_string += self.condition_shim(effect)

            case "AdjustReagent":
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

                effect_string += self.condition_shim(effect)

            case "Polymorph":
                effect_string += (
                    f"Causes polymorph into {effect.get('prototype', 'unknown')} "
                )

                effect_string += self.condition_shim(effect)

            case "ChemRemovePsionic":
                effect_string += "Removes psionics from the metaboliser "

                effect_string += self.condition_shim(effect)

            case "ChemRerollPsionic":
                effect_string += "Rerolls psionics for the metaboliser "

                effect_string += self.condition_shim(effect)

            case "Electrocute":
                probability = effect.get("probability")

                if probability:
                    effect_string += (
                        f"Has a {int(probability * 100)}% "
                        f"chance to electrocute the mob "
                    )
                else:
                    effect_string += "Electrocutes the mob "

                effect_string += self.condition_shim(effect)

            case "Drunk":
                effect_string += "Causes drunkenness "

                effect_string += self.condition_shim(effect)

            case "Jitter":
                effect_string += "Causes jittering "

                effect_string += self.condition_shim(effect)

            case "ChemVomit":
                probability = effect.get("probability")
                if not probability:
                    return ""

                effect_string += (
                    f"Has a {int(probability * 100)}% chance to cause vomiting "
                )

                effect_string += self.condition_shim(effect)

            case "SatiateThirst":
                if not isinstance(effect, dict):
                    return effect_string

                effect_string += (
                    f"Satiates thirst at {effect.get('factor', '?')}x rate "
                )

                effect_string += self.condition_shim(effect)

            case "SatiateHunger":
                if not isinstance(effect, dict):
                    return effect_string

                factor = effect.get("factor")

                effect_string += "Satiates hunger "
                if factor:
                    effect_string += f"at a {factor}x rate "

                effect_string += self.condition_shim(effect)

            case "ModifyBleedAmount":
                effect_string += (
                    f"Modifies bleed amount by {effect.get('amount', '?')} "
                )

                effect_string += self.condition_shim(effect)

            case "MovespeedModifier":
                walk_modifier = effect.get("walkSpeedModifier", "?")
                sprint_modifier = effect.get("sprintSpeedModifier", "?")
                effect_string += (
                    f"Modifies walk speed by {walk_modifier} "
                    f"and sprint speed by {sprint_modifier} "
                )

                effect_string += self.condition_shim(effect)

            case "ModifyBloodLevel":
                effect_string += f"Modifies blood level by {effect.get('amount', '?')} "

                effect_string += self.condition_shim(effect)

            case "ChemCleanBloodstream":
                effect_string += (
                    f"Cleans the bloodstream at a rate of "
                    f"{effect.get('cleanseRate', '?')} "
                )

                effect_string += self.condition_shim(effect)

            case "AdjustTemperature":
                amount = effect.get("amount")
                if not amount:
                    return ""

                effect_string += f"Modifies body temperature by {amount / 1000} kJ "

                effect_string += self.condition_shim(effect)

            case "FlammableReaction":
                effect_string += (
                    f"Causes a flammable reaction with multiplier "
                    f"{effect.get('multiplier', '?')} "
                )

                effect_string += self.condition_shim(effect)

            case "Ignite":
                effect_string += "Ignites the mob "

                effect_string += self.condition_shim(effect)

            case "ReduceRotting":
                rot_seconds = effect.get("seconds")
                if not rot_seconds:
                    return ""

                effect_string += f"Regenerates {rot_seconds} seconds of rotting "

                effect_string += self.condition_shim(effect)

            case "CureZombieInfection":
                effect_string += "Cures an ongoing zombie infection "
                if effect.get("innoculate"):
                    effect_string += "and provides immunity to future infections "

                effect_string += self.condition_shim(effect)

            case "CauseZombieInfection":
                effect_string += "Causes a zombie infection "

                effect_string += self.condition_shim(effect)

            case "MakeSentient":
                effect_string += "Makes the metabolizer sentient "

                effect_string += self.condition_shim(effect)

            case "Addicted":
                probability = effect.get("probability")

                if probability:
                    effect_string += f"Has a {int(probability * 100)}% chance to "

                effect_string += "cause " if probability else "Causes "
                effect_string += "the mob to become addicted "

                effect_string += self.condition_shim(effect)

            case "SuppressAddiction":
                effect_string += "Suppresses addiction "

                effect_string += self.condition_shim(effect)

            case "ResetNarcolepsy":
                effect_string += "Temporarily staves off narcolepsy "

                effect_string += self.condition_shim(effect)

            case "ChemHealEyeDamage":
                effect_string += "Heals eye damage"

                effect_string += self.condition_shim(effect)

            case "PopupMessage":
                return ""

            case "Emote":
                return ""

            case "GenericStatusEffect":
                effect_type = effect.get("type", "Causes")

                effect_string += (
                    f"{effect_type} effect {effect.get('key', "unknown status")} "
                )
                effect_time = effect.get("time")
                if effect_time:
                    effect_string += f" for at least {effect_time} seconds "

                effect_string += self.condition_shim(effect)

            # catch-all in case new effect types are added
            case _:
                raise NotImplementedError(f"undefined effect tag: {effect.tag}")

        return effect_string.rstrip()

    def condition_shim(self, effect: Tagged) -> str:
        """
        Calls self.generate_sub_condition_string() if conditions found in effect

        param effect: The effect object
        :type effect: Tagged
        :return: human-readable string describing conditions for the passed effect
        :rtype: str
        """
        condition_string = ""
        conditions = effect.get("conditions", []) if isinstance(effect, dict) else []
        for condition in conditions:
            condition_string += self.generate_sub_condition_string(condition)

        return condition_string

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

            case "TotalDamage":
                condition_string += "when total damage is "
                max_dam = condition.get("max")
                min_dam = condition.get("min")
                if max_dam and min_dam:
                    condition_string += f"above {min_dam} and below {max_dam} "
                elif max_dam:
                    condition_string += f"below {max_dam} "
                elif min_dam:
                    condition_string += f"above {min_dam} "

            case "OrganType":
                organ_type = condition.get("type", "unknown")
                should_have = condition.get("shouldHave", True)

                condition_string += (
                    f"when the mob {'has' if should_have else 'does not have'} "
                    f"{organ_type} organs "
                )

            case "HasTag":
                tag = condition.get("tag", "unknown")
                tag_invert = condition.get("invert", False)
                condition_string += "when the mob "
                condition_string += f"{'has' if not tag_invert else 'does not have'} "
                condition_string += f"the {tag} tag "

            case "Hunger":
                condition_string += "when hunger is "
                max_hunger = condition.get("max")
                min_hunger = condition.get("min")
                if max_hunger and min_hunger:
                    condition_string += f"above {min_hunger} and below {max_hunger} "
                elif max_hunger:
                    condition_string += f"below {max_hunger} "
                elif min_hunger:
                    condition_string += f"above {min_hunger} "

            case "JobCondition":
                jobs = condition.get("job", [])
                condition_string += "when the metaboliser's job is "
                if len(jobs) < 1:
                    pass
                elif len(jobs) == 1:
                    condition_string += f"{jobs[0]} "
                else:
                    for job in jobs:
                        condition_string += f"{job}, "
                    condition_string = condition_string.removesuffix(", ") + " "

            # catch-all in case new condition types are added
            case _:
                raise NotImplementedError(f"undefined condition tag: {condition.tag}")

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
        metabolism_rate = None
        if not chem_name:
            return
        if chem.get("abstract"):
            return

        chem_metabolisms = chem.get("metabolisms", {})
        metabolism_types = ["Medicine", "Narcotic", "Poison", "Food", "Drink"]
        effects = []
        for metabolism_type in metabolism_types:
            effects.extend(chem_metabolisms.get(metabolism_type, {}).get("effects", []))
            if not metabolism_rate and chem_metabolisms.get(metabolism_type, {}).get(
                "metabolismRate"
            ):
                metabolism_rate = (
                    str(chem_metabolisms.get(metabolism_type, {}).get("metabolismRate"))
                    + "u/s"
                )
        if not metabolism_rate:
            metabolism_rate = "0.5 u/s"

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
            "metabolic_rate": metabolism_rate,
        }

    def populate_recipes(self, recipes: dict):
        """
        Populates recipes into each chem

        :param recipes: Dictionary containing chem recipe strings in wiki format
        :type recipes: dict
        """
        for chem_name, chem in self.chems.items():
            chem["recipe"] = recipes.get(chem_name, {}).get("final_recipe", "None")


class ChemRecipe:
    """
    Class to handle chem recipes
    """

    def __init__(self):
        self.chem_recipes_raw = []
        self.chems_recipes = {}
        self.icon_map = {}

        self.build_icon_map()
        self.read_in_chem_recipe_files()
        self.construct_basic_recipe_bodies()

        # construct simple bodies for use in final final recipe tooltips
        self.construct_final_recipe_bodies(simple=True)
        self.construct_final_recipe_bodies(simple=False)

    def build_icon_map(self):
        """
        Builds a simple dict mapping requiredMixerCategories to icon file names
        """
        self.icon_map = {
            "Mix": "[[File:Beaker.png]] Mix",
            "Electrolysis": "[[File:Electrolysis Unit.png]] Electrolyze",
            "Centrifuge": "[[File:Centrifuge.png]] Centrifuge",
            "Shake": "[[File:Shaker.png]] Shake",
        }

    def read_in_chem_recipe_files(self):
        """
        Reads in chem files describing recipes
        """
        prefix = "Resources/Prototypes/"
        chem_recipe_files = [
            f"{prefix}Recipes/Reactions/biological.yml",
            f"{prefix}Recipes/Reactions/botany.yml",
            f"{prefix}Recipes/Reactions/chemicals.yml",
            f"{prefix}Recipes/Reactions/cleaning.yml",
            f"{prefix}Recipes/Reactions/drinks.yml",
            f"{prefix}Recipes/Reactions/food.yml",
            f"{prefix}Recipes/Reactions/fun.yml",
            f"{prefix}Recipes/Reactions/gas.yml",
            f"{prefix}Recipes/Reactions/medicine.yml",
            f"{prefix}Recipes/Reactions/pyrotechnic.yml",
            f"{prefix}Recipes/Reactions/single_reagent.yml",
            f"{prefix}_DV/Recipes/Reactions/medicine.yml",
            f"{prefix}_Floof/Recipes/Reactions/medicine.yml",
            f"{prefix}_Funkystation/Recipes/Reactions/medicine.yml",
            f"{prefix}Nyanotrasen/Recipes/Reactions/drink.yml",
            f"{prefix}_DV/Recipes/Reactions/drinks.yml",
            f"{prefix}_NF/Recipes/Reactions/drinks.yml",
            f"{prefix}Nyanotrasen/Recipes/Reactions/food.yml",
            f"{prefix}_DV/Recipes/Reactions/food.yml",
        ]

        for chem_recipe_file in chem_recipe_files:
            self.chem_recipes_raw.extend(read_yaml(chem_recipe_file))

    def construct_basic_recipe_bodies(self):
        """
        Construct basic recipe bodies for all chems
        """
        for recipe in self.chem_recipes_raw:
            if recipe.get("requiredMixerCategories"):
                self.construct_basic_recipe_body_special(recipe)
            else:
                self.construct_basic_recipe_body(recipe)

    def construct_basic_recipe_body_special(self, recipe: dict) -> dict:
        """
        Construct basic recipe body for chems with requiredMixerCategories. Each recipe
        may have multiple products, i.e. electrolysing cellulose into sugar and carbon

        :param chem: A chem object describing its recipe
        :type chem: dict
        """
        min_temp = recipe.get("minTemp")
        products = recipe.get("products")

        recipe_dict = {}
        # default to "Mix" if specified MixerCategory not in icon_map
        recipe_dict["prefix"] = (
            f"{self.icon_map.get(recipe.get('requiredMixerCategories', ["Mix"])[0])} "
        )
        recipe_dict["prefix"] += f"above {min_temp} K<br>" if min_temp else "<br>"
        recipe_dict["reactants"] = recipe.get("reactants", {})

        for chem_name in products.keys():
            if not self.chems_recipes.get(chem_name):
                self.chems_recipes[chem_name] = {}

            if self.chems_recipes[chem_name].get("special_recipes") is not None:
                self.chems_recipes[chem_name]["special_recipes"].append(recipe_dict)
            else:
                self.chems_recipes[chem_name]["special_recipes"] = [recipe_dict]

    def construct_basic_recipe_body(self, recipe: dict) -> dict:
        """
        Construct basic recipe body for a single chem

        :param chem: A chem object describing its recipe
        :type chem: dict
        """
        chem_name = recipe.get("id")
        min_temp = recipe.get("minTemp")

        recipe_dict = {}
        recipe_dict["prefix"] = f"{self.icon_map.get("Mix")} "
        recipe_dict["prefix"] += f"above {min_temp} K<br>" if min_temp else "<br>"
        recipe_dict["reactants"] = recipe.get("reactants", {})

        if not self.chems_recipes.get(chem_name):
            self.chems_recipes[chem_name] = {}

        if self.chems_recipes[chem_name].get("basic_recipes") is not None:
            self.chems_recipes[chem_name]["basic_recipes"].append(recipe_dict)
        else:
            self.chems_recipes[chem_name]["basic_recipes"] = [recipe_dict]

    def construct_final_recipe_bodies(self, simple: bool):
        """
        Construct final recipe bodies for all chems

        :param simple: If true, generates a simple recipe body with no tooltips/links
        :type simple: bool
        """
        for recipes in self.chems_recipes.values():
            chem_recipe_body = ""

            for recipe in recipes.get("basic_recipes", []):
                chem_recipe_body += self.construct_final_recipe_body_component(
                    recipe, simple
                )
            for recipe in recipes.get("special_recipes", []):
                chem_recipe_body += self.construct_final_recipe_body_component(
                    recipe, simple
                )

            chem_recipe_body = chem_recipe_body.removesuffix("<br>")
            if simple:
                recipes["final_recipe_simple"] = chem_recipe_body
            else:
                recipes["final_recipe"] = chem_recipe_body

    def construct_final_recipe_body_component(self, recipe: dict, simple: bool) -> str:
        """
        Construct one part of a recipe body for a chem that may have multiple recipes

        :param recipe: Dict containing the recipe prefix and reactants
        :type recipe: dict
        :param simple: _description_
        :type simple: bool
        :return: String formatted for use on the wiki
        :rtype: str
        """
        recipe_body = recipe.get("prefix", "")

        if simple:
            for reactant, value in recipe.get("reactants", {}).items():
                recipe_body += f"{value.get("amount", "?")} part {reactant}"
                recipe_body += "<sup>(catalyst)</sup>" if value.get("catalyst") else ""
                recipe_body += "<br>"
            return recipe_body

        for reactant, value in recipe.get("reactants", {}).items():
            reactant_recipe = self.chems_recipes.get(reactant)
            recipe_body += f"{value.get("amount", "?")} part "
            if reactant_recipe:
                reactant_cataylst_str = (
                    f"{reactant}"
                    f"{'<sup>(catalyst)</sup>' if value.get('catalyst') else ''}"
                )
                recipe_body += f"{{{{Tooltip|[[#{reactant}|{reactant_cataylst_str}]]|"
                recipe_body += self.chems_recipes[reactant].get(
                    "final_recipe_simple", "?"
                )
                recipe_body += "}}<br>"
            else:
                recipe_body += f"{reactant}"
                recipe_body += "<sup>(catalyst)</sup>" if value.get("catalyst") else ""
                recipe_body += "<br>"

        return recipe_body


class Biological(Chem):
    """
    Represents biological chems
    """

    def __init__(self):
        super().__init__()
        self.reagent_files = [
            "Resources/Prototypes/Reagents/biological.yml",
            "Resources/Prototypes/_DV/Reagents/biological.yml",
        ]

        self.read_in_chem_effect_files()
        self.construct_chem_effect_bodies()
        self.chems = dict(sorted(self.chems.items()))  # sort chems alphabetically


class Botany(Chem):
    """
    Represents botanical chems
    """

    def __init__(self):
        super().__init__()
        self.reagent_files = [
            "Resources/Prototypes/Reagents/botany.yml",
        ]

        self.read_in_chem_effect_files()
        self.construct_chem_effect_bodies()
        self.chems = dict(sorted(self.chems.items()))  # sort chems alphabetically


class Chemicals(Chem):
    """
    Represents chemical chems
    """

    def __init__(self):
        super().__init__()
        self.reagent_files = [
            "Resources/Prototypes/Reagents/chemicals.yml",
        ]

        self.read_in_chem_effect_files()
        self.construct_chem_effect_bodies()
        self.chems = dict(sorted(self.chems.items()))  # sort chems alphabetically


class Cleaning(Chem):
    """
    Represents cleaning chems
    """

    def __init__(self):
        super().__init__()
        self.reagent_files = [
            "Resources/Prototypes/Reagents/cleaning.yml",
        ]

        self.read_in_chem_effect_files()
        self.construct_chem_effect_bodies()
        self.chems = dict(sorted(self.chems.items()))  # sort chems alphabetically


class Drinks(Chem):
    """
    Represents drink chems
    """

    def __init__(self):
        super().__init__()
        self.reagent_files = [
            "Resources/Prototypes/Reagents/Consumable/Drink/alcohol.yml",
            "Resources/Prototypes/Reagents/Consumable/Drink/base_drink.yml",
            "Resources/Prototypes/Reagents/Consumable/Drink/drinks.yml",
            "Resources/Prototypes/Reagents/Consumable/Drink/juice.yml",
            "Resources/Prototypes/Reagents/Consumable/Drink/soda.yml",
            "Resources/Prototypes/Nyanotrasen/Reagents/Consumable/Drink/drinks.yml",
            "Resources/Prototypes/_DV/Reagents/Consumable/Drink/drinks.yml",
            "Resources/Prototypes/_NF/Reagents/Consumables/Drink/drinks.yml",
        ]

        self.read_in_chem_effect_files()
        self.construct_chem_effect_bodies()
        self.chems = dict(sorted(self.chems.items()))  # sort chems alphabetically


class Elements(Chem):
    """
    Represents elements chems
    """

    def __init__(self):
        super().__init__()
        self.reagent_files = [
            "Resources/Prototypes/Reagents/elements.yml",
        ]

        self.read_in_chem_effect_files()
        self.construct_chem_effect_bodies()
        self.chems = dict(sorted(self.chems.items()))  # sort chems alphabetically


class Foods(Chem):
    """
    Represents food chems
    """

    def __init__(self):
        super().__init__()
        prefix = "Resources/Prototypes/"
        self.reagent_files = [
            f"{prefix}Reagents/Consumable/Food/condiments.yml",
            f"{prefix}Reagents/Consumable/Food/food.yml",
            f"{prefix}Reagents/Consumable/Food/ingredients.yml",
            f"{prefix}Nyanotrasen/Reagents/Consumable/Food/condiments.yml",
            f"{prefix}Nyanotrasen/Reagents/Consumable/Food/food.yml",
            f"{prefix}Nyanotrasen/Entities/Objects/Consumable/Food/ingredients.yml",
        ]

        self.read_in_chem_effect_files()
        self.construct_chem_effect_bodies()
        self.chems = dict(sorted(self.chems.items()))  # sort chems alphabetically


class Fun(Chem):
    """
    Represents fun chems
    """

    def __init__(self):
        super().__init__()
        self.reagent_files = [
            "Resources/Prototypes/Reagents/fun.yml",
            "Resources/Prototypes/_DV/Reagents/fun.yml",
        ]

        self.read_in_chem_effect_files()
        self.construct_chem_effect_bodies()
        self.chems = dict(sorted(self.chems.items()))  # sort chems alphabetically


class Gases(Chem):
    """
    Represents gas chems
    """

    def __init__(self):
        super().__init__()
        self.reagent_files = [
            "Resources/Prototypes/Reagents/gases.yml",
        ]

        self.read_in_chem_effect_files()
        self.construct_chem_effect_bodies()
        self.chems = dict(sorted(self.chems.items()))  # sort chems alphabetically


class Medicine(Chem):
    """
    Represents medicine chems
    """

    def __init__(self):
        super().__init__()
        self.reagent_files = [
            "Resources/Prototypes/Reagents/medicine.yml",
            "Resources/Prototypes/_DV/Reagents/medicine.yml",
            "Resources/Prototypes/_Floof/Reagents/medicine.yml",
            "Resources/Prototypes/_Funkystation/Reagents/medicine.yml",
        ]

        self.read_in_chem_effect_files()
        self.construct_chem_effect_bodies()
        self.chems = dict(sorted(self.chems.items()))  # sort chems alphabetically


class Narcotics(Chem):
    """
    Represents narcotic chems
    """

    def __init__(self):
        super().__init__()
        self.reagent_files = [
            "Resources/Prototypes/Reagents/narcotics.yml",
        ]

        self.read_in_chem_effect_files()
        self.construct_chem_effect_bodies()
        self.chems = dict(sorted(self.chems.items()))  # sort chems alphabetically


class Pyrotechnic(Chem):
    """
    Represents pyrotechnic chems
    """

    def __init__(self):
        super().__init__()
        self.reagent_files = [
            "Resources/Prototypes/Reagents/pyrotechnic.yml",
        ]

        self.read_in_chem_effect_files()
        self.construct_chem_effect_bodies()
        self.chems = dict(sorted(self.chems.items()))  # sort chems alphabetically


class Toxins(Chem):
    """
    Represents toxin chems
    """

    def __init__(self):
        super().__init__()
        self.reagent_files = [
            "Resources/Prototypes/Reagents/toxins.yml",
        ]

        self.read_in_chem_effect_files()
        self.construct_chem_effect_bodies()
        self.chems = dict(sorted(self.chems.items()))  # sort chems alphabetically


if __name__ == "__main__":
    chem_recipes = ChemRecipe().chems_recipes
    chem_dict = {}

    chem_dict["Biological"] = Biological()
    chem_dict["Botany"] = Botany()
    chem_dict["Chemicals"] = Chemicals()
    chem_dict["Cleaning"] = Cleaning()
    chem_dict["Drinks"] = Drinks()
    chem_dict["Elements"] = Elements()
    chem_dict["Foods"] = Foods()
    chem_dict["Fun"] = Fun()
    chem_dict["Gases"] = Gases()
    chem_dict["Medicine"] = Medicine()
    chem_dict["Narcotics"] = Narcotics()
    chem_dict["Pyrotechnic"] = Pyrotechnic()
    chem_dict["Toxins"] = Toxins()

    environment = Environment(
        loader=FileSystemLoader("Tools/wiki_generators/templates")
    )
    header_template = environment.get_template("page_header.j2")
    template = environment.get_template("chem_wiki_section.j2")

    print(header_template.render())

    for chem_type, chem_class in chem_dict.items():
        chem_class.populate_recipes(chem_recipes)

        output = template.render(
            wiki_section=chem_type, chem_list=chem_class.chems.values()
        )
        print(output)

    print("\n{{Guides Menu}}")
