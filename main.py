"""Neighborly Wiki Generator

Generates an HTML wiki for generated Neighborly worlds.

"""

from __future__ import annotations

import random
import argparse
import json
import os
import pathlib
from typing import Any
from neighborly.simulation import Simulation
from neighborly.ecs import GameObject
from neighborly.config import SimulationConfig, LoggingConfig
from neighborly.plugins import default_content
from neighborly.components.settlement import Settlement, District
from neighborly.components.character import Character, MemberOfHousehold, Species
from neighborly.components.business import Business, Occupation
from neighborly.components.location import FrequentedLocations, CurrentSettlement, CurrentDistrict
from neighborly.components.skills import Skills
from neighborly.components.traits import Traits
from neighborly.components.shared import Age
from neighborly.components.relationship import Relationships, Reputation, Romance
import jinja2

TEMPLATES_DIR = pathlib.Path(__file__).parent / "templates"
"""The path to the directory containing the Jinja templates."""

OUTPUT_DIR = pathlib.Path(os.getcwd()) / "output"
"""The path to the output directory."""

FILE_LOADER = jinja2.FileSystemLoader(TEMPLATES_DIR)
"""Reference to Jinja's file loader."""

JINJA_ENV = jinja2.Environment(loader=FILE_LOADER)
"""Reference to the Jinja environment instance."""


def get_args() -> argparse.Namespace:
    """Configure CLI argument parser and parse args.

    Returns
    -------
    argparse.Namespace
        parsed CLI arguments.
    """

    parser = argparse.ArgumentParser("Neighborly Wiki Generator.")

    parser.add_argument(
        "-s",
        "--seed",
        default=str(random.randint(0, 9999999)),
        type=str,
        help="The world seed.",
    )

    parser.add_argument(
        "-y",
        "--years",
        default=10,
        type=int,
        help="The number of years to simulate.",
    )

    # parser.add_argument(
    #     "-o",
    #     "--output",
    #     type=pathlib.Path,
    #     help="Specify path to write generated JSON data.",
    # )

    parser.add_argument(
        "--disable-logging",
        help="Disable logging events to a file.",
        action="store_true",
    )

    return parser.parse_args()


def generate_trait_page(sim: Simulation, gameobject: GameObject) -> None:
    """Generate a page for a residential building."""
    raise NotImplementedError()


def generate_residence_page(sim: Simulation, gameobject: GameObject) -> None:
    """Generate a page for a residential building."""

    residence_name: str = gameobject.name
    activity_status = "Active" if gameobject.is_active else "Inactive"

    # Get district info
    district_id: int = gameobject.get_component("ResidentialBuilding").disctrict
    district_name: str = sim.world.gameobjects[district_id].name
    district: tuple[str, str] = (
        district_name,
        f"../gameobjects/{district_id}.html",
    )

    # Get trait info
    traits: list[dict[str, Any]] = []
    for trait_id, trait_instance in gameobject.get_component(Traits).traits.items():
        trait_name = trait_instance.trait.name
        trait_description = trait_instance.description
        traits.append({"name": trait_name, "description": trait_description})

    # Get resident info
    units: list[dict[str, Any]] = []
    for unit_id in gameobject["components"]["ResidentialBuilding"]["units"]:
        unit = sim["gameobjects"][str(unit_id)]

        residents: list[tuple[str, str]] = []

        for resident_id in unit.get_component("Residence").residents:
            resident = sim.world.gameobjects[resident_id]
            residents.append((resident.name, f"../gameobjects/{resident_id}.html"))

        units.append({"number": unit_id, "residents": residents})

    template = JINJA_ENV.get_template("residence.jinja")
    rendered_page = template.render(
        residence_name=residence_name,
        district=district,
        traits=traits,
        units=units,
        activity_status=activity_status,
    )

    with open(
        OUTPUT_DIR / "gameobjects" / f"{gameobject['id']}.html", "w", encoding="utf-8"
    ) as file:
        file.write(rendered_page)


def generate_business_page(sim: Simulation, gameobject: GameObject) -> None:
    """Generate a page for a business."""

    business_name: str = gameobject.name

    # Get activity status
    activity_status = "Active" if gameobject.is_active else "Inactive"

    # Get district information
    district_id: int = gameobject.get_component(CurrentDistrict).district.uid
    district = gameobject.get_component(CurrentDistrict).district
    district_name: str = district.name
    district_link: str = f"../gameobjects/{district_id}.html" 

    # Get business owner information
    # district_id: int = entry["components"]["Business"]["district"]
    owner_name: str = "TBD"
    owner_link: str = "#"

    # Frequented by
    frequented_by: list[GameObject] = []

    # Get trait info
    traits: list[dict[str, Any]] = []
    for trait_id, trait_instance in gameobject.get_component(Traits).traits.items():
        trait_name = trait_instance.trait.name
        trait_description = trait_instance.description
        traits.append({"name": trait_name, "description": trait_description})

    # Get event data
    events: list[dict[str, Any]] = []

    template = JINJA_ENV.get_template("business.jinja")
    rendered_page = template.render(
        business_name=business_name,
        district_name=district_name,
        district_link=district_link,
        activity_status=activity_status,
        owner_name=owner_name,
        owner_link=owner_link,
        frequented_by=frequented_by,
        traits=traits,
        events=events,
    )

    with open(
        OUTPUT_DIR / "gameobjects" / f"{gameobject.uid}.html",
        "w",
        encoding="utf-8",
    ) as file:
        file.write(rendered_page)


def generate_character_page(sim: Simulation, gameobject: GameObject) -> None:
    """Generate a page for a character."""

    character_name = gameobject.name

    # Get activity status
    activity_status = "Active" if gameobject.is_active else "Inactive"

    age = int(gameobject.get_component(Age).value)
    sex = gameobject.get_component(Character).sex.name
    life_stage = gameobject.get_component(Character).life_stage.name
    species = gameobject.get_component(Species).species.name

    household_name = "N/A"
    household_link = "#"
    if member_of_household := gameobject.try_component(MemberOfHousehold):
        household_id: int = member_of_household.household.uid
        household_name = member_of_household.household.name
        household_link = f"../gameobjects/{household_id}.html"

    occupation_name = "N/A"
    occupation_link = "#"
    if occupation_data := gameobject.try_component(Occupation):
        business_id: int = occupation_data.business.uid
        occupation_name = occupation_data.business.name
        occupation_link = f"../gameobjects/{business_id}.html"

    # Get trait info
    traits: list[dict[str, Any]] = []
    for trait_id, trait_instance in gameobject.get_component(Traits).traits.items():
        trait_name = trait_instance.trait.name
        trait_description = trait_instance.description
        traits.append({"name": trait_name, "description": trait_description})

    # Get skill info
    skills: list[dict[str, Any]] = []
    for skill_id, skill_instance in gameobject.get_component(Skills).skills.items():
        skill_name = skill_instance.skill.name
        skill_description = skill_instance.skill.description
        skills.append(
            {"name": skill_name, "level": skill_instance.stat.value, "description": skill_description}
        )

    # Frequented locations
    frequented_locations: list[dict[str, Any]] = []
    for location in gameobject.get_component(FrequentedLocations):
        frequented_locations.append(
            {"name": location.name, "link": f"../gameobjects/{location.uid}.html"}
        )

    # Get relationship data
    relationships: list[dict[str, Any]] = []
    outgoing_relationship_data = gameobject.get_component(Relationships).outgoing
    for target, relationship in outgoing_relationship_data.items():

        relationship_traits: list[dict[str, Any]] = []
        for trait_id, trait_instance in relationship.get_component(Traits).traits.items():
            trait_name = trait_instance.trait.name
            trait_description = trait_instance.description
            relationship_traits.append(
                {"name": trait_name, "description": trait_description}
            )

        relationships.append(
            {
                "target_name": target.name,
                "target_link": f"../gameobjects/{target.uid}.html",
                "reputation": relationship.get_component(Reputation).stat.value,
                "romance": relationship.get_component(Romance).stat.value,
                "traits": relationship_traits,
            }
        )

    # Get event data
    events: list[dict[str, Any]] = []

    template = JINJA_ENV.get_template("character.jinja")
    rendered_page = template.render(
        character_name=character_name,
        activity_status=activity_status,
        age=age,
        life_stage=life_stage,
        sex=sex,
        species=species,
        household_link=household_link,
        household_name=household_name,
        occupation_link=occupation_link,
        occupation_name=occupation_name,
        frequented_locations=frequented_locations,
        traits=traits,
        skills=skills,
        relationships=relationships,
        events=events,
    )

    with open(
        OUTPUT_DIR / "gameobjects" / f"{gameobject.uid}.html",
        "w",
        encoding="utf-8",
    ) as file:
        file.write(rendered_page)


def generate_skill_page(sim: Simulation, gameobject: GameObject) -> None:
    """Generate a page for a skill."""
    raise NotImplementedError()


def generate_district_page(sim: Simulation, gameobject: GameObject) -> None:
    """Generate a page for a district."""

    district_name: str = gameobject.name
    #description: str = gameobject.get_component(District).description

    settlement_id: int = gameobject.get_component(CurrentSettlement).settlement.uid
    settlement_name: str = gameobject.get_component(CurrentSettlement).settlement.name
    settlement: tuple[str, str] = (
        settlement_name,
        f"../gameobjects/{settlement_id}.html",
    )
    
    locations: list[GameObject] = gameobject.get_component(District).locations
    location_links: list[tuple[str, str]] = []
    for location in locations:
        location_links.append((location.name, f"../gameobjects/{location.uid}.html"))

    template = JINJA_ENV.get_template("district.jinja")
    rendered_page = template.render(
        district_name=district_name,
        #description=description,
        settlement_name=settlement_name,
        locations=locations,
        settlement=settlement,
    )

    with open(
        OUTPUT_DIR / "gameobjects" / f"{gameobject.uid}.html",
        "w",
        encoding="utf-8",
    ) as file:
        file.write(rendered_page)


def generate_settlement_page(sim: Simulation, gameobject: GameObject) -> None:
    """Generate a page for a settlement."""
    settlement = gameobject.get_component(Settlement)
    settlement_name: str = gameobject.name
    population: int = settlement.population
    districts: list[tuple[str, str]] = []

    for district in settlement.districts:
        districts.append((district.name, f"../gameobjects/{district.uid}.html"))

    template = JINJA_ENV.get_template("settlement.jinja")
    rendered_page = template.render(
        settlement_name=settlement_name,
        population=population,
        districts=districts,
    )

    with open(
        OUTPUT_DIR / "gameobjects" / f"{gameobject.uid}.html",
        "w",
        encoding="utf-8",
    ) as file:
        file.write(rendered_page)


def generate_home_page(sim: Simulation) -> None:
    """Generate the homepage (index.html)."""

    settlements: list[tuple[str, str]] = []
    districts: list[tuple[str, str]] = []
    businesses: list[tuple[str, str]] = []
    characters: list[tuple[str, str]] = []

    # Extract the core GameObjects into the lists

    for entry in sim.world.gameobjects.gameobjects:
        if entry.has_component(Settlement):
            settlements.append((entry.name, f"/gameobjects/{entry.uid}.html"))
            continue

        if entry.has_component(District):
            districts.append((entry.name, f"/gameobjects/{entry.uid}.html"))
            continue

        if entry.has_component(Business):
            is_active = entry.is_active
            businesses.append(
                (
                    f"{entry.name}{' (inactive)' if not is_active else ''}",
                    f"/gameobjects/{entry.uid}.html",
                )
            )
            continue

        if entry.has_component(Character):
            is_active = entry.is_active
            characters.append(
                (
                    f"{entry.name}{' (inactive)' if not is_active else ''}",
                    f"/gameobjects/{entry.uid}.html",
                )
            )
            continue

    template = JINJA_ENV.get_template("index.jinja")
    rendered_page = template.render(
        settlements=settlements,
        districts=districts,
        businesses=businesses,
        characters=characters,
    )

    with open(OUTPUT_DIR / "index.html", "w", encoding="utf-8") as file:
        file.write(rendered_page)


def main() -> None:
    """The main entry point."""
    args = get_args()

    sim = Simulation(
        SimulationConfig(
            seed=args.seed,
            logging=LoggingConfig(
                logging_enabled=not bool(args.disable_logging),
                log_level="DEBUG",
                log_to_terminal=False,
            ),
        )
    )

    default_content.load_plugin(sim)
    sim.run_for(args.years)

    # Create the output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "gameobjects").mkdir(parents=True, exist_ok=True)

    # Loop through the gameobjects
    for gameobject in sim.world.gameobjects.gameobjects:
        if gameobject.has_component(Settlement):
            generate_settlement_page(sim, gameobject)

        elif gameobject.has_component(District):
           generate_district_page(sim, gameobject)

        elif gameobject.has_component(Character):
            generate_character_page(sim, gameobject)

        elif gameobject.has_component(Business):
           generate_business_page(sim, gameobject)

    # Create the home page
    generate_home_page(sim)


if __name__ == "__main__":
    main()
