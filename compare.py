import argparse
import datetime
import json
import re
from collections import Counter
from enum import Enum
from pathlib import Path

import pandas as pd
from rich.console import Console

console = Console(highlight=False)


class CorruptionResult(Enum):
    NOT_CORRUPTED = 0
    NO_EFFECT = 1
    REROLLED_MODS = 2
    EIGHT_MOD = 3
    VAAL_IMPLICIT = 4
    VAAL_TEMPLE = 5
    TIER_CHANGE = 6

    def __str__(self):
        match self:
            case self.NOT_CORRUPTED:
                return "[bold red]Not corrupted![/]"
            case self.NO_EFFECT:
                return "[bold]No effect[/]"
            case self.REROLLED_MODS:
                return "[bold blue]Rerolled mods[/]"
            case self.EIGHT_MOD:
                return "[bold yellow]8 explicit mods[/]"
            case self.VAAL_IMPLICIT:
                return "[bold magenta]Vaal implicit[/]"
            case self.VAAL_TEMPLE:
                return "[bold red]Vaal temple[/]"
            case self.TIER_CHANGE:
                return "[bold cyan]Tier change[/]"
            case _:
                return "N/A"

    def fmt(self) -> str:
        match self:
            case self.NOT_CORRUPTED:
                return "Not corrupted"
            case self.NO_EFFECT:
                return "No effect"
            case self.REROLLED_MODS:
                return "Rerolled mods"
            case self.EIGHT_MOD:
                return "8 affixes"
            case self.VAAL_IMPLICIT:
                return "Vaal implicit"
            case self.VAAL_TEMPLE:
                return "Vaal temple map"
            case self.TIER_CHANGE:
                return "Tier change"
            case _:
                return "N/A"


def count_affixes(item):
    explicit_mods = item.get("explicitMods", []).copy()
    affix_cnt = 0

    def has_affix(mods, affix_part):
        return any(
            affix_part.lower() in mod.lower()
            or re.search(affix_part, mod, re.IGNORECASE)
            for mod in mods
        )

    def remove_affix(mods, affix_part):
        for mod in mods[:]:
            if affix_part.lower() in mod.lower() or re.search(
                affix_part, mod, re.IGNORECASE
            ):
                mods.remove(mod)

    if has_affix(explicit_mods, "Monsters cannot be Stunned"):
        remove_affix(explicit_mods, "Monsters cannot be Stunned")
        remove_affix(explicit_mods, "more Monster Life")
        affix_cnt += 1

    if has_affix(explicit_mods, "more Monster Life"):
        remove_affix(explicit_mods, "more Monster Life")
        affix_cnt += 1

    if has_affix(explicit_mods, "increased Accuracy Rating"):
        remove_affix(explicit_mods, "increased Accuracy Rating")
        remove_affix(explicit_mods, "to amount of Suppressed Spell Damage Prevented")
        affix_cnt += 1

    if has_affix(explicit_mods, "less Area of Effect"):
        remove_affix(explicit_mods, "less Area of Effect")
        affix_cnt += 1

    if has_affix(explicit_mods, "of Maximum Life as Extra Maximum Energy Shield"):
        remove_affix(explicit_mods, "of Maximum Life as Extra Maximum Energy Shield")
        affix_cnt += 1

    if has_affix(explicit_mods, "less Cooldown Recovery Rate"):
        remove_affix(explicit_mods, "less Cooldown Recovery Rate")
        affix_cnt += 1

    if has_affix(explicit_mods, "less Armour"):
        remove_affix(explicit_mods, "less Armour")
        remove_affix(explicit_mods, "reduced Chance to Block")
        affix_cnt += 1

    if has_affix(explicit_mods, "increased Monster Damage"):
        remove_affix(explicit_mods, "increased Monster Damage")
        affix_cnt += 1

    if has_affix(explicit_mods, "All Monster Damage from Hits always Ignites"):
        remove_affix(explicit_mods, "All Monster Damage from Hits always Ignites")
        affix_cnt += 1

    if has_affix(explicit_mods, "less Accuracy Rating"):
        remove_affix(explicit_mods, "less Accuracy Rating")
        affix_cnt += 1

    if has_affix(explicit_mods, "Area contains many Totems"):
        remove_affix(explicit_mods, "Area contains many Totems")
        affix_cnt += 1

    if has_affix(explicit_mods, "more Magic Monsters"):
        remove_affix(explicit_mods, "more Magic Monsters")
        affix_cnt += 1

    if has_affix(explicit_mods, "Monsters Poison on Hit"):
        remove_affix(explicit_mods, "Monsters Poison on Hit")
        affix_cnt += 1

    if has_affix(explicit_mods, "Monsters are Hexproof"):
        remove_affix(explicit_mods, "Monsters are Hexproof")
        affix_cnt += 1

    if has_affix(explicit_mods, "extra Physical Damage as Fire"):
        remove_affix(explicit_mods, "extra Physical Damage as Fire")
        affix_cnt += 1

    if has_affix(explicit_mods, "extra Physical Damage as Lightning"):
        remove_affix(explicit_mods, "extra Physical Damage as Lightning")
        affix_cnt += 1

    if has_affix(explicit_mods, "reduced Extra Damage from Critical Strikes"):
        remove_affix(explicit_mods, "reduced Extra Damage from Critical Strikes")
        affix_cnt += 1

    if has_affix(explicit_mods, "Monsters Blind on Hit"):
        remove_affix(explicit_mods, "Monsters Blind on Hit")
        affix_cnt += 1

    if has_affix(explicit_mods, "Players are Cursed with Vulnerability"):
        remove_affix(explicit_mods, "Players are Cursed with Vulnerability")
        affix_cnt += 1

    if has_affix(explicit_mods, "less effect of Curses on Monsters"):
        remove_affix(explicit_mods, "less effect of Curses on Monsters")
        affix_cnt += 1

    if has_affix(explicit_mods, "Unique Bosses are Possessed"):
        remove_affix(explicit_mods, "Unique Bosses are Possessed")
        affix_cnt += 1

    if has_affix(explicit_mods, "Players are Cursed with Elemental Weakness"):
        remove_affix(explicit_mods, "Players are Cursed with Elemental Weakness")
        affix_cnt += 1

    if has_affix(explicit_mods, "increased Monster Movement Speed"):
        remove_affix(explicit_mods, "increased Monster Movement Speed")
        remove_affix(explicit_mods, "increased Monster Attack Speed")
        remove_affix(explicit_mods, "increased Monster Cast Speed")
        affix_cnt += 1

    if has_affix(
        explicit_mods, "Monsters steal Power, Frenzy and Endurance charges on Hit"
    ):
        remove_affix(
            explicit_mods, "Monsters steal Power, Frenzy and Endurance charges on Hit"
        )
        affix_cnt += 1

    if has_affix(explicit_mods, "to all maximum Resistances"):
        remove_affix(explicit_mods, "to all maximum Resistances")
        affix_cnt += 1

    if has_affix(explicit_mods, "Area has patches of Chilled Ground"):
        remove_affix(explicit_mods, "Area has patches of Chilled Ground")
        affix_cnt += 1

    if has_affix(
        explicit_mods, "Monsters' Action Speed cannot be modified to below Base Value"
    ):
        remove_affix(
            explicit_mods,
            "Monsters' Action Speed cannot be modified to below Base Value",
        )
        remove_affix(explicit_mods, "Monsters cannot be Taunted")
        remove_affix(
            explicit_mods,
            "Monsters' Movement Speed cannot be modified to below Base Value",
        )
        affix_cnt += 1

    if has_affix(explicit_mods, "chance to Suppress Spell Damage"):
        remove_affix(explicit_mods, "chance to Suppress Spell Damage")
        affix_cnt += 1

    if has_affix(explicit_mods, "Monsters Hinder on Hit with Spells"):
        remove_affix(explicit_mods, "Monsters Hinder on Hit with Spells")
        affix_cnt += 1

    if has_affix(explicit_mods, "reduced Flask Charges"):
        remove_affix(explicit_mods, "reduced Flask Charges")
        affix_cnt += 1

    if has_affix(explicit_mods, "less Recovery Rate of Life and Energy Shield"):
        remove_affix(explicit_mods, "less Recovery Rate of Life and Energy Shield")
        affix_cnt += 1

    if has_affix(explicit_mods, "chance to Impale on Hit"):
        remove_affix(explicit_mods, "chance to Impale on Hit")
        affix_cnt += 1

    if has_affix(explicit_mods, "Monsters gain an Endurance Charge on Hit"):
        remove_affix(explicit_mods, "Monsters gain an Endurance Charge on Hit")
        affix_cnt += 1

    if has_affix(explicit_mods, "Players are Cursed with Enfeeble"):
        remove_affix(explicit_mods, "Players are Cursed with Enfeeble")
        affix_cnt += 1

    if has_affix(explicit_mods, "extra Physical Damage as Cold"):
        remove_affix(explicit_mods, "extra Physical Damage as Cold")
        affix_cnt += 1

    if has_affix(explicit_mods, "Monster Elemental Resistances"):
        remove_affix(explicit_mods, "Monster Elemental Resistances")
        remove_affix(explicit_mods, "Monster Chaos Resistance")
        affix_cnt += 1

    if has_affix(explicit_mods, "increased Critical Strike Chance"):
        remove_affix(explicit_mods, "increased Critical Strike Chance")
        remove_affix(explicit_mods, "to Monster Critical Strike Multiplier")
        affix_cnt += 1

    if has_affix(explicit_mods, "Area is inhabited by Abominations"):
        remove_affix(explicit_mods, "Area is inhabited by Abominations")
        affix_cnt += 1

    if has_affix(explicit_mods, "Monsters gain a Power Charge on Hit"):
        remove_affix(explicit_mods, "Monsters gain a Power Charge on Hit")
        affix_cnt += 1

    if has_affix(explicit_mods, "Monsters gain a Frenzy Charge on Hit"):
        remove_affix(explicit_mods, "Monsters gain a Frenzy Charge on Hit")
        affix_cnt += 1

    if has_affix(explicit_mods, "increased number of Rare Monsters"):
        remove_affix(explicit_mods, "increased number of Rare Monsters")
        affix_cnt += 1

    if has_affix(explicit_mods, "reduced effect of Non-Curse Auras from Skills"):
        remove_affix(explicit_mods, "reduced effect of Non-Curse Auras from Skills")
        affix_cnt += 1

    if has_affix(explicit_mods, "chance to Ignite, Freeze and Shock on Hit"):
        remove_affix(explicit_mods, "chance to Ignite, Freeze and Shock on Hit")
        affix_cnt += 1

    if has_affix(explicit_mods, "Area has patches of desecrated ground"):
        remove_affix(explicit_mods, "Area has patches of desecrated ground")
        affix_cnt += 1

    if has_affix(explicit_mods, "Players cannot inflict Exposure"):
        remove_affix(explicit_mods, "Players cannot inflict Exposure")
        affix_cnt += 1

    if has_affix(explicit_mods, "of Elemental Damage"):
        remove_affix(explicit_mods, "of Elemental Damage")
        affix_cnt += 1

    if has_affix(explicit_mods, "Monsters cannot be Leeched from"):
        remove_affix(explicit_mods, "Monsters cannot be Leeched from")
        affix_cnt += 1

    if has_affix(explicit_mods, "Area is inhabited by Humanoids"):
        remove_affix(explicit_mods, "Area is inhabited by Humanoids")
        affix_cnt += 1

    if has_affix(explicit_mods, "Area contains two Unique Bosses"):
        remove_affix(explicit_mods, "Area contains two Unique Bosses")
        affix_cnt += 1

    if has_affix(explicit_mods, "Monsters fire 2 additional Projectiles"):
        remove_affix(explicit_mods, "Monsters fire 2 additional Projectiles")
        affix_cnt += 1

    if has_affix(explicit_mods, "Monsters Maim on Hit with Attacks"):
        remove_affix(explicit_mods, "Monsters Maim on Hit with Attacks")
        affix_cnt += 1

    if has_affix(explicit_mods, "Area is inhabited by Demons"):
        remove_affix(explicit_mods, "Area is inhabited by Demons")
        affix_cnt += 1

    if has_affix(explicit_mods, "Area is inhabited by Animals"):
        remove_affix(explicit_mods, "Area is inhabited by Animals")
        affix_cnt += 1

    if has_affix(explicit_mods, "chance to Avoid Elemental Ailments"):
        remove_affix(explicit_mods, "chance to Avoid Elemental Ailments")
        affix_cnt += 1

    if has_affix(explicit_mods, "Buffs on Players expire"):
        remove_affix(explicit_mods, "Buffs on Players expire")
        affix_cnt += 1

    if has_affix(explicit_mods, "Players are Cursed with Temporal Chains"):
        remove_affix(explicit_mods, "Players are Cursed with Temporal Chains")
        affix_cnt += 1

    if has_affix(explicit_mods, "chance to avoid Poison, Impale, and Bleeding"):
        remove_affix(explicit_mods, "chance to avoid Poison, Impale, and Bleeding")
        affix_cnt += 1

    if has_affix(explicit_mods, "Monsters' skills Chain 2 additional times"):
        remove_affix(explicit_mods, "Monsters' skills Chain 2 additional times")
        affix_cnt += 1

    if has_affix(explicit_mods, "Area has increased monster variety"):
        remove_affix(explicit_mods, "Area has increased monster variety")
        affix_cnt += 1

    if has_affix(explicit_mods, "Area has patches of Burning Ground"):
        remove_affix(explicit_mods, "Area has patches of Burning Ground")
        affix_cnt += 1

    if has_affix(explicit_mods, "Monster Physical Damage Reduction"):
        remove_affix(explicit_mods, "Monster Physical Damage Reduction")
        affix_cnt += 1

    if has_affix(explicit_mods, "Area is inhabited by Sea Witches and their Spawn"):
        remove_affix(explicit_mods, "Area is inhabited by Sea Witches and their Spawn")
        affix_cnt += 1

    if has_affix(explicit_mods, "Area is inhabited by Cultists of Kitava"):
        remove_affix(explicit_mods, "Area is inhabited by Cultists of Kitava")
        affix_cnt += 1

    if has_affix(explicit_mods, "Area is inhabited by Solaris fanatics"):
        remove_affix(explicit_mods, "Area is inhabited by Solaris fanatics")
        affix_cnt += 1

    if has_affix(explicit_mods, "Area is inhabited by Goatmen"):
        remove_affix(explicit_mods, "Area is inhabited by Goatmen")
        affix_cnt += 1

    if has_affix(explicit_mods, "Area is inhabited by Lunaris fanatics"):
        remove_affix(explicit_mods, "Area is inhabited by Lunaris fanatics")
        affix_cnt += 1

    if has_affix(explicit_mods, "Area is inhabited by Skeletons"):
        remove_affix(explicit_mods, "Area is inhabited by Skeletons")
        affix_cnt += 1

    if has_affix(
        explicit_mods, "Players cannot Regenerate Life, Mana or Energy Shield"
    ):
        remove_affix(
            explicit_mods, "Players cannot Regenerate Life, Mana or Energy Shield"
        )
        affix_cnt += 1

    if has_affix(explicit_mods, "Area is inhabited by ranged monsters"):
        remove_affix(explicit_mods, "Area is inhabited by ranged monsters")
        affix_cnt += 1

    if has_affix(explicit_mods, "Area is inhabited by Ghosts"):
        remove_affix(explicit_mods, "Area is inhabited by Ghosts")
        affix_cnt += 1

    if has_affix(explicit_mods, "Area has patches of Consecrated Ground"):
        remove_affix(explicit_mods, "Area has patches of Consecrated Ground")
        affix_cnt += 1

    if has_affix(explicit_mods, "Area is inhabited by Undead"):
        remove_affix(explicit_mods, "Area is inhabited by Undead")
        affix_cnt += 1

    if has_affix(
        explicit_mods,
        "Area has patches of Shocked Ground which increase Damage taken by",
    ):
        remove_affix(
            explicit_mods,
            "Area has patches of Shocked Ground which increase Damage taken by",
        )
        affix_cnt += 1

    if has_affix(explicit_mods, r"Monsters have \d+% increased Area of Effect"):
        remove_affix(explicit_mods, r"Monsters have \d+% increased Area of Effect")
        affix_cnt += 1

    if has_affix(explicit_mods, r"Monsters reflect \d+% of Physical Damage"):
        remove_affix(explicit_mods, r"Monsters reflect \d+% of Physical Damage")
        affix_cnt += 1

    if has_affix(explicit_mods, r"Unique Boss has \d+% increased Life"):
        remove_affix(explicit_mods, r"Unique Boss has \d+% increased Life")
        remove_affix(explicit_mods, r"Unique Boss has \d+% increased Area of Effect")
        affix_cnt += 1

    if has_affix(explicit_mods, r"Unique Boss deals \d+% increased Damage"):
        remove_affix(explicit_mods, r"Unique Boss deals \d+% increased Damage")
        remove_affix(
            explicit_mods, r"Unique Boss has \d+% increased Attack and Cast Speed"
        )
        affix_cnt += 1

    if has_affix(
        explicit_mods,
        r"Monsters gain \d+% of their Physical Damage as Extra Chaos Damage",
    ):
        remove_affix(
            explicit_mods,
            r"Monsters gain \d+% of their Physical Damage as Extra Chaos Damage",
        )
        remove_affix(explicit_mods, r"Monsters Inflict Withered for \d+ seconds on Hit")
        affix_cnt += 1

    if len(explicit_mods) > 0:
        print(f"Remaining explicit mods: {explicit_mods}")

    return affix_cnt


def get_map_tier(item):
    for prop in item["properties"]:
        if prop["name"] == "Map Tier":
            return int(prop["values"][0][0])


def compare_items(before, after) -> CorruptionResult:
    if not after.get("corrupted", False):
        console.print(
            f"[bold red]Map not corrupted at position: {before['x']}, {before['y']}[/]"
        )
        return CorruptionResult.NOT_CORRUPTED

    if get_map_tier(before) != get_map_tier(after):
        return CorruptionResult.TIER_CHANGE

    if after["baseType"] == "Vaal Temple Map":
        return CorruptionResult.VAAL_TEMPLE

    if len(after.get("implicitMods", [])) > len(before.get("implicitMods", [])):
        return CorruptionResult.VAAL_IMPLICIT

    if before.get("explicitMods", []) == after.get("explicitMods", []):
        return CorruptionResult.NO_EFFECT

    if count_affixes(after) == 8:
        return CorruptionResult.EIGHT_MOD

    if before.get("explicitMods", []) != after.get("explicitMods", []):
        return CorruptionResult.REROLLED_MODS

    return CorruptionResult.NO_EFFECT


def print_result(pos: tuple[int, int], result: CorruptionResult, before, after):
    if after["name"]:
        console.print(
            f"{pos[0]:2d}, {pos[1]:2d}: [bold]{after['name']} - {after.get('baseType')}[/]"
        )
    else:
        console.print(f"{pos[0]:2d}, {pos[1]:2d}: [bold]{after.get('baseType')}[/]")

    console.print(f"    Result: {result}")

    if before.get("rarity") != after.get("rarity"):
        console.print(f"    Rarity: {before.get('rarity')} -> {after.get('rarity')}")

    if result in (CorruptionResult.EIGHT_MOD, CorruptionResult.REROLLED_MODS):
        console.print(f"    Mods: {count_affixes(after)}")

    console.print()


def compare_stashes(before, after):
    assert before["id"] == after["id"]

    items_before: dict[tuple[int, int], dict] = {}
    items_after: dict[tuple[int, int], dict] = {}

    for item in before["items"]:
        items_before[(item["x"], item["y"])] = item

    for item in after["items"]:
        items_after[(item["x"], item["y"])] = item

    nonempty_positions = set(pos for pos in sorted(items_before)) | set(
        pos for pos in sorted(items_after)
    )

    results = []

    for pos in sorted(nonempty_positions):
        item_before = items_before.get(pos, {})
        item_after = items_after.get(pos, {})

        result = compare_items(item_before, item_after)
        print_result(pos, result, item_before, item_after)

        results.append(result)

    df = pd.DataFrame(
        [(res.fmt(), cnt) for res, cnt in Counter(results).items()],
        columns=["Outcome", "Count"],
    ).set_index("Outcome")

    print(df)

    dt = datetime.datetime.now().strftime("%y%m%d%H%M%S")
    df.to_csv(f"outcomes-{dt}.csv")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("before")
    parser.add_argument("after")

    args = parser.parse_args()

    with Path(args.before).open() as f_before, Path(args.after).open() as f_after:
        stash_before = json.load(f_before)
        stash_after = json.load(f_after)

    compare_stashes(stash_before, stash_after)


if __name__ == "__main__":
    main()
