from itertools import zip_longest

import os
import json
import zipfile
import requests


class Item(dict):
	"""
	Represents a Minecraft item with its properties, inheriting from dict.
	"""

	def __init__(self, name: str, namespace_id: str, stackability: int, obtainable: bool, cost: int = 1):
		"""
		Initializes a new Item instance.

		Args:
			name: The name of the item.
			namespace_id: The namespace ID of the item.
			stackability: The stackability of the item.
			obtainable: Whether the item is obtainable in survival mode.
		"""
		super().__init__(
			name=name,
			namespace_id=namespace_id,
			stackability=stackability,
			obtainable=obtainable,
			cost=cost)
		self.name = name
		self.namespace_id = namespace_id
		self.id = namespace_id.split(":")[-1]
		self.stackability = stackability
		self.obtainable = obtainable
		self.cost = cost

	def __str__(self):
		return f"Item(name='{self['name']}', namespace_id='{self['namespace_id']}', stackability={self['stackability']}, obtainable={self['obtainable']}, cost={self['cost']})"


def get_minecraft_items(url) -> dict[str, Item]:
	"""
	Fetches Minecraft item IDs from the given URL and returns them as a dictionary.

	Args:
		url: The URL to scrape the item IDs from.

	Returns:
		A set of Minecraft item IDs.
	"""
	response = requests.get(url, timeout=10)
	response.raise_for_status()  # Raise an exception for bad status codes

	data = json.loads(response.text)
	key_list = data["key_list"]
	item_ids = data["properties"]["id"]["entries"]
	item_stackability = data["properties"]["stackability"]["entries"]
	survival_obtainable = data["properties"]["survival_obtainable"]["entries"]
	items = {}
	for item in key_list:
		# items[item] = {
		# 	"namespace_id": "minecraft:"+ item_ids[item],
		# 	"stackability": 1 if item_stackability[item] == "Unstackable" else item_stackability[item],
		# 	"obtainable": survival_obtainable.get(item) != "No"
		# }
		items[item] = Item(
			item,
			"minecraft:"+ item_ids[item],
			1 if item_stackability[item] == "Unstackable" else item_stackability[item],
			survival_obtainable.get(item) != "No")

	return items

def is_valid_fuzzy(string: str, *dictionaries: dict):
	for dictionary in dictionaries:
		for values in dictionary.values():
			for value in values:
				if value in string:
					return True
	return False

def is_valid(string: str, *dictionaries: dict):
	for dictionary in dictionaries:
		for values in dictionary.values():
			if string in values:
				return True
	return False

def filter_items(items: dict[str, Item]) -> dict[str, Item]:
	"""
	Removes blacklisted items from the given dictionary of Minecraft items.

	Args:
		items: A dictionary of Minecraft items.

	Returns:
		A dictionary of Minecraft items with the blacklisted items removed.
	"""
	blacklist = [
		"bedrock", "potato", "poisonous_potato", "lava", "water", "air",
		"farmland", "tipped_arrow", "bow", "trident", "crossbow",
		"elytra", "shield", "dead_bush", "end_portal_frame",
		"turtle_egg", "flint_and_steel", "saddle", "dragon_egg",
		"fishing_rod", "shears", "command_block", "spectral_arrow",
		"barrier", "debug_stick", "structure_block", "ancient_debris",
		"firework_rocket", "firework_star"
	]
	blacklist_fuzzy = [
		"netherite", "music_disc", "potion", "_helmet",
		"_chestplate", "_sword", "_pickaxe", "_leggings", "_hoe", "_axe",
		"_horse_armor", "head", "map", "shovel", "boots", "_book", "bed",
		"stew", "soup", "pattern", "_bucket", "_minecart", "_a_stick",
		"_anvil", "gold", "boat", "shulker_box", "bell", "void", "command",
		"skull"
	]
	whitelist_fuzzy = [
		"apple", "carrot", "iron_nugget", "raw_iron"
	]
	item_counts = {
		32: [
			"emerald"
		]
	}
	item_costs_fuzzy = {
		64: [
			"spawner"
		],
		32: [
			"_spawn_egg"
		]
	}
	item_counts_fuzzy = {
		16: [
			"ender_pearl", "snowball", "bucket", "honey_bottle",
			"_banner", "_sign", "beacon", "nether_star", "end_crystal",
			"armor_stand", "redstone_block", "iron_block", "ender_chest",
			"_ore", "name_tag", "phantom_membrane", "respawn_anchor",
			"wither_rose"
		],
		8: [
			"conduit", "lapis_block", "emerald_block", "diamond_block",
			"sea_pickle", "experience_bottle", "lodestone"
		],
		3: [
			"emerald_block"
		],
		2: [item for items in item_costs_fuzzy.values() for item in items] + [
			"totem_of_undying"
		]
	}

	for item_name, item_data in items.copy().items():
		def log(status, reason): print(f"{status}: '{item_name} ({item_data.id})' reason: '{reason}'")
		if item_data.id not in blacklist \
			and not is_valid_fuzzy(item_data.id, {None:blacklist_fuzzy}) \
			and (is_valid(item_data.id, item_counts) \
			or is_valid_fuzzy(
					item_data.id,
					item_counts_fuzzy,
					item_costs_fuzzy,
					{None:whitelist_fuzzy})):
			for item_cost, _items in item_costs_fuzzy.items():
				for _item in _items:
					if _item in item_data.id:
						items[item_name]["cost"] = item_cost
						break
			for item_count, _items in item_counts.items():
				if item_data.id in _items:
					items[item_name]["stackability"] = item_count
					break
			for item_count, _items in item_counts_fuzzy.items():
				for _item in _items:
					if _item in item_data.id:
						items[item_name]["stackability"] = item_count
						break
			continue
		for banned_item, banned_item_fuzzy in zip_longest(blacklist, blacklist_fuzzy):
			if item_data.stackability == 1:
				log("Banned (unstackable)", "unstackable")
				items.pop(item_name)
				break
			if not item_data.obtainable:
				log("Banned (unobtainable)", "unobtainable")
				items.pop(item_name)
				break
			if item_data.id == banned_item:
				log("Banned (blacklist)", banned_item)
				items.pop(item_name)
				break
			if banned_item_fuzzy in item_data.id:
				log("Banned (blacklist_fuzzy)", banned_item_fuzzy)
				items.pop(item_name)
				break
	return items

def create_folder(folder_name: str):
	if not os.path.isdir(folder_name):
		os.makedirs(folder_name)

def zip_folder(folder_path, zip_path):
    """Zips the contents of a folder into a zip file."""

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)

def write_item_to_json_file(item: Item, path: str = "."):
	filename = item.id +".json"
	path = os.path.join(path, filename)
	print(path)
	data = {
		"type": "crafting_shapeless",
		"ingredients": [
			{
				"item": item.namespace_id
			},
			{
				"item": "minecraft:poisonous_potato",
				"count": item.cost
			}
		],
		"result": {
			"item": item.namespace_id,
			"count": item.stackability
		},
		"group": "potato_duplication"
	}

	with open(path, "w", encoding="utf8") as file:
		json.dump(data, file, indent=4)


def main():
	url = "https://joakimthorsen.github.io/MCPropertyEncyclopedia/data/item_data.json"
	minecraft_items = get_minecraft_items(url)
	filtered_items = filter_items(minecraft_items.copy())
	# print(minecraft_items)
	print(len(minecraft_items))
	print(len(filtered_items))
	# print("\n".join(list(f"Banned: {item}" for item in minecraft_items.keys() - filtered_items.keys())))
	# print("\n".join(item.id for _, item in filtered_items.items()))
	print(filtered_items["Emerald"])
	print(filtered_items["Ender Pearl"])
	print(filtered_items["Beacon"])
	print(filtered_items["Block of Emerald"])
	print(filtered_items["Warden Spawn Egg"])
	print(filtered_items["Sponge"])
	folder = "dump/data/minecraft/recipe/potato_duplication"
	create_folder(folder)
	write_item_to_json_file(filtered_items["Sponge"], folder)
	zip_folder(folder.split("/", maxsplit=1)[0], "potato_duping_datapack_v2.zip")


if __name__ == "__main__":
	main()
