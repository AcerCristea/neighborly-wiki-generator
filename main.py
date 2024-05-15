"""Neighborly Wiki Generator

Generates an HTML wiki for generated Neighborly worlds.

"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
from typing import Any

import jinja2

TEMPLATES_DIR = pathlib.Path(__file__).parent / "templates"
"""The path to the directory containing the Jinja templates."""

OUTPUT_DIR = pathlib.Path(os.getcwd()) / "output"
"""The path to the output directory."""

FILE_LOADER = jinja2.FileSystemLoader(TEMPLATES_DIR)
"""Reference to Jinja's file loader."""

JINJA_ENV = jinja2.Environment(loader=FILE_LOADER)
"""Reference to the Jinja environment instance."""


def get_commandline_args() -> argparse.Namespace:
    """Parse the commandline arguments."""

    parser = argparse.ArgumentParser(
        "Simulation Wiki Generator",
        description="Generate wiki HTML pages using exported simulation JSON data.",
    )

    parser.add_argument(
        "source",
        type=pathlib.Path,
        help="The path to the JSON file containing simulation data.",
    )

    return parser.parse_args()


def generate_trait_page(sim: dict[str, Any], gameobject: dict[str, Any]) -> None:
    """Generate a page for a residential building."""
    raise NotImplementedError()


def generate_residence_page(sim: dict[str, Any], gameobject: dict[str, Any]) -> None:
    """Generate a page for a residential building."""

    residence_name: str = gameobject["name"]
    activity_status = "Active" if "Active" in gameobject["components"] else "Inactive"

    # Get district info
    district_id: int = gameobject["components"]["ResidentialBuilding"]["district"]
    district_name: str = sim["gameobjects"][str(district_id)]["name"]
    district: tuple[str, str] = (
        district_name,
        f"../gameobjects/{district_id}.html",
    )

    # Get trait info
    traits: list[dict[str, Any]] = []
    for trait_id in gameobject["components"]["Traits"]["traits"]:
        trait = sim["gameobjects"][str(trait_id)]["components"]["Trait"]
        trait_name = trait["display_name"]
        trait_description = trait["description"]
        traits.append({"name": trait_name, "description": trait_description})

    # Get resident info
    units: list[dict[str, Any]] = []
    for unit_id in gameobject["components"]["ResidentialBuilding"]["units"]:
        unit = sim["gameobjects"][str(unit_id)]

        residents: list[tuple[str, str]] = []

        for resident_id in unit["components"]["Residence"]["residents"]:
            resident = sim["gameobjects"][str(resident_id)]
            residents.append((resident["name"], f"../gameobjects/{resident_id}.html"))

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


def generate_business_page(sim: dict[str, Any], gameobject: dict[str, Any]) -> None:
    """Generate a page for a business."""

    business_name: str = gameobject["name"]

    # Get activity status
    activity_status = "Active" if "Active" in gameobject["components"] else "Inactive"

    # Get district information
    district_id: int = gameobject["components"]["Business"]["district"]
    district: dict[str, Any] = sim["gameobjects"][str(district_id)]
    district_name: str = district["name"]
    district_link: str = f"../gameobjects/{district_id}.html"

    # Get business owner information
    # district_id: int = entry["components"]["Business"]["district"]
    owner_name: str = "TBD"
    owner_link: str = "#"

    # Frequented by
    frequented_by: list[dict[str, Any]] = []

    # Get trait info
    traits: list[dict[str, Any]] = []
    for trait_id in gameobject["components"]["Traits"]["traits"]:
        trait = sim["gameobjects"][str(trait_id)]["components"]["Trait"]
        trait_name = trait["display_name"]
        trait_description = trait["description"]
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
        OUTPUT_DIR / "gameobjects" / f"{gameobject['id']}.html",
        "w",
        encoding="utf-8",
    ) as file:
        file.write(rendered_page)


def generate_character_page(sim: dict[str, Any], gameobject: dict[str, Any]) -> None:
    """Generate a page for a character."""

    character_name = gameobject["name"]

    # Get activity status
    activity_status = "Active" if "Active" in gameobject["components"] else "Inactive"

    age = gameobject["components"]["Character"]["age"]
    sex = gameobject["components"]["Character"]["sex"]
    life_stage = gameobject["components"]["Character"]["life_stage"]
    species = gameobject["components"]["Character"]["species"]

    residence_name = "N/A"
    residence_link = "#"
    if resident_data := gameobject["components"].get("Resident"):
        residence_id: int = resident_data["residence"]
        building_id: int = sim["gameobjects"][str(residence_id)]["parent"]
        residence_name = sim["gameobjects"][str(building_id)]["name"]
        residence_link = f"../gameobjects/{building_id}.html"

    occupation_name = "N/A"
    occupation_link = "#"
    if occupation_data := gameobject["components"].get("Occupation"):
        business_id: int = occupation_data["business"]
        occupation_name = sim["gameobjects"][str(business_id)]["name"]
        occupation_link = f"../gameobjects/{business_id}.html"

    # Get trait info
    traits: list[dict[str, Any]] = []
    for trait_id in gameobject["components"]["Traits"]["traits"]:
        trait = sim["gameobjects"][str(trait_id)]["components"]["Trait"]
        trait_name = trait["display_name"]
        trait_description = trait["description"]
        traits.append({"name": trait_name, "description": trait_description})

    # Get skill info
    skills: list[dict[str, Any]] = []
    for skill_id, skill_level in gameobject["components"]["Skills"].items():
        skill = sim["gameobjects"][str(skill_id)]["components"]["Skill"]
        skill_name = skill["display_name"]
        skill_description = skill["description"]
        skills.append(
            {"name": skill_name, "level": skill_level, "description": skill_description}
        )

    # Frequented locations
    frequented_locations: list[dict[str, Any]] = []
    for location_id in gameobject["components"]["FrequentedLocations"]["locations"]:
        location = sim["gameobjects"][str(location_id)]
        frequented_locations.append(
            {"name": location["name"], "link": f"../gameobjects/{location_id}.html"}
        )

    # Get relationship data
    relationships: list[dict[str, Any]] = []
    outgoing_relationship_data = gameobject["components"]["Relationships"]["outgoing"]
    for target_id_str, relationship_id in outgoing_relationship_data.items():
        target = sim["gameobjects"][target_id_str]
        relationship = sim["gameobjects"][str(relationship_id)]

        relationship_traits: list[dict[str, Any]] = []
        for trait_id in relationship["components"]["Traits"]["traits"]:
            trait = sim["gameobjects"][str(trait_id)]["components"]["Trait"]
            trait_name = trait["display_name"]
            trait_description = trait["description"]
            relationship_traits.append(
                {"name": trait_name, "description": trait_description}
            )

        relationships.append(
            {
                "target_name": target["name"],
                "target_link": f"../gameobjects/{target_id_str}.html",
                "reputation": relationship["components"]["Stats"]["reputation"],
                "romance": relationship["components"]["Stats"]["romance"],
                "compatibility": relationship["components"]["Stats"]["compatibility"],
                "romantic_compatibility": relationship["components"]["Stats"][
                    "romantic_compatibility"
                ],
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
        residence_link=residence_link,
        residence_name=residence_name,
        occupation_link=occupation_link,
        occupation_name=occupation_name,
        frequented_locations=frequented_locations,
        traits=traits,
        skills=skills,
        relationships=relationships,
        events=events,
    )

    with open(
        OUTPUT_DIR / "gameobjects" / f"{gameobject['id']}.html",
        "w",
        encoding="utf-8",
    ) as file:
        file.write(rendered_page)


def generate_skill_page(sim: dict[str, Any], gameobject: dict[str, Any]) -> None:
    """Generate a page for a skill."""
    raise NotImplementedError()


def generate_district_page(sim: dict[str, Any], gameobject: dict[str, Any]) -> None:
    """Generate a page for a district."""

    district_name: str = gameobject["name"]
    population: int = gameobject["components"]["District"].get("population", -1)
    description: str = gameobject["components"]["District"].get("description", "N/A")

    settlement_id: int = gameobject["components"]["District"]["settlement"]
    settlement_name: str = sim["gameobjects"][str(settlement_id)]["name"]
    settlement: tuple[str, str] = (
        settlement_name,
        f"../gameobjects/{settlement_id}.html",
    )

    residence_ids: list[int] = gameobject["components"]["District"]["residences"]
    residents: list[tuple[str, str]] = []
    residences: list[tuple[str, str]] = []
    for residence_id in residence_ids:
        residence = sim["gameobjects"][str(residence_id)]
        residences.append((residence["name"], f"../gameobjects/{residence_id}.html"))

        # Loop through the residential units to get residents
        unit_ids: list[int] = residence["components"]["ResidentialBuilding"]["units"]
        for unit_id in unit_ids:
            unit = sim["gameobjects"][str(unit_id)]["components"]["Residence"]
            for resident_id in unit["residents"]:
                resident = sim["gameobjects"][str(resident_id)]
                residents.append(
                    (resident["name"], f"../gameobjects/{resident_id}.html")
                )

    business_ids: list[int] = gameobject["components"]["District"]["businesses"]
    businesses: list[tuple[str, str]] = []
    for business_id in business_ids:
        business = sim["gameobjects"][str(business_id)]
        businesses.append((business["name"], f"../gameobjects/{business_id}.html"))

    template = JINJA_ENV.get_template("district.jinja")
    rendered_page = template.render(
        district_name=district_name,
        population=population,
        description=description,
        settlement_name=settlement_name,
        residences=residences,
        businesses=businesses,
        residents=residents,
        settlement=settlement,
    )

    with open(
        OUTPUT_DIR / "gameobjects" / f"{gameobject['id']}.html",
        "w",
        encoding="utf-8",
    ) as file:
        file.write(rendered_page)


def generate_settlement_page(sim: dict[str, Any], gameobject: dict[str, Any]) -> None:
    """Generate a page for a settlement."""

    settlement_name: str = gameobject["name"]
    population: int = gameobject["components"]["Settlement"].get("population", -1)
    description: str = gameobject["components"]["Settlement"].get("description", "N/A")
    districts: list[tuple[str, str]] = []

    for district_id in gameobject["components"]["Settlement"]["districts"]:
        district_name = sim["gameobjects"][str(district_id)]["name"]
        districts.append((district_name, f"../gameobjects/{district_id}.html"))

    template = JINJA_ENV.get_template("settlement.jinja")
    rendered_page = template.render(
        settlement_name=settlement_name,
        population=population,
        description=description,
        districts=districts,
    )

    with open(
        OUTPUT_DIR / "gameobjects" / f"{gameobject['id']}.html",
        "w",
        encoding="utf-8",
    ) as file:
        file.write(rendered_page)


def generate_home_page(sim: dict[str, Any]) -> None:
    """Generate the homepage (index.html)."""

    settlements: list[tuple[str, str]] = []
    districts: list[tuple[str, str]] = []
    businesses: list[tuple[str, str]] = []
    characters: list[tuple[str, str]] = []

    # Extract the core GameObjects into the lists

    for _, entry in sim["gameobjects"].items():
        if "Settlement" in entry["components"]:
            settlements.append((entry["name"], f"/gameobjects/{entry['id']}.html"))
            continue

        if "District" in entry["components"]:
            districts.append((entry["name"], f"/gameobjects/{entry['id']}.html"))
            continue

        if "Business" in entry["components"]:
            is_active = "Active" in entry["components"]
            businesses.append(
                (
                    f"{entry['name']}{' (inactive)' if not is_active else ''}",
                    f"/gameobjects/{entry['id']}.html",
                )
            )
            continue

        if "Character" in entry["components"]:
            is_active = "Active" in entry["components"]
            characters.append(
                (
                    f"{entry['name']}{' (inactive)' if not is_active else ''}",
                    f"/gameobjects/{entry['id']}.html",
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
    args = get_commandline_args()

    # load the source json
    with open(args.source, "r", encoding="utf-8") as file:
        sim: dict[str, Any] = json.load(file)

    gameobjects: dict[str, dict[str, Any]] = sim["gameobjects"]

    # Create the output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "gameobjects").mkdir(parents=True, exist_ok=True)

    # Loop through the gameobjects
    for _, gameobject in gameobjects.items():
        if "Settlement" in gameobject["components"]:
            generate_settlement_page(sim, gameobject)

        elif "District" in gameobject["components"]:
            generate_district_page(sim, gameobject)

        elif "Character" in gameobject["components"]:
            generate_character_page(sim, gameobject)

        elif "Business" in gameobject["components"]:
            generate_business_page(sim, gameobject)

        elif "ResidentialBuilding" in gameobject["components"]:
            generate_residence_page(sim, gameobject)

    # Create the home page
    generate_home_page(sim)


if __name__ == "__main__":
    main()
