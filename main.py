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
		# self.name = name
		# self.namespace_id = namespace_id
		# self.id = namespace_id.split(":")[-1]
		# self.stackability = stackability
		# self.obtainable = obtainable
		# self.cost = cost

	def __str__(self):
		return f"Item(name='{self['name']}', namespace_id='{self['namespace_id']}', stackability={self['stackability']}, obtainable={self['obtainable']}, cost={self['cost']})"

	@property
	def stackability(self):
		return self["stackability"]

	@property
	def name(self):
		return self["name"]

	@property
	def namespace_id(self):
		return self["namespace_id"]

	@property
	def id(self):
		return self["namespace_id"].split(":")[-1]

	@property
	def obtainable(self):
		return self["obtainable"]

	@property
	def cost(self):
		return self["cost"]


def get_minecraft_items(url) -> dict[str, Item]:
	"""
	Fetches Minecraft item IDs from the given URL and returns them as a dictionary.

	Args:
		url: The URL to scrape the item IDs from.

	Returns:
		A set of Minecraft item IDs.
	"""
	# Fetch block data
	response = requests.get(url, timeout=10)
	response.raise_for_status()
	block_data = json.loads(response.text)

	# Fetch item data to get stackability and survival_obtainable properties
	item_url = "https://joakimthorsen.github.io/MCPropertyEncyclopedia/data/item_data.json"
	item_response = requests.get(item_url, timeout=10)
	item_response.raise_for_status()
	item_data = json.loads(item_response.text)

	item_ids = item_data["properties"]["id"]["entries"]
	item_stackability = item_data["properties"]["stackability"]["entries"]
	survival_obtainable = item_data["properties"]["survival_obtainable"]["entries"]

	# Build mapping of item namespace ID -> (stackability, obtainable)
	item_info = {}
	for item_name, raw_id in item_ids.items():
		ns_id = "minecraft:" + raw_id
		stack = item_stackability.get(item_name, 64)
		if stack == "Unstackable":
			stack = 1
		obt = survival_obtainable.get(item_name) != "No"
		item_info[ns_id] = (stack, obt)

	key_list = block_data["key_list"]
	block_ids = block_data["properties"]["block_id"]["entries"]
	items = {}
	for item in key_list:
		if item not in block_ids:
			continue

		namespace_id = block_ids[item]

		if namespace_id in item_info:
			stackability, obtainable = item_info[namespace_id]
		else:
			# Handle new blocks not present in the legacy item database
			stackability = 64
			obtainable = True
			lower_id = namespace_id.lower()
			if (
				"wall_" in lower_id
				or "potted_" in lower_id
				or ("stem" in lower_id and "crimson_stem" not in lower_id and "warped_stem" not in lower_id)
				or lower_id in [
					"minecraft:air", "minecraft:cave_air", "minecraft:void_air", 
					"minecraft:water", "minecraft:lava", "minecraft:moving_piston", 
					"minecraft:piston_head", "minecraft:frosted_ice", "minecraft:tripwire", 
					"minecraft:nether_portal", "minecraft:end_portal", "minecraft:end_gateway", 
					"minecraft:fire", "minecraft:soul_fire",
					"minecraft:bamboo_sapling", "minecraft:sweet_berry_bush",
					"minecraft:torchflower_crop", "minecraft:beetroots", "minecraft:carrots",
					"minecraft:potatoes", "minecraft:cave_vines", "minecraft:cave_vines_plant",
					"minecraft:kelp_plant", "minecraft:lava_cauldron", "minecraft:water_cauldron",
					"minecraft:powder_snow_cauldron", "minecraft:redstone_wire",
					"minecraft:twisting_vines_plant", "minecraft:bubble_column",
					"minecraft:pitcher_crop", "minecraft:cocoa", "minecraft:weeping_vines_plant"
				]
			):
				obtainable = False

		items[item] = Item(
			item,
			namespace_id,
			stackability,
			obtainable)

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
		"firework_rocket", "firework_star", "moving_piston", "piston_head",
		"frosted_ice", "tripwire", "fire", "portal", "void_air", "cave_air",
		"heavy_core", "sniffer_egg", "vault", "tall_seagrass", "powder_snow"
	]
	blacklist_fuzzy = [
		"netherite", "music_disc", "potion", "_helmet",
		"_chestplate", "_sword", "_pickaxe", "_leggings", "_hoe", "_axe",
		"_horse_armor", "head", "map", "shovel", "boots", "_book", "bed",
		"stew", "soup", "pattern", "_bucket", "_minecart", "_a_stick",
		"_anvil", "gold", "boat", "shulker_box", "bell", "void", "command",
		"skull", "_cake", "gilded", "_wall_"
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
		32: [
			"_furnace",
		],
		16: [
			"ender_pearl", "snowball", "bucket", "honey_bottle",
			"_banner", "_sign", "beacon", "nether_star", "end_crystal",
			"armor_stand", "redstone_block", "iron_block", "ender_chest",
			"_ore", "name_tag", "phantom_membrane", "respawn_anchor",
			"wither_rose", "sculk_"
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
		
		# Check blacklist
		if item_data.id in blacklist:
			log("Banned (blacklist)", item_data.id)
			items.pop(item_name)
			continue
			
		# Check blacklist_fuzzy
		is_banned_fuzzy = False
		for banned_item_fuzzy in blacklist_fuzzy:
			if banned_item_fuzzy in item_data.id:
				log("Banned (blacklist_fuzzy)", banned_item_fuzzy)
				items.pop(item_name)
				is_banned_fuzzy = True
				break
		if is_banned_fuzzy:
			continue
			
		# Check obtainable
		if not item_data.obtainable:
			log("Banned (unobtainable)", "unobtainable")
			items.pop(item_name)
			continue
			
		# Check stackability
		if item_data.stackability == 1:
			log("Banned (unstackable)", "unstackable")
			items.pop(item_name)
			continue

		# Process whitelist/custom stackability and costs
		if is_valid(item_data.id, item_counts) or is_valid_fuzzy(
			item_data.id,
			item_counts_fuzzy,
			item_costs_fuzzy,
			{None:whitelist_fuzzy}
		):
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
	return items

def create_folder(folder_name: str):
	if not os.path.isdir(folder_name):
		os.makedirs(folder_name)

def clear_folder(path: str):
	if os.path.exists(path):
		for root, dirs, files in os.walk(path, topdown=False):
			for file in files:
				os.remove(os.path.join(root, file))
			for dir in dirs:
				os.rmdir(os.path.join(root, dir))

def write_pack_mcmeta(path: str):
	data = {
		"pack": {
			"min_format": 107,
			"max_format": 107,
			"description": "Poisonous potato custom crafting pack."
		}
	}
	with open(os.path.join(path, "pack.mcmeta"), "w", encoding="utf8") as file:
		json.dump(data, file, indent=4)

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
	
	ingredients = [item.namespace_id]
	for _ in range(item.cost):
		ingredients.append("minecraft:poisonous_potato")
		
	if len(ingredients) > 9:
		return

	data = {
		"type": "crafting_shapeless",
		"ingredients": ingredients,
		"result": {
			"id": item.namespace_id,
			"count": item.stackability
		},
		"group": "potato_duplication"
	}

	with open(path, "w", encoding="utf8") as file:
		json.dump(data, file, indent=4)


def main():
	# url = "https://joakimthorsen.github.io/MCPropertyEncyclopedia/data/item_data.json"
	url = "https://joakimthorsen.github.io/MCPropertyEncyclopedia/data/block_data_experimental.json"
	minecraft_items = get_minecraft_items(url)
	filtered_items = filter_items(minecraft_items.copy())
	# print(minecraft_items)
	print(f"{len(filtered_items)} / {len(minecraft_items)} items are valid for potato duplication")
	# print(filtered_items["Emerald"])
	# print(filtered_items["Ender Pearl"])
	# print(filtered_items["Beacon"])
	# print(filtered_items["Block of Emerald"])
	# print(filtered_items["Warden Spawn Egg"])
	# print(filtered_items["Sponge"])
	
	clear_folder("dump")
	
	folder = "dump/data/minecraft/recipe/potato_duplication"
	create_folder(folder)
	
	write_pack_mcmeta("dump")
	
	for _, item in filtered_items.items():
		#print(item)
		write_item_to_json_file(item, folder)
	zip_folder(folder.split("/", maxsplit=1)[0], "potato_duping_datapack_v107.zip")



if __name__ == "__main__":
	main()

